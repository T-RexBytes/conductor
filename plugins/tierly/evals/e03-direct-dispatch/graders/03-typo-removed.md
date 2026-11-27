---
type: regex
pattern: 'retrun'
match: not_contains
target: {source: file, path: calc.py}
weight: 1
---

The original typo is absent from calc.py.
