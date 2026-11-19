"""Build the compact evidence ledger from retained, sanitized run artifacts."""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Annotated

import awkward as ak
import numpy as np
import typer
import uproot

from probe import HERE, REPO, data_root, run_dir, sha, write_json

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


def loaded(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_source_sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def keys(arrays):
    return np.rec.fromarrays([ak.to_numpy(arrays[n]) for n in ("run", "lb", "event")])


def alignment(records):
    """Check same-file event identities and native collection sizes; no h or n."""
    arrays = {}
    for record in records:
        if record["status"] != "succeeded":
            continue
        with uproot.open(record["files"][0]) as f:
            tree = f[record["observations"][0]["tree"]]
            fields = ["run", "lb", "event"]
            if record["id"] in ("smoke", "tracks", "track-hits", "calo-emfrac", "calo-sampling", "calo-validity"):
                fields += [n for n in tree.keys() if n.startswith(("jet_", "track_"))]
            arrays[record["id"]] = tree.arrays(fields, library="ak")
    baseline = keys(arrays["smoke"])
    result = {"same_event_order_as_smoke": {name: bool(np.array_equal(keys(a), baseline))
                                           for name, a in arrays.items()}}
    jet_counts = ak.num(arrays["smoke"].jet_pt, axis=1)
    result["same_jet_counts_as_smoke"] = {name: bool(ak.all(ak.num(a[next(n for n in a.fields if n.startswith("jet_"))], axis=1) == jet_counts))
        for name, a in arrays.items() if name.startswith("calo-")}
    result["same_track_counts_hits_kinematics"] = bool(ak.all(
        ak.num(arrays["tracks"].track_pt, axis=1) == ak.num(arrays["track-hits"].track_npixel, axis=1)))
    sampling = arrays["calo-sampling"].jet_sampling
    lengths = ak.to_numpy(ak.flatten(ak.num(sampling, axis=2)))
    result["sampling_vector_lengths"] = {str(int(x)): int((lengths == x).sum()) for x in np.unique(lengths)}
    result["negative_sampling_values"] = int(ak.sum(sampling < 0))
    emfrac = arrays["calo-emfrac"].jet_emfrac
    result["emfrac_outside_0_1"] = int(ak.sum((emfrac < 0) | (emfrac > 1)))
    result["limitation"] = "Same file/native collection order only; no cross-tier join, physical object matching, axis definition, region flags or A yield."
    return result


def markdown_escape(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


@app.command()
def checkpoint(
    run_id: Annotated[str, typer.Option()],
    data_root_override: Annotated[Path | None, typer.Option("--data-root")] = None,
):
    """Rebuild the bounded inventory and freeze a reproducible review checkpoint."""
    root, _ = data_root(data_root_override)
    work = run_dir(root, run_id)
    records = sorted([loaded(p) for p in work.glob("*/attempt.json")], key=lambda r: r["id"])
    for name, field in (("calratio-abcd-spec.md", "specification_sha256"),
                        ("calratio-probe-samples.yaml", "sample_manifest_sha256")):
        snapshot = work / name
        current = REPO / "spec" / name
        if not snapshot.exists():
            if any(r[field] != sha(current) for r in records):
                raise ValueError("Current input differs from original probe input; reconcile before checkpointing")
            snapshot.write_bytes(current.read_bytes())
        if (any(r[field] != sha(snapshot) for r in records)
                or normalized_source_sha(current) != normalized_source_sha(snapshot)):
            raise ValueError("Specification/sample changed; existing probes cannot be silently reused")
    probes = []
    for record in records:
        probe = {k: record[k] for k in ("id", "status", "transport", "timestamp_utc", "did", "nfiles", "cuts",
                  "request_ids", "code_sha256", "query_sha256", "specification_sha256", "sample_manifest_sha256")}
        probe["software_ref"] = "runtime"
        probe["query"] = record["query"]
        probe["query_language"] = "func_adl normalized AST unparse (including metadata)"
        probe["artifact"] = f"{record['id']}/attempt.json"
        for request in record["request_ids"]:
            diagnostic = loaded(work / (request + "-diagnostics.json"))
            probe["backend_image"] = diagnostic["status"]["image"]
            probe["query"] = diagnostic["status"]["selection"]
            probe["query_language"] = "QASTLE; exact submitted selection from ServiceX status"
            probe["input_files"] = [r["file-path"].split("/")[-1] for r in diagnostic["results"]]
            probe["remote_counts"] = {k: diagnostic["status"][k] for k in
                                      ("files", "files_completed", "files_failed", "files_remaining")}
        if record["status"] == "succeeded":
            observation = dict(record["observations"][0])
            observation["file"] = Path(observation["file"]).relative_to(work).as_posix()
            # Drop irrelevant unit labels from generic inspector; table supplies field units.
            observation.pop("units", None)
            probe["observations"] = observation
            probe["physics_equivalence"] = "unverified (raw storage test on positive-control sample)"
        else:
            probe["error_category"] = "hosted transform failure; cause unclassified"
            probe["error"] = record.get("error")
            probe["decisive_evidence"] = "Remote: 1 file failed, 0 completed. Per-file results omit worker error. Client reported No ROOT files delivered after a callback exception."
            probe["positive_control_id"] = "smoke"
            probe["next_action"] = "Inspect worker error for this request before changing accessor or declaring missing content; no automatic resubmission."
        probes.append(probe)
    evidence_ids = {p["id"] for p in probes}
    requirements = []
    for row in loaded(HERE / "requirements.json"):
        r = dict(row)
        r["probe_ids"] = [x for x in r.pop("probes") if x in evidence_ids]
        r["depends_on"] = {"ratio-h": ["calo-components", "calo-validity"],
                           "cone-count": ["track-kinematics", "track-quality"],
                           "roles": ["jet-kinematics", "ratio-h", "cone-count", "trigger", "cleaning", "timing"]}.get(r["id"], [])
        r["status"] = "verified" if r["id"] == "identity" else "backup" if r.get("backup_for") else "unverified"
        r["limitation"] = r["next"]
        r["extraction_status"] = "inspected raw values" if r["probe_ids"] else "not probed; explicit blocker/next action"
        if r["id"] in ("ratio-h", "cone-count"):
            r["extraction_status"] = "raw dependencies inspected; derived nominal quantity not evaluated"
        requirements.append(r)
    table_counts = dict(Counter(r["status"] for r in requirements))
    ledger = {"schema_version": 1,
        "specification": {"path": "../../spec/calratio-abcd-spec.md", "sha256": sha(REPO / "spec/calratio-abcd-spec.md")},
        "models": {"steering": "Codex based on GPT-6; exact deployed model identifier unavailable", "workers": [],
                   "roles": "All work performed directly; no model/delegation comparison claimed."},
        "artifact_base": f"<data-root>/calratio/{run_id}/",
        "runtime": records[0]["versions"], "requirements": requirements, "probes": probes,
        "counts": table_counts, "cross_probe_checks": alignment(records),
        "catalog_evidence": "catalog-evidence.json",
        "unresolved": ["Calorimeter jet definition/calibration and valid E_H/E_EM construction",
                       "Reference-to-Run-3 track quality and all-track completeness after upstream thinning",
                       "Period-specific single-candidate trigger, tag-only support, matching, plateau and exposure",
                       "GRL/PV/timing/cleaning/MET/BIB common selection and independent/special-stream sources",
                       "LC-topo hosted failure cause; exact-release configuration access",
                       "Two-working-day review gate has not elapsed; this is an initial frozen checkpoint."]}
    write_json(HERE / "data-source-evidence.json", ledger)
    lines = ["# CalRatio bounded extraction contract", "", "Scope: issue #8 one-file feasibility only, against the current specification. "
             "Successful raw extraction and nominal physics equivalence are recorded separately. "
             "The 69-row historical full-analysis fixture is not promoted to current evidence.", "",
             f"Inventory: {len(requirements)} rows; " + ", ".join(f"{n} {s}" for s, n in sorted(table_counts.items())) + ".",
             "", "| ID / columns | Use / specification | Scope and type | Units | Proposed source / evidence | Nominal status; blocker and next action |",
             "| --- | --- | --- | --- | --- | --- |"]
    for r in requirements:
        values = [r["id"] + " / " + r["column"], r["purpose"] + "; " + r["spec_ref"],
                  r["scope"], r["units"], r["source"] + "; " + (", ".join(r["probe_ids"]) or "not probed"),
                  r["status"] + "; " + r["next"]]
        lines.append("| " + " | ".join(markdown_escape(v) for v in values) + " |")
    lines += ["", "## Role-to-source plan", "",
        "All period choices are unresolved. The one data23 run is an extraction control, not a selected analysis year. "
        "The same Main parent could support several trigger selections; their overlap and exposure require explicit checks.", "",
        "| Role (spec Data Samples) | Requiredness / source kind | Candidate and compatibility | Next action |",
        "| --- | --- | --- | --- |",
        "| Extraction positive control | Prototype-required event source | Exact supplied PHYSLITE DID; identity and raw fields inspected | No nominal acceptance claim |",
        "| Nominal ABCD | Required selection on collision data; parent relationship unverified | Positive-control Main DID is a candidate only | Confirm periods, single-tag trigger, common selection and upstream h/n retention |",
        "| Inclusive-jet closure/efficiency | Required independent selection/event source; parent relationship unverified | No additional DID selected | Establish jet trigger, prescales, overlaps and retained sidebands |",
        "| Empty, unpaired, zero-bias | Required separate event sources; shared-parent relationships unknown | No catalog-confirmed source chosen | Resolve bunch categories, relaxed timing/PV, exposure and overlay metadata |",
        "| Signal | Required for later inference; outside bounded extraction | No tier or dataset approved; preserve 13 exact mass pairs | Resolve generation/lifetimes and detector simulation separately |",
        "| QCD and prompt MC | Required auxiliary QCD / conditional prompt audit; outside bounded extraction | No nominal MC chosen | Use current official recommendations after data-tier contract is resolved |",
        "| GRL, lumi, menus, prescales | Required external metadata | Source/version unresolved | Retrieve period-specific accounting; do not use one-file denominators |", "",
        "## Interpretation and joins", "",
        "`identity` is verified only for the tested positive-control file. All other nominal requirements remain unverified; "
        "`emfrac-backup` is a separately labelled exploratory option with no nominal h conversion. "
        "Raw access succeeds for standard AnalysisJets, sampling energies, EM fraction and retained tracks/hit summaries. "
        "The exact QASTLE, request IDs, transformer images, types/counts/ranges and original code hashes are in the JSON.", "",
        "Cross-probe comparisons check unique run/lb/event keys and native collection sizes on the same input file. "
        "They do not demonstrate a PHYSLITE/PHYS join. Any future cross-tier augmentation must establish common AOD parents, "
        "stream/skim coverage, unique event keys and overlap/missing-event counts, then object matching with angular/energy "
        "tolerances, ambiguity/unmatched rates and calibration mapping. Row position and DSID are insufficient.", "",
        "The failed LC-topo transform does not prove absence. No PHYS/specialist transform was submitted because there is "
        "no demonstrated content gap yet. Current-main documentation motivates a thinning investigation but cannot replace "
        "the inaccessible exact-release job configuration. Independent trigger/closure, non-collision constraints, signal "
        "acceptance, kappa and numerical limits are unestablished. No h/n plane, tag/probe roles or region-A observation was computed.", ""]
    (HERE / "data-sources.md").write_text("\n".join(lines), encoding="utf-8")
    frozen_paths = [HERE / n for n in ("probe.py", "queries.py", "checkpoint.py", "test_probe.py", "pyproject.toml", "uv.lock",
        "requirements.json", "catalog-evidence.json", "issue-snapshot.json", "data-source-evidence.json", "data-sources.md", "README.md")]
    frozen_paths += [REPO / "spec/calratio-abcd-spec.md", REPO / "spec/calratio-probe-samples.yaml", REPO / "spec/calratio-feasibility-status.md"]
    bulk_paths = sorted(work.glob("*/attempt.json")) + sorted(work.glob("*-diagnostics.json"))
    bulk_paths += [Path(r["files"][0]) for r in records if r["status"] == "succeeded"]
    bulk_paths += [work / "calratio-abcd-spec.md", work / "calratio-probe-samples.yaml"]
    handoff = {"schema_version": 1, "checkpoint_utc": datetime.now(timezone.utc).isoformat(),
        "issue": {"url": "https://github.com/gordonwatts/iris-hep-llm-performance/issues/8", "updated_at": "2026-11-10T01:26:33Z"},
        "base_commit": "9c124c3906b160d641e79081d096c30d93b6db7d", "branch": "codex/calratio-abcd-feasibility",
        "artifact_base": ledger["artifact_base"],
        "timebox": {"limit_working_days": 2, "state": "initial review checkpoint; two-day gate pending",
                    "elapsed_working_days": None, "note": "Actual initial work occurred on 2026-11-09 local time. No claim two working days elapsed; no future unattended continuation scheduled."},
        "unfinished": ledger["unresolved"], "pr_policy": "Draft until Gordon explicitly approves; never merge as part of this task",
        "hash_basis": "source_normalized_lf_sha256 uses LF-normalized UTF-8 source bytes; bulk_sha256 and original probe input/code hashes use raw bytes",
        "source_normalized_lf_sha256": {p.relative_to(REPO).as_posix(): normalized_source_sha(p) for p in frozen_paths if p.is_file()},
        "bulk_sha256": {p.relative_to(work).as_posix(): sha(p) for p in bulk_paths},
        "skills": {"analysisbase_commit": "e8e78e1c8a00b1d599888367b251851e2ee63944",
                   "iris_hep_marketplace_commit": "7f5540b7ffccab80381ace38544d00d595e0a61a",
                   "files_sha256": {str(p.relative_to(REPO / ".work")).replace("\\", "/"): sha(p) for p in [
                       REPO / ".work/analysisbase/plugins/atlas-analysis/skills/analysis-data-sources/SKILL.md",
                       REPO / ".work/analysisbase/plugins/atlas-analysis/skills/analysis-data-sources/references/evidence-contract.md",
                       REPO / ".work/analysisbase/plugins/atlas-analysis/skills/analysis-data-sources/scripts/validate_evidence.py",
                       REPO / ".work/analysisbase/plugins/atlas-analysis/skills/find-atlas-datasets/SKILL.md",
                       REPO / ".work/marketplace/iris-hep/skills/servicex/SKILL.md"] if p.is_file()},
                   "historical_fixture_spec_sha256": "448a52433f4bfcf7bc8b10ec7b264c0a036ff88717a8a253fc789cfe25e8e384"}}
    write_json(HERE / "handoff.json", handoff)
    write_json(work / "handoff.json", dict(handoff, resolved_data_root=str(root)))
    typer.echo(json.dumps({"requirements": len(requirements), "probes": len(probes), "counts": table_counts,
                           "cross_probe_checks": ledger["cross_probe_checks"]}))


if __name__ == "__main__":
    app()
