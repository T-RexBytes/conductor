---
tags: [orchestration]
runs: 1
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Agent, Read, Glob, Grep, Write, Edit, TaskCreate, TaskUpdate]
---

/tierly --yes run python -m pytest -q and fix whatever fails
