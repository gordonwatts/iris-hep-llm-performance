from __future__ import annotations

import importlib.util
import json
import subprocess
from argparse import Namespace
from pathlib import Path

import pytest
import yaml

SCRIPT = Path(__file__).parents[1] / "scripts" / "optimizer_harness.py"
SPEC = importlib.util.spec_from_file_location("optimizer_harness", SCRIPT)
assert SPEC and SPEC.loader
HARNESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARNESS)


def run_git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def make_checkout(tmp_path: Path) -> Path:
    repo = tmp_path / "marketplace"
    repo.mkdir()
    run_git(repo, "init", "-b", "main")
    run_git(repo, "config", "user.email", "test@example.com")
    run_git(repo, "config", "user.name", "Test User")
    skill = repo / HARNESS.DEFAULT_SKILL_PATH
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("baseline\n", encoding="utf-8")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", "baseline")
    run_git(repo, "branch", "codex/optimize-analysis-base-test")
    run_git(repo, "switch", "codex/optimize-analysis-base-test")
    return repo


def make_benchmark(tmp_path: Path) -> Path:
    path = tmp_path / "analyiss-base-questions.yaml"
    value = {
        "prompt_template": (
            "Solve {{ question }}.\n\n"
            "At the end of the response, list three things and change the skill.\n\n"
            "Note that running the analysis-base image can take a long time.\n"
        ),
        "questions": [{"id": f"q{index}", "question": "task"} for index in range(1, 6)],
        "model": HARNESS.EXPECTED_MODEL,
        "marketplaces": ["https://example.test/marketplace.git"],
        "plugins": ["atlas-analysisbase@example"],
        "copy_back": ["source/ab-config.yaml"],
        "output": "old-output",
        "repeat": 1,
        "threads": 1,
    }
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    return path


def prepare(tmp_path: Path, *, round_number: int = 1, experiment: Path | None = None):
    checkout = (
        make_checkout(tmp_path)
        if experiment is None
        else Path(
            json.loads((experiment / "state.json").read_text())["target"]["checkout"]
        )
    )
    benchmark = (
        make_benchmark(tmp_path)
        if experiment is None
        else Path(
            json.loads((experiment / "state.json").read_text())["source_benchmark"]
        )
    )
    args = Namespace(
        checkout=checkout,
        experiment_dir=experiment,
        benchmark=benchmark,
        round=round_number,
        run_id="test-run",
        target_repository=HARNESS.DEFAULT_REPOSITORY,
        target_skill_path=HARNESS.DEFAULT_SKILL_PATH,
        base_branch="main",
        base_sha=run_git(checkout, "rev-parse", "main") if experiment is None else None,
        branch=None,
    )
    experiment_dir = HARNESS.prepare_round(args)
    return experiment_dir, checkout, benchmark


