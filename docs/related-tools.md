# Related leftover tools

These are not Spotticus. Spotticus wraps and verifies leftover probes; it does
not reimplement their HTTP or decrypt browser cookies.

**Unsorted inventory** (stars, collectors, name collisions, open questions):
[research/leftover-tool-landscape.md](research/leftover-tool-landscape.md).
Later research and executive agents should sort that packet. This page is the
short index.

**Do not drop these from the catalog.** They were missed once.

## Named links that must stay in the catalog

| What | URL | Role |
| --- | --- | --- |
| **aiquota** (Go CLI) | https://github.com/kohii/aiquota | Machine-readable leftover for Claude, Codex, Cursor, Copilot from local CLI/IDE creds. `--json`. No cookie decrypt. Pace / `--proj` is the same “behind linear reset” idea as Spotticus spare capacity. Tiny repo; method notes, not a community hub. |
| **AIQuota** (macOS app) | https://aiquota.app | Native menu-bar + widgets for Codex and Claude Code (macOS 15+). Browser-backed ChatGPT/Claude sessions in Keychain. Human gauges, not a dispatch CLI. Source appears to be [niederme/ai-quota](https://github.com/niederme/ai-quota). **Not the same project as kohii/aiquota.** |
| **aiuse** | https://github.com/djbclark/aiuse | Python aggregator. Shells out to CodexBar, caut, cswap, tokscale, OpenUsage. Ranks use-it-or-lose-it. `aiuse --json`. Not a probe itself. Tiny repo; its collector table is the map. |

If you only remember three URLs, remember those three. Then read the research dump.

## Community hubs (leftover-adjacent, not a wrap decision)

Language does not matter. Maintenance and a group chasing vendor URL churn does.

| Tool | URL | Snapshot 2026-09-01 | Role |
| --- | --- | --- | --- |
| CodexBar | https://github.com/steipete/CodexBar | ~21k stars, ~365 contribs, push same day | Leftover via `codexbar usage --json`. Method catalog in `docs/`. Linux CLI is what Waybar/KDE/GNOME/COSMIC/Windows ports wrap. |
| ccusage | https://github.com/ccusage/ccusage | ~18k stars, ~77 contribs | **Local spend logs**, not leftover. Do not dispatch on it. |
| tokscale | https://github.com/junhoyeo/tokscale | ~5k stars, ~137 contribs | Cost TUI plus bolted-on `tokscale usage --json`. |
| claude-swap | https://github.com/realiti4/claude-swap | ~2k stars, ~40 contribs | Claude multi-account leftover (`cswap list --json`). |
| Claude-Code-Usage-Monitor | https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor | ~8.7k stars, 6 contribs, last push 2026-07-05 | Popular Claude TUI; re-check whether the community is still live. |
| Win-CodexBar | https://github.com/Finesssee/Win-CodexBar | ~1k stars, ~75 contribs | Windows CodexBar port. |

## Same landscape, already in the leftover notes

| Tool | URL | Role |
| --- | --- | --- |
| cclimits | https://github.com/cruzanstx/cclimits | Portable leftover CLI (Python). Claude, Codex, Gemini, Antigravity. **No Cursor.** Thin community. |
| caut | https://github.com/Dicklesworthstone/coding_agent_usage_tracker | Independent multi-provider leftover (CodexBar-class). Solo. |
| OpenUsage.sh | https://github.com/janekbaraniewski/openusage | Terminal dashboard; mix of leftover, spend, local telemetry. |

## How Spotticus should treat them

- **Wrap a named leftover CLI** per product. Pin version. Fail closed.
- Prefer a hub that other people will patch when Anthropic/OpenAI/Cursor move URLs.
- **aiuse** is a ranking UI over those CLIs. Useful as a human check; not the probe we pin.
- **aiquota.app** is desk visibility. It does not replace a `--json` leftover probe.
- **ccusage** (the 18k-star one) is cost. Do not mix it into dispatch.
- Do not invent `api2.cursor.sh` scraping. Cursor leftover, if we pin it, comes from a named wrapper that already does `state.vscdb` + `cursor.com/api/usage-summary` (CodexBar, aiquota).
