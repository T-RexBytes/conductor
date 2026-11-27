# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - unreleased

Renamed from the working names Allot and Conductor to Tierly; the command is `/tierly`.

### Added

- `/tierly` orchestrator skill with triage gate, four-axis scoring, hard floors, profiles,
  plan approval, watcher review and escalation ladder.
- Agents: scout, worker, builder, builder-plus, architect, watcher.
- Routing table `tiers.json` and rubric `ROUTING.md`.
- Non-interference guarantees N1–N11 with static checks in CI.
- Repository validator, pytest suite, CI workflows, benchmark harness with seed tasks.
- Documentation: MVP, build spec, non-interference, savings model, pricing snapshot, bridges
  design, troubleshooting, contribution guides.
- Behavioral evals E1-E6, E9 and E10 for `claude plugin eval` in `plugins/tierly/evals/`.
- Benchmark harness options `--repeat` and `--baseline-effort`. Reference-solution overlays,
  generic tests, the `inventory` fixture and tasks T03-T10.
- Routing clarifications with the same score bands. Score before triage and apply the same
  watcher rule to direct dispatch and full orchestration. Read-only scout lookups never
  escalate to a tier that can write. The `builder-plus` watcher fallback is review-only.
- Skill fixes from live evals. Print the one-line plan before direct dispatch and ask one
  clarifying question when needed. Label the cost index as an estimate for dispatched work
  only, excluding the orchestrator's own Opus usage.
- GitHub-only distribution through this repo's own marketplace, with no directory listing.
- Monthly Dependabot updates grouped by ecosystem. Text files use LF line endings.
