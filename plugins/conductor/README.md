# Conductor plugin

Cost-aware, plan-first orchestration for Claude Code. Type `/conductor <task>` and Conductor splits
the task into micro-tasks, scores how much attention each one needs, and routes each to the
cheapest Claude model and effort level that can do it well: Haiku for lookups and mechanical
edits, Sonnet for implementation, Opus for design and review. A read-only Opus watcher checks
every non-trivial change, and failed work is redone one tier up.

Conductor runs only when you type `/conductor`. It ships no hooks, settings, MCP servers or
executables, and never changes your configuration.

Usage:

```text
/conductor [--plan-only] [--yes] [--no-recon] [--profile budget|balanced|quality] [--parallel N] <task>
```

Full documentation: <https://github.com/T-RexBytes/conductor>
