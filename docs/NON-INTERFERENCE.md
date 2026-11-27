# Non-interference guarantees

Installing Allot must not change how Claude Code behaves for anything except `/allot:run`. This
page lists each guarantee, how it is built, and how it is checked. The IDs match
[BUILD-SPEC.md](BUILD-SPEC.md) section 6.

## Guarantees

| ID | Guarantee | Mechanism | Enforced by |
|---|---|---|---|
| N1 | Allot runs only when you type `/allot:run` | `disable-model-invocation: true` on the skill, so Claude cannot load it on its own and its description is not in context | CI |
| N2 | No hooks | The plugin ships no `hooks/hooks.json`, no `hooks` manifest key, and no `hooks` in skill or agent frontmatter | CI |
| N3 | No session-wide side effects | No plugin `settings.json`, monitors, MCP servers, LSP servers or `bin/` executables | CI |
| N4 | Allot's agents are not used for your normal work | Each agent description begins "Internal to the allot plugin. Do not select this agent unless dispatched by /allot:run" | CI |
| N5 | Your MCP tools and skills stay available | Agents restrict tools with `disallowedTools` only (never a `tools` allowlist); the skill has no `disallowed-tools` | CI |
| N6 | No probing | Allot never runs web, network or shell actions for its own purposes. Reconnaissance is Read/Glob/Grep inside the project. Task-required shell or web actions are listed in the plan with a reason | CI (rule present) + release check |
| N7 | Your configuration is never touched | No edits to settings, permissions, env vars, MCP config, hooks, other plugins or skills | CI (rule present) + release check |
| N8 | The model override ends with the run | The skill's `model: opus` applies to the turn that invokes it only | Release check |
| N9 | No stray files | Plan and report live in the conversation; only task files are written | Release check |
| N10 | Bounded cost | Agents cannot spawn agents (`Agent` is denied) | CI |
| N11 | Permission prompts are respected | No `permissionMode`; denied actions are not retried another way | CI + release check |

## Why there are no hooks at all

Plugin hooks register when the plugin loads and fire on their events for every session, whether
or not a plugin skill is used. Hooks declared in a skill's frontmatter register when the skill is
invoked and stay registered for the rest of the session. Either kind would affect your work
outside Allot, so Allot uses neither. The cost of this choice: the report shows an estimated cost
index instead of measured usage (see BUILD-SPEC item V1).

## What Allot does use

- One skill (`/allot:run`) and six subagents, all inside the plugin.
- Standard tools in your session, under your existing permission rules.
- AskUserQuestion to approve the plan, when available.

## Reporting a violation

If Allot affects anything outside an `/allot:run` invocation, that is a release-blocking bug.
Open an issue with the "Bug report" template and include what you ran and what changed.
