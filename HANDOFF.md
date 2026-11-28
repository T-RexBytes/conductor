# HANDOFF

Snapshot date: 2026-11-28

Read first: `CLAUDE.md`, then `docs/MVP.md` and `docs/BUILD-SPEC.md`.

## Done

- The 0.1.0 items listed under Added in CHANGELOG.md: orchestrator, six agents, routing,
  non-interference checks, validator, CI, benchmark harness and tasks, documentation, evals,
  routing clarifications, live-eval fixes, GitHub marketplace distribution and Dependabot.
- Live evals: E1, E2, E4, E6 and E9 passed. E3 passed except its one-line plan printed in 2 of 3
  runs. E5 and E10 exposed gaps; fixes are in the skill and are being re-checked. E7, E8, V1, V3
  and V4 are manual checks in docs/MANUAL-CHECKS.md.
- GitHub install checked with Claude Code 2.1.332: marketplace add and plugin install succeeded,
  the plugin was enabled, and `claude plugin validate` passed.
- CI is green.
- The benchmark harness has 10 tasks, but there are no valid measured results yet. Savings remain
  modeled ranges.

## Remaining, in order

1. Re-check E5 and E10.
2. Re-check the one-line plan in E3.
3. Run benchmarks in subscription mode once the harness fix lands.
4. Complete the manual checks in docs/MANUAL-CHECKS.md.
5. Complete the MVP section 5 checkboxes.
6. Tag v0.1.0.

## Running checks

- Gate: `python scripts/validate_repo.py`, `python -m pytest -q`, `claude plugin validate .`
  and `claude plugin validate ./plugins/tierly`.
- Evals: `claude plugin eval ./plugins/tierly --scaffold --allow-tools "Write,Edit" --ablation
  none --no-publish --judge-model sonnet`. On Windows, plugin eval refuses any shell grant because
  there is no sandbox, so E4 and E6 (which run pytest) are run as headless
  `claude -p --plugin-dir ./plugins/tierly` sessions in a copy of each case's `files/` and graded
  by hand. A Haiku judge read graders too literally, so use Sonnet.
- Benchmarks without an API key: `python benchmarks/run_benchmark.py --auth subscription --tasks
  T03,T06 --max-cost-usd 3`. Runs count against the plan's usage limits.

## Decisions that stand

- Name: Tierly. Owner: Sourish Panda.
- GitHub only; no directory listing.
- No hooks and no probing.
- Use `disallowedTools` only.
- Use model aliases.
- No worktrees in v0.1.
- Label the cost index as an estimate.
