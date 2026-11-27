"""Tests for the benchmark harness and check scripts. No network, no claude CLI needed."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BENCH = REPO / "benchmarks"
sys.path.insert(0, str(BENCH))

import run_benchmark as rb  # noqa: E402


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
        {"task": "T01", "variant": "baseline", "passed": True, "total_cost_usd": 1.0, "wall_s": 10},
        {"task": "T01", "variant": "conductor", "passed": True, "total_cost_usd": 0.6, "wall_s": 12},
    ]
    text = rb.summarize(rows)
    assert "| baseline | 1/1 | 1.0000 |" in text
    assert "| conductor | 1/1 | 0.6000 |" in text


def test_dry_run_runs_nothing(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args, **kwargs):
        raise AssertionError("subprocess must not run in dry-run")

    monkeypatch.setattr(subprocess, "run", boom)
    assert rb.main(["--dry-run", "--tasks", "T01"]) == 0
    out = capsys.readouterr().out
    assert "[T01 baseline] claude --bare -p" in out
    assert "[T01 conductor] claude --bare -p '/conductor:conductor --yes" in out


def _run_check(task_id: str, workdir: Path) -> int:
    task = rb.load_tasks({task_id})[0]
    fixture = BENCH / "fixtures" / task.fixture
    return subprocess.run(
        [sys.executable, str(BENCH / task.check), str(workdir), str(fixture)],
        capture_output=True, text=True,
    ).returncode


@pytest.fixture()
def calc_copy(tmp_path: Path) -> Path:
    dest = tmp_path / "calc"
    shutil.copytree(BENCH / "fixtures" / "calc", dest)
    return dest


def test_t01_check_fails_on_fixture(calc_copy: Path) -> None:
    assert _run_check("T01", calc_copy) != 0


def test_t01_check_passes_on_reference_solution(calc_copy: Path) -> None:
    with (calc_copy / "calc.py").open("a", encoding="utf-8") as fh:
        fh.write(
            "\n\ndef divide(a: float, b: float) -> float:\n"
            "    \"\"\"Return a / b.\"\"\"\n"
            "    if b == 0:\n"
            "        raise ValueError(\"division by zero\")\n"
            "    return a / b\n"
        )
    with (calc_copy / "tests" / "test_calc.py").open("a", encoding="utf-8") as fh:
        fh.write(
            "\n\ndef test_divide():\n"
            "    assert calc.divide(6, 3) == 2\n\n\n"
            "def test_divide_by_zero():\n"
            "    import pytest\n"
            "    with pytest.raises(ValueError):\n"
            "        calc.divide(1, 0)\n"
        )
    assert _run_check("T01", calc_copy) == 0


def test_t02_check_fails_on_fixture(calc_copy: Path) -> None:
    assert _run_check("T02", calc_copy) != 0


def test_t02_check_passes_on_reference_solution(calc_copy: Path) -> None:
    docs = calc_copy / "docs"
    docs.mkdir()
    blocks = "".join(
        f"## {name}(a, b)\n\nReturns a number.\n\n```python\ncalc.{name}(1, 2)\n```\n\n"
        for name in ("add", "subtract", "multiply")
    )
    (docs / "API.md").write_text("# API\n\n" + blocks, encoding="utf-8")
    assert _run_check("T02", calc_copy) == 0


def test_t02_check_fails_if_source_modified(calc_copy: Path) -> None:
    docs = calc_copy / "docs"
    docs.mkdir()
    (docs / "API.md").write_text("add subtract multiply\n```\nx\n```\n", encoding="utf-8")
    with (calc_copy / "calc.py").open("a", encoding="utf-8") as fh:
        fh.write("\n# edited\n")
    assert _run_check("T02", calc_copy) != 0
