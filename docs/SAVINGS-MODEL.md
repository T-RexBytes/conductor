# Savings model

How Tierly's cost compares with running everything on one model, how it is estimated during a
run, and how it is measured.

## Where cost goes up and down

| Effect | Direction | Size |
|---|---|---|
| Routine tokens move from Opus to Haiku or Sonnet | down | Largest. Haiku is 1/40 and Sonnet 1/2 of Opus per token |
| Each subagent starts with a small, fresh context instead of the whole session history | down | Grows with session length |
| Lower effort on routine tasks | down | Moderate |
| Planning and integration on Opus | up | Fixed per run |
| Watcher reviews | up | Proportional to reviewed tasks; batching reduces it |
| Escalations (redoing work one tier up) | up | Proportional to watcher fail rate |
| Cold starts: subagents re-read files the main session already read | up | Briefs pass paths and findings to limit it |

Tierly often uses more tokens in total while costing less. The goal is lower cost at equal
quality, not fewer tokens.

## Illustrative model (not a measurement)

A medium feature, priced at list prices from [PRICING-SNAPSHOT.md](PRICING-SNAPSHOT.md). Haiku's
cache-write price is assumed to be 1.25x its input price.

### Baseline: one Opus 5.5 session

| Tokens | Count | Price / M | Cost |
|---|---|---|---|
| Uncached input | 150,000 | $4.00 | $0.60 |
| Cache writes | 200,000 | $5.00 | $1.00 |
| Cache reads | 3,000,000 | $0.20 | $0.60 |
| Output | 80,000 | $20.00 | $1.60 |
| **Total** | 3,430,000 | | **$3.80** |

### Tierly run

| Role | Model | Uncached in | Cache write | Cache read | Output | Cost |
|---|---|---|---|---|---|---|
| Orchestrator | Opus | 30k | 40k | 400k | 15k | $0.70 |
| 4 scouts | Haiku | 200k | 100k | 1,000k | 20k | $0.05 |
| Builders | Sonnet | 100k | 150k | 1,500k | 50k | $1.23 |
| Watcher | Opus | 60k | 0 | 100k | 10k | $0.46 |
| **Total** | | | | | 3,775k tokens | **$2.44** |

Result: about **36% lower cost** with about **10% more tokens**. All token counts are assumptions
chosen to be plausible; real runs vary widely.

## Expected ranges by task type

| Task type | Expected cost vs all-Opus | Why |
|---|---|---|
| Read- and research-heavy (audits, codebase Q&A, migrations planning) | 50–75% lower | Most tokens go to Haiku scouts |
| Mixed feature work | 25–40% lower | Implementation on Sonnet, judgment on Opus |
| Judgment-heavy (architecture, hard debugging) | 0–15% lower | Most work stays on Opus by design |
| Tiny tasks | Same or lower via the triage gate | Without the gate: 10–30% higher |

These are modeled ranges. They become claims only when the benchmark suite reproduces them.

## In-run estimate: the cost index

During a run Tierly cannot see token counts (BUILD-SPEC item V1), so the plan and report show a
**relative cost index**: the sum of `cost_index` (Haiku 1, Sonnet 20, Opus 40) for every
dispatch, next to the index if every dispatch ran on Opus. It ranks plans; it is not a bill.

## Measured cost: the benchmark suite

`benchmarks/run_benchmark.py` runs each task twice from a clean fixture, baseline and Tierly,
with `claude -p --output-format json`, which reports `total_cost_usd` and a per-model breakdown.
Those figures are client-side estimates and can differ slightly from the bill. Each run's check
script decides pass or fail. Routing changes are accepted only when pass rate holds and cost does
not rise.

## Subscriptions

On Pro and Max plans, subagent requests count toward the same usage limits as the main
conversation. Moving work to cheaper models is expected to slow how fast limits are used, but
Anthropic does not publish an exact per-model weighting, so Tierly makes no numeric claim for
subscriptions.
