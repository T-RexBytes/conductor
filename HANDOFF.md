# HANDOFF: project status and where to continue

| | |
|---|---|
| Snapshot date | 2026-11-27 |
| Prepared for | Claude Code (and the maintainer), continuing the build from this repo |
| Current version | 0.1.0 (unreleased) |
| Read first | `CLAUDE.md` → this file → `docs/MVP.md` → `docs/BUILD-SPEC.md` |

## 1. What this project is

Tierly is a Claude Code plugin. `/tierly <task>` plans the task, scores each micro-task,
routes it to the cheapest Claude tier that can do it well (Haiku / Sonnet / Opus subagents at fixed
effort levels), reviews non-trivial work with a read-only Opus watcher, escalates failures one
tier up, and reports. It must never interfere with anything outside `/tierly`
(BUILD-SPEC section 6).

## 2. Work already done (verified)

### Plugin (draft complete)

| File | Status |
|---|---|
| `.claude-plugin/marketplace.json` | Done |
| `plugins/tierly/.claude-plugin/plugin.json` | Done (version 0.1.0) |
| `plugins/tierly/README.md` | Done |
| `plugins/tierly/skills/tierly/SKILL.md` | Done: hard rules, flags, triage, decomposition, scoring, plan approval, dispatch, watcher, escalation, integration, report, failure handling |
| `plugins/tierly/skills/tierly/reference/tiers.json` | Done: single source of truth for tiers |
| `plugins/tierly/skills/tierly/reference/ROUTING.md` | Done: rubric, hard floors, watcher policy, worked examples |
| `plugins/tierly/skills/tierly/reference/{PLAN,BRIEF,REPORT}_TEMPLATE.md`, `WATCHER_RUBRIC.md` | Done |
| `plugins/tierly/agents/{scout,worker,builder,builder-plus,architect,watcher}.md` | Done |

### Docs (done)

