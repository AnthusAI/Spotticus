# Related leftover tools

These are not Spotticus. Spotticus wraps leftover probes and **dispatches**.
The healthy communities watch. They do not dispatch.

Landscape dump (inventory, collisions, satellites):
[research/leftover-tool-landscape.md](research/leftover-tool-landscape.md).

## Two jobs, two communities

Do not collapse leftover and spend. Do not treat 0–1 star glue as the hub.

| Job | Follow | What it reports |
| --- | --- | --- |
| **Live leftover** | **[CodexBar](https://github.com/steipete/CodexBar)** first (~21k stars, commits today, `codexbar usage --json`). Next: **[OpenUsage.ai](https://www.openusage.ai)** ([robinebers/openusage](https://github.com/robinebers/openusage), ~4k, macOS menu bar, `127.0.0.1:6736/v1/limits`). Then **[tokscale](https://github.com/junhoyeo/tokscale)** (~5k, `tokscale usage --json`). | Remaining %, reset, which window. Vendor URLs rot; these communities chase them. |
| **Historical spend** | **[ccusage](https://github.com/ccusage/ccusage)** / [ccusage.com](https://ccusage.com) (~18k stars). Continuum guide exists. | What you already burned, from local JSONL. **Not remaining-%.** |

Skip **[Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor)** (stars, last push July 2026, stalled). Skip **[aiuse](https://github.com/djbclark/aiuse)** as “the community.”

## Glue that must stay in the catalog

Real tools. One or two people. They will not keep up when Cursor changes billing.

| What | URL | Role |
| --- | --- | --- |
| **aiquota** (Go CLI) | https://github.com/kohii/aiquota | Claude / Codex / Cursor / Copilot leftover from local creds. `--json`. No cookie decrypt. `--proj` is spare-pace. |
| **AIQuota** (macOS app) | https://aiquota.app | Menu-bar gauges for Codex and Claude. **Different product** from kohii/aiquota. Source: [niederme/ai-quota](https://github.com/niederme/ai-quota). |
| **aiuse** | https://github.com/djbclark/aiuse | Aggregator. Shells out to CodexBar, caut, cswap, tokscale, OpenUsage. Collector map is useful. Not a hub. |

OpenUsage.sh ([janekbaraniewski/openusage](https://github.com/janekbaraniewski/openusage), ~180 stars) is **not** OpenUsage.ai.

## How Spotticus should treat them

- Wrap **CodexBar leftover** (`codexbar usage --format json`) as the default live probe, with OpenUsage.ai / tokscale `usage` as next communities.
- Use **ccusage** only if we need a bill / local-cost number. Never for spare-pace dispatch.
- Portable fallback: [cclimits](https://github.com/cruzanstx/cclimits). Unofficial Cursor also exists in CodexBar and aiquota.
- Do not invent `api2.cursor.sh` scraping.
