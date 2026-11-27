"""Tests for the benchmark harness and check scripts. No network, no claude CLI needed."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO / "benchmarks"
sys.path.insert(0, str(BENCH))

import run_benchmark as rb  # noqa: E402

TASKS = rb.load_tasks()
REFERENCE = BENCH / "reference"


def test_tasks_load_and_reference_existing_files() -> None:
    tasks = rb.load_tasks()
    assert {t.id for t in tasks} >= {"T01", "T02"}
    for task in tasks:
        assert (BENCH / "fixtures" / task.fixture).is_dir()
        assert (BENCH / task.check).is_file()
        assert task.timeout_s > 0


def test_unknown_task_id_rejected() -> None:
    with pytest.raises(SystemExit):
        rb.load_tasks({"T99"})


def test_build_command_variants() -> None:
    task = rb.load_tasks({"T01"})[0]
    base = rb.build_command(task, "baseline")
    conductor = rb.build_command(task, "conductor")
    assert base[:3] == ["claude", "--bare", "-p"]
    assert base[3] == task.prompt
    assert base[base.index("--effort") + 1] == "medium"
    assert "--plugin-dir" not in base
    assert conductor[3].startswith("/conductor:conductor --yes ")
    assert conductor[conductor.index("--plugin-dir") + 1] == str(rb.PLUGIN_DIR)
    assert base[base.index("--allowedTools") + 1] == task.allowed_tools
    assert conductor[conductor.index("--allowedTools") + 1] == f"{task.allowed_tools},Agent"
    for cmd in (base, conductor):
        assert cmd[cmd.index("--output-format") + 1] == "json"
        assert cmd[cmd.index("--model") + 1] == "opus"
    with pytest.raises(ValueError):
        rb.build_command(task, "other")


def test_parse_result_fields() -> None:
    out = json.dumps({"total_cost_usd": 0.42, "is_error": False, "num_turns": 7,
                      "duration_ms": 1234, "modelUsage": {"claude-haiku-5-5": {}}})
    parsed = rb.parse_result(out)
    assert parsed["total_cost_usd"] == 0.42
    assert parsed["is_error"] is False
    assert parsed["num_turns"] == 7
    assert parsed["per_model"] == {"claude-haiku-5-5": {}}


@pytest.mark.parametrize("bad", ["not json", "[]", ""])
def test_parse_result_bad_output(bad: str) -> None:
    parsed = rb.parse_result(bad)
    assert parsed["parse_error"] is True
    assert parsed["is_error"] is True


def test_summarize_table() -> None:
    rows = [
        {"task": "T01", "variant": "baseline", "run": 1, "passed": True, "total_cost_usd": 1.0},
        {"task": "T01", "variant": "baseline", "run": 2, "passed": False, "total_cost_usd": 0.0},
        {"task": "T01", "variant": "baseline", "run": 3, "passed": True, "total_cost_usd": None},
        {"task": "T01", "variant": "conductor", "run": 1, "passed": False, "total_cost_usd": None},
    ]
    text = rb.summarize(rows)
    assert "| Task | Variant | Run |" in text
    assert "| T01 | baseline | 3 | yes | n/a |" in text
    assert "| baseline | 3 | 2/3 (66.7%) | 0.5000 | 1.0000 | 1 |" in text
    assert "| conductor | 1 | 0/1 (0.0%) | n/a | 0.0000 | 1 |" in text


def test_dry_run_repeats_and_sets_baseline_effort(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("subprocess must not run in dry-run")

    monkeypatch.setattr(subprocess, "run", boom)
    assert rb.main(["--dry-run", "--tasks", "T01", "--repeat", "2", "--baseline-effort", "high"]) == 0
    baseline_1, baseline_2, conductor_1, conductor_2 = capsys.readouterr().out.splitlines()
    for run, line in enumerate((baseline_1, baseline_2), start=1):
        assert line.startswith(f"[T01 baseline run {run}] claude --bare -p")
        assert line.endswith("--effort high")
    for run, line in enumerate((conductor_1, conductor_2), start=1):
        assert line.startswith(f"[T01 conductor run {run}] claude --bare -p '/conductor:conductor --yes")
        assert "--effort" not in line


@pytest.mark.parametrize("repeat", [0, -1])
def test_repeat_must_be_positive(repeat: int) -> None:
    with pytest.raises(SystemExit) as exc:
        rb.main(["--dry-run", "--repeat", str(repeat)])
    assert exc.value.code == 2


def test_repeat_writes_one_row_per_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, str]] = []

    def fake_run(task: rb.Task, variant: str, baseline_effort: str) -> dict[str, Any]:
        calls.append((task.id, variant, baseline_effort))
        return {"task": task.id, "variant": variant, "passed": True, "total_cost_usd": 0.5}

    monkeypatch.setattr(shutil, "which", lambda _: "claude")
    monkeypatch.setattr(rb, "run_one", fake_run)
    results = tmp_path / "results.jsonl"
    assert rb.main([
        "--tasks", "T01,T02", "--repeat", "3", "--baseline-effort", "low", "--out", str(results),
    ]) == 0

    rows = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    expected = [
        (task_id, variant, run)
        for task_id in ("T01", "T02")
        for variant in rb.VARIANTS
        for run in (1, 2, 3)
    ]
    assert [(row["task"], row["variant"], row["run"]) for row in rows] == expected
    assert {row["baseline_effort"] for row in rows} == {"low"}
    assert calls == [(task_id, variant, "low") for task_id, variant, _ in expected]


@pytest.fixture()
def fixture_copy(task: rb.Task, tmp_path: Path) -> Path:
    return shutil.copytree(BENCH / "fixtures" / task.fixture, tmp_path / task.fixture)


@pytest.mark.parametrize("task", TASKS, ids=lambda task: task.id)
def test_check_fails_on_untouched_fixture(task: rb.Task, fixture_copy: Path) -> None:
    assert not rb.run_check(task, fixture_copy)


@pytest.fixture()
def reference_copy(task: rb.Task, fixture_copy: Path) -> Path:
    overlay = REFERENCE / task.id
    if not overlay.is_dir():
        pytest.skip(f"no reference directory for {task.id}")
    return shutil.copytree(overlay, fixture_copy, dirs_exist_ok=True)


@pytest.mark.parametrize("task", TASKS, ids=lambda task: task.id)
def test_check_passes_on_reference_solution(task: rb.Task, reference_copy: Path) -> None:
    assert rb.run_check(task, reference_copy)


def test_all_tasks_have_references() -> None:
    missing = [task.id for task in TASKS if not (REFERENCE / task.id).is_dir()]
    assert not missing, f"Missing reference directories for {', '.join(missing)}"


@pytest.mark.parametrize("task", [task for task in TASKS if task.id == "T02"], ids=["T02"])
def test_t02_check_fails_if_source_modified(task: rb.Task, reference_copy: Path) -> None:
    with (reference_copy / "calc.py").open("a", encoding="utf-8") as fh:
        fh.write("\n# edited\n")
    assert not rb.run_check(task, reference_copy)
