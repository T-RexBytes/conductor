# Routing rubric

The tier table (models, effort levels, score bands, cost index) lives in `tiers.json`. This file
explains how to score a micro-task and which rules override the score.

## Scoring axes

Score each axis from 0 to 3. Score the micro-task, not the whole request.

### Complexity: how hard is the reasoning?

| Score | Meaning | Examples |
|---|---|---|
| 0 | Lookup or copy | Find where `X` is defined; list the files in `src/api/` |
| 1 | Mechanical change with an obvious answer | Rename a symbol; add a field to a type; write a docstring |
| 2 | Normal engineering judgment | Implement a function from a clear spec; fix a bug with a known cause |
| 3 | Deep reasoning or design | Choose an architecture; find an unknown root cause; concurrency, algorithms |

### Ambiguity: how fully is the task specified?

| Score | Meaning |
|---|---|
| 0 | Fully specified; one correct result |
| 1 | Small gaps that conventions in the codebase answer |
| 2 | Several reasonable approaches; a choice must be made and justified |
| 3 | Goal unclear. **Ask the user before dispatching.** Do not route ambiguity to a bigger model. |

### Risk: what does a mistake cost?

| Score | Meaning |
|---|---|
| 0 | Read-only, or output the user will read and discard |
| 1 | Local and easily reverted (docs, tests, internal helpers) |
| 2 | User-facing behavior, public APIs, shared modules, data formats |
| 3 | Security, authentication, payments, secrets, data deletion or migration, production infrastructure, anything irreversible |

### Breadth: how much context must the agent hold?

| Score | Meaning |
|---|---|
| 0 | One small file or a single fact |
| 1 | A few files in one module |
| 2 | Several modules, or one large file |
| 3 | Cross-cutting, or likely to need more than about 100k tokens of context |

## From score to tier

1. `raw = Complexity + Ambiguity + Risk + Breadth` (0 to 12).
2. `score = clamp(raw + profile_shift, 0, 12)`. The shift comes from `profiles` in
   `tiers.json`: budget -2, balanced 0, quality +2.
3. Pick the tier whose `score_min..score_max` band contains `score`.

## Hard floors (override the score)

Apply in order; the highest floor wins.

| Condition | Floor | Why |
|---|---|---|
| The task writes or edits files | `worker` | `scout` is read-only by design |
| Breadth = 3 | `builder` | Large context; Haiku 5.5 prices rise 5x above 100k input tokens and quality drops in long prompts |
| Risk = 3, design or decision work | `architect` | A wrong call is expensive |
| Risk = 3, implementation of an agreed design | `builder-plus` | Careful implementation; the watcher is mandatory |
| Complexity = 3 and Ambiguity >= 2 | `architect` | Judgment-heavy |
| Ambiguity = 3 | none: ask the user | Bigger models do not resolve missing requirements |

A floor raises the tier; it never lowers it. Profiles never move a task below its floor.

## Watcher policy

The watcher reviews a task when any of these is true:

- it writes files and its final score is 5 or more;
- its Risk is 2 or more;
- the profile is `quality` and the task writes files;
- its report is `partial`, malformed, or missing.

The orchestrator checks read-only scout output itself.

The watcher runs on Sonnet at high effort with cost index 20. The architect remains the Opus
tier for design and other judgment-heavy work.

## Worked examples

| Micro-task | C | A | R | B | Raw | Tier (balanced) | Notes |
|---|---|---|---|---|---|---|---|
| Find every caller of `charge()` | 0 | 0 | 0 | 1 | 1 | scout | Read-only |
| Add JSDoc to 6 exported functions in `utils/date.ts` | 1 | 0 | 1 | 1 | 3 | worker | Not reviewed (score below 5, Risk 1) |
| Write unit tests for `parseInvoice()` from its spec | 1 | 1 | 1 | 1 | 4 | worker | |
| Add pagination to `/orders` following the `/users` pattern | 2 | 1 | 2 | 1 | 6 | builder | Reviewed (Risk 2) |
| Fix flaky test with unknown cause in the queue worker | 3 | 1 | 1 | 2 | 7 | builder | Escalates on fail |
| Refactor the config loader used by 4 services | 2 | 1 | 2 | 3 | 8 | builder-plus | Breadth floor already met |
| Design token-refresh flow for the auth service | 3 | 2 | 3 | 2 | 10 | architect | Risk 3 design floor |
| Implement the agreed token-refresh design | 2 | 0 | 3 | 2 | 7 | builder-plus | Risk 3 implementation floor; watcher mandatory |

## Cost index

`cost_index` in `tiers.json` is the per-token price ratio between models (Haiku 1, Sonnet 20,
Opus 40), from list prices on the snapshot date. It ranks plans by relative cost; it is not a
bill. Real cost also depends on tokens used, effort, and caching.
