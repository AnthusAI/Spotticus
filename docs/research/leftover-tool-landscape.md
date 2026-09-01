# Leftover-tool landscape (research dump)

**Status:** inventory plus a settled ranking (below). Not a product spec.
Not an implementation of probes.

**For later agents:** the ranking in the next section is the scale to use.
Do not treat aiuse/aiquota as the community. Re-verify GitHub signals before
acting. Do not collapse **live leftover** and **historical spend**.

**Snapshot:** 2026-09-01, from GitHub `repos` + `contributors` API plus project
READMEs, plus a second-session ranking. Stars will be stale by the next
vendor URL change.

**Why this exists:** vendor leftover endpoints are undocumented and rot.
Spotticus should wrap a living probe, not invent scrapers. Language does
not matter. Nobody in the healthy watch communities is building spot-task
dispatch; that gap is Spotticus.

Related shorter notes: [../related-tools.md](../related-tools.md),
[../leftover.md](../leftover.md).

## Settled ranking (2026-09-01)

aiuse and aiquota are real. They do leftover. They are 0–1 star glue: one
or two people, no community that will keep up when Cursor changes billing.

Two different jobs:

1. **Live leftover** (what is left, when it resets). Follow **CodexBar**
   first. ~21k stars, 100+ contributors (365 on the GitHub API including
   bots), commits today, menu bar plus CLI, Codex/Claude/Cursor/Copilot/Grok/Antigravity.
   That is the project that will chase vendor API churn.
   Next leftover communities: **OpenUsage.ai**
   ([robinebers/openusage](https://github.com/robinebers/openusage), ~3971
   stars this snapshot, macOS menu bar, local API
   `127.0.0.1:6736/v1/limits`) and **tokscale** (~5k, TUI,
   `tokscale usage --json`).
2. **Historical spend** (what you already burned, from local logs).
   **ccusage** / [ccusage.com](https://ccusage.com). ~18k stars, large npm
   weekly install base, ~77 contributors. Continuum already wrote a guide.
   It is not remaining-%. It reads JSONL off disk.

If you follow two: CodexBar for leftover, ccusage for the bill.

Skip the popular-but-stalled
[Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor)
(last push 2026-07). Skip aiuse as “the community.”

The healthy repos **watch**. They do not dispatch.

## What Spotticus actually needs

Server-side leftover for included subscription windows:

- percent used / remaining
- reset time
- which window (5h session, weekly, monthly, dual tank)

Not:

- local JSONL / SQLite cost scans (`ccusage daily`, `codexbar cost`, tokscale
  models/monthly)
- menu-bar UX
- account switching (unless it also exposes leftover JSON)

A tool can do both. If it does, say which command is leftover.

## Name collisions (do not merge these)

| Name you will see | Distinct things |
| --- | --- |
| aiquota | [kohii/aiquota](https://github.com/kohii/aiquota) Go CLI; [aiquota.app](https://aiquota.app) native macOS app (source [niederme/ai-quota](https://github.com/niederme/ai-quota)); [yagcioglutoprak/AIQuotaBar](https://github.com/yagcioglutoprak/AIQuotaBar) Python menu bar with browser-cookie decrypt |
| quotabar | [majiayu000/quotabar](https://github.com/majiayu000/quotabar) Tauri menubar; [thrawny/quotabar](https://github.com/thrawny/quotabar) Waybar Linux port of CodexBar |
| quota | [Ozperium/quota](https://github.com/Ozperium/quota) terminal tracker |
| ccusage | [ccusage/ccusage](https://github.com/ccusage/ccusage) (also [ryoppippi/ccusage](https://github.com/ryoppippi/ccusage)) local log cost CLI, ~18k stars; [wakamex/ccusage](https://github.com/wakamex/ccusage) Claude OAuth leftover CLI, 2 stars. **Different products.** |
| tokscale | [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) ~5k stars, `tokscale.ai`; [tokscale/tokscale](https://github.com/tokscale/tokscale) 1-star unrelated/collision |
| CodexBar | [steipete/CodexBar](https://github.com/steipete/CodexBar) upstream; [Finesssee/Win-CodexBar](https://github.com/Finesssee/Win-CodexBar) Windows port; [thalestomme/CodexBar](https://github.com/thalestomme/CodexBar) stale Tauri fork |
| OpenUsage | **[OpenUsage.ai](https://www.openusage.ai)** / [robinebers/openusage](https://github.com/robinebers/openusage) (~4k stars) native macOS menu bar + loopback `127.0.0.1:6736/v1/limits`. **[OpenUsage.sh](https://openusage.sh)** / [janekbaraniewski/openusage](https://github.com/janekbaraniewski/openusage) (~180 stars) terminal dashboard. Distinct products. |
| cswap | [realiti4/claude-swap](https://github.com/realiti4/claude-swap) Claude multi-account leftover (`cswap list --json`); [GoDiao/cswap](https://github.com/GoDiao/cswap) provider-isolation launcher. **Different products.** |

## Community signal (inventory)

GitHub contributor totals include bots. Last-push “today” does not prove
leftover probes still work. The **settled ranking is above**; this table is
the rest of the inventory.

### Hubs worth a second look (community + leftover-adjacent)

These are the ones that look like people are actually co-maintaining against
vendor churn.

| Project | URL | Stars | Contribs | Last push | Lang | Leftover vs spend | Why it is a hub |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CodexBar | https://github.com/steipete/CodexBar | 20791 | 365 | 2026-09-01 | Swift + Linux CLI | **Leftover** via `codexbar usage --format json`. Cost is a different command. | **Follow first** for live leftover. |
| OpenUsage.ai | https://github.com/robinebers/openusage | 3971 | (re-fetch) | 2026-09-01 | Swift | Leftover via `127.0.0.1:6736/v1/limits` | **Second leftover community.** macOS 15+. Not OpenUsage.sh. |
| tokscale (junhoyeo) | https://github.com/junhoyeo/tokscale | 5238 | 137 | 2026-09-01 | Rust/npm | Cost TUI plus `tokscale usage --json` leftover | **Third leftover community** for live usage JSON. |
| ccusage | https://github.com/ccusage/ccusage | 18269 | 77 | 2026-09-01 | Rust | **Spend logs**, not leftover. `npx ccusage`, https://ccusage.com | **The bill**, never spare-pace dispatch. |
| Claude-Code-Usage-Monitor | https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor | 8667 | 6 | 2026-07-05 | Python | Mix | **Skip.** Popular, stalled (last push July 2026). |
| claude-swap (cswap) | https://github.com/realiti4/claude-swap | 2102 | 40 | 2026-09-01 | Python | **Claude leftover**, multi-account. `cswap list --json` | Active. aiuse calls this the canonical multi-account Claude leftover source. Not multi-product. |
| Win-CodexBar | https://github.com/Finesssee/Win-CodexBar | 1011 | 75 | 2026-08-31 | Rust | Leftover, Windows tray. Same spirit as CodexBar. | Official-feeling Windows port. Same GitHub user also as nesszer/Win-CodexBar. |

### CodexBar satellite UIs (community exists *because* of the CLI contract)

These mostly shell out to `codexbar usage --format json`. They are evidence that
CodexBar is the leftover hub. They are not themselves wrap targets unless we
need a desktop.

| Project | URL | Stars | Notes |
| --- | --- | --- | --- |
| codexbar-waybar | https://github.com/Marouan-chak/codexbar-waybar | 12 | Waybar + GTK4 popover |
| codexbar-cosmic-applet | https://github.com/andrew-verde/codexbar-cosmic-applet | 0 | COSMIC panel; does not talk to vendors itself |
| noctalia-codex-usage | https://github.com/rayoplateado/noctalia-codex-usage | 4 | Noctalia/Quickshell |
| CodexBar Meter | https://github.com/noctalia-dev/community-plugins/tree/main/codexbar-meter | (in community-plugins) | Noctalia v5 store widget |
| KodexBar | https://github.com/tylxr59/KodexBar | 11 | KDE Plasma |
| codexbar-kde | https://github.com/adrianorocha-dev/codexbar-kde | 0 | Plasma 6 plasmoid |
| codexbar-plasmoid | https://github.com/psimaker/codexbar-plasmoid | 14 | Plasma 6, 5 contribs |
| CodexBar Plasma | https://github.com/Lucenx9/codexbar-plasma | 3 | Plasma 6, pushed 2026-09-01 |
| Codexbar GNOME | https://extensions.gnome.org/extension/9841/codexbar/ | (GNOME extensions) | Shell extension |
| UsageMonitor | https://github.com/prodesert22/UsageMonitor | 0 | Rust Linux *reimplementation* of CodexBar fetchers, not a CLI wrapper |
| thrawny/quotabar | https://github.com/thrawny/quotabar | 0 | Waybar; independent Linux port of the idea |
| thalestomme/CodexBar | https://github.com/thalestomme/CodexBar | 0 | Tauri fork; last push 2026-03-03, likely stale |

### Smaller leftover CLIs (useful code, thin community)

Good for method notes and `--json` shapes. Weak as a “community will keep the
URLs alive” bet unless they sit on top of CodexBar/cclimits.

| Project | URL | Stars | Contribs | Last push | Lang | Role |
| --- | --- | --- | --- | --- | --- | --- |
| caut | https://github.com/Dicklesworthstone/coding_agent_usage_tracker | 82 | 1 | 2026-08-24 | Rust | Multi-provider leftover CLI. CodexBar-class probes. Solo. |
| OpenUsage.sh | https://github.com/janekbaraniewski/openusage | 181 | 10 | 2026-08-31 | Go | Terminal dashboard + daemon + SQLite. Mix of leftover, spend, local telemetry. Site: https://openusage.sh |
| cclimits | https://github.com/cruzanstx/cclimits | 27 | 2 | 2026-08-07 | Python | Portable leftover: Claude, Codex, Gemini, Antigravity. **No Cursor.** File creds. |
| majiayu000/quotabar | https://github.com/majiayu000/quotabar | 45 | 1 | 2026-09-01 | TS/Tauri | Menubar Claude/Codex/Cursor/Antigravity. Local cost too. |
| AIUsageTracker | https://github.com/rygel/AIUsageTracker | 44 | 5 | 2026-08-26 | C# | Windows tray. Multi-provider. Testers-welcome on several. |
| AIQuotaBar | https://github.com/yagcioglutoprak/AIQuotaBar | 27 | ~0–1 | 2026-05-31 | Python | Menu bar; **browser cookie decrypt**. Last push May. Spotticus policy: do not add cookie decryptors as first-party. |
| aiquota CLI | https://github.com/kohii/aiquota | 1 | 1 | 2026-08-05 | Go | Claude/Codex/Cursor/Copilot leftover. `--json`. `--proj` = spare-pace. No cookie decrypt. Inspired by CodexBar. |
| AIQuota.app | https://aiquota.app | (see niederme/ai-quota: 10 stars, 2 contribs, 2026-08-28) | Swift | macOS 15+ gauges for Codex + Claude. Browser-backed sessions. Not a dispatch CLI. |
| aiuse | https://github.com/djbclark/aiuse | 0 | 1 | 2026-08-24 | Python | **Aggregator.** Shells out to cswap, CodexBar, caut, tokscale, OpenUsage.ai, OpenUsage.sh. Ranks use-it-or-lose-it. Map of collectors is valuable even if the repo is tiny. |
| gauge | https://github.com/howells/gauge | 0 | 1 | 2026-08-29 | TypeScript | Claude/Codex/Cursor leftover dashboard. JSON by default in non-TTY. Multi-account. |
| Ozperium/quota | https://github.com/Ozperium/quota | 0 | 1 | 2026-08-20 | TypeScript | Terminal leftover. Claude/Codex local files; Cursor/Grok “coming soon.” Has `quota serve` for Stoke routing. |
| vibeusage | https://github.com/victorGPT/vibeusage | 131 | 1 | 2026-07-31 | JS | Local hooks/logs + optional cloud dashboard. **Spend/activity**, not leftover. |
| wakamex/ccusage | https://github.com/wakamex/ccusage | 2 | 1 | 2026-08-15 | Python | Claude OAuth leftover (`api.anthropic.com/api/oauth/usage`). Name-collides with the big ccusage. |
| Tatendaz/claude-usage | https://github.com/Tatendaz/claude-usage | 0 | 1 | 2026-08-24 | Python | Claude leftover in terminal status bars. Agent-oriented docs (`AGENTS.md`). |
| claude_usage | https://github.com/thiswillbeyourgithub/claude_usage | 2 | 1 | 2026-08-07 | Python | Claude leftover JSON + skill to wait for reset. |
| claude-code-usage | https://github.com/StephenLReed/claude-code-usage | 3 | 1 | 2026-01-05 | Java | OAuth leftover. Stale. |
| LightspeedDMS/claude-usage | https://github.com/LightspeedDMS/claude-usage | 6 | 1 | 2026-07-12 | Python | Claude leftover CLI. |

### Adjacent, huge, not leftover probes

| Project | URL | Stars | Why it showed up | Keep? |
| --- | --- | --- | --- | --- |
| CC Switch | https://github.com/farion1231/cc-switch | 130527 | Claude Code all-in-one desktop; provider/account switching | Not a leftover JSON probe. Adjacent ecosystem only. |
| GoDiao/cswap | https://github.com/GoDiao/cswap | (not ranked here) | Name-collides with claude-swap | Provider isolation launcher, not leftover. |
| qxbyte/muse | https://github.com/qxbyte/muse | 0 | aiuse mentions a `muse` collector | This repo is an agent CLI, probably not that collector. Research agent: find the real muse leftover tool. |

## Method notes already seen (Anthus Mac, 2026-09-01)

Do not treat as still true without re-verify.

| Product | Official leftover CLI? | Working leftover path seen | Do not do |
| --- | --- | --- | --- |
| Claude Code | No JSON. `claude /usage` is human text | CodexBar `usage --provider claude --source cli --format json`. Portable: cclimits / `~/.claude/.credentials.json` → `api.anthropic.com/api/oauth/usage` | Mix `ccusage claude daily` (local logs) into dispatch |
| Codex | `codex app-server` `account/rateLimits/read` | CodexBar usage JSON. Portable: cclimits / aiquota via `~/.codex/auth.json` → `chatgpt.com/backend-api/wham/usage` | |
| Antigravity | `agy` TUI | cclimits `--antigravity`; CodexBar talks to local language_server / agy HTTPS | Treat empty Claude tank as empty Gemini tank |
| Cursor | **No.** `cursor-agent about` has plan tier only | Unofficial: `state.vscdb` token + `cursor.com/api/usage-summary`. CodexBar and aiquota. cclimits does not. | Invent `api2.cursor.sh` scraping as first-party Spotticus |
| Grok Bot | No | CodexBar `get-sand-usage-status` | Dump Grok leftover into Cursor on-demand |

## aiuse collector map (copy from their README, 2026-09-01)

aiuse does not probe vendors itself. It ranks leftover from tools on PATH:

| Collector | Command / API | aiuse’s claim |
| --- | --- | --- |
| cswap (realiti4/claude-swap) | `cswap list --json` | Canonical multi-account Claude leftover |
| CodexBar | `codexbar usage --format json` | Preferred non-Claude leftover; disable CodexBar Claude on macOS if Keychain prompts |
| caut | `caut usage --json` | Cross-check; same Keychain-prompt caution on macOS |
| OpenUsage.ai | `openusage` / `127.0.0.1:6736/v1/limits` | Distinct collector key `openusage_ai` |
| OpenUsage.sh | `openusage-sh export --output - --format json` | Distinct key `openusage_sh`; lowest-priority backup |
| tokscale | `tokscale usage --json` | Independent leftover; preferred for Copilot fill-in |

Also mentioned as skippable collectors in aiuse flags: muse, qwencloud, bailian.
**Not identified in this pass** beyond Alibaba DashScope quotas inside OpenUsage.sh.
Follow-up research: find those three repos.

## Suggested work for later agents (do not execute here)

Research:

1. Re-fetch GitHub stats. Flag anything with last push older than ~30 days.
2. For each leftover candidate, record: install command, `--json` sample
   (redacted), windows, auth path, last verified date, fail-closed behavior.
3. Identify aiuse’s `muse`, `qwencloud`, `bailian` collectors.
4. Compare CodexBar leftover JSON vs OpenUsage.ai `/v1/limits` vs tokscale
   `usage --json` **on the same machine** for Claude + Codex + Cursor.

Executive (already ranked, do not re-litigate scale):

1. Wrap CodexBar leftover as the default living probe.
2. OpenUsage.ai and tokscale `usage` are the next leftover communities.
3. ccusage is the bill, never spare-pace dispatch.
4. aiuse/aiquota stay as glue notes. Claude-Code-Usage-Monitor is skipped.
5. Policy already in contributing-providers.md: no first-party cookie
   decrypt; no first-party `api2.cursor.sh`.

## What this pass did not do

- Did not run every CLI.
- Did not implement Spotticus probes or dispatch.
