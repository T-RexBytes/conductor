#!/usr/bin/env python3
"""Allot benchmark harness.

Runs each task twice from a clean copy of its fixture:

* baseline: plain Claude Code on Opus, no plugin
* allot:    the same prompt through `/allot:run --yes`, with the plugin loaded

Both runs use `claude --bare -p ... --output-format json`, which reports `total_cost_usd`
(a client-side estimate). Each task's check script decides pass or fail.

Requires the `claude` CLI and ANTHROPIC_API_KEY (bare mode does not use subscription login).
Running it costs money. Use --dry-run to print the commands without running anything.

Usage:
    python benchmarks/run_benchmark.py [--tasks T01,T02] [--variants baseline,allot]
                                       [--out results.jsonl] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BENCH_DIR = Path(__file__).resolve().parent
REPO_ROOT = BENCH_DIR.parent
PLUGIN_DIR = REPO_ROOT / "plugins" / "allot"
VARIANTS = ("baseline", "allot")


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    kind: str
    fixture: str
    prompt: str
    allowed_tools: str
    check: str
    timeout_s: int

    @classmethod
    def from_file(cls, path: Path) -> "Task":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            id=data["id"],
            title=data["title"],
            kind=data["kind"],
            fixture=data["fixture"],
            prompt=data["prompt"],
            allowed_tools=data["allowed_tools"],
            check=data["check"],
            timeout_s=int(data.get("timeout_s", 900)),
        )


def load_tasks(selected: set[str] | None = None) -> list[Task]:
    tasks = [Task.from_file(p) for p in sorted((BENCH_DIR / "tasks").glob("*.json"))]
    if selected:
        unknown = selected - {t.id for t in tasks}
        if unknown:
            raise SystemExit(f"unknown task ids: {sorted(unknown)}")
        tasks = [t for t in tasks if t.id in selected]
    return tasks


def build_command(task: Task, variant: str) -> list[str]:
    """Return the claude CLI argv for one run."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    prompt = task.prompt if variant == "baseline" else f"/allot:run --yes {task.prompt}"
    cmd = [
        "claude", "--bare", "-p", prompt,
        "--model", "opus",
        "--output-format", "json",
        "--permission-mode", "acceptEdits",
        "--allowedTools", task.allowed_tools,
    ]
    if variant == "allot":
        # The orchestrator dispatches subagents through the Agent tool.
        cmd[cmd.index("--allowedTools") + 1] = f"{task.allowed_tools},Agent"
        cmd += ["--plugin-dir", str(PLUGIN_DIR)]
    return cmd


def parse_result(stdout: str) -> dict[str, Any]:
    """Extract cost and status fields from `claude -p --output-format json` output."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return {"parse_error": True, "total_cost_usd": None, "is_error": True}
    if not isinstance(data, dict):
        return {"parse_error": True, "total_cost_usd": None, "is_error": True}
    per_model = data.get("modelUsage", data.get("model_usage"))
    return {
        "parse_error": False,
        "total_cost_usd": data.get("total_cost_usd"),
        "is_error": bool(data.get("is_error", False)),
        "num_turns": data.get("num_turns"),
        "duration_ms": data.get("duration_ms"),
        "per_model": per_model,
    }


def run_check(task: Task, workdir: Path) -> bool:
    script = BENCH_DIR / task.check
    fixture = BENCH_DIR / "fixtures" / task.fixture
    result = subprocess.run(
        [sys.executable, str(script), str(workdir), str(fixture)],
        capture_output=True, text=True, timeout=300,
    )
    return result.returncode == 0


def run_one(task: Task, variant: str) -> dict[str, Any]:
    fixture = BENCH_DIR / "fixtures" / task.fixture
    with tempfile.TemporaryDirectory(prefix=f"allot-{task.id}-{variant}-") as tmp:
        workdir = Path(tmp) / task.fixture
        shutil.copytree(fixture, workdir)
        started = time.time()
        try:
            proc = subprocess.run(
                build_command(task, variant), cwd=workdir,
                capture_output=True, text=True, timeout=task.timeout_s,
            )
            result = parse_result(proc.stdout)
            result["exit_code"] = proc.returncode
        except subprocess.TimeoutExpired:
            result = {"parse_error": False, "total_cost_usd": None, "is_error": True,
                      "exit_code": None, "timeout": True}
        result["wall_s"] = round(time.time() - started, 1)
        result["passed"] = run_check(task, workdir)
    return {"task": task.id, "kind": task.kind, "variant": variant, **result}


def summarize(rows: list[dict[str, Any]]) -> str:
    lines = ["| Task | Variant | Passed | Cost (USD, est.) | Wall (s) |",
             "|---|---|---|---|---|"]
    totals: dict[str, float] = {v: 0.0 for v in VARIANTS}
    passes: dict[str, int] = {v: 0 for v in VARIANTS}
    counts: dict[str, int] = {v: 0 for v in VARIANTS}
    for row in rows:
        cost = row.get("total_cost_usd")
        cost_s = f"{cost:.4f}" if isinstance(cost, (int, float)) else "n/a"
        lines.append(f"| {row['task']} | {row['variant']} | {'yes' if row['passed'] else 'no'} "
                     f"| {cost_s} | {row.get('wall_s', 'n/a')} |")
        v = row["variant"]
        counts[v] += 1
        passes[v] += int(bool(row["passed"]))
        if isinstance(cost, (int, float)):
            totals[v] += cost
    lines.append("")
    lines.append("| Variant | Pass rate | Total cost (USD, est.) |")
    lines.append("|---|---|---|")
    for v in VARIANTS:
        if counts[v]:
            lines.append(f"| {v} | {passes[v]}/{counts[v]} | {totals[v]:.4f} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Allot benchmark suite.")
    parser.add_argument("--tasks", default="", help="comma-separated task ids (default: all)")
    parser.add_argument("--variants", default=",".join(VARIANTS))
    parser.add_argument("--out", type=Path, default=None, help="write JSONL results here")
    parser.add_argument("--dry-run", action="store_true", help="print commands only")
    args = parser.parse_args(argv)

    selected = {t.strip() for t in args.tasks.split(",") if t.strip()} or None
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    for v in variants:
        if v not in VARIANTS:
            parser.error(f"unknown variant: {v}")
    tasks = load_tasks(selected)

    if args.dry_run:
        for task in tasks:
            for variant in variants:
                print(f"[{task.id} {variant}] " + shlex.join(build_command(task, variant)))
        return 0

    if shutil.which("claude") is None:
        print("error: the claude CLI is not on PATH", file=sys.stderr)
        return 2

    rows = []
    for task in tasks:
        for variant in variants:
            print(f"running {task.id} ({variant})...", file=sys.stderr)
            rows.append(run_one(task, variant))
    if args.out:
        with args.out.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
    print(summarize(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
