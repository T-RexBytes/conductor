---
tags: [orchestration]
runs: 1
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Agent, Read, Glob, Grep, Write, Edit, TaskCreate, TaskUpdate, Bash(python -m pytest*)]
---

/conductor --yes make every test in tests/ pass without editing any file under tests/. Check with: python -m pytest -q
