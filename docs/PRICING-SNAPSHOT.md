# Pricing and effort snapshot

| | |
|---|---|
| Snapshot date | 2026-11-27 |
| Used for | `cost_index` in `tiers.json`, the savings model, and effort choices |
| Refresh | On every model release or price change (routing review) |

Prices change. Routing does not depend on exact prices, only on their rough ratios. Always check
the official pricing page for current numbers.

## API list prices (USD per million tokens)

| Model | Input | Output | Cache read | 5-minute cache write | Notes |
|---|---|---|---|---|---|
| Claude Opus 5.5 | 4.00 | 20.00 | 0.20 | 5.00 | |
| Claude Sonnet 5.5 | 2.00 | 10.00 | 0.10 | 2.50 | Cache read halved from 0.20 when Haiku 5.5 shipped |
| Claude Haiku 5.5 | 0.10 | 0.50 | 0.1x input | not confirmed | Prompts up to 100k tokens; above that 0.50 input / 2.50 output |

Ratios used as `cost_index`: Haiku 1, Sonnet 20, Opus 40 (same ratio for input and output at
prompts up to 100k tokens).

Fable-tier models cost well above Opus and are not used by Conductor.

## Effort defaults and guidance (per Anthropic's effort documentation)

| Model | Default effort | Guidance used by Conductor |
|---|---|---|
| Opus 5.5 | medium | Set explicitly; Conductor uses `high` for architect and watcher |
| Sonnet 5.5 | high (API) | `medium` for well-specified agentic coding, `high` for harder or longer tasks |
| Haiku 5.5 | medium | `medium` for most work including agentic coding; `low` for short tool tasks only |

All three support `low`, `medium`, `high`, `xhigh` and `max`. Conductor uses only `low`, `medium`
and `high` in v0.1.

## Sources

- Anthropic pricing: <https://platform.claude.com/docs/en/about-claude/pricing>
- Effort: <https://platform.claude.com/docs/en/build-with-claude/effort>
- Opus 5.5 launch pricing coverage: The New Stack, Finout (September–October 2026)
- Sonnet 5.5 pricing: Apidog pricing summary (October 2026)
- Haiku 5.5 pricing and Sonnet cache-read change: TechEnclave, Tech Insider (October 2026)
