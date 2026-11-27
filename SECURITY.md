# Security policy

## Supported versions

| Version | Supported |
|---|---|
| Latest release | Yes |
| Older releases | No; please upgrade |

## Reporting a vulnerability

Please do not open a public issue. Use GitHub's private vulnerability reporting on this
repository ("Security" tab → "Report a vulnerability"). Include steps to reproduce, the Tierly
version, and the impact.

You can expect an acknowledgement within 7 days and a status update within 14 days.

## In scope

- Prompt injection that makes a Tierly agent act on instructions found in files, tool output or
  web content.
- Any way Tierly widens permissions, bypasses permission prompts, or changes user configuration.
- Agents writing outside their owned paths, or the watcher missing a destructive change because
  of how Tierly builds briefs.
- Tierly affecting sessions or work outside a `/tierly` invocation.

## Out of scope

- Vulnerabilities in Claude Code, Claude models or other plugins (report those to their owners).
- Cost overruns without a security impact (open a normal issue).
