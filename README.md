# LLM Performance On IRIS-HEP Skills And Questions

This repo contains a few sets of benchmark questions that are used to test skill, LLM, and (eventually) MCP performance.

Browse the benchmark suites and available results on the [IRIS-HEP LLM Performance website](https://gordonwatts.github.io/iris-hep-llm-performance/).

## Usage

Currently the results aren't being stored here (they are too big). But the raw test files are. They can be run with the following command on a windows machine with `wsl2` installed and the distro's that are indicated. `uv` must also be installed on the windows side for this to work. `codex` should already be signed in on the distro you will be running these on.

The following will execute question `q1` in the `iris-hep-llm-questions.yaml` file. Use `--help` for many many more confusing options on how to run this.

```Powershell
uvx --from git+https://github.com/gordonwatts/test-wsl2-llm.git test-wsl2-llm template run .\iris-hep-llm-questions.yaml q1
```

## Specification-to-data benchmark (issue #5)

The `ntuple-leaves-from-spec` question exercises the `analysis-data-sources`
skill in the ATLAS Analysis marketplace. It uses the existing CalRatio
Run 3 specification and asks for a verified extraction map, including gaps and
PHYSLITE-only backups. The small `calratio-probe-samples.yaml` manifest supplies
a Run 3 PHYSLITE collision sample, separating accessor testing
from the preceding dataset-discovery stage. A successful positive control does
not establish trigger acceptance or coverage of all analysis sample roles.

Prepare Ubuntu with Codex signed in and `uv` on its login-shell PATH. The
selected AF MCP server must be authenticated. ServiceX's Python client also
needs its own configuration; MCP catalog access does not supply that client
configuration. This question copies the existing Windows-side
`C:\Users\gordo\servicex.yaml` using the established `copy_files` convention.
Update that path for another machine. The configuration is excluded from
`copy_back`; keep its token out of Git and published artifacts.

```powershell
uvx --from git+https://github.com/gordonwatts/test-wsl2-llm.git test-wsl2-llm template run .\spec-tests.yaml ntuple-leaves-from-spec --model gpt-6-astra:medium --timeout 3600 --output .\results\issue5\run3\sources
```

The run returns exactly three named files: `data-sources.md`, the compact
`data-source-evidence.json`, and `servicex-smoke.root` when delivery succeeds.
Both Markdown and JSON are written in the analysis workspace root. The JSON
contains the tested query, sample/request provenance, versions, observations
and concise failures, so the files can be reviewed without a probe archive.
Scripts, intermediate files, full logs and duplicate ROOT deliveries stay local.
Use `--keep-workspace` when running if those debugging files may be needed later.
The skill validates the root files and JSON references before finishing. The ROOT
validator checks the smoke tree and required branches. Review nonzero counts,
ServiceX provenance, requirement coverage, units and physics equivalence
separately: passing the smoke check does not mean every analysis input is ready.
The first question, `spec-from-old-analysis-modified`, explicitly targets Run 3
and uses the IRIS-HEP specification skill, whose ATLAS default is also Run 3.
Generate it separately with `--model gpt-6-astra:medium`, review the returned
`specification.md`, then copy its exact bytes to `spec/calratio-abcd-spec.md`
before running `ntuple-leaves-from-spec`. Check run, energy, triggers,
normalization and ABCD sidebands at the handoff. The marketplace URLs currently
pin review branches containing the tested skills.


## Website and performance results

Giordon's catalogue and the existing interactive performance report are built together:

```powershell
pixi run preview
```

Install [Pixi](https://pixi.sh) and [uv](https://docs.astral.sh/uv/) first. The build
uses uv to run a pinned version of test-wsl2-llm with Python 3.13. It recursively
reads saved YAML reports under `results/`, generates `site/public/performance.html`,
and publishes it with the catalogue in `site/dist/`. No benchmarks are executed.
The homepage, suite, question, and model entries link to the report using its
existing URL filters. Entries without matching runs retain their empty state.

To use another results directory, set an absolute path before building:

```powershell
$env:RESULTS_DIR = 'C:\path\to\saved-results'
pixi run preview
```

Run the build again after results change. To force a fresh build when changing
RESULTS_DIR with Pixi, use `pixi run --force build`, then `pixi run preview`.
The generated HTML and link index are ignored by Git. The report includes prompts,
responses, validation messages, costs, and timings from the input reports.

### Publishing

The deployment workflow builds and uploads the report automatically **when saved
results are present before the build step**. Results are excluded from Git, so a
clean checkout builds the catalogue with empty results panels. To publish results,
add a download/restore step for your chosen results storage before `pixi run build`,
staging reports in `results/` or setting `RESULTS_DIR`. This change does not select
or upload a results archive. A configured RESULTS_DIR that does not exist fails
the build, as does a failing report generator, rather than publishing stale data.
