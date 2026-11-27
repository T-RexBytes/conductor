# CLAUDE.md

Instructions for Claude Code (and humans) working **on** this repository. This file is not part
of the plugin: Claude Code does not load a CLAUDE.md from a plugin root.

## What this repo is

Allot is a Claude Code plugin. `/allot:run` plans a task, routes each micro-task to the cheapest
Claude tier that can do it well (Haiku, Sonnet, Opus subagents at set effort levels), checks the
work with a read-only watcher, and reports. The spec is `docs/BUILD-SPEC.md`; the MVP scope is
`docs/MVP.md`. Read the relevant section before changing behavior.

## Layout

| Path | What |
|---|---|
| `.claude-plugin/marketplace.json` | Marketplace manifest (repo root is the marketplace) |
| `plugins/allot/.claude-plugin/plugin.json` | Plugin manifest; `version` is the release version |
| `plugins/allot/skills/run/SKILL.md` | The orchestrator procedure (keep under 500 lines) |
| `plugins/allot/skills/run/reference/tiers.json` | **Single source of truth** for tiers, models, effort, bands |
| `plugins/allot/skills/run/reference/*.md` | Rubric, templates, watcher rubric |
| `plugins/allot/agents/*.md` | The six agents |
| `scripts/validate_repo.py` | Static checks run in CI |
| `tests/` | pytest suite |
| `benchmarks/` | Cost and quality harness, tasks, fixtures |

## Commands

```bash
python -m pip install -r requirements-dev.txt   # once
python scripts/validate_repo.py                 # must pass before every commit
python -m pytest -q                             # must pass before every commit
claude plugin validate . && claude plugin validate ./plugins/allot
claude --plugin-dir ./plugins/allot             # try the plugin locally
python benchmarks/run_benchmark.py --dry-run    # show benchmark commands without running them
```

## Invariants (never break these)

1. **Non-interference (BUILD-SPEC section 6).** No hooks anywhere (plugin `hooks/`, `plugin.json`,
   skill or agent frontmatter). No `settings.json`, `monitors/`, `.mcp.json`, `.lsp.json` or
   `bin/` in the plugin. The skill keeps `disable-model-invocation: true`. Agent descriptions
   start with `Internal to the allot plugin`. Agents use `disallowedTools`, never `tools`
   allowlists. No `permissionMode`.
2. **No probing.** Neither the skill nor any agent may tell Claude to run web, network or shell
   actions for Allot's own purposes. Such actions happen only when the user's task needs them and
   the plan lists them.
3. **`tiers.json` is authoritative.** Changing a tier's model or effort means changing
   `tiers.json`, the matching agent frontmatter, `ROUTING.md`, `BUILD-SPEC.md` section 5.4, and
   the README table in the same PR. The validator checks agents against `tiers.json`.
4. **Only documented frontmatter keys.** Claude Code silently ignores unknown keys, so a typo
   fails silently. The validator holds the allowlist; update it only with a docs link in the PR.
5. **Honest cost claims.** Anything shown to users as a cost figure is either labeled an estimate
   or comes from the benchmark suite.
6. **Agents never spawn agents.** `Agent` stays in every agent's `disallowedTools`.

## Style

- Plain, direct English. Short sentences. No marketing language in docs or prompts.
- Prompts (SKILL.md, agents) give reasons for rules; they read as instructions to a capable
  colleague, not shouted commands.
- Markdown: one H1 per file, tables for comparisons, fenced code blocks with a language.
- Python: standard library plus PyYAML only for `scripts/`; type hints; no network access.

## When changing routing

Routing changes need evidence. Run the benchmark suite before and after, and put both result
tables in the PR. Quality (pass rate) must not drop. See `CONTRIBUTING.md`.

## When Anthropic ships a new model or changes effort guidance

Open a "routing review" issue. Re-read the effort documentation, update `tiers.json`, the agents
and `docs/PRICING-SNAPSHOT.md` (with the new date), re-run benchmarks, then release.
