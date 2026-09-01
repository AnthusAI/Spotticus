# Leftover probes

Spotticus maintains a **curated** set of ways to read current included-quota leftover for products Anthus uses. The catalog is the product. The probes are not.

Vendors do not ship a personal leftover SDK. Community tools reuse local CLI credentials and undocumented usage URLs. Those URLs rot. We pin a working method per product, re-verify it, and fail closed when it stops working.

## What we measure

Server-side leftover, not local JSONL spend:

- percent used / remaining on each window
- reset time
- which window (session 5h, weekly, monthly pool)

`codexbar cost` / `ccusage` / tokscale log scans are a different number
(historical spend). Do not mix them into dispatch.

## Anthus cares about (first catalog)

| Product | Windows | Official leftover CLI? | Working method we saw (2026-09-01) | Notes |
| --- | --- | --- | --- | --- |
| Claude Code | session (5h), weekly | No JSON. `claude /usage` is human text | `codexbar usage --provider claude --source cli --format json` (this Mac). Portable candidate: `cclimits --json` via `~/.claude/.credentials.json` → `api.anthropic.com/api/oauth/usage` | Keychain prompting on macOS; prefer file creds on Linux |
| Codex | 5h, weekly | `codex app-server` `account/rateLimits/read` | `codexbar usage --provider codex --format json`. Portable: `cclimits` / `aiquota` via `~/.codex/auth.json` → `chatgpt.com/backend-api/wham/usage` | |
| Antigravity | Gemini vs Claude/GPT; 5h + weekly | `agy` `/usage` TUI | `cclimits --antigravity` via `~/.gemini/antigravity-cli` → Cloud Code Assist RPCs. CodexBar talks to local `language_server` / `agy` HTTPS | Two tanks; exhausting one is not exhausting the other |
| Cursor | monthly Cursor Models vs Other Models; Grok Bot weekly extra | **No.** `cursor-agent about` has plan tier only | Unofficial: local `state.vscdb` token + `cursor.com/api/usage-summary` / `GetCurrentPeriodUsage`. CodexBar and aiquota do this. cclimits does not | Do not scrape `api2.cursor.sh` as a first-party Spotticus invention. Pin a named wrapper and fail closed |
| Grok Bot | weekly included on paid Cursor | No | CodexBar `get-sand-usage-status` | Same Cursor session; different clock |

## Tools we wrap or consult (keep these URLs)

Full catalog: [related-tools.md](related-tools.md). Landscape dump:
[research/leftover-tool-landscape.md](research/leftover-tool-landscape.md).

Two jobs, two communities:

- **Live leftover** (remaining %, reset): follow **[CodexBar](https://github.com/steipete/CodexBar)** first (`codexbar usage --json`). Next: **[OpenUsage.ai](https://www.openusage.ai)** ([robinebers/openusage](https://github.com/robinebers/openusage), local `127.0.0.1:6736/v1/limits`), then **[tokscale](https://github.com/junhoyeo/tokscale)** `tokscale usage --json`.
- **Historical spend** (what you already burned, local JSONL): **[ccusage](https://github.com/ccusage/ccusage)** / [ccusage.com](https://ccusage.com). Not remaining-%.

Glue that still belongs in the catalog (0–1 star, not the community):

- **[aiquota](https://github.com/kohii/aiquota)** — Go CLI. `--json`. No cookie decrypt. `--proj` is spare-pace coloring.
- **[AIQuota for macOS](https://aiquota.app)** — different product from kohii/aiquota.
- **[aiuse](https://github.com/djbclark/aiuse)** — aggregator over CodexBar and friends. Do not treat it as the community.

Skip **[Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor)** (popular, last push 2026-07, stalled).

Portable fallback if CodexBar is a poor fit on a given machine: [cclimits](https://github.com/cruzanstx/cclimits) (Python, file creds, Claude/Codex/Gemini/Antigravity, no Cursor).

Spotticus should call these, not reimplement their HTTP. Per-product modules here record: command, JSON path, windows, failure mode, last verified date.

## Fail closed

If a probe returns nothing readable, do not dispatch on that pool. Stale bars are not leftover.

## Out of catalog unless a PR lands

Copilot, Windsurf, Cline, Aider, PostHog, Kimi, z.ai, etc. See [contributing-providers.md](contributing-providers.md).
