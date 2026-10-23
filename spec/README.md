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

Run stage 2, then copy its two returned artifacts into this directory before
running stage 3. Use outputs from the same run and specification; the ledger's
specification SHA-256 must match `calratio-abcd-spec.md`. Keep the real evidence,
including failures and unresolved fields. Do not substitute a hand-written
successful probe or a fabricated dataset list.

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
