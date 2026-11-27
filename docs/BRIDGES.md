# Bridges (planned for v0.3): opt-in workers from other providers

Status: **design only. Not in v0.1.** Allot is Claude-first. Bridges lets a user who also has
another AI subscription (for example OpenAI Codex) have some micro-tasks run there, with the same
routing discipline and the same Claude watcher.

## Principles

1. **Off unless asked.** Bridges activates only when the user names a provider in the run
   (`--with codex`, or "use my Codex too" in the task). Never on its own.
2. **Official tools only.** Work goes through the provider's official CLI or plugin that the user
   has installed and logged into. Allot never reads, copies or reuses credentials.
3. **No probing.** Allot does not run commands to discover installed CLIs or model catalogs. The
   model table is a versioned registry in the repo. The first bridged dispatch is the check: if
   it fails, Allot reports the error and continues on Claude tiers.
4. **Same quality bar.** Bridged work gets the same brief, the same `ALLOT-REPORT` contract, the
   same Claude watcher and the same escalation ladder. Escalation can move a task back to Claude.
5. **Sandboxed.** Read-only tasks run read-only; write tasks get workspace-write access to their
   owned paths only. Never full access.
6. **Separate accounting.** Bridged usage counts against the other provider's limits and is shown
   in its own column of the report.

## Codex registry (draft, to be re-checked at implementation time)

Codex model names and effort scales change often, which is why they live in a registry file
(`bridges/providers/codex.toml`) rather than in prompts.

| Allot tier | Codex model | Reasoning effort | Rationale |
|---|---|---|---|
| scout | gpt-6-luna | low | Fast, affordable; `minimal` is rejected on this model |
| worker | gpt-6-luna | medium | Focused, high-volume coding and transformation |
| builder | gpt-6.1-sol | medium | Complex coding when cost matters |
| builder-plus | gpt-6.1-sol | high | Harder multi-step work |
| architect | gpt-6-astra | high | Hardest end-to-end work; higher levels only when justified |

Effort levels differ by model (`minimal` to `xhigh`, with `max` or `ultra` on some). The registry
records each model's supported levels; Allot maps its five-level scale to the nearest supported
value and, on a rejection, retries once at the nearest lower level.

## Integration options

| Option | Notes |
|---|---|
| OpenAI's Codex plugin for Claude Code (`openai/codex-plugin-cc`) | Preferred when installed: provides task delegation and reviews through a subagent |
| `codex exec` non-interactive mode | Fallback; `--sandbox read-only` or `workspace-write`, `-c model_reasoning_effort=...` |

## Open questions

- How to pass owned-path restrictions to the other agent reliably (sandbox scope vs. prompt).
- Whether to allow bridged tasks to run in parallel with Claude tasks on disjoint paths in v0.3,
  or serialize them.
- Gemini: Gemini CLI headless mode (`-p`, `--output-format json`) works similarly, but some
  account types are moving to a different CLI; support waits until that settles.