`README.md`, `CLAUDE.md`, `docs/MVP.md`, `docs/BUILD-SPEC.md`, `docs/NON-INTERFERENCE.md`,
`docs/SAVINGS-MODEL.md`, `docs/PRICING-SNAPSHOT.md`, `docs/BRIDGES.md` (v0.3 design only),
`docs/TROUBLESHOOTING.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
`CHANGELOG.md`, `LICENSE`.

### Tooling (done)

| Item | Status |
|---|---|
| `scripts/validate_repo.py` | Done; passes |
| `tests/test_validate_repo.py`, `tests/test_benchmarks.py` | Done; 46 tests pass |
| `benchmarks/run_benchmark.py` + tasks T01, T02 + `fixtures/calc` + checks | Done; dry run works; **never run against real Claude yet** |
| `.github/workflows/ci.yml` | Done (validate, plugin-validate, markdown, links, spelling) |
| `.github/workflows/benchmark.yml` | Done (manual dispatch only) |
| Issue templates, PR template, CODEOWNERS, dependabot | Done |

### Checks run on this snapshot

- `python scripts/validate_repo.py` → passed
- `python -m pytest -q` → 46 passed
- `markdownlint-cli2 "**/*.md"` → 0 issues
- `codespell` → clean
- Relative link and anchor check → 0 problems
- `claude plugin validate .` → passed (Claude Code 2.1.332)
- Stricter quality check (`claude plugin validate ./plugins/tierly --profile directory`) →
  passed, 1 warning (no icon)

Facts confirmed by those runs:

- `claude plugin validate` works **without authentication** (closes BUILD-SPEC item V5).
- The plugin exposes `/tierly`, `tierly:scout`, `tierly:worker`, `tierly:builder`,
  `tierly:builder-plus`, `tierly:architect`, `tierly:watcher` (supports item V2;
  dispatch still to be tested in a live session).

## 3. Start here: next tasks, in order

Do them in this order. After each one, run `python scripts/validate_repo.py` and
`python -m pytest -q`.

### Step 1: Finish the paperwork from this snapshot (small)

1. In `docs/BUILD-SPEC.md` section 13, mark **V5 resolved** (validate runs without auth) and
   record for **V2** that the validator lists the agents as `tierly:<name>`; a live dispatch test
   is still needed.
2. In `.github/workflows/ci.yml`, use the stricter quality check for the plugin step:
   `claude plugin validate ./plugins/tierly --profile directory`.
3. Commit: `chore: record verification results and tighten plugin validation`.

### Step 2: Put the repo on GitHub (milestone M1)

1. `git init`, commit, push to `T-RexBytes/conductor`.
2. Confirm all CI jobs pass on GitHub. If `markdownlint-cli2-action@v19` or another action version
   fails to resolve, bump it to the latest major and note it in the commit.
3. The 2026-11-27 name check found that "conductor" collided, so the plugin was renamed Tierly and
   needs no further name check because it is not published to any directory.

### Step 3: Live verification (milestones M2–M5)

Run Claude Code with `claude --plugin-dir ./plugins/tierly` in a scratch project and work through
the behavioral evals **E1–E10** in `docs/BUILD-SPEC.md` section 11.2. Record each result.

While doing that, answer the open verification items and update BUILD-SPEC section 13:

| Item | How to check |
|---|---|
| V1 | After a dispatch, see whether the Agent tool result shows token usage to the orchestrator |
| V2 | Confirm `/tierly` actually dispatches `tierly:scout` etc. by those names |
| V3 | Approve a plan via the question card, then check the orchestrator is still on Opus |
| V4 | If possible, test with an account or setting without Opus access |

If any eval fails, fix SKILL.md, the agent or the reference file, then re-run that eval.

### Step 4: Benchmarks (milestone M6)

1. With `ANTHROPIC_API_KEY` set, run `python benchmarks/run_benchmark.py --out results.jsonl`.
2. Acceptance: Tierly pass rate equals baseline, total cost lower (MVP criteria A3, A4).
3. If `total_cost_usd` or the per-model field names differ from what `parse_result()` expects,
   update the harness and its tests.
4. Add more tasks (target 10+, mixed kinds) following `benchmarks/README.md`.

### Step 5: Release (milestone M7)

1. A square PNG icon at `plugins/tierly/.claude-plugin/icon.png` (512–2048 px, under 2 MB) is
   optional and only removes the validator warning.
2. Replace modeled savings ranges in README with measured results once benchmarks support them.
3. Tick every box in `docs/MVP.md` section 5, update `CHANGELOG.md`, tag `v0.1.0`.

## 4. Decisions already made (do not reopen without an issue)

- **Name:** Tierly (chosen by the maintainer on 2026-11-27 after "Conductor" collided with
  several existing Claude Code plugins and products). Earlier working names: "Allot" and
  "Conductor". "Tierward" and "Cadre" were rejected because they are taken.
- **Distribution:** GitHub only, from this repo's own marketplace. Not submitted to the official
  plugin directory or any other listing.
- **Claude-first.** Other providers (Codex, Gemini) are v0.3 "Bridges", opt-in only.
- **No hooks at all.** Plugin hooks fire every session, and skill-frontmatter hooks stay
  registered after the skill runs. Both would break non-interference.
- **No probing.** Tierly never runs web, network or shell actions for its own purposes.
- **`disallowedTools` only, never `tools` allowlists,** so the user's MCP tools stay available.
- **Model aliases** (`haiku`, `sonnet`, `opus`), not pinned IDs. Effort only `low|medium|high` in
  v0.1.
- **No worktrees in v0.1.** Overlapping writes are serialized instead.
- **Cost shown as a relative index** (Haiku 1, Sonnet 20, Opus 40), labeled as an estimate.

## 5. Known gaps and risks

- The benchmark harness has never run against real Claude. Its output parsing is based on the
  documented JSON fields and may need adjustment.
- Prices and effort guidance in `docs/PRICING-SNAPSHOT.md` date from 2026-11-27. Refresh them on
  any model release.
- CI action versions were chosen without a live run. Dependabot will keep them current after the
  first green build.
