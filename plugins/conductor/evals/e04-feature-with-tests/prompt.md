---
tags: [orchestration]
runs: 1
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Agent, Read, Glob, Grep, Write, Edit, TaskCreate, TaskUpdate, Bash(python -m pytest*)]
---

/conductor --yes --profile quality add a stats.py module with mean, median and mode functions (raise ValueError on empty input), add tests in tests/test_stats.py, and document them in README.md. All tests must pass with: python -m pytest -q
