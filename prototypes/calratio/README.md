# CalRatio one-file feasibility prototype

This prototype accompanies [issue #8](https://github.com/gordonwatts/iris-hep-llm-performance/issues/8).
Read [the status note](../../spec/calratio-feasibility-status.md) first. The
current result demonstrates raw extraction on a collision-data positive control;
it does not establish nominal CalRatio ABCD feasibility. No region-A observation,
tag/probe assignment, h/n plane, closure result or limit is produced.

## Environment and local configuration

Run from the repository root with Python 3.12 and `uv`:

```powershell
uv sync --project prototypes/calratio --locked
$config = Join-Path $env:USERPROFILE 'servicex.yaml'
```

Supply your own ServiceX client configuration outside the checkout; never commit
it. AF MCP credentials and the Python client configuration are separate.
`uv.lock` freezes the client environment; the evidence records the actual hosted
transformer image separately.

Bulk-root precedence is `--data-root`, then `IRIS_HEP_DATA_DIR`, then `[data].root`
in the repository's ignored `data.local.toml`. The directory must already exist
and be accessible. There is no checkout fallback. Deliveries, ServiceX caches,
attempt metadata, full sanitized logs and diagnostics go under
`<data-root>/calratio/<run-id>/`. Each attempt records the resolved root and
configuration source. Keep `.venv` and the uv package cache on fast local storage.
On WSL, supply a verified mount path explicitly; Windows drive paths are rejected.

## New bounded attempt

Choose a fresh run ID. Existing probe directories are never overwritten:

```powershell
uv run --project prototypes/calratio --locked python prototypes/calratio/probe.py run --probe smoke --config $config --run-id issue8-review-01
```

The DID is read from `spec/calratio-probe-samples.yaml`. Every query uses
`NFiles=1`, with no event or object cuts. The smoke query retrieves run, luminosity
block, event ID and aligned jet pT, eta, phi, energy and mass. A successful control
must contain events and jets, unique event keys, aligned arrays and finite values.

After inspecting the smoke attempt, run the separate raw-input probes:

```powershell
foreach ($probe in @('calo-validity', 'calo-sampling', 'calo-emfrac', 'tracks', 'track-hits')) {
    uv run --project prototypes/calratio --locked python prototypes/calratio/probe.py run --probe $probe --config $config --run-id issue8-review-01
    if ($LASTEXITCODE -ne 0) { break }
}
```

`calo-emfrac` is explicitly exploratory. It never converts EMFrac to h.
`calo-collection` is a separate source-like `AntiKt4LCTopoJets` storage test; its
recorded hosted failure is unresolved. Do not automatically resubmit failures or
infer missing content from them. Make at most two informed repairs per failed
probe, recording the change and original request. No PHYS/specialist fallback
has been executed or silently substituted.

The dataset-level `NFiles=1` choice is not a guarantee of the same selected file
on a later remote request. The frozen run records the actual file identity and
checksum. Local replay is the deterministic reproduction path for those results.

## Replay the recorded deliveries

The initial retained run is `issue8-20261109`. With that run under the configured
bulk root, replay each successful probe without credentials or network access:

```powershell
foreach ($probe in @('smoke', 'calo-validity', 'calo-sampling', 'calo-emfrac', 'tracks', 'track-hits')) {
    uv run --project prototypes/calratio --locked python prototypes/calratio/probe.py replay --run-id issue8-20261109 --probe $probe
    if ($LASTEXITCODE -ne 0) { break }
}
```

Replay reopens the ROOT tree and compares its checksum, observed types, entries,
finite/range summaries, event-key uniqueness and collection alignment against
`attempt.json`. Original paths are rebased under the configured root when a run
is copied to another host. ROOT files are bulk artifacts, excluded from the PR.

Read-only remote diagnostics for an existing request:

```powershell
uv run --project prototypes/calratio --locked python prototypes/calratio/probe.py diagnose --run-id issue8-20261109 --request-id 5cc8fe4b-b956-4c5b-b389-b0eaea4764b3 --config $config
```

The collector saves an allowlist of provenance fields. Full ServiceX status
models contain object-store credentials and must never be dumped. Client logs
remove configuration secrets, JWTs and HTTP URLs; signed cached URLs are removed
after each attempt. Replay uses delivered local paths rather than cached URLs.

## Review checkpoint and validation

`requirements.json` is the bounded inventory. `checkpoint.py` rebuilds the
Markdown table, compact evidence ledger and `handoff.json` from retained attempts
and the sanitized diagnostics collected with `diagnose`. It compares keys and
native collection sizes across the same file without computing either ABCD axis.
It requires the six successful raw-input deliveries from this investigation.
The bulk handoff also keeps byte-exact input snapshots. Source hashes in the
handoff normalize line endings for checkout portability; the original per-probe
code/input hashes and bulk checksums describe raw bytes. A specification or sample
change beyond line endings requires reconciliation before rebuilding evidence.

```powershell
uv run --project prototypes/calratio --locked python prototypes/calratio/checkpoint.py --run-id issue8-20261109
uv run --project prototypes/calratio --locked python -m unittest discover -s prototypes/calratio -p test_probe.py -v
```

The existing source-mapping skill's structural validator is also used:

```powershell
uv run --project prototypes/calratio --locked python .work/analysisbase/plugins/atlas-analysis/skills/analysis-data-sources/scripts/validate_evidence.py --workspace prototypes/calratio
```

That validator belongs to the separately versioned marketplace checkout recorded
in `handoff.json`; it is not vendored here. The unit tests use small synthetic
ROOT files only to test safeguards, never as real-data extraction evidence.

The current handoff is an **initial frozen checkpoint**, not a claim that two
working days have elapsed. The two-day final review gate remains pending. Resume
only bounded investigation of the recorded blockers; freeze unfinished work at
that gate. Keep the PR draft until Gordon explicitly approves it; do not merge.
