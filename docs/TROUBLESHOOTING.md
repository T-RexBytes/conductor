# Troubleshooting

## `/tierly` does not appear in the `/` menu

- If `/tierly` is taken by another command, type `/tierly:tierly`.
- Run `/plugin` and check that `tierly@tierly` is installed and enabled.
- Run `/reload-plugins` or start a new session.
- If you installed from a local clone, run `claude plugin validate ./plugins/tierly` and fix any
  error it reports.

## Claude never uses Tierly unless I type the command

That is intended (guarantee N1). Tierly is invoked only by `/tierly`.

## Every subagent seems to run on the same model

Check whether `CLAUDE_CODE_SUBAGENT_MODEL` and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` are set in your
environment or settings. With the force variable on, Claude Code ignores agent `model` fields,
so Tierly's routing cannot take effect. Tierly does not change this for you; unset it yourself
if you want routing.

## The report says "reduced verification"

Your account could not run the Opus watcher, so reviews ran on Sonnet at high effort. Results are
still reviewed, but less strictly.

## Approval asked in plain text instead of a question card

AskUserQuestion was not available in your session. Reply "approve" or describe your edits. If
you want the approval to stay inside the same turn, run `--plan-only` first, then rerun with
`--yes` once you are happy with the plan.

## A task stopped with "blocked"

The agent needed something its brief did not give it (a decision, a file, a permission). The
report lists what. Answer it, then rerun the remaining work.

## A permission prompt appeared during a run

Tierly works under your normal permission rules and never bypasses them. Approve or deny as
usual. A denied action marks that task as blocked; Tierly does not try another way around it.

## Costs look higher than expected

- Very small tasks should take the direct path. If they did not, report it with the plan output.
- `--profile quality` reviews every write task and routes higher; use `balanced` or `budget`.
- The cost index is an estimate. Check your Claude usage view for actual spend.
