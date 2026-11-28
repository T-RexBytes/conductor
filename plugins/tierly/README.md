# Tierly plugin

Cost-aware, plan-first orchestration for Claude Code. Type `/tierly <task>` and Tierly splits
the task into micro-tasks, scores how much attention each one needs, and routes each to the
cheapest Claude model and effort level that can do it well: Haiku for lookups and mechanical
edits, Sonnet for implementation, Opus for design, and a read-only Sonnet watcher checks
every non-trivial change, and failed work is redone one tier up.

Tierly runs only when you type `/tierly`. It ships no hooks, settings, MCP servers or
executables, and never changes your configuration.

Usage:

```text
/tierly [--plan-only] [--yes] [--no-recon] [--profile budget|balanced|quality] [--parallel N] <task>
```

Full documentation: <https://github.com/T-RexBytes/tierly>
