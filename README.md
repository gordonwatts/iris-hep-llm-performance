# LLM Performance On IRIS-HEP Skills And Questions

This repo contains a few sets of benchmark questions that are used to test skill, LLM, and (eventually) MCP performance.

Browse the benchmark suites and available results on the [IRIS-HEP LLM Performance website](https://gordonwatts.github.io/iris-hep-llm-performance/).

## Usage

Currently the results aren't being stored here (they are too big). But the raw test files are. They can be run with the following command on a windows machine with `wsl2` installed and the distro's that are indicated. `uv` must also be installed on the windows side for this to work. `codex` should already be signed in on the distro you will be running these on.

The following will execute question `q1` in the `iris-hep-llm-questions.yaml` file. Use `--help` for many many more confusing options on how to run this.

```Powershell
uvx --from git+https://github.com/gordonwatts/test-wsl2-llm.git test-wsl2-llm template run .\iris-hep-llm-questions.yaml q1
```

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
