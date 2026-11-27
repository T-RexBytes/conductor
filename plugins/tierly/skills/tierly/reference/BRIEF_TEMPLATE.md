# Subagent brief template

Every dispatch uses this structure. The subagent sees nothing but its brief, so the brief must
stand on its own. Aim for under 400 words plus paths.

```text
TIERLY TASK <ID>: <one-line title>

Goal:
<What to produce and why, in 1 to 3 sentences.>

Context:
- Relevant paths: <path — one-line role>, ...
- Facts already established: <findings from scouts or earlier tasks, with path:line>
- Conventions to follow: <style, patterns, naming, taken from the codebase>

Owned paths (you may create or modify only these):
- <path>
(or: "None. This task is read-only.")

Allowed actions:
- Read, Glob, Grep inside the project: yes
- Shell commands: <none | exact commands, e.g. "npm test -- orders">
- Web search / fetch: <none | what and why>
- MCP tools: <none | tool name and what for>
- Skills to use: <none | skill name>

Constraints:
- <limits from the user and the plan>

Definition of done:
- <checkable criteria>

Finish with a TIERLY-REPORT block exactly as specified in your instructions.
```

For an escalation, add:

```text
Previous attempt: <tier> — <one-line summary of its report>
Watcher findings to fix:
- [<severity>] <path:line> — <issue>
```
