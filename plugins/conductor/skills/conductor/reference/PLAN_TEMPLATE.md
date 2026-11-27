# Plan template

Show the plan in this shape. Keep each cell short.

```text
Conductor plan: <one-line goal>
Profile: <balanced>   Parallel: <4>   Mode: <full orchestration | direct dispatch>
Done means: <the user's definition of done, one line>

| ID | Micro-task | C A R B | Score | Agent             | Model / effort | After | Owns (paths) | Extra actions | Watcher |
|----|------------|---------|-------|-------------------|----------------|-------|--------------|---------------|---------|
| T1 | ...        | 0 0 0 1 | 1     | conductor:scout   | haiku / low    | -     | (read-only)  | -             | no  |
| T2 | ...        | 2 1 2 1 | 6     | conductor:builder | sonnet / medium| T1    | src/api/orders.ts | Bash: npm test (user asked for passing tests) | yes |

Extra actions: shell, web, or MCP actions a task needs, each with the reason. "-" means none.

Relative cost index: <sum of task indexes + watcher indexes> (all-Opus equivalent: <N x 40 + watcher>)
This is an estimate from list-price ratios, not a bill.

Questions before starting: <none | the question>
```

Then ask: approve / approve on budget profile / edit / cancel.
