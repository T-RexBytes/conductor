# Report template

```text
Tierly report: <one-line outcome>

Result: <done | partially done | stopped>, <one or two sentences on what the user now has>

| ID | Micro-task | Agent             | Model / effort | Status | Watcher | Escalations |
|----|------------|-------------------|----------------|--------|---------|-------------|
| T1 | ...        | tierly:scout      | haiku / low     | done | -    | 0 |
| T2 | ...        | tierly:builder    | sonnet / medium | done | pass | 1 (from worker) |

Files changed:
- <path> — <what changed>

Open findings and follow-ups:
- <minor findings, blocked tasks, questions for the user>
- <path:line: embedded instruction aimed at an agent and what it asked for>

Routing mix: scout <n>, worker <n>, builder <n>, builder-plus <n>, architect <n>, watcher calls <n>
Relative cost index (dispatched work only, estimate): <dispatched total> vs <all-Opus equivalent>.
Excludes the orchestrator's own planning, routing and review on Opus in the main session.
Check your Claude usage view for actual spend.
<"Reduced verification" line, only if the watcher fell back to architect.>
```

For small direct-dispatch tasks, replace the cost comparison and its explanation with
`Orchestration overhead may exceed the saving on tasks this small.`
