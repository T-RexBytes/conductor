# Benchmarks

Measures whether Tierly lowers cost **without** lowering quality. Each task runs in two
variants, with a fresh fixture copy for each run. The commands below use the default auth mode.

| Variant | Command |
|---|---|
| baseline | `claude --bare -p "<prompt>" --model opus --effort medium --output-format json ...` |
| tierly | `claude --bare -p "/tierly:tierly --yes <prompt>" --model opus --plugin-dir ./plugins/tierly ...` |

The harness records `total_cost_usd` from the JSON output (a client-side estimate) and runs the
task's check script for pass or fail.

## Run

```bash
python benchmarks/run_benchmark.py --dry-run          # print the commands, run nothing
export ANTHROPIC_API_KEY=...                           # bare mode needs an API key
python benchmarks/run_benchmark.py --out results.jsonl
python benchmarks/run_benchmark.py --repeat 3 --baseline-effort high --out results.jsonl
python benchmarks/run_benchmark.py --tasks T01 --variants tierly
```

The default `--auth api-key` uses `--bare` and requires `ANTHROPIC_API_KEY`. If you have a Claude
subscription, sign in to Claude Code and use `--auth subscription`. Both variants then use
`--safe-mode --strict-mcp-config`, and the Tierly variant loads the plugin for that session.
Subscription runs count against your plan's usage limits, so start with a small pilot.
The reported dollar amounts are CLI list-price estimates for comparison only.

```bash
python benchmarks/run_benchmark.py --auth subscription --tasks T03,T06 --repeat 1 --max-cost-usd 3
```

`--repeat N` runs each task and variant N times (default 1, minimum 1). The dry run prints
each command with its run index. `--baseline-effort` accepts `low`, `medium`, or `high` and
defaults to `medium`, the documented Opus default. The Tierly skill sets its orchestrator's
effort. Each JSONL row records the run index, selected baseline effort, and auth mode.
The summary reports pass rate over all runs and mean cost over runs with a reported cost.
`--max-cost-usd FLOAT` stops before launching another run once completed reported costs reach
the cap. Runs without a reported cost count as zero. A capped or usage-limited suite writes the
completed rows and a partial summary, then exits with status 3.

API-key runs incur API charges. In CI the suite runs only on manual dispatch (`benchmark.yml`).

## Layout

| Path | Contents |
|---|---|
| `tasks/*.json` | One task per file: id, title, kind, fixture, prompt, allowed tools, check script, timeout |
| `fixtures/<name>/` | Starting project for tasks; copied fresh for every run |
| `checks/*.py` | Pass/fail scripts, called as `python check.py <workdir> <fixture_dir>` |
| `checks/hidden/<id>/` | Hidden tests that check scripts may copy into the workdir after the agent finishes. The agent under test never sees them. |
| `reference/<id>/` | Reference solution files copied over a fresh fixture, replacing files at matching paths |
| `run_benchmark.py` | The harness |

## Adding a task

1. Add or reuse a fixture under `fixtures/`. Keep it small and deterministic.
2. Write `checks/check_<id>.py`. It must print `PASS` or `FAIL: <reason>` and exit 0 only on pass.
   Check behavior, not wording.
3. Add `tasks/<id>-<slug>.json`. List only the tools the task needs in `allowed_tools`.
4. Add `reference/<id>/` with a reference solution. The generic tests check it.

Aim for a mix of `kind` values: `read-heavy`, `mixed`, `judgment-heavy`, `tiny`.

## Acceptance rule for routing changes

Mean pass rate must not drop, and mean cost per run must not rise, compared with `main`.
