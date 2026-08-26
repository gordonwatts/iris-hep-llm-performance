# LLM Performance On IRIS-HEP Skills And Questions

This repo contains a few sets of benchmark questions that are used to test skill, LLM, and (eventually) MCP performance.

## Usage

Currently the results aren't being stored here (they are too big). But the raw test files are. They can be run with the following command on a windows machine with `wsl2` installed and the distro's that are indicated. `uv` must also be installed on the windows side for this to work. `codex` should already be signed in on the distro you will be running these on.

The following will execute question `q1` in the `iris-hep-llm-questions.yaml` file. Use `--help` for many many more confusing options on how to run this.

```Powershell
uvx --from git+https://github.com/gordonwatts/test-wsl2-llm.git test-wsl2-llm template run .\iris-hep-llm-questions.yaml q1
```
