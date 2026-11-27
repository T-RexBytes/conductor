# Allot plugin

Cost-aware, plan-first orchestration for Claude Code. Type `/allot:run <task>` and Allot splits
the task into micro-tasks, scores how much attention each one needs, and routes each to the
cheapest Claude model and effort level that can do it well: Haiku for lookups and mechanical
edits, Sonnet for implementation, Opus for design and review. A read-only Opus watcher checks
every non-trivial change, and failed work is redone one tier up.

Allot runs only when you type `/allot:run`. It ships no hooks, settings, MCP servers or
executables, and never changes your configuration.

Usage:

```text
/allot:run [--plan-only] [--yes] [--no-recon] [--profile budget|balanced|quality] [--parallel N] <task>
```

Full documentation: <https://github.com/Dronzer2code/allot>
