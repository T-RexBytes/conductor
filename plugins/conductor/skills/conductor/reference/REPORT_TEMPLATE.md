# Report template

```text
Conductor report: <one-line outcome>

Result: <done | partially done | stopped>, <one or two sentences on what the user now has>

| ID | Micro-task | Agent             | Model / effort | Status | Watcher | Escalations |
|----|------------|-------------------|----------------|--------|---------|-------------|
| T1 | ...        | conductor:scout   | haiku / low     | done | -    | 0 |
| T2 | ...        | conductor:builder | sonnet / medium | done | pass | 1 (from worker) |

Files changed:
- <path> — <what changed>

Open findings and follow-ups:
- <minor findings, blocked tasks, questions for the user>

Routing mix: scout <n>, worker <n>, builder <n>, builder-plus <n>, architect <n>, watcher calls <n>
Relative cost index: <run total> vs <all-Opus equivalent>. Estimate from list-price ratios;
check your Claude usage view for actual spend.
<"Reduced verification" line, only if the watcher fell back to builder-plus.>
```
