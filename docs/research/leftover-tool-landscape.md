# Leftover-tool landscape (research dump)

**Status:** unsorted research packet. Not a wrap decision. Not a product spec.

**For later agents:** read this whole file before ranking, wrapping, or implementing
probes. Executive agents should pick a hub and a wrap list. Research agents should
re-verify GitHub signals and whether each tool reports **server-side leftover**
or only **local spend logs**. Do not collapse those two numbers.

**Snapshot:** 2026-09-01, from GitHub `repos` + `contributors` API plus project
READMEs. Stars, forks, open issues, last push, and contributor counts will be
stale by the next vendor URL change. Re-fetch before acting.

**Why this exists:** vendor leftover endpoints are undocumented and rot.
Spotticus should wrap a living probe, not invent scrapers. Ryan asked for
well-maintained projects with an **active community** chasing that churn.
Language does not matter.

Related shorter notes: [../related-tools.md](../related-tools.md),
[../leftover.md](../leftover.md).

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
| OpenUsage | [openusage.sh](https://openusage.sh) / [janekbaraniewski/openusage](https://github.com/janekbaraniewski/openusage) terminal dashboard; [openusage.ai](https://www.openusage.ai) macOS menu-bar + loopback `/v1/limits`. aiuse treats them as **distinct collectors**. |
| cswap | [realiti4/claude-swap](https://github.com/realiti4/claude-swap) Claude multi-account leftover (`cswap list --json`); [GoDiao/cswap](https://github.com/GoDiao/cswap) provider-isolation launcher. **Different products.** |

## Community signal (hint only)

GitHub contributor totals include bots. Last-push “today” does not prove
leftover probes still work. Use this as a **starting rank**, not a wrap list.

### Hubs worth a second look (community + leftover-adjacent)

These are the ones that look like people are actually co-maintaining against
vendor churn.

| Project | URL | Stars | Contribs | Last push | Lang | Leftover vs spend | Why it is a hub |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CodexBar | https://github.com/steipete/CodexBar | 20791 | 365 | 2026-09-01 | Swift + Linux CLI | **Leftover** via `codexbar usage --format json`. Cost is a different command. | Richest method catalog (`docs/*.md` per provider). Linux CLI is the contract many desktop ports wrap. Homebrew, AUR, `codexbar serve`. Site: https://codex.bar |
| ccusage | https://github.com/ccusage/ccusage | 18269 | 77 | 2026-09-01 | Rust | **Spend logs**, not leftover. `npx ccusage`, https://ccusage.com | Largest *cost* community. Do not dispatch on it. Useful as “what people already run.” |
| tokscale (junhoyeo) | https://github.com/junhoyeo/tokscale | 5238 | 137 | 2026-09-01 | Rust/npm | Mostly **cost**. Also `tokscale usage --json` for live subscription leftover. | Active npm (`tokscale` / `@tokscale/cli`). Site: https://tokscale.ai |
| Claude-Code-Usage-Monitor | https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor | 8667 | 6 | 2026-07-05 | Python | Mix: local JSONL + later OAuth leftover discussion | Huge star count, **few contributors**, last push ~2 months before this snapshot. Re-check if it is still the Claude leftover community or a popular older TUI. |
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
3. Confirm OpenUsage.ai GitHub/source (site fetch timed out this pass).
4. Identify aiuse’s `muse`, `qwencloud`, `bailian` collectors.
5. Decide whether Claude-Code-Usage-Monitor is still maintained (stars vs
   2026-07-05 push vs 6 contributors).
6. Compare CodexBar Linux CLI vs cclimits vs caut vs aiquota vs tokscale
   `usage` **on the same machine** for Claude + Codex leftover JSON.

Executive:

1. Pick the **community hub** we will track (likely CodexBar, with satellites
   as proof). Language is irrelevant.
2. Pick **one wrap CLI per Anthus product**, with a portable fallback.
   Current hedge in leftover.md: cclimits portable, CodexBar richest, aiquota
   for unofficial Cursor.
3. Explicitly reject wrapping spend-only tools (ccusage daily, vibeusage,
   tokscale models) for dispatch.
4. Policy already in contributing-providers.md: no first-party cookie
   decrypt; no first-party `api2.cursor.sh`.

## What this pass did not do

- Did not run every CLI.
- Did not rank a winner.
- Did not copy Chattic Git Flow (see AGENTS.md; discuss first).
- Did not implement Spotticus probes or dispatch.