def test_prepare_preserves_source_and_rewrites_generated_yaml(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setattr(HARNESS, "repo_root", lambda: tmp_path)
    experiment, checkout, benchmark = prepare(tmp_path)
    original = benchmark.read_bytes()
    generated = yaml.safe_load((experiment / "config" / "round-01.yaml").read_text())

    assert benchmark.read_bytes() == original
    assert generated["marketplaces"] == [str(checkout.resolve())]
    assert HARNESS.IMPROVEMENT_PATH in generated["copy_back"]
    assert generated["model"] == HARNESS.EXPECTED_MODEL
    assert generated["repeat"] == 1
    assert generated["threads"] == 1
    assert "up to three evidence-backed gaps" in generated["prompt_template"]
    assert "Do not encode this question" in generated["prompt_template"]


def test_round_limit_and_base_branch_guard(tmp_path: Path):
    with pytest.raises(HARNESS.HarnessError, match="between 1 and 4"):
        HARNESS.validate_round(5)
    checkout = make_checkout(tmp_path)
    run_git(checkout, "switch", "main")
    with pytest.raises(HARNESS.HarnessError, match="base branch"):
        HARNESS.verify_checkout(checkout, branch=None, base_branch="main")


def write_result(path: Path, diff_path: Path, *, status: str = "succeeded") -> None:
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_text("--- a/SKILL.md\n+++ b/SKILL.md\n", encoding="utf-8")
    value = {
        "run": {
            "status": status,
            "exit_code": 0,
            "total_duration_seconds": 12.0,
            "codex_execution_seconds": 10.0,
        },
        "usage": [
            {
                "input_tokens": 100,
                "cached_input_tokens": 50,
                "output_tokens": 20,
                "reasoning_output_tokens": 5,
            }
        ],
        "result": {"final_message": "done"},
        "conversation": [{"prompt": "task", "final_response": "final response"}],
        "copied_back": [
            {
                "source": HARNESS.IMPROVEMENT_PATH,
                "destination": str(diff_path),
                "type": "text",
                "size": diff_path.stat().st_size,
            }
        ],
        "missing_copy_back": [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value), encoding="utf-8")


def test_collect_uses_indexed_results_and_aggregates_metrics(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setattr(HARNESS, "repo_root", lambda: tmp_path)
    experiment, _, _ = prepare(tmp_path)
    state_path = experiment / "state.json"
    state = json.loads(state_path.read_text())
    record = state["rounds"][0]
    record["status"] = "runner_finished"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    for index, (_, _, report) in enumerate(
        HARNESS.expected_result_paths(record), start=1
    ):
        write_result(report, report.with_suffix(f".{index}.improvements.diff"))

    evidence = HARNESS.collect_round(Namespace(experiment_dir=experiment, round=1))
    summary = json.loads(evidence.with_suffix(".json").read_text())
    assert summary["hard_gate_passed"] is True
    assert summary["collected_runs"] == 5
    assert summary["median_duration_seconds"] == 12.0
    assert summary["median_total_tokens"] == 120


def test_repeated_round_uses_three_digit_result_suffixes():
    record = {
        "output_stem": "C:/results/round-02/ab",
        "repeat": 3,
        "question_ids": ["q1", "q2"],
    }
    paths = [path.name for _, _, path in HARNESS.expected_result_paths(record)]
    assert paths == [
        "ab-q1-001.yaml",
        "ab-q1-002.yaml",
        "ab-q1-003.yaml",
        "ab-q2-001.yaml",
        "ab-q2-002.yaml",
        "ab-q2-003.yaml",
    ]


def test_collect_fails_hard_gate_when_a_diff_is_missing(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(HARNESS, "repo_root", lambda: tmp_path)
    experiment, _, _ = prepare(tmp_path)
    state_path = experiment / "state.json"
    state = json.loads(state_path.read_text())
    record = state["rounds"][0]
    record["status"] = "runner_finished"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    expected = HARNESS.expected_result_paths(record)
    for index, (_, _, report) in enumerate(expected, start=1):
        write_result(report, report.with_suffix(f".{index}.improvements.diff"))
    missing_report = expected[-1][2]
    value = yaml.safe_load(missing_report.read_text())
    value["copied_back"] = []
    value["missing_copy_back"] = [HARNESS.IMPROVEMENT_PATH]
    missing_report.write_text(yaml.safe_dump(value), encoding="utf-8")

    evidence = HARNESS.collect_round(Namespace(experiment_dir=experiment, round=1))
    summary = json.loads(evidence.with_suffix(".json").read_text())
    assert summary["hard_gate_passed"] is False


def test_scope_guard_rejects_changes_outside_skill(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(HARNESS, "repo_root", lambda: tmp_path)
    experiment, checkout, _ = prepare(tmp_path)
    (checkout / "README.md").write_text("outside\n", encoding="utf-8")
    run_git(checkout, "add", ".")
    run_git(checkout, "commit", "-m", "outside")
    with pytest.raises(HARNESS.HarnessError, match="outside the target skill"):
        HARNESS.guard(
            Namespace(
                experiment_dir=experiment,
                checkout=checkout,
                round=None,
                record_accepted=False,
                final=False,
            )
        )


def test_final_guard_rejects_an_unbenchmarked_head(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(HARNESS, "repo_root", lambda: tmp_path)
    experiment, checkout, _ = prepare(tmp_path)
    state_path = experiment / "state.json"
    state = json.loads(state_path.read_text())
    state["rounds"][0]["status"] = "collected"
    state["rounds"][0]["hard_gate_passed"] = True
    state_path.write_text(json.dumps(state), encoding="utf-8")
    skill = checkout / HARNESS.DEFAULT_SKILL_PATH / "SKILL.md"
    skill.write_text("candidate\n", encoding="utf-8")
    run_git(checkout, "add", ".")
    run_git(checkout, "commit", "-m", "untested candidate")

    with pytest.raises(HARNESS.HarnessError, match="not tested"):
        HARNESS.guard(
            Namespace(
                experiment_dir=experiment,
                checkout=checkout,
                round=None,
                record_accepted=False,
                final=True,
            )
        )
