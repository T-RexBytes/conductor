# Tierly

<p align="center"><img src="docs/assets/tierly-logo.png" alt="Tierly" width="420"></p>

Tierly is a Claude Code plugin that plans larger tasks, routes work to suitable Claude tiers,
checks non-trivial changes with a watcher, and reports what ran. It runs only when you invoke it.

[![CI](https://github.com/T-RexBytes/tierly/actions/workflows/ci.yml/badge.svg)](https://github.com/T-RexBytes/tierly/actions/workflows/ci.yml)

## How it works

Tierly sends a small request directly to an agent. For larger requests, it creates a plan, waits
for approval unless `--yes` is set, dispatches independent work, reviews non-trivial changes, and
reports the outcome. You can edit or cancel the plan.

## Install

In Claude Code, run:

```text
/plugin marketplace add T-RexBytes/tierly
/plugin install tierly@tierly
```

Then invoke `/tierly`. If that command name is taken, use `/tierly:tierly`.

## Usage

```text
/tierly [flags] <task>
```

| Flag | Effect | Default |
|---|---|---|
| `--plan-only` | Show the plan and stop without dispatching | off |
| `--yes` | Skip plan approval; the plan is still shown | off |
| `--no-recon` | Plan from your text without reading project files first | off |
| `--profile` | Select `budget`, `balanced`, or `quality` routing | `balanced` |
| `--parallel N` | Set concurrent subagents, from 1 to 8 | 4 |

## Routing

| Tier | Model / effort | Typical work |
|---|---|---|
| scout | Haiku / low | Read-only lookups |
| worker | Haiku / medium | Mechanical edits from a clear specification |
| builder | Sonnet / medium | Well-specified features and bug fixes |
| builder-plus | Sonnet / high | Harder implementation and debugging |
| architect | Opus / high | Design and judgment-heavy work |
| watcher | Sonnet / high | Independent read-only review |
| orchestrator | Opus / medium | Planning and integration |

## Cost, measured so far

In a two-task pilot, current Tierly cost 0.60 USD versus 0.37 USD for plain Opus, with both
passing both tasks. That is about 1.6 times the baseline; the pilot had one run per task and is
not statistically solid. See [the benchmark results](docs/BENCHMARK-RESULTS.md) for method and
limits.

## Requirements and compatibility

- Claude Code only. Tierly dispatches Claude Code subagents (`tierly:*`) with set models and
  effort levels. It does not run on claude.ai, the Skills API, or other agent harnesses.
- A Claude plan or API access with Haiku, Sonnet, and Opus.
- If a tier's model is unavailable, Tierly re-dispatches to the next tier up. If Sonnet is
  unavailable for the watcher, the watcher role falls back to architect in a review-only brief,
  and the report says "reduced verification".

## Non-interference

Tierly runs only when invoked. It adds no hooks, settings changes, or MCP servers, and does not
probe your machine. See [the guarantees](docs/NON-INTERFERENCE.md).

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and contribution guidance.

## License

MIT. Copyright Sourish Panda. See [LICENSE](LICENSE).
