#!/usr/bin/env python3
"""Tierly benchmark harness.

Runs each task in two variants, with a fresh fixture copy for each run:

* baseline: plain Claude Code on Opus, no plugin
* tierly: the same prompt through `/tierly:tierly --yes`, with the plugin loaded

Both variants use `claude -p ... --output-format json`, which reports `total_cost_usd`
(a client-side estimate). Each task's check script decides pass or fail.

Requires the `claude` CLI. The default uses `--bare` with ANTHROPIC_API_KEY.
Use `--auth subscription` to use your Claude login and plan usage limits.
Use --dry-run to print the commands without running anything.

Usage:
    python benchmarks/run_benchmark.py [--tasks T01,T02] [--variants baseline,tierly]
                                       [--repeat N] [--baseline-effort low|medium|high]
                                       [--auth api-key|subscription]
                                       [--max-cost-usd FLOAT]
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
PLUGIN_DIR = REPO_ROOT / "plugins" / "tierly"
VARIANTS = ("baseline", "tierly")
DEFAULT_BASELINE_EFFORT = "medium"
DEFAULT_AUTH = "api-key"
USAGE_LIMIT_PHRASES = ("usage limit", "5-hour limit", "weekly limit")


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


def build_command(
    task: Task, variant: str, baseline_effort: str = DEFAULT_BASELINE_EFFORT,
    auth: str = DEFAULT_AUTH,
) -> list[str]:
    """Return the claude CLI argv for one run."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    prompt = task.prompt if variant == "baseline" else f"/tierly:tierly --yes {task.prompt}"
    auth_flags = ["--safe-mode", "--strict-mcp-config"] if auth == "subscription" else ["--bare"]
    cmd = [
        "claude", *auth_flags, "-p", prompt,
        "--model", "opus",
        "--output-format", "json",
        "--permission-mode", "acceptEdits",
        "--allowedTools", task.allowed_tools,
    ]
    if variant == "baseline":
        cmd += ["--effort", baseline_effort]
    else:
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
    result_text = data.get("result")
    if not isinstance(result_text, str):
        result_text = None
    else:
        result_text = result_text[:500]
    return {
        "parse_error": False,
        "total_cost_usd": data.get("total_cost_usd"),
        "is_error": bool(data.get("is_error", False)),
        "num_turns": data.get("num_turns"),
        "duration_ms": data.get("duration_ms"),
        "per_model": per_model,
        "result": result_text,
    }


def run_check(task: Task, workdir: Path) -> bool:
    script = BENCH_DIR / task.check
    fixture = BENCH_DIR / "fixtures" / task.fixture
    result = subprocess.run(
        [sys.executable, str(script), str(workdir), str(fixture)],
        capture_output=True, text=True, timeout=300,
    )
    return result.returncode == 0


def run_one(
    task: Task, variant: str, baseline_effort: str = DEFAULT_BASELINE_EFFORT,
    auth: str = DEFAULT_AUTH,
) -> dict[str, Any]:
    fixture = BENCH_DIR / "fixtures" / task.fixture
    with tempfile.TemporaryDirectory(prefix=f"tierly-{task.id}-{variant}-") as tmp:
        workdir = Path(tmp) / task.fixture
        shutil.copytree(fixture, workdir)
        started = time.time()
        try:
            proc = subprocess.run(
                build_command(task, variant, baseline_effort, auth), cwd=workdir,
                capture_output=True, text=True, timeout=task.timeout_s,
            )
            result = parse_result(proc.stdout)
            result["exit_code"] = proc.returncode
            result["stderr"] = proc.stderr[:500]
        except subprocess.TimeoutExpired:
            result = {"parse_error": False, "total_cost_usd": None, "is_error": True,
                      "exit_code": None, "timeout": True, "result": None, "stderr": ""}
        result["wall_s"] = round(time.time() - started, 1)
        result["passed"] = run_check(task, workdir)
    return {"task": task.id, "kind": task.kind, "variant": variant, **result}


