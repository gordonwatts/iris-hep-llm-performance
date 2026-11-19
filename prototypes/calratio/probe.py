"""One-file CalRatio extraction and local replay, with no analysis selections."""

import ast
import asyncio
import contextlib
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import re
import sys
import tomllib
from datetime import datetime, timezone
from typing import Annotated

import awkward as ak
import numpy as np
import typer
import uproot
import yaml

from queries import PROBES

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def data_root(override=None):
    """Do not create or silently fall back from a missing bulk root."""
    configured = override or os.environ.get("IRIS_HEP_DATA_DIR")
    source = "override" if override else "IRIS_HEP_DATA_DIR"
    if not configured:
        config = REPO / "data.local.toml"
        configured = tomllib.loads(config.read_text(encoding="utf-8"))["data"]["root"]
        source = "data.local.toml"
    root = Path(configured).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Configured bulk-data root is not a directory")
    # Explicitly reject accidental use of an untranslated Windows path under WSL.
    if sys.platform != "win32" and re.match(r"^[A-Za-z]:", str(configured)):
        raise ValueError("Translate Windows data root to WSL and verify the mount first")
    with os.scandir(root):
        pass
    return root, source


def run_dir(root, run_id):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", run_id):
        raise ValueError("run-id must be a short directory name")
    return root / "calratio" / run_id


def delivery_paths(work, record):
    """Rebase original provenance paths when a retained run moves to another root."""
    original = record["data_root"].replace("\\", "/").rstrip("/") + "/calratio/" + work.name + "/"
    paths = []
    for stored in record["files"]:
        normalized = stored.replace("\\", "/")
        if not normalized.startswith(original):
            raise ValueError("Delivery path is outside its recorded run directory")
        relative = normalized[len(original):]
        if ".." in relative.split("/"):
            raise ValueError("Invalid relative delivery path")
        path = (work / relative).resolve()
        if not path.is_relative_to(work.resolve()):
            raise ValueError("Delivery path escapes current run directory")
        paths.append(path)
    return paths


