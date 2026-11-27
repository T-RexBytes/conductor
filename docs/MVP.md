# Tierly MVP (v0.1.0)

The smallest release that proves the core claim: **routing micro-tasks to cheaper Claude tiers,
with an independent watcher, cuts cost without losing quality, and never gets in the user's way.**

Full technical detail: [BUILD-SPEC.md](BUILD-SPEC.md).

## 1. Who it is for

Claude Code users on API billing or a subscription who run multi-step coding and knowledge tasks
and want lower spend or slower usage-limit burn without supervising model choice by hand.

## 2. User stories

| ID | As a user, I want to... | So that... |
|---|---|---|
| U1 | type `/tierly <task>` and get the task done | I do not pick models and effort myself |
| U2 | see the plan (tasks, tiers, cost index) before anything runs | I stay in control of spend |
| U3 | approve, edit, switch to a budget profile, or cancel the plan | the run matches my priorities |
| U4 | trust that cheap tiers did not cut corners | quality matches what I would get from Opus |
| U5 | have Tierly stay silent unless I call it | my normal work, skills and MCP tools are untouched |
| U6 | get a short report of what ran where and what changed | I can review the work quickly |
| U7 | have small requests handled without ceremony | I never pay orchestration overhead for a one-line fix |

## 3. In scope

1. Plugin installable from GitHub through a Claude Code marketplace.
2. One skill, `/tierly`, with flags `--plan-only`, `--yes`, `--no-recon`, `--profile`,
   `--parallel`.
3. Six agents: scout, worker, builder, builder-plus, architect, watcher.
4. Routing: four-axis scoring, score bands, hard floors, profiles (`tiers.json`, `ROUTING.md`).
5. Triage gate with direct dispatch for small work.
6. Plan approval through AskUserQuestion, with a plain-reply fallback.
7. Watcher review, batching, escalation ladder (at most 2 per task).
8. Report with routing mix and relative cost index (labeled as an estimate).
9. Non-interference guarantees N1–N11, with static checks enforced in CI.
10. CI: repo validator, pytest, official plugin validation, markdownlint, offline link check,
    codespell.
11. Benchmark harness with 2 seed tasks and one fixture.
12. Contributor docs: CLAUDE.md, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, issue and PR templates.

## 4. Out of scope (and why)

| Item | Reason | Planned |
|---|---|---|
| Other providers (Codex, Gemini) | Claude-first; adds auth, quota and sandbox complexity | v0.3 |
| Measured token usage per task in the report | Depends on verification item V1 | v0.2 |
| Worktree isolation for parallel writes | Needs merge handling; MVP serializes overlapping work instead | v0.4 |
| `xhigh` / `max` effort, Fable tier | Cost rarely justified for routine orchestration | v0.4 (opt-in) |
| claude.ai / Skills API support | Those surfaces reject required frontmatter and lack subagent model routing | not planned |
| Auto-activation | Contradicts the non-interference promise | never |

## 5. Acceptance criteria

The MVP ships when every item below is true.

### Functional

- [ ] A1. Fresh install from the GitHub marketplace works; `/tierly` appears in the `/` menu.
- [ ] A2. Behavioral evals E1–E10 from BUILD-SPEC section 11.2 pass and are recorded in the
      release PR.
- [ ] A3. On the seed benchmark tasks, Tierly's pass rate equals the baseline's.
- [ ] A4. On the seed benchmark tasks, Tierly's total cost is lower than the baseline's.
- [ ] A5. A one-line request takes the direct-dispatch path with no approval prompt.
- [ ] A6. `--plan-only` writes no files and dispatches nothing.

### Non-interference

- [ ] A7. CI enforces N1–N5, N10 and the static parts of N6, N7 and N11.
- [ ] A8. Manual checks for N6–N9 and N11 pass (no probing commands, no settings changes, model
      override ends with the run, no stray files, denied permissions not worked around).

### Quality and project hygiene

- [ ] A9. All CI jobs green on `main`.
- [ ] A10. Verification items V1–V5 resolved and the spec updated with the answers.
- [ ] A11. README states savings only as modeled ranges until benchmarks show measured numbers.
- [ ] A12. CHANGELOG has the 0.1.0 entry; tag `v0.1.0` created.

## 6. Success metrics (first 30 days after release)

| Metric | Target |
|---|---|
| Median cost reduction on the benchmark suite, quality held | ≥ 25% |
| Watcher `fail` rate on first attempt | ≤ 15% (higher means routing is too aggressive) |
| Tasks needing more than one escalation | ≤ 5% |
| Bug reports about Tierly interfering with non-Tierly work | 0 |

## 7. Milestones

| # | Milestone | Output | Exit check |
|---|---|---|---|
| M1 | Scaffold | Repo, manifests, CI green on docs and validator | CI passes |
| M2 | Agents and routing | Six agents, `tiers.json`, `ROUTING.md` | Validator passes; E1 passes |
| M3 | Orchestrator | SKILL.md and templates | E2, E3, E9 pass |
| M4 | Watcher and escalation | Watcher rubric, escalation flow | E4, E6 pass |
| M5 | Hardening | Injection, permissions, MCP checks | E5, E7, E8, E10 pass |
| M6 | Verification and benchmarks | V1–V5 closed; seed benchmarks run | A3, A4 pass |
| M7 | Release | Docs final, CHANGELOG, tag | A1–A12 all checked |

## 8. Demo script (for README GIF and presentations)

1. Show a normal prompt in Claude Code: Tierly does nothing (non-interference).
2. `/tierly --plan-only add pagination to the orders API with tests` → the plan table.
3. `/tierly add pagination to the orders API with tests` → approve → progress → watcher
   verdicts → report with routing mix and cost index.
4. `/tierly fix the typo in README` → direct dispatch, no approval prompt.

## 9. Risks

| Risk | Mitigation |
|---|---|
| Cheap tiers miss subtle bugs | Watcher on all non-trivial writes; floors for Risk and Breadth; escalation |
| Overhead exceeds savings on small tasks | Triage gate; batching watcher calls; brief length limits |
| Model or effort guidance changes | Aliases in agents; routing review on each model release |
| Users expect exact cost numbers | Cost index is labeled as an estimate; benchmarks give measured numbers |
| Name collision on publish | Renamed to Tierly after the 2026-11-27 check; not published to any directory |