def summarize(rows: list[dict[str, Any]], auth: str = DEFAULT_AUTH,
              partial_reason: str | None = None) -> str:
    title = f"Benchmark summary (auth mode {auth})"
    if partial_reason:
        title += f" [partial: {partial_reason}]"
    lines = [title, "",
             "| Task | Variant | Run | Passed | Cost (USD, est.) | Wall (s) |",
             "|---|---|---|---|---|---|"]
    totals: dict[str, float] = {v: 0.0 for v in VARIANTS}
    passes: dict[str, int] = {v: 0 for v in VARIANTS}
    counts: dict[str, int] = {v: 0 for v in VARIANTS}
    missing_costs: dict[str, int] = {v: 0 for v in VARIANTS}
    for row in rows:
        cost = row.get("total_cost_usd")
        cost_s = f"{cost:.4f}" if isinstance(cost, (int, float)) else "n/a"
        lines.append(f"| {row['task']} | {row['variant']} | {row.get('run', 1)} "
                     f"| {'yes' if row['passed'] else 'no'} "
                     f"| {cost_s} | {row.get('wall_s', 'n/a')} |")
        v = row["variant"]
        counts[v] += 1
        passes[v] += int(bool(row["passed"]))
        if isinstance(cost, (int, float)):
            totals[v] += cost
        else:
            missing_costs[v] += 1
    lines.append("")
    lines.append("| Variant | Runs | Pass rate | Mean cost per run (USD, est.) "
                 "| Total cost (USD, est.) | Runs without cost |")
    lines.append("|---|---|---|---|---|---|")
    for v in VARIANTS:
        if counts[v]:
            with_cost = counts[v] - missing_costs[v]
            mean_cost = f"{totals[v] / with_cost:.4f}" if with_cost else "n/a"
            pass_rate = passes[v] / counts[v]
            lines.append(f"| {v} | {counts[v]} | {passes[v]}/{counts[v]} ({pass_rate:.1%}) "
                         f"| {mean_cost} | {totals[v]:.4f} | {missing_costs[v]} |")
    if auth == "subscription":
        lines.extend(["", "The CLI's `total_cost_usd` is a list-price estimate for comparison only. "
                          "Runs count against your plan's usage limits."])
    return "\n".join(lines)


def has_usage_limit_error(row: dict[str, Any]) -> bool:
    """Return whether an errored run reports a Claude usage limit."""
    if not row.get("is_error"):
        return False
    text = " ".join(str(row.get(field, "")) for field in ("result", "stderr"))
    lowered = text.lower()
    return any(phrase in lowered for phrase in USAGE_LIMIT_PHRASES)


def row_cost(row: dict[str, Any]) -> float:
    """Return a completed run's cap cost; missing or invalid costs count as zero."""
    cost = row.get("total_cost_usd")
    return float(cost) if isinstance(cost, (int, float)) else 0.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Tierly benchmark suite.")
    parser.add_argument("--tasks", default="", help="comma-separated task ids (default: all)")
    parser.add_argument("--variants", default=",".join(VARIANTS))
    parser.add_argument("--repeat", type=int, default=1, help="runs per task and variant (default: 1)")
    parser.add_argument("--baseline-effort", choices=("low", "medium", "high"),
                        default=DEFAULT_BASELINE_EFFORT, help="baseline Opus effort (default: medium)")
    parser.add_argument("--auth", choices=("api-key", "subscription"), default=DEFAULT_AUTH,
                        help="Claude authentication mode (default: api-key)")
    parser.add_argument("--max-cost-usd", type=float, default=None,
                        help="stop before a run when completed cost reaches this cap")
    parser.add_argument("--out", type=Path, default=None, help="write JSONL results here")
    parser.add_argument("--dry-run", action="store_true", help="print commands only")
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    if args.max_cost_usd is not None and args.max_cost_usd < 0:
        parser.error("--max-cost-usd must not be negative")

    selected = {t.strip() for t in args.tasks.split(",") if t.strip()} or None
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    for v in variants:
        if v not in VARIANTS:
            parser.error(f"unknown variant: {v}")
    tasks = load_tasks(selected)

    if not args.dry_run and shutil.which("claude") is None:
        print("error: the claude CLI is not on PATH", file=sys.stderr)
        return 2

    rows: list[dict[str, Any]] = []
    total_runs = len(tasks) * len(variants) * args.repeat
    stopped_reason: str | None = None
    missing_cost_seen = False
    for task in tasks:
        for variant in variants:
            for run in range(1, args.repeat + 1):
                label = f"{task.id} {variant} run {run}"
                if args.dry_run:
                    command = build_command(task, variant, args.baseline_effort, args.auth)
                    print(f"[{label}] {shlex.join(command)}")
                    continue
                if args.max_cost_usd is not None:
                    spent = sum(row_cost(row) for row in rows)
                    if spent >= args.max_cost_usd:
                        stopped_reason = (f"stopped at cost cap after {len(rows)} of "
                                          f"{total_runs} runs")
                        break
                print(f"running {label}...", file=sys.stderr)
                row = run_one(task, variant, args.baseline_effort, args.auth)
                row = {**row, "run": run, "baseline_effort": args.baseline_effort,
                       "auth": args.auth}
                rows.append(row)
                if "total_cost_usd" not in row or not isinstance(
                        row.get("total_cost_usd"), (int, float)):
                    missing_cost_seen = True
                if has_usage_limit_error(row):
                    stopped_reason = (f"stopped after usage-limit error after {len(rows)} of "
                                      f"{total_runs} runs")
                    break
            if stopped_reason:
                break
        if stopped_reason:
            break
    if args.dry_run:
        return 0
    if stopped_reason:
        skipped = total_runs - len(rows)
        note = ""
        if args.max_cost_usd is not None and missing_cost_seen:
            note = "; missing costs counted as $0 toward the cap"
        print(f"{stopped_reason}; skipped {skipped} runs{note}", file=sys.stderr)
    if args.out:
        with args.out.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
    print(summarize(rows, args.auth, stopped_reason))
    return 3 if stopped_reason else 0


if __name__ == "__main__":
    sys.exit(main())
