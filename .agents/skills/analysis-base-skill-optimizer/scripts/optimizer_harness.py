# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6.0,<7"]
# ///
"""Deterministic harness for the AnalysisBase skill optimization experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import uuid
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

RUNNER_SOURCE = "git+https://github.com/gordonwatts/test-wsl2-llm.git"
DEFAULT_REPOSITORY = "gordonwatts/atlas-analysisbase-marketplace"
DEFAULT_SKILL_PATH = "plugins/atlas-analysisbase/skills/analysis-base"
EXPECTED_MODEL = "gpt-5.6-luna:high"
MAX_ROUNDS = 4
QUESTION_COUNT = 5
IMPROVEMENT_PATH = "run/improvements.diff"


class HarnessError(RuntimeError):
    """A user-actionable experiment invariant failed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise HarnessError(f"expected a YAML mapping: {path}")
    return value


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def load_state(experiment_dir: Path) -> dict[str, Any]:
    path = experiment_dir / "state.json"
    if not path.is_file():
        raise HarnessError(f"experiment state does not exist: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise HarnessError(f"unsupported experiment state: {path}")
    return value


def save_state(experiment_dir: Path, state: dict[str, Any]) -> None:
    path = experiment_dir / "state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(checkout: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(checkout), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise HarnessError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.strip()


def normalized_skill_path(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise HarnessError("target skill path must be a repository-relative path")
    return str(path).rstrip("/")


def validate_round(round_number: int) -> int:
    if not 1 <= round_number <= MAX_ROUNDS:
        raise HarnessError(f"round must be between 1 and {MAX_ROUNDS}")
    return 1 if round_number == 1 else 3


def verify_checkout(
    checkout: Path, *, branch: str | None, base_branch: str, require_clean: bool = True
) -> tuple[str, str]:
    checkout = checkout.resolve()
    if not (checkout / ".git").exists():
        raise HarnessError(f"target checkout is not a Git repository: {checkout}")
    current_branch = git(checkout, "branch", "--show-current")
    if not current_branch:
        raise HarnessError("target checkout must not use a detached HEAD")
    if current_branch == base_branch:
        raise HarnessError(f"refusing to optimize on the base branch: {base_branch}")
    if branch and current_branch != branch:
        raise HarnessError(
            f"checkout branch is {current_branch!r}, but experiment branch is {branch!r}"
        )
    if require_clean and git(checkout, "status", "--porcelain"):
        raise HarnessError(
            "target checkout must be clean before preparing or accepting a round"
        )
    return current_branch, git(checkout, "rev-parse", "HEAD")


def rewrite_prompt(prompt: str) -> str:
    start_marker = "At the end of the response"
    end_marker = "Note that running the analysis-base image"
    start = prompt.find(start_marker)
    end = prompt.find(end_marker)
    if start < 0 or end < 0 or end <= start:
        raise HarnessError(
            "benchmark prompt no longer contains the expected improvement block"
        )
    replacement = (
        "At the end of the response, identify up to three evidence-backed gaps in the skill "
        "that affected this run. Modify the isolated installed skill to address only reusable "
        "AnalysisBase guidance, then generate a unified diff at `run/improvements.diff`. "
        "Do not encode this question's requested values or solution as a general recipe. "
        "Do not treat transient infrastructure, network, CVMFS, or host failures as skill "
        "guidance. If no general improvement is justified, create an empty diff and say so.\n\n"
    )
    return prompt[:start] + replacement + prompt[end:]


def round_record(state: dict[str, Any], round_number: int) -> dict[str, Any]:
    for record in state.get("rounds", []):
        if record.get("round") == round_number:
            return record
    raise HarnessError(f"round {round_number} has not been prepared")


def prepare_round(args: argparse.Namespace) -> Path:
    repeat = validate_round(args.round)
    checkout = args.checkout.resolve()
    benchmark = (
        args.benchmark or (repo_root() / "analyiss-base-questions.yaml")
    ).resolve()
    if not benchmark.is_file():
        raise HarnessError(f"benchmark YAML does not exist: {benchmark}")

    if args.experiment_dir:
        experiment_dir = args.experiment_dir.resolve()
        state = load_state(experiment_dir)
        if args.round != state.get("current_round", 0) + 1:
            raise HarnessError("rounds must be prepared exactly once and in order")
        previous = round_record(state, args.round - 1)
        if previous.get("status") != "collected":
            raise HarnessError("collect the previous round before preparing another")
        branch = state["target"]["branch"]
        base_branch = state["target"]["base_branch"]
        if checkout != Path(state["target"]["checkout"]).resolve():
            raise HarnessError("cannot change the target checkout during an experiment")
        verify_checkout(checkout, branch=branch, base_branch=base_branch)
        if str(benchmark) != state["source_benchmark"]:
            raise HarnessError("cannot change the benchmark YAML during an experiment")
        if sha256_file(benchmark) != state["source_benchmark_sha256"]:
            raise HarnessError("source benchmark YAML changed during the experiment")
    else:
        if args.round != 1:
            raise HarnessError("--experiment-dir is required after round 1")
        run_id = args.run_id or (
            datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
            + "-"
            + uuid.uuid4().hex[:6]
        )
        experiment_dir = (
            repo_root() / "results" / "skill-optimizer" / run_id
        ).resolve()
        if (experiment_dir / "state.json").exists():
            raise HarnessError(f"experiment already exists: {experiment_dir}")
        base_branch = args.base_branch
        branch, head = verify_checkout(
            checkout, branch=args.branch, base_branch=base_branch
        )
        base_sha = args.base_sha
        if not base_sha:
            try:
                base_sha = git(checkout, "rev-parse", f"origin/{base_branch}")
            except HarnessError:
                base_sha = head
        state = {
            "schema_version": 1,
            "run_id": run_id,
            "created_at": utc_now(),
            "source_benchmark": str(benchmark),
            "source_benchmark_sha256": sha256_file(benchmark),
            "target": {
                "repository": args.target_repository,
                "skill_path": normalized_skill_path(args.target_skill_path),
                "checkout": str(checkout),
                "base_branch": base_branch,
                "base_sha": base_sha,
                "branch": branch,
            },
            "current_round": 0,
            "accepted_commits": [],
            "rounds": [],
        }
        try:
            git(checkout, "merge-base", "--is-ancestor", base_sha, head)
        except HarnessError as error:
            raise HarnessError(
                "base SHA must be an ancestor of the optimization branch"
            ) from error

    current_branch, tested_commit = verify_checkout(
        checkout,
        branch=state["target"]["branch"],
        base_branch=state["target"]["base_branch"],
    )
    source = read_yaml(benchmark)
    questions = source.get("questions")
    if not isinstance(questions, list) or len(questions) != QUESTION_COUNT:
        raise HarnessError(f"benchmark must contain exactly {QUESTION_COUNT} questions")
    question_ids = [
        question.get("id") for question in questions if isinstance(question, dict)
    ]
    if len(question_ids) != QUESTION_COUNT or any(not item for item in question_ids):
        raise HarnessError("every benchmark question must have an id")
    if source.get("model") != EXPECTED_MODEL:
        raise HarnessError(f"benchmark model must remain {EXPECTED_MODEL}")

    generated = dict(source)
    generated["prompt_template"] = rewrite_prompt(
        str(source.get("prompt_template", ""))
    )
    generated["marketplaces"] = [str(checkout)]
    copied = list(generated.get("copy_back") or [])
    if IMPROVEMENT_PATH not in copied:
        copied.append(IMPROVEMENT_PATH)
    generated["copy_back"] = copied
    output_stem = experiment_dir / "results" / f"round-{args.round:02d}" / "ab"
    generated["output"] = str(output_stem)
    generated["repeat"] = repeat
    generated["threads"] = 1

    config_path = experiment_dir / "config" / f"round-{args.round:02d}.yaml"
    write_yaml(config_path, generated)
    record = {
        "round": args.round,
        "repeat": repeat,
        "status": "prepared",
        "prepared_at": utc_now(),
        "tested_commit": tested_commit,
        "branch": current_branch,
        "config": str(config_path),
        "output_stem": str(output_stem),
        "question_ids": question_ids,
    }
    state["rounds"].append(record)
    state["current_round"] = args.round
    save_state(experiment_dir, state)
    print(f"experiment_dir={experiment_dir}")
    print(f"round={args.round} repeat={repeat} tested_commit={tested_commit}")
    print(f"config={config_path}")
    return experiment_dir


def runner_command(record: dict[str, Any], *, config_only: bool = False) -> list[str]:
    command = [
        "uvx",
        "--from",
        RUNNER_SOURCE,
        "test-wsl2-llm",
        "template",
        "run",
        record["config"],
        "--repeat",
        str(record["repeat"]),
        "--threads",
        "1",
    ]
    if config_only:
        resolved = str(
            Path(record["config"]).with_name(
                Path(record["config"]).stem + "-resolved.yaml"
            )
        )
        command.extend(["--save-config", resolved, "--config-only"])
    return command


def run_round(args: argparse.Namespace) -> int:
    experiment_dir = args.experiment_dir.resolve()
    state = load_state(experiment_dir)
    record = round_record(state, args.round)
    allowed = {"prepared"} if not args.config_only else {"prepared", "config_validated"}
    if record.get("status") not in allowed:
        raise HarnessError(
            f"round {args.round} is not ready to run: {record.get('status')}"
        )
    command = runner_command(record, config_only=args.config_only)
    print("command=" + subprocess.list2cmdline(command), flush=True)
    if not args.config_only:
        record["status"] = "running"
        record["started_at"] = utc_now()
        save_state(experiment_dir, state)
    try:
        completed = subprocess.run(command, cwd=repo_root(), check=False)
    except KeyboardInterrupt:
        if not args.config_only:
            record["status"] = "interrupted"
            record["runner_exit_code"] = 130
            record["runner_finished_at"] = utc_now()
            save_state(experiment_dir, state)
        return 130
    except OSError as error:
        if not args.config_only:
            record["status"] = "runner_failed"
            record["runner_error"] = str(error)
            record["runner_finished_at"] = utc_now()
            save_state(experiment_dir, state)
        raise HarnessError(f"could not start benchmark runner: {error}") from error
    record["runner_exit_code"] = completed.returncode
    record["runner_finished_at"] = utc_now()
    if args.config_only:
        if completed.returncode == 0:
            record["config_validated_at"] = utc_now()
        else:
            record["config_validation_exit_code"] = completed.returncode
    else:
        record["status"] = (
            "runner_finished" if completed.returncode == 0 else "runner_failed"
        )
    save_state(experiment_dir, state)
    return completed.returncode


def expected_result_paths(record: dict[str, Any]) -> list[tuple[str, int, Path]]:
    stem = Path(record["output_stem"])
    repeat = int(record["repeat"])
    expected: list[tuple[str, int, Path]] = []
    for question_id in record["question_ids"]:
        for repetition in range(1, repeat + 1):
            suffix = "" if repeat == 1 else f"-{repetition:03d}"
            expected.append(
                (
                    question_id,
                    repetition,
                    stem.parent / f"{stem.name}-{question_id}{suffix}.yaml",
                )
            )
    return expected


def final_response(result: dict[str, Any]) -> str:
    conversation = result.get("conversation") or []
    for turn in reversed(conversation):
        if isinstance(turn, dict) and turn.get("final_response"):
            return str(turn["final_response"])
    final = result.get("result") or {}
    return str(final.get("final_message") or "") if isinstance(final, dict) else ""


def usage_totals(result: dict[str, Any]) -> dict[str, int]:
    keys = (
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
    )
    totals = {key: 0 for key in keys}
    for entry in result.get("usage") or []:
        if isinstance(entry, dict):
            for key in keys:
                totals[key] += int(entry.get(key) or 0)
    # The runner reports reasoning tokens as a subset of output tokens.
    totals["total_tokens"] = totals["input_tokens"] + totals["output_tokens"]
    return totals


def collect_round(args: argparse.Namespace) -> Path:
    experiment_dir = args.experiment_dir.resolve()
    state = load_state(experiment_dir)
    record = round_record(state, args.round)
    if record.get("status") not in {"runner_finished", "runner_failed", "interrupted"}:
        raise HarnessError(f"round {args.round} has not finished running")

    runs: list[dict[str, Any]] = []
    missing_reports: list[str] = []
    durations: list[float] = []
    tokens: list[int] = []
    for question_id, repetition, report_path in expected_result_paths(record):
        if not report_path.is_file():
            missing_reports.append(str(report_path))
            continue
        result = read_yaml(report_path)
        run = result.get("run") or {}
        copied_files: list[dict[str, Any]] = []
        improvement: dict[str, Any] | None = None
        for copied in result.get("copied_back") or []:
            if not isinstance(copied, dict):
                continue
            destination = Path(str(copied.get("destination", "")))
            item = {
                "source": copied.get("source"),
                "destination": str(destination),
                "type": copied.get("type"),
                "size": copied.get("size"),
                "root_contents": copied.get("root_contents") or [],
                "error": copied.get("error"),
            }
            copied_files.append(item)
            if copied.get("source") == IMPROVEMENT_PATH and destination.is_file():
                improvement = {
                    "path": str(destination),
                    "size": destination.stat().st_size,
                    "sha256": sha256_file(destination),
                }
        usage = usage_totals(result)
        duration = float(run.get("total_duration_seconds") or 0.0)
        durations.append(duration)
        tokens.append(usage["total_tokens"])
        response = final_response(result)
        runs.append(
            {
                "question_id": question_id,
                "repetition": repetition,
                "report": str(report_path),
                "status": run.get("status"),
                "exit_code": run.get("exit_code"),
                "duration_seconds": duration,
                "codex_execution_seconds": run.get("codex_execution_seconds"),
                "usage": usage,
                "missing_copy_back": result.get("missing_copy_back") or [],
                "copied_back": copied_files,
                "improvement_diff": improvement,
                "final_response_excerpt": response[-4000:],
            }
        )

    expected_count = len(expected_result_paths(record))
    hard_gate = (
        not missing_reports
        and len(runs) == expected_count
        and all(item["status"] == "succeeded" for item in runs)
        and all(not item["missing_copy_back"] for item in runs)
        and all(item["improvement_diff"] is not None for item in runs)
    )
    summary = {
        "schema_version": 1,
        "round": args.round,
        "repeat": record["repeat"],
        "tested_commit": record["tested_commit"],
        "collected_at": utc_now(),
        "expected_runs": expected_count,
        "collected_runs": len(runs),
        "hard_gate_passed": hard_gate,
        "missing_reports": missing_reports,
        "median_duration_seconds": statistics.median(durations) if durations else None,
        "median_total_tokens": statistics.median(tokens) if tokens else None,
        "runs": runs,
    }
    evidence_dir = experiment_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    json_path = evidence_dir / f"round-{args.round:02d}.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    markdown_path = evidence_dir / f"round-{args.round:02d}.md"
    markdown_path.write_text(render_evidence(summary), encoding="utf-8")
    record["status"] = "collected"
    record["collected_at"] = summary["collected_at"]
    record["hard_gate_passed"] = hard_gate
    record["evidence_json"] = str(json_path)
    record["evidence_markdown"] = str(markdown_path)
    record["median_duration_seconds"] = summary["median_duration_seconds"]
    record["median_total_tokens"] = summary["median_total_tokens"]
    save_state(experiment_dir, state)
    print(f"evidence={markdown_path}")
    print(f"hard_gate_passed={str(hard_gate).lower()}")
    return markdown_path


def render_evidence(summary: dict[str, Any]) -> str:
    lines = [
        f"# Optimization evidence: round {summary['round']}",
        "",
        f"- Tested commit: `{summary['tested_commit']}`",
        f"- Runs: {summary['collected_runs']}/{summary['expected_runs']}",
        f"- Hard gate: {'passed' if summary['hard_gate_passed'] else 'failed'}",
        f"- Median duration: {summary['median_duration_seconds']}",
        f"- Median total tokens: {summary['median_total_tokens']}",
        "",
        "| Question | Rep | Status | Seconds | Tokens | Missing | Diff SHA-256 |",
        "|---|---:|---|---:|---:|---|---|",
    ]
    for item in summary["runs"]:
        improvement = item["improvement_diff"] or {}
        missing = ", ".join(item["missing_copy_back"]) or "—"
        lines.append(
            f"| {item['question_id']} | {item['repetition']} | {item['status']} | "
            f"{item['duration_seconds']:.1f} | {item['usage']['total_tokens']} | {missing} | "
            f"{improvement.get('sha256', 'missing')} |"
        )
    if summary["missing_reports"]:
        lines.extend(["", "## Missing reports", ""])
        lines.extend(f"- `{path}`" for path in summary["missing_reports"])
    lines.extend(["", "## Review inputs", ""])
    for item in summary["runs"]:
        lines.append(f"### {item['question_id']} / repetition {item['repetition']}")
        lines.append("")
        if item["improvement_diff"]:
            lines.append(f"- Diff: `{item['improvement_diff']['path']}`")
        lines.append(f"- Full result: `{item['report']}`")
        excerpt = item["final_response_excerpt"].strip()
        if excerpt:
            lines.extend(["", "Final response excerpt:", "", "```text", excerpt, "```"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def changed_paths(checkout: Path, base_sha: str, head: str) -> list[str]:
    output = git(checkout, "diff", "--name-only", f"{base_sha}..{head}")
    return [line.replace("\\", "/") for line in output.splitlines() if line]


def guard(args: argparse.Namespace) -> None:
    experiment_dir = args.experiment_dir.resolve()
    checkout = args.checkout.resolve()
    state = load_state(experiment_dir)
    target = state["target"]
    branch, head = verify_checkout(
        checkout, branch=target["branch"], base_branch=target["base_branch"]
    )
    prefix = target["skill_path"].rstrip("/") + "/"
    outside = [
        path
        for path in changed_paths(checkout, target["base_sha"], head)
        if not path.startswith(prefix)
    ]
    if outside:
        raise HarnessError(
            "changes outside the target skill package: " + ", ".join(outside)
        )

    if args.record_accepted:
        if args.round is None:
            raise HarnessError("--round is required with --record-accepted")
        record = round_record(state, args.round)
        if record.get("status") != "collected" or not record.get("hard_gate_passed"):
            raise HarnessError(
                "only a collected round that passed the hard gate can be accepted"
            )
        if head != record.get("tested_commit"):
            raise HarnessError("checkout HEAD is not the commit tested by this round")
        record["decision"] = "accepted"
        record["decision_at"] = utc_now()
        if head not in state["accepted_commits"]:
            state["accepted_commits"].append(head)
        save_state(experiment_dir, state)

    if args.final:
        latest = state["rounds"][-1] if state.get("rounds") else None
        if not latest or latest.get("status") != "collected":
            raise HarnessError("the latest prepared round has not been collected")
        if not latest.get("hard_gate_passed"):
            raise HarnessError("the latest round did not pass the hard gate")
        if head != latest.get("tested_commit"):
            raise HarnessError(
                "branch HEAD contains changes that were not tested in the latest round"
            )
        if args.round is not None:
            raise HarnessError("--round is not used with --final")
        state["final_guard"] = {
            "passed_at": utc_now(),
            "commit": head,
            "round": latest["round"],
        }
        save_state(experiment_dir, state)
    print(f"guard=passed branch={branch} head={head}")


def show_status(args: argparse.Namespace) -> None:
    state = load_state(args.experiment_dir.resolve())
    compact = {
        "run_id": state["run_id"],
        "target": state["target"],
        "current_round": state["current_round"],
        "accepted_commits": state["accepted_commits"],
        "final_guard": state.get("final_guard"),
        "rounds": [
            {
                key: record.get(key)
                for key in (
                    "round",
                    "repeat",
                    "status",
                    "tested_commit",
                    "hard_gate_passed",
                    "decision",
                    "median_duration_seconds",
                    "median_total_tokens",
                    "config",
                    "evidence_markdown",
                )
                if record.get(key) is not None
            }
            for record in state["rounds"]
        ],
    }
    print(json.dumps(compact, indent=2))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser(
        "prepare", help="prepare one bounded benchmark round"
    )
    prepare.add_argument("--checkout", type=Path, required=True)
    prepare.add_argument("--experiment-dir", type=Path)
    prepare.add_argument("--benchmark", type=Path)
    prepare.add_argument("--round", type=int, default=1)
    prepare.add_argument("--run-id")
    prepare.add_argument("--target-repository", default=DEFAULT_REPOSITORY)
    prepare.add_argument("--target-skill-path", default=DEFAULT_SKILL_PATH)
    prepare.add_argument("--base-branch", default="main")
    prepare.add_argument("--base-sha")
    prepare.add_argument("--branch")
    prepare.set_defaults(action=prepare_round)

    run = subparsers.add_parser("run", help="run a prepared round")
    run.add_argument("--experiment-dir", type=Path, required=True)
    run.add_argument("--round", type=int, required=True)
    run.add_argument("--config-only", action="store_true")
    run.set_defaults(action=run_round)

    collect = subparsers.add_parser(
        "collect", help="collect a round into compact evidence"
    )
    collect.add_argument("--experiment-dir", type=Path, required=True)
    collect.add_argument("--round", type=int, required=True)
    collect.set_defaults(action=collect_round)

    check = subparsers.add_parser(
        "guard", help="verify scope and tested-commit invariants"
    )
    check.add_argument("--experiment-dir", type=Path, required=True)
    check.add_argument("--checkout", type=Path, required=True)
    check.add_argument("--round", type=int)
    check.add_argument("--record-accepted", action="store_true")
    check.add_argument("--final", action="store_true")
    check.set_defaults(action=guard)

    status = subparsers.add_parser("status", help="show resumable experiment state")
    status.add_argument("--experiment-dir", type=Path, required=True)
    status.set_defaults(action=show_status)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        outcome = args.action(args)
        return outcome if isinstance(outcome, int) else 0
    except HarnessError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
