# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - unreleased

Renamed from the working name Allot to Conductor; the command is `/conductor`.

### Added

- `/conductor` orchestrator skill with triage gate, four-axis scoring, hard floors, profiles,
  plan approval, watcher review and escalation ladder.
- Agents: scout, worker, builder, builder-plus, architect, watcher.
- Routing table `tiers.json` and rubric `ROUTING.md`.
- Non-interference guarantees N1–N11 with static checks in CI.
- Repository validator, pytest suite, CI workflows, benchmark harness with seed tasks.
- Documentation: MVP, build spec, non-interference, savings model, pricing snapshot, bridges
  design, troubleshooting, contribution guides.
