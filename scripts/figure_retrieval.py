#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["typer>=0.12", "PyYAML>=6", "Pillow>=11", "pypdf>=5", "pydantic>=2"]
# ///
"""Stage private figure benchmarks and independently check returned file bytes.

No network reads or credential handling happen here. Live access remains the
model's MCP operation, recorded in its retained tool trace and evidence ledger.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tomllib
from urllib.parse import urlsplit

import typer
import yaml

REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / "spec" / "figure-retrieval-cases.json"
app = typer.Typer(no_args_is_help=True)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def normalized(value: str) -> str:
    return " ".join(value.split()).casefold()


def native(path: str | Path) -> Path:
    value = str(path)
    if os.name == "nt" and re.match(r"^/mnt/[a-z]/", value):
        value = value[5].upper() + ":/" + value[7:]
    return Path(value)


def wsl(path: Path) -> str:
    value = str(path.resolve()).replace("\\", "/")
    return "/mnt/" + value[0].lower() + value[2:] if re.match(r"^[A-Za-z]:/", value) else value


def local_file(workspace: Path, row: dict) -> Path:
    path = (workspace / row["path"]).resolve()
    path.relative_to(workspace.resolve())
    if not path.is_file() or path.stat().st_size > 25 * 1024 * 1024:
        raise ValueError("missing or oversized evidence file")
    if digest(path) != row["sha256"]:
        raise ValueError("evidence file hash mismatch")
    return path


def check_payload(path: Path, media_type: str) -> None:
    if media_type in {"image/png", "image/jpeg"}:
        from PIL import Image
        with Image.open(path) as image:
            expected = "PNG" if media_type == "image/png" else "JPEG"
            if image.format != expected or min(image.size) < 16:
                raise ValueError("wrong image format or dimensions")
            image.verify()
        with Image.open(path) as image:
            if image.convert("L").getextrema()[0] == image.convert("L").getextrema()[1]:
                raise ValueError("uniform placeholder image")
    elif media_type == "application/pdf":
        from pypdf import PdfReader
        if not path.read_bytes().startswith(b"%PDF-"):
            raise ValueError("not a PDF")
        try:
            reader = PdfReader(path)
        except Exception as error:
            raise ValueError("unreadable PDF") from error
        if reader.is_encrypted or len(reader.pages) != 1:
            raise ValueError("return a single figure, not the complete note")
        content = reader.pages[0].get_contents()
        if content is None or not content.get_data().strip():
            raise ValueError("empty PDF page")
        if not any(op in {b"Do", b"m", b"l", b"c", b"re"} for _, op in content.operations):
            raise ValueError("PDF has no figure graphics")
    else:
        raise ValueError("unsupported figure media type")


def load_targets(fixture: Path, case_id: str) -> tuple[dict, dict]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["cases"][case_id]
    target = json.loads(fixture.read_text(encoding="utf-8-sig"))["cases"][case_id]
    if target["note_id"] != catalog["note_id"] or target["figure_numbers"] != catalog["figure_numbers"]:
        raise ValueError("private fixture changes the requested note or figures")
    if not target.get("caption_hint"):
        raise ValueError("private caption/search hint required")
    if catalog.get("archived_pdf_sha256"):
        if target.get("archive_sha256") != catalog["archived_pdf_sha256"]:
            raise ValueError("private archive reference does not match the pinned PDF")
        if any(not target.get("expected_captions", {}).get(str(n)) for n in catalog["figure_numbers"]):
            raise ValueError("exact archived figure caption required")
    expected_hash = catalog.get("caption_hint_sha256")
    if expected_hash and hashlib.sha256(normalized(target["caption_hint"]).encode()).hexdigest() != expected_hash:
        raise ValueError("private caption/search hint does not match the pinned reference")
    return catalog, target


def validate_manifest(workspace: Path, fixture: Path, case_id: str) -> dict:
    """A hit, caption, filename, or blocked access never counts as retrieval.

    This checks collected files and their identity/mapping receipts. The actual
    MCP tool trace remains the independent evidence for whether calls occurred.
    """
    errors: list[str] = []
    outcomes: list[dict] = []
    try:
        catalog, target = load_targets(fixture, case_id)
        manifest = json.loads((workspace / "retrieval-evidence.json").read_text(encoding="utf-8"))
        if manifest.get("schema_version") != 1 or manifest.get("case_id") != case_id:
            raise ValueError("wrong manifest schema or case")
        rows = manifest["figures"]
        numbers = [row["number"] for row in rows]
        if sorted(numbers) != catalog["figure_numbers"] or len(set(numbers)) != len(numbers):
            raise ValueError("missing, duplicate, or unexpected figure result")
        requests = {r["id"]: r for r in manifest["requests"]}
        if len(requests) != len(manifest["requests"]):
            raise ValueError("duplicate request ID")
        used_payloads: set[str] = set()
        revisions: set[str] = set()
        hint_matches: list[int] = []
        for row in rows:
            number = row["number"]
            outcome = {"number": number, "status": row.get("status"), "passed": False}
            outcomes.append(outcome)
            try:
                if row.get("status") != "retrieved":
                    raise ValueError("figure not retrieved (" + str(row.get("status")) + ")")
                if row.get("note_id") != target["note_id"]:
                    raise ValueError("wrong note identity")
                caption = row.get("caption", "")
                if not caption or row.get("mapping_verified") is not True:
                    raise ValueError("figure-number/caption mapping unverified")
                expected_caption = target.get("expected_captions", {}).get(str(number))
                if expected_caption and normalized(caption) != normalized(expected_caption):
                    raise ValueError("caption differs from archived reference")
                receipt_path = local_file(workspace, row["mapping_receipt"])
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                if (receipt.get("note_id"), receipt.get("figure_number"), normalized(receipt.get("caption", ""))) != (
                    target["note_id"], number, normalized(caption)
                ):
                    raise ValueError("mapping receipt disagrees with note/figure/caption")
                if not receipt.get("source_record"):
                    raise ValueError("mapping receipt lacks source record locator")
                revision = row.get("source_version")
                if not revision or receipt.get("source_version") != revision:
                    raise ValueError("missing or inconsistent source document revision")
                revisions.add(revision)
                request = requests[row["retrieval_request_id"]]
                if not (request.get("tool", "").startswith("mcp__atlas_af__")
                        and request.get("stage") == "payload" and request.get("status") == "succeeded"
                        and request.get("query") and request.get("result_record")):
                    raise ValueError("missing successful MCP payload request provenance")
                locator = urlsplit(row["payload"]["source_locator"])
                if locator.scheme not in {"https", "mcp"} or locator.username or locator.password or locator.query:
                    raise ValueError("use a canonical source locator without credentials/signed query")
                payload = local_file(workspace, row["payload"])
                if payload.stat().st_size != row["payload"]["bytes"] or not payload.stat().st_size:
                    raise ValueError("empty payload or incorrect byte count")
                check_payload(payload, row["payload"]["media_type"])
                if row["payload"]["sha256"] in used_payloads:
                    raise ValueError("same payload used for distinct figures")
                used_payloads.add(row["payload"]["sha256"])
                if row["payload"].get("route") not in {"mcp_figure", "mcp_pdf_crop"}:
                    raise ValueError("archive/reference extraction is not live retrieval")
                if row["payload"]["route"] == "mcp_pdf_crop":
                    crop = row["payload"].get("crop", {})
                    if not (crop.get("source_pdf") and crop.get("page", 0) > 0
                            and len(crop.get("bbox", [])) == 4):
                        raise ValueError("PDF crop requires original PDF hash/page/bounding box")
                    from pypdf import PdfReader
                    source_pdf = PdfReader(local_file(workspace, crop["source_pdf"]))
                    page = source_pdf.pages[crop["page"] - 1]
                    x0, y0, x1, y1 = crop["bbox"]
                    width, height = float(page.mediabox.width), float(page.mediabox.height)
                    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height
                            and (x1 - x0) * (y1 - y0) < 0.95 * width * height):
                        raise ValueError("invalid or whole-page figure crop")
                if normalized(target["caption_hint"]) in normalized(caption):
                    hint_matches.append(number)
                outcome["passed"] = True
            except Exception as error:
                outcome["error"] = str(error)
                errors.append(f"figure {number}: {error}")
        if not hint_matches:
            errors.append("supplied caption/search hint was not mapped to any retrieved figure")
        if len(revisions) > 1:
            errors.append("requested figures come from different source document revisions")
        return {"passed": not errors, "case_id": case_id, "figures": outcomes,
                "caption_hint_matched_figures": hint_matches, "errors": errors,
                "scope": "file/receipt validation; independently review retained MCP trace"}
    except (ValueError, KeyError, TypeError, OSError) as error:
        return {"passed": False, "case_id": case_id, "figures": outcomes, "errors": [str(error)]}


def resolve_root(explicit: Path | None) -> Path:
    configured = {}
    if (REPO / "data.local.toml").is_file():
        configured = tomllib.loads((REPO / "data.local.toml").read_text(encoding="utf-8-sig"))
    value = explicit or os.environ.get("IRIS_HEP_DATA_DIR") or configured.get("data", {}).get("root")
    if not value or not Path(value).is_dir():
        raise ValueError("configure an existing bulk root or pass --data-root")
    return Path(value).resolve()


def prepare_run(case_id: str, fixture: Path, root: Path, run_name: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", run_name):
        raise ValueError("invalid run name")
    fixture.resolve().relative_to(root)
    _, target = load_targets(fixture, case_id)
    run = root / "figure-retrieval" / run_name
    run.mkdir(parents=True, exist_ok=False)
    (run / "workspaces").mkdir()
    inputs = run / "inputs"
    inputs.mkdir()
    # Stage the search target, never the archived PDF/reference payload.
    staged = inputs / "figure-targets.json"
    staged.write_text(json.dumps({"cases": {case_id: {k: v for k, v in target.items()
        if k in {"note_id", "figure_numbers", "caption_hint", "expected_captions"}}}}, indent=2) + "\n")
    config = yaml.safe_load((REPO / "atlas-metadata-queries.yaml").read_text(encoding="utf-8"))
    question = next(q for q in config["questions"] if q["id"] == case_id)
    contract = inputs / "figure-retrieval.md"
    contract.write_bytes((REPO / "docs/figure-retrieval.md").read_bytes())
    question["copy_files"] = [str(staged), str(contract)]
    config.update(questions=[question], output=str(run / "report"), wsl_parent=wsl(run / "workspaces"),
                  cleanup=False, repeat=1, threads=1)
    runtime = run / "run.yaml"
    runtime.write_text("# yaml-language-server: $schema=test-wsl2-llm-template.schema.json\n"
                       + yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    (run / "provenance.json").write_text(json.dumps({"case_id": case_id, "data_root": str(root),
        "private_fixture_sha256": digest(fixture), "staged_target_sha256": digest(staged),
        "contract_sha256": digest(contract), "catalog_sha256": digest(CATALOG),
        "validator_sha256": digest(Path(__file__)),
        "runtime_sha256": digest(runtime), "payloads_seeded": False,
        "public_results": False}, indent=2) + "\n")
    return runtime


def register(private_fixture: Path) -> None:
    """Register with the ordinary runner before it validates the runtime YAML."""
    from pydantic import BaseModel, ConfigDict
    from test_wsl2_llm.validation import register_validator
    class Arguments(BaseModel):
        model_config = ConfigDict(extra="forbid")
        case_id: str
    def check(result, case_id):
        evidence = validate_manifest(native(result.run.workspace_path), private_fixture, case_id)
        return evidence["passed"], json.dumps(evidence)
    register_validator("figure_retrieval", Arguments, check)


@app.command()
def validate(workspace: Path, private_fixture: Path, case_id: str):
    result = validate_manifest(workspace, private_fixture, case_id)
    typer.echo(json.dumps(result))
    raise typer.Exit(0 if result["passed"] else 1)


@app.command()
def run(case_id: str, private_fixture: Path = typer.Option(..., exists=True, dir_okay=False), data_root: Path | None = None,
        run_name: str = "figure-check", execute: bool = False):
    """Prepare a private run; --execute requires working MCP access and runner."""
    root = resolve_root(data_root)
    runtime = prepare_run(case_id, private_fixture, root, run_name)
    typer.echo(str(runtime))
    if execute:
        # Verify the Windows/WSL spelling refers to the same staged bytes.
        import subprocess
        staged = runtime.parent / "inputs/figure-targets.json"
        measured = subprocess.run(["wsl", "-d", "Ubuntu", "--exec", "sha256sum", wsl(staged)],
                                  capture_output=True, text=True, check=True, timeout=30)
        if measured.stdout.split()[0] != digest(staged):
            raise ValueError("WSL data-root mapping does not refer to the staged bytes")
        from test_wsl2_llm.cli import app as runner
        register(private_fixture)
        runner(args=["template", "run", str(runtime), case_id, "--keep-workspace"], prog_name="test-wsl2-llm")


if __name__ == "__main__":
    app()
