# Specification benchmark stages

`spec-tests.yaml` runs each question in an isolated workspace. Question order
does not transfer artifacts or establish dependencies.

1. `spec-from-old-analysis-modified` produces the Run 3 `specification.md`.
   `calratio-abcd-spec.md` is the current saved specification on main.
2. `ntuple-leaves-from-spec` uses `analysis-data-sources` to produce a tested
   tier/accessor contract and, on success, a ServiceX smoke file.
3. `dataset-ids-from-data-sources` uses a hash-matched specification and that
   contract to produce the required Rucio DID manifest.

The legacy `datasets-from-spec` discovery question from main is retained.
The new manifest benchmark currently uses the frozen trio under
`dataset-discovery-fixture/`, captured before main's specification was updated.
That snapshot intentionally tests discovery against incomplete, older evidence;
its specification must not be mixed with the current Run 3 specification.

The frozen `data-sources.md` and `data-source-evidence.json` were generated
by rerunning stage 2 on 2026-10-22 with `gpt-6.1-sol:medium`. They contain 69
requirements (65 unverified and four backups), with five evidence records.
No event access was verified: that run lacked ServiceX configuration and catalog
tools. These are real, incomplete upstream outputs for dataset discovery; their
tier proposals are not certified analysis readiness.

The local report stem is
`results/spec-tests/data-source-rerun-datasets-from-spec-gpt-6-1-sol-medium`.
Both required files were collected and passed `validate_evidence.py`; the runner
returned exit 1 solely because the old optional `*.ipynb` copy-back pattern had
no match. That older run collected the two mapping deliverables. The newer
`ntuple-leaves-from-spec` question also requests a genuine ServiceX smoke file.

For a fresh mapping, run stage 2, then replace all three files in
`dataset-discovery-fixture/` together: the exact specification supplied to that
run and its two returned artifacts. Before stage 3, the ledger specification
SHA-256 must match the fixture `calratio-abcd-spec.md`. Keep the real evidence,
including failures and unresolved fields. Do not substitute a hand-written
successful probe or a fabricated dataset list.

The suite enables the `atlas-af` MCP server from the UChicago plugin, as in
`uchicago-mcp.yaml`. The runner needs that server configured (or discoverable in
an enabled local plugin) on Windows and authenticated for the WSL target. Stage 2
also copies a ServiceX configuration using the path declared in its question;
update that machine-specific path when running on another host. That private
file is never committed or copied back.
A connected retry on this host stopped at preflight because `atlas-af` was not
configured; it did not replace the generated inventory.

The runner resolves MCP definitions from the **Windows** Codex configuration
before installing plugins in WSL. A marketplace URL in this YAML alone therefore
does not supply the server definition. If the host has no enabled cached plugin
defining it, add the public endpoint to the Windows `~/.codex/config.toml`:

```toml
[mcp_servers.atlas-af]
url = "https://mcp.af.uchicago.edu/mcp"
```

Configure and sign in on the selected WSL target too:

```powershell
wsl -d Ubuntu -- bash -lc 'codex mcp add atlas-af --url https://mcp.af.uchicago.edu/mcp'
# If it is already configured but needs a login:
wsl -d Ubuntu -- bash -lc 'codex mcp login atlas-af'
```

Complete the browser sign-in when prompted. The runner selectively copies the
target's stored MCP login into its isolated environment; no token belongs in
this YAML or the returned evidence. A preflight failure before model execution
does not evaluate the dataset skill.

## Live dataset-table validation

On 2026-10-23, the `dataset-ids-from-data-sources` question completed with
`gpt-6.1-sol:medium` in 1,281 seconds (about 21 minutes), exit code 0. The isolated
`atlas-af` OAuth preflight passed after completing `codex mcp login atlas-af` in
Ubuntu. The earlier trial stopped at login preflight and did not run the model.

The local result stem is
`results/spec-tests/dataset-table-trial-3-dataset-ids-from-data-sources-gpt-6-1-sol-medium`;
the copied deliverable has suffix `.datasets.md`. Results remain local under
the existing ignored `results/` directory.

The returned table has 201 rows: 167 unique scoped DIDs and 34 unresolved entries.
Inspection found eight columns in every row, no wildcards/placeholders in DID
cells, and all 69 upstream requirement IDs in the reconciliation. The output
keeps catalog identity separate from usable production and verified accessors,
flags empty containers and partial production, and distinguishes Central Page
baseline membership from a uniquely established default.

