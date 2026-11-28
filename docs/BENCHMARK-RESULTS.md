# Benchmark results

## Pilot

The pilot ran tasks T03 (architecture document, read-heavy) and T06 (pagination bug fix, mixed).
There was one run per task and configuration on 2026-11-28/29 with Claude Code 2.1.332 and
`--auth subscription`. Costs are the CLI's list-price estimates in USD.

| Configuration | T03 | T06 | Total | Pass rate |
|---|---:|---:|---:|---:|
| Baseline: plain Opus, medium effort | 0.26 | 0.11 | 0.37 | 2/2 |
| Tierly v0.1 draft (Opus orchestrator high, Opus watcher) | 0.41 | 0.57 | 0.98 | 2/2 |
| Orchestrator at medium effort | 0.34 | 0.50 | 0.84 | 2/2 |
| Current: watcher on Sonnet high, compact routing card | 0.42 | 0.19 | 0.60 | 2/2 |
| Rejected: orchestrator on Sonnet high | 0.59 | 0.33 | 0.92 | 2/2 |

Baseline runs varied between 0.36 and 0.41 across runs. The Sonnet-orchestrator experiment was
rejected because it cost more and failed behavioral eval E10.

## Method

The harness command was:

```bash
python benchmarks/run_benchmark.py --tasks T03,T06 --auth subscription --max-cost-usd 3
```

The pilot used one run per task and configuration. Subscription mode reports CLI list-price
estimates, not subscription charges. A task passes when its benchmark check script returns pass.
The pass rate counts the task checks; it does not measure statistical quality across repeated
runs.

## Reading the result

On these small and mid-size tasks, current Tierly costs about 1.6 times plain Opus at the same
pass rate. The cheap tiers' own work is a small part of the cost. Most of the cost is
orchestration overhead on Opus. Savings are expected only where delegated work is large compared
with planning; that case has not been measured. One run per task is a pilot, not a statistically
solid result.

Behavioral evals on the current configuration: E1, E2, E3, E5, E9 and E10 pass. E4 and E6 passed
as headless runs. E7, E8, V1, V3 and V4 are manual checks documented in
[MANUAL-CHECKS.md](MANUAL-CHECKS.md). Earlier runs printed E3's plan line in about 2 of 3 runs.