class SafeLog(io.TextIOBase):
    """Buffer lines so a split write cannot leak part of a credential."""
    def __init__(self, output, secrets):
        self.output, self.secrets, self.pending = output, secrets, ""

    def clean(self, text):
        for secret in self.secrets:
            text = text.replace(secret, "[REDACTED]")
        text = re.sub(r"https?://[^\s\"'<>]+", "[URL REMOVED]", text)
        text = re.sub(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[JWT REMOVED]", text)
        return text

    def write(self, text):
        self.pending += text
        while "\n" in self.pending:
            line, self.pending = self.pending.split("\n", 1)
            self.output.write(self.clean(line) + "\n")
        return len(text)

    def flush(self):
        if self.pending:
            self.output.write(self.clean(self.pending))
            self.pending = ""
        self.output.flush()


def config_secrets(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if any(s in str(key).lower() for s in ("token", "password", "secret", "api_key")):
                if isinstance(item, str) and item:
                    yield item
            else:
                yield from config_secrets(item)
    elif isinstance(value, list):
        for item in value:
            yield from config_secrets(item)


def inspect_files(paths):
    """Only storage summaries; never compute a CalRatio axis, regions or yields."""
    observations = []
    for path in paths:
        with uproot.open(path) as f:
            trees = [x for x in f.values() if hasattr(x, "arrays")]
            if len(trees) != 1:
                raise ValueError("Expected exactly one delivered event tree")
            tree = trees[0]
            arrays = tree.arrays(library="ak")
            columns = {}
            for name in arrays.fields:
                values = arrays[name]
                flat = ak.to_numpy(ak.flatten(values, axis=None))
                finite = np.isfinite(flat)
                columns[name] = {"type": str(ak.type(values)), "root_type": tree[name].typename,
                    "values": len(flat), "finite": int(finite.sum()),
                    "nonfinite": int((~finite).sum()),
                    "min": flat[finite].min().item() if finite.any() else None,
                    "max": flat[finite].max().item() if finite.any() else None}
                if name.startswith(("jet_", "track_")):
                    counts = ak.to_numpy(ak.num(values, axis=1))
                    columns[name]["nonempty_events"] = int((counts > 0).sum())
            aligned = {}
            for prefix in ("jet_", "track_"):
                names = [n for n in arrays.fields if n.startswith(prefix)]
                if names:
                    first = ak.num(arrays[names[0]], axis=1)
                    aligned[prefix] = all(bool(ak.all(ak.num(arrays[n], axis=1) == first)) for n in names)
            keys = list(zip(ak.to_list(arrays.run), ak.to_list(arrays.lb), ak.to_list(arrays.event)))
            observations.append({"file": str(path), "sha256": sha(path), "bytes": path.stat().st_size,
                "tree": tree.name, "entries": tree.num_entries, "columns": columns,
                "alignment": aligned, "unique_event_keys": len(set(keys)),
                "duplicate_event_keys": len(keys) - len(set(keys)),
                "units": {"jet_pt,e,m": "MeV / 1000 -> GeV", "track_pt": "MeV / 1000 -> GeV",
                          "eta": "dimensionless", "phi": "rad", "emfrac": "dimensionless"}})
    return observations


def request_ids(cache):
    ids = set()
    for path in cache.rglob("db.json"):
        try:
            text = path.read_text(encoding="utf-8")
            ids.update(re.findall(r'"request_id"\s*:\s*"([a-fA-F0-9-]+)"', text))
        except OSError:
            pass
    return sorted(ids)


def scrub_cache(cache, cleaner):
    # ServiceX stores signed URLs even for local delivery. Local replay uses the
    # explicit file paths in attempt.json instead of those cached URLs.
    for pattern in ("*.json", "*.log"):
        for path in cache.rglob(pattern):
            text = path.read_text(encoding="utf-8")
            cleaned = cleaner.clean(text)
            if text != cleaned:
                path.write_text(cleaned, encoding="utf-8")


def public_diagnostics(status, results):
    """Service responses contain credentials; keep public provenance only."""
    fields = {"request_id", "did", "did_id", "title", "selection", "image",
              "result_format", "status", "app_version", "files", "files_completed",
              "files_failed", "files_remaining", "submit_time", "finish_time"}
    result_fields = {"request-id", "file-path", "transform_status", "transform_time",
                     "total-events", "total-bytes", "created_at"}
    return {"status": {k: v for k, v in status.items() if k in fields},
            "results": [{k: v for k, v in row.items() if k in result_fields}
                        for row in results.get("results", [])]}


@app.command()
def run(
    probe: Annotated[str, typer.Option(help="See queries.py for the bounded probe inventory")],
    config: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    run_id: Annotated[str, typer.Option()],
    data_root_override: Annotated[Path | None, typer.Option("--data-root")] = None,
):
    """Submit exactly one uncut file; preserve a sanitized attempt even on failure."""
    from servicex import deliver, ServiceXSpec, Sample, dataset
    from servicex.servicex_client import ProgressBarFormat

    if probe not in PROBES:
        raise typer.BadParameter("Unknown probe")
    root, source = data_root(data_root_override)
    work = run_dir(root, run_id)
    work.mkdir(parents=True, exist_ok=True)
    if probe != "smoke":
        control = work / "smoke" / "attempt.json"
        if not control.is_file() or json.loads(control.read_text())["status"] != "succeeded":
            raise typer.BadParameter("Inspect a successful smoke control in this run before axis probes")
    folder = work / probe
    folder.mkdir(exist_ok=False)
    cache = folder / "cache"
    config = config.resolve()
    secrets = list(config_secrets(yaml.safe_load(config.read_text(encoding="utf-8"))))
    sample_file = REPO / "spec/calratio-probe-samples.yaml"
    did = yaml.safe_load(sample_file.read_text())["samples"][0]["did"]
    record = {"id": probe, "status": "blocked", "transport": "servicex",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "data_root": str(root), "data_root_source": source,
        "did": did, "nfiles": 1, "cuts": "none",
        "jet_collection": "AntiKt4LCTopoJets" if probe == "calo-collection" else "AnalysisJets (PHYSLITE helper default; not used by track-only probes)",
        "specification_sha256": sha(REPO / "spec/calratio-abcd-spec.md"),
        "sample_manifest_sha256": sha(sample_file),
        "code_sha256": {p.name: sha(p) for p in (HERE / "probe.py", HERE / "queries.py", HERE / "uv.lock")},
        "versions": {n: importlib.metadata.version(n) for n in
            ("servicex", "func-adl", "func-adl-servicex-xaodr25", "uproot", "awkward", "numpy", "typer")},
        "python": platform.python_version(), "request_ids": [],
        "blinding": "No h/n combination, tag/probe selection, ABCD yields or physics plots are computed."}
    write_json(folder / "attempt.json", record)
    with (folder / "client.log").open("w", encoding="utf-8") as log:
        safe = SafeLog(log, secrets)
        try:
            with contextlib.redirect_stdout(safe), contextlib.redirect_stderr(safe):
                query = PROBES[probe]()
                record["query_ast"] = ast.dump(query.query_ast, include_attributes=False)
                record["query"] = ast.unparse(query.query_ast)
                record["query_sha256"] = hashlib.sha256(record["query_ast"].encode()).hexdigest()
                write_json(folder / "attempt.json", record)
                spec = ServiceXSpec(Sample=[Sample(Name="calratio_" + probe.replace("-", "_"),
                    Dataset=dataset.Rucio(did), NFiles=1, Query=query)])
                output = deliver(spec, config_path=str(config), cache_dir=str(cache),
                                 progress_bar=ProgressBarFormat.none)
                paths = [Path(p).resolve() for p in output[spec.Sample[0].Name]]
                if not paths:
                    raise ValueError("No ROOT files delivered")
                if len(paths) != 1:
                    raise ValueError("Expected exactly one output for NFiles=1")
                record["files"] = [str(p) for p in paths]
                record["observations"] = inspect_files(paths)
                nonempty = sum(o["entries"] for o in record["observations"]) > 0
                if not nonempty:
                    raise ValueError("Delivered file has no events")
                if probe == "smoke":
                    o = record["observations"][0]
                    if (not o["alignment"].get("jet_") or o["duplicate_event_keys"]
                            or o["columns"]["jet_pt"]["values"] == 0
                            or any(c["nonfinite"] for c in o["columns"].values())):
                        raise ValueError("Smoke output failed alignment/identity/finite/nonempty checks")
                record["status"] = "succeeded"
        except Exception as error:
            record["status"] = "failed"
            record["error_type"] = type(error).__name__
            record["error"] = safe.clean(str(error))
        finally:
            safe.flush()
            log_text = (folder / "client.log").read_text(encoding="utf-8")
            logged_ids = re.findall(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
                                    re.sub(r"\s+", "", log_text), re.I)
            record["request_ids"] = sorted(set(request_ids(cache) + logged_ids))
            scrub_cache(cache, safe)
            write_json(folder / "attempt.json", record)
    typer.echo(json.dumps({k: record.get(k) for k in ("id", "status", "request_ids", "error_type", "error")}))
    if record["status"] != "succeeded":
        raise typer.Exit(1)


@app.command()
def diagnose(
    run_id: Annotated[str, typer.Option()],
    request_id: Annotated[str, typer.Option()],
    config: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    data_root_override: Annotated[Path | None, typer.Option("--data-root")] = None,
):
    """Read status and per-file diagnostics without submitting another transform."""
    import httpx
    from servicex.servicex_adapter import ServiceXAdapter

    if not re.fullmatch(r"[a-f0-9-]{36}", request_id):
        raise typer.BadParameter("Expected a request UUID")
    root, _ = data_root(data_root_override)
    work = run_dir(root, run_id)
    cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
    endpoints = cfg["api_endpoints"]
    endpoint = next((x for x in endpoints if x["name"] == cfg.get("default-endpoint")), endpoints[0])
    safe = SafeLog(io.StringIO(), list(config_secrets(cfg)))

    async def fetch():
        adapter = ServiceXAdapter(endpoint["endpoint"].rstrip("/"), endpoint.get("token"))
        status = await adapter.get_transform_status(request_id)
        headers = await adapter._get_authorization()
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(adapter.url + f"/servicex/transformation/{request_id}/results", headers=headers)
            response.raise_for_status()
        # TransformStatus also contains temporary object-store credentials.
        # Retain only explicitly public provenance, never the full model dump.
        return public_diagnostics(status.model_dump(mode="json"), response.json())

    value = json.loads(safe.clean(json.dumps(asyncio.run(fetch()))))
    write_json(work / (request_id + "-diagnostics.json"), value)
    typer.echo(json.dumps({"request_id": request_id, "status": value["status"]["status"],
                           "files_failed": value["status"]["files_failed"]}))


@app.command()
def replay(
    run_id: Annotated[str, typer.Option()],
    probe: Annotated[str, typer.Option()] = "smoke",
    data_root_override: Annotated[Path | None, typer.Option("--data-root")] = None,
):
    """Reinspect local delivery; no ServiceX connection or credentials needed."""
    root, _ = data_root(data_root_override)
    folder = run_dir(root, run_id) / probe
    record = json.loads((folder / "attempt.json").read_text(encoding="utf-8"))
    if record["status"] != "succeeded":
        raise typer.BadParameter("This attempt has no successful delivery")
    paths = delivery_paths(folder.parent, record)
    observations = inspect_files(paths)
    expected = [dict(o) for o in record["observations"]]
    # Absolute paths document the original host; compare actual content on replay.
    for row in observations + expected:
        row.pop("file")
    if observations != expected:
        raise ValueError("Replay differs from frozen observations")
    typer.echo(json.dumps({"status": "matched", "files": len(paths),
                           "entries": sum(o["entries"] for o in observations)}))


if __name__ == "__main__":
    app()
