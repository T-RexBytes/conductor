# HANDOFF

Snapshot date: 2026-11-29

Read first: `CLAUDE.md`, then `docs/MVP.md` and `docs/BUILD-SPEC.md`.

## Done

- The 0.1.0 items listed under Added in CHANGELOG.md: orchestrator, six agents, routing,
  non-interference checks, validator, CI, benchmark harness and tasks, documentation, evals,
  routing clarifications, live-eval fixes, GitHub marketplace distribution and Dependabot.
- Current behavioral evals: E1, E2, E3, E5, E9 and E10 pass. E4 and E6 passed as headless runs.
  E7, E8, V1, V3 and V4 are manual checks in MANUAL-CHECKS.md. Earlier runs printed E3's plan
  line in about 2 of 3 runs.
- GitHub install checked with Claude Code 2.1.332: marketplace add and plugin install succeeded,
  the plugin was enabled, and `claude plugin validate` passed.
- CI is green.
- Benchmark experiments completed for T03 and T06, including the effort, watcher, and routing
  card configurations. See docs/BENCHMARK-RESULTS.md; current Tierly costs more on these tasks.

## Remaining, in order

1. Complete the manual checks in MANUAL-CHECKS.md.
2. Resolve V1, V3 and V4.
3. Review Dependabot PRs #9 and #10; they wait for the owner's OK.
4. Reach lower cost than baseline (A4).
5. Create the v0.1.0 tag.
6. Set branch protection when the owner asks.

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
