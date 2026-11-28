# Tierly

**Cost-aware, plan-first orchestration for Claude Code.** Tierly breaks your task into
micro-tasks, gives each one to the cheapest Claude model and effort level that can do it well,
checks the work with an independent reviewer, and tells you what ran where.

```text
/tierly add pagination to the orders API, with tests that pass
```

[![CI](https://github.com/T-RexBytes/tierly/actions/workflows/ci.yml/badge.svg)](https://github.com/T-RexBytes/tierly/actions/workflows/ci.yml)
![Status: pre-release](https://img.shields.io/badge/status-pre--release-orange)
![License: MIT](https://img.shields.io/badge/license-MIT-blue)

## Why

One Claude Code session usually runs every step on one model. Searching for a symbol then costs
as much per token as designing a migration. Per-token prices across Claude models differ by up
to 40x, so routine steps are where most of the waste is. Tierly moves routine steps down to Haiku
and Sonnet, keeps judgment on Opus, and has a Sonnet watcher check anything that matters.

## Install

In Claude Code:

```text
/plugin marketplace add T-RexBytes/tierly
/plugin install tierly@tierly
```

## Use

Type `/tierly` (or `/tierly:tierly` if the name is taken), followed by your task:

```text
/tierly [--plan-only] [--yes] [--no-recon] [--profile budget|balanced|quality] [--parallel N] <task>
```

| Flag | Effect | Default |
|---|---|---|
| `--plan-only` | Show the plan and stop | off |
| `--yes` | Skip plan approval (the plan is still shown) | off |
| `--no-recon` | Plan from your text only; no reading of project files first | off |
| `--profile` | `budget` routes lower, `quality` routes higher and reviews more | `balanced` |
| `--parallel N` | Subagents running at once (1–8) | 4 |

What happens:

1. **Understand.** Tierly restates your goal and asks one question if something important is
   unclear.
2. **Triage.** Small requests go straight to the right agent, with no plan to approve.
3. **Plan.** Larger work is split into micro-tasks. Each is scored 0–3 on complexity,
   ambiguity, risk and breadth, and routed to a tier. You see the plan and approve, edit, or
   cancel it.
4. **Run.** Independent tasks run in parallel. Each subagent gets a self-contained brief.
5. **Check.** A read-only Sonnet watcher reviews every non-trivial change. Failed work is redone one
   tier up, at most twice, and then Tierly asks you.
6. **Report.** Outcome, files changed, what ran on which model, and a relative cost estimate.

## Routing

| Tier | Model / effort | Typical work |
|---|---|---|
| scout | Haiku / low | Read-only lookups: find files, symbols, usages |
| worker | Haiku / medium | Mechanical edits from a clear spec: boilerplate, tests, docs |
| builder | Sonnet / medium | Well-specified features, bug fixes with a known cause |
| builder-plus | Sonnet / high | Harder, cross-module or debugging work |
| architect | Opus / high | Design decisions, security-sensitive and judgment-heavy work |
| watcher | Sonnet / high | Independent read-only review |

Hard rules override the score: anything security-, payment- or data-destructive goes to
architect (design) or builder-plus (implementation) with mandatory review, and large-context work
never goes to Haiku. Details: [ROUTING.md](plugins/tierly/skills/tierly/reference/ROUTING.md).

## What Tierly will never do

- Run unless you type `/tierly`.
- Install hooks, change settings, permissions, environment variables, MCP servers or other
  plugins.
- Hide your MCP tools or skills from the work. Subagents can use them when a task needs them.
- Run web searches or shell commands to probe your machine. Shell or web actions happen only when
  your task needs them, and the plan lists each one.
- Keep routing your later messages after the run ends.

How each promise is enforced: [docs/NON-INTERFERENCE.md](docs/NON-INTERFERENCE.md).

## Cost

Savings depend on the task. Modeled ranges compared with running everything on Opus (not yet
measured; benchmark results will replace these):

| Task type | Expected cost |
|---|---|
| Read- and research-heavy | 50–75% lower |
| Mixed feature work | 25–40% lower |
| Judgment-heavy | 0–15% lower |

Tierly often uses *more* tokens in total while costing less, because most tokens move to cheaper
models. The report shows a relative cost index, not a bill. On a subscription, subagent usage
counts toward the same limits as your main conversation. See
[docs/SAVINGS-MODEL.md](docs/SAVINGS-MODEL.md).

## Requirements and compatibility

- Claude Code only. Tierly dispatches Claude Code subagents (`tierly:*`) with set models and effort
  levels. It does not run on claude.ai, the Skills API or other agent harnesses.
- A Claude plan or API access with Haiku, Sonnet and Opus.
- If a tier's model is unavailable, Tierly re-dispatches to the next tier up. If Sonnet is unavailable for the watcher, the watcher role falls back to architect in a review-only brief, and the report says "reduced verification".
- The skill loads only when you type `/tierly`. Between runs, only six short agent descriptions sit
  in context. Tierly adds no hooks, MCP servers or settings changes.

## Documentation

| Doc | Contents |
|---|---|
| [docs/MVP.md](docs/MVP.md) | v0.1 scope, acceptance criteria, milestones |
| [docs/BUILD-SPEC.md](docs/BUILD-SPEC.md) | Full specification |
| [docs/NON-INTERFERENCE.md](docs/NON-INTERFERENCE.md) | Guarantees and how they are enforced |
| [docs/SAVINGS-MODEL.md](docs/SAVINGS-MODEL.md) | How cost is modeled and measured |
| [docs/PRICING-SNAPSHOT.md](docs/PRICING-SNAPSHOT.md) | Prices and effort defaults used for routing |
| [docs/BRIDGES.md](docs/BRIDGES.md) | Planned opt-in support for other providers |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common problems |

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) first; routing changes need
benchmark evidence. Security issues: [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
