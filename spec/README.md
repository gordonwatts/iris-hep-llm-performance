# Specification benchmark stages

`spec-tests.yaml` runs each question in an isolated workspace. Question order
does not transfer artifacts or establish dependencies.

1. `spec-from-old-analysis-modified` produces `specification.md` from the paper.
   `calratio-abcd-spec.md` is the existing saved specification used below.
2. `datasets-from-spec` (the existing question ID) uses `analysis-data-sources`
   to produce the Run 3 tier/accessor contract: `data-sources.md` and
   `data-source-evidence.json`.
3. `dataset-ids-from-data-sources` uses that contract and the same specification
   to produce `datasets.md`, a Markdown table of all required analysis-tier
   Rucio DIDs and official central background recommendation evidence.

The checked-in `data-sources.md` and `data-source-evidence.json` were generated
by rerunning stage 2 on 2026-10-22 with `gpt-6.1-sol:medium`. They contain 69
requirements (65 unverified and four backups), with five evidence records.
No event access was verified: that run lacked ServiceX configuration and catalog
tools. These are real, incomplete upstream outputs for dataset discovery; their
tier proposals are not certified analysis readiness.

The local report stem is
`results/spec-tests/data-source-rerun-datasets-from-spec-gpt-6-1-sol-medium`.
Both required files were collected and passed `validate_evidence.py`; the runner
returned exit 1 solely because the old optional `*.ipynb` copy-back pattern had
no match. The test now collects only its two required deliverables.

For a fresh mapping, run stage 2, then copy its two returned artifacts into this
directory before running stage 3. Use outputs from the same run and specification; the ledger's
specification SHA-256 must match `calratio-abcd-spec.md`. Keep the real evidence,
including failures and unresolved fields. Do not substitute a hand-written
successful probe or a fabricated dataset list.

The suite enables the `atlas-af` MCP server from the UChicago plugin, as in
`uchicago-mcp.yaml`. The runner needs that server configured (or discoverable in
an enabled local plugin) on Windows and authenticated for the WSL target. Stage 2
also copies the existing `~/servicex.yaml` configuration, as in the other
ServiceX benchmarks. That private file is never committed or copied back.
A connected retry on this host stopped at preflight because `atlas-af` was not
configured; it did not replace the generated inventory.

The `.gitattributes` entries preserve the specification's CRLF bytes and the
generated outputs' LF bytes, so the recorded specification hash also validates
after a fresh checkout.

```powershell
uvx --from git+https://github.com/gordonwatts/test-wsl2-llm.git test-wsl2-llm template run .\spec-tests.yaml datasets-from-spec
# Copy data-sources.md and data-source-evidence.json from the returned artifacts
# into .\spec\, then:
uvx --from git+https://github.com/gordonwatts/test-wsl2-llm.git test-wsl2-llm template run .\spec-tests.yaml dataset-ids-from-data-sources
```

The AnalysisBase marketplace is pinned to the companion skill PR branch so the
new question exercises its analysis-ready manifest behavior. After that PR is
merged, this pin can move to the merged revision.

Review the resulting table for complete scoped DIDs, catalog existence,
applicable central nominal recommendations, required sample/period coverage,
duplicate or overlapping productions, and field compatibility scoped to actual
probe evidence. Catalog lookup success does not establish extraction readiness.
Blocked searches must return unresolved rows and an incomplete conclusion. The runner's
built-in validators do not validate this table's scientific claims; collecting
the files alone is not a passing scientific evaluation.
