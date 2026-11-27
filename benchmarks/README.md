# Benchmarks

Measures whether Allot lowers cost **without** lowering quality. Every task runs twice from a
clean copy of its fixture:

| Variant | Command |
|---|---|
| baseline | `claude --bare -p "<prompt>" --model opus --output-format json ...` |
| allot | `claude --bare -p "/allot:run --yes <prompt>" --model opus --plugin-dir ./plugins/allot ...` |

The harness records `total_cost_usd` from the JSON output (a client-side estimate) and runs the
task's check script for pass or fail.

## Run

```bash
python benchmarks/run_benchmark.py --dry-run          # print the commands, run nothing
export ANTHROPIC_API_KEY=...                           # bare mode needs an API key
python benchmarks/run_benchmark.py --out results.jsonl
python benchmarks/run_benchmark.py --tasks T01 --variants allot
```

Running the suite costs money. In CI it runs only on manual dispatch (`benchmark.yml`).

## Layout

| Path | Contents |
|---|---|
| `tasks/*.json` | One task per file: id, title, kind, fixture, prompt, allowed tools, check script, timeout |
| `fixtures/<name>/` | Starting project for tasks; copied fresh for every run |
| `checks/*.py` | Pass/fail scripts, called as `python check.py <workdir> <fixture_dir>` |
| `run_benchmark.py` | The harness |

## Adding a task

1. Add or reuse a fixture under `fixtures/`. Keep it small and deterministic.
2. Write `checks/check_<id>.py`. It must print `PASS` or `FAIL: <reason>` and exit 0 only on pass.
   Check behavior, not wording.
3. Add `tasks/<id>-<slug>.json`. List only the tools the task needs in `allowed_tools`.
4. Add a test in `tests/test_benchmarks.py` proving the check fails on the untouched fixture and
   passes on a reference solution.

Aim for a mix of `kind` values: `read-heavy`, `mixed`, `judgment-heavy`, `tiny`.

## Acceptance rule for routing changes

Pass rate must not drop, and total cost must not rise, compared with `main`.