This is a successful discovery-workflow test, not complete analysis readiness.
The output retains gaps for all 13 exact signal mass points, special-stream
roles/tiers, approved year/GRL/trigger exposure, production-tag impact checks,
and several optional-background and field-compatibility questions. Empty
containers and provisional candidates must not be treated as ready inputs.
No new ServiceX field verification was performed by this discovery stage.

### Audit of trial 3 and tightened selection contract

The 201-row result was a discovery inventory, not a minimal required-input list.
There were no exact DID duplicates or repeated (DSID, campaign) pairs. Its 167
resolved identities comprised four annual Main containers, three empty delayed
containers, and 160 MC entries (40 DSIDs across four campaigns). The MC split
was 40 multijet validation inputs and 120 conditional contamination-audit inputs:
84 V+jets, 12 ttbar and 24 single-top. The specification makes the latter audit
conditional; including all of them in the main table overstates required scope.
Campaigns and disjoint generator slices must not simply be deleted as duplicates.
They need an explicit year/exposure mapping and filter/normalization evidence.

The 34 unresolved rows also mixed different kinds of work: 13 exact signal mass
points, 12 special-control rows expanded over four assumed years, and nine other
scope/retention/audit/metadata entries. ABCD regions and some single-jet controls
can potentially share a physical source, subject to trigger, skim and overlap
checks. Empty/unpaired/random controls are not established skims of Main. A skim
cannot recover events or fields absent from its parent. Different signal masses
are not skim substitutes, and unsuccessful discovery does not prove a production
is absent. GRLs, conditions, normalization and joins are dependencies rather than
additional event datasets.

The revised skill and question require a role-to-source plan before expansion,
separate conditional families and rejected candidates, classify missing-source
relationships, and consolidate shared unknown-year blockers. The upstream
`analysis-data-sources` skill now carries these distinctions forward; the existing
generated fixtures remain unchanged, testing compatibility with older ledgers.
Shared catalog/provenance evidence and requirement groups should be written once
rather than repeating full metadata and accessor definitions for every sample.

Scientific acceptance criteria for the rerun are: preserve all 13 signal pairs
and all 69 requirement IDs; keep inactive EWK/top families out of required inputs;
exclude empty containers from selected coverage; distinguish selections and
external dependencies from unresolved production; expose year/campaign assumptions;
and retain honest field-access limitations. A shorter file alone is not success.

Trial 4 completed in 929 seconds with exit code 0. Its 47 KB manifest (versus
404 KB previously) contains 11 unique candidate sources, all 69 requirement IDs
and all 13 signal pairs. Inactive EWK/top inputs and the empty delayed container
are outside the required-source table. It uses an explicitly provisional
2022/mc23a scenario: the reduction from four campaigns to one is a scope
assumption, not deduplication. The report verifies identical members for the
short/full-tag aliases of each of the ten multijet containers.

Scientific review found a production-status regression despite successful file
collection: the selected r14622 MC candidates lacked the tag's muon-trigger
warning. A fresh AMI tag lookup reports invalid status, while a newer official
sample advisory qualifies applicability by sample size. Neither blanket rejection
nor catalog VALID status settles dataset/task-specific impact. The skill and
canonical question now explicitly require production-advisory checks independently
of the central physics-sample defaults. A focused refinement run uses the trial-4
manifest as dated discovery evidence and checks this correction without repeating
the unchanged data membership inventory. It is not a second independent full
discovery run.

The merge with current main preserves its revised Run 3 specification and
`ntuple-leaves-from-spec` test. The earlier matched discovery inputs were moved
together into `dataset-discovery-fixture/`; schema, staged paths and hashes pass,
and all 11 site suite-loading integration checks pass with four spec questions.

The `.gitattributes` entries preserve the specification's CRLF bytes and the
generated outputs' LF bytes, so the recorded specification hash also validates
after a fresh checkout.

```powershell
uvx --from git+https://github.com/gordonwatts/test-wsl2-llm.git test-wsl2-llm template run .\spec-tests.yaml ntuple-leaves-from-spec
# Copy data-sources.md and data-source-evidence.json from the returned artifacts
# plus its exact specification into .\spec\dataset-discovery-fixture\, then:
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
