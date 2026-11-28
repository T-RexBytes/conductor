# Manual release checks

Work through these checks by hand in a real interactive Claude Code session before a release.
Use a scratch project for each check. Start Claude Code from the repository with
`claude --plugin-dir ./plugins/tierly`.

## V3: Approval keeps the Opus model override

**Proves:** Approving the plan through the AskUserQuestion card keeps the orchestrator on Opus
for the rest of that turn.

**Setup:** Use a scratch project and start `claude --plugin-dir ./plugins/tierly`.

**Steps:**

1. Type `/tierly update README.md with a short purpose note and add a matching note to
   CONTRIBUTING.md`.
2. When the plan appears, approve it using the AskUserQuestion card.
3. After the run finishes, open the session transcript (the newest `.jsonl` under
   `~/.claude/projects/<project>/`) and check the `message.model` field of the assistant
   messages that come after the approval answer.

**Look at:** The `message.model` fields on assistant messages after the approval answer in the
newest session transcript.

**Pass condition:** Those messages show an Opus model.

**Result:** ______________________________

## V4: Account cannot use Opus (optional)

**Proves:** The behavior is understood when the account cannot use Opus.

**Setup:** This check is optional. It is only possible with an account or setting that cannot use
Opus. Use a scratch project and start `claude --plugin-dir ./plugins/tierly`.

**Steps:**

1. Type `/tierly explain the purpose of the README in one sentence`.
2. Observe the result when Tierly attempts to use Opus.

**Look at:** Whether the run continues, reports an error, or follows the documented fallback.

**Pass condition:** Document the behavior; the skill's fallback already covers agents.

**Result:** ______________________________

## V1: Agent result exposes token usage

**Proves:** Whether the Agent tool result exposes token usage to the orchestrator.

**Setup:** Use a scratch project and start `claude --plugin-dir ./plugins/tierly`.

**Steps:**

1. Type `/tierly add a one-line comment to README.md explaining its purpose`.
2. Approve the plan if asked and wait for an agent dispatch.
3. Inspect the Agent tool result shown to the orchestrator.
4. Check the scratch project for files beyond those the task requested.

**Look at:** The Agent tool result for any token usage fields or figures, plus the scratch
project for stray files. Do not run probing commands for Tierly's own purposes.

**Pass condition:** Does the Agent tool result expose token usage to the orchestrator? No files
beyond those the task needs are created.

**Result:** ______________________________

## E7: User MCP tool remains available

**Proves:** A task that needs a configured user MCP server can name and use that tool.

**Setup:** Configure the MCP server in the scratch project or account before starting Claude Code.
Start `claude --plugin-dir ./plugins/tierly`.

**Steps:**

1. Replace `<tool name>` and `<specific lookup>` with a tool and operation provided by your MCP
   server.
2. Type `/tierly Use the MCP tool <tool name> to perform <specific lookup>, then summarize the
   result.`
3. Approve the plan if asked and let the run finish.

**Look at:** The brief for the name of the tool, and the agent's tool call and returned result.

**Pass condition:** Brief names the tool; agent uses it successfully.

**Result:** ______________________________

## E8: Normal chat after a Tierly run

**Proves:** Later turns after a Tierly run use the session's own model without subagent routing.

**Setup:** Use a scratch project and start `claude --plugin-dir ./plugins/tierly`.

**Steps:**

1. Type `/tierly explain in one sentence what README.md is for` and finish the run.
2. In the next turn, type `Now explain the same thing in simpler words.`
3. Check the model with `/model` or the status line. Observe whether any subagent is dispatched.

**Look at:** The model and tool activity on the later, ordinary chat turn.

**Pass condition:** Later turns use the session's own model; no subagent routing.

**Result:** ______________________________

## E10: Denied permission is respected

**Proves:** A denied permission blocks the task without an alternate route around the denial.

**Setup:** Use a disposable scratch project and start `claude --plugin-dir ./plugins/tierly`.
Choose an action that will cause Claude Code to show a permission prompt.

**Steps:**

1. Type `/tierly create a file named permission-check.txt containing the word ready`.
2. When Claude Code asks permission for the write, deny it.
3. Let the run report its outcome.

**Look at:** The task status and subsequent tool actions. Check that no alternate method attempts
that denied write.

**Pass condition:** Task marked blocked; no workaround attempted.

**Result:** ______________________________

## Remaining manual non-interference checks

### N7: No settings changes

**Proves:** Tierly does not change settings, permissions, environment variables, or other plugins.

**Setup:** Use a scratch project and start `claude --plugin-dir ./plugins/tierly`.

**Steps:**

1. Type `/tierly summarize the purpose of README.md` and complete the run.
2. Review the run's tool activity for changes to settings, permissions, environment variables, or
   other plugins.

**Look at:** The tool activity and relevant scratch-project state.

**Pass condition:** No settings, permissions, environment variables, or other plugins are changed.

**Result:** ______________________________

## Recording results

Copy the V1, V3, and V4 results into BUILD-SPEC.md section 13. Copy the E7, E8, and E10 results
into the release PR.
