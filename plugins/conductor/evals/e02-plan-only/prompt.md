---
tags: [smoke]
runs: 1
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Agent, Read, Glob, Grep, Write, Edit, TaskCreate, TaskUpdate]
---

/conductor --plan-only add multiply(a, b) and power(a, b) to calc.py with tests for both in tests/test_calc.py
