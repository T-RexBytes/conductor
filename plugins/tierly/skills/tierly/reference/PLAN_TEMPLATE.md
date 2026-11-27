# Plan template

Show the plan in this shape. Keep each cell short.

```text
Tierly plan: <one-line goal>
Profile: <balanced>   Parallel: <4>   Mode: <full orchestration | direct dispatch>
Done means: <the user's definition of done, one line>

| ID | Micro-task | C A R B | Score | Agent             | Model / effort | After | Owns (paths) | Extra actions | Watcher |
|----|------------|---------|-------|-------------------|----------------|-------|--------------|---------------|---------|
| T1 | ...        | 0 0 0 1 | 1     | tierly:scout      | haiku / low    | -     | (read-only)  | -             | no  |
| T2 | ...        | 2 1 2 1 | 6     | tierly:builder    | sonnet / medium| T1    | src/api/orders.ts | Bash: npm test (user asked for passing tests) | yes |

Extra actions: shell, web, or MCP actions a task needs, each with the reason. "-" means none.

Relative cost index (dispatched work only, estimate): <sum of task indexes + watcher indexes>
All-Opus equivalent: <N x 40 + watcher>
The estimate uses list-price ratios and excludes the orchestrator's own planning, routing and
review, which run on Opus in the main session.

Questions before starting: <none | the question>
```

Then ask: approve / approve on budget profile / edit / cancel.
