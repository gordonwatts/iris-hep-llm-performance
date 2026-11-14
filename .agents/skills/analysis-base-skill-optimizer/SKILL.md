---
name: analysis-base-skill-optimizer
description: Run a bounded, evidence-driven optimization loop for the atlas-analysisbase AnalysisBase skill using analyiss-base-questions.yaml, an isolated GitHub branch, and test-wsl2-llm. Use when asked to benchmark and improve that skill and deliver a tested pull request; do not use for ordinary AnalysisBase work or generic skill editing.
---

# AnalysisBase Skill Optimizer

Improve the AnalysisBase skill without turning the five benchmark questions into recipes. Use the GitHub connector for repository inspection, branch updates, and the final pull request. Run the local harness for deterministic preparation, execution, collection, and safety checks. A capable outer model such as `gpt-5.6-sol:medium` is recommended; do not change the benchmark worker model from `gpt-5.6-luna:high`.

## Fixed experiment boundary

- Use only `analyiss-base-questions.yaml` from the benchmark repository. Never edit it in place.
- Target `gordonwatts/atlas-analysisbase-marketplace` and `plugins/atlas-analysisbase/skills/analysis-base/` unless the user explicitly supplies replacements.
- Create a fresh branch such as `codex/optimize-analysis-base-<date>-<short-id>` from the default branch. Never optimize on the default branch.
- Keep the target checkout clean and synchronized with the GitHub branch before preparing a round.
- Run at most four rounds: round 1 uses one repetition; rounds 2 through 4 use three. Keep one runner thread.
- Round 4 is validation-only. Do not apply its proposed changes. Stop earlier when further edits are not supported by the evidence.

The current runner shallow-clones a Git marketplace's default branch and has no ref option. Therefore clone the optimization branch locally on Windows and let the generated YAML point `marketplaces` at that checkout. Do not invent a URL fragment or modify the runner.

## Start or resume

The harness is a PEP 723 script. Run it with `uv run --script` from the benchmark repository:

```powershell
uv run --script .agents/skills/analysis-base-skill-optimizer/scripts/optimizer_harness.py prepare --checkout C:\path\to\atlas-analysisbase-marketplace
```

`prepare` prints the experiment directory and generated YAML. For later rounds, pass that directory and the round number:

```powershell
uv run --script .agents/skills/analysis-base-skill-optimizer/scripts/optimizer_harness.py prepare --experiment-dir results/skill-optimizer/<run-id> --checkout C:\path\to\atlas-analysisbase-marketplace --round 2
```

If context is compacted or execution is interrupted, run `status --experiment-dir ...` before doing anything else. Treat `state.json` as the experiment ledger; do not reconstruct progress from memory.

## Run and collect a round

Run the prepared round in the foreground. The command can take hours and should be left in a persistent terminal session. Poll it only periodically and avoid repeatedly loading full output.

```powershell
uv run --script .agents/skills/analysis-base-skill-optimizer/scripts/optimizer_harness.py run --experiment-dir results/skill-optimizer/<run-id> --round 1
uv run --script .agents/skills/analysis-base-skill-optimizer/scripts/optimizer_harness.py collect --experiment-dir results/skill-optimizer/<run-id> --round 1
```

Read the compact evidence Markdown first. Open full result YAML, final artifacts, or individual `improvements.diff` files only when needed to resolve a claim.

## Judge and edit

Correct output is a hard gate. A successful process alone is not proof: inspect the requested files, ROOT inventory, final response, missing copy-backs, and relevant logs. Classify failures as skill, task implementation, runner, or environment failures before proposing an edit.

Prefer changes that:

- solve a demonstrated recurring gap across runs or encode a stable AnalysisBase invariant;
- reduce wasted discovery, retries, tokens, or runtime without weakening validation;
- remain useful for requests beyond the five benchmark questions; and
- fit the existing `SKILL.md`/reference split without duplicating guidance.

Reject question-shaped snippets, one-off paths presented as universal, speculative fixes, contradictory suggestions, environmental workarounds, and changes supported only by a self-authored diff. Repeated suggestions are stronger evidence, but consensus does not override incorrect behavior. Compare median duration and token use in repeated rounds only as secondary signals.

Translate accepted ideas into clean edits in the repository paths. Never blindly apply a copied diff: its headers refer to an isolated plugin cache. Commit updates to the GitHub branch, refresh the clean local checkout, and prepare the next round. A candidate is accepted only after a later round tests its exact commit.

After collection, use the guard to record an accepted tested commit or to verify final readiness:

```powershell
uv run --script .agents/skills/analysis-base-skill-optimizer/scripts/optimizer_harness.py guard --experiment-dir results/skill-optimizer/<run-id> --checkout C:\path\to\atlas-analysisbase-marketplace --round 2 --record-accepted
uv run --script .agents/skills/analysis-base-skill-optimizer/scripts/optimizer_harness.py guard --experiment-dir results/skill-optimizer/<run-id> --checkout C:\path\to\atlas-analysisbase-marketplace --final
```

If a tested candidate regresses, revert it through GitHub, refresh the checkout, and either try a materially different evidence-backed edit in the next available round or stop. Do not consume rounds retrying unchanged external failures.

## Finish

The final guard must pass before opening a pull request. Create a ready-for-review PR through GitHub. Limit the PR to the target skill package and include:

- accepted and rejected/deferred improvements by round;
- correctness evidence and any environmental limitations;
- median duration/token trends where comparable;
- the benchmark file, worker model, repetition schedule, and tested commit; and
- confirmation that the source benchmark YAML was unchanged.

Return a concise report and the PR link. If GitHub access or write permission is missing, stop before mutation and report that requirement rather than substituting an unreviewed local-only delivery.
