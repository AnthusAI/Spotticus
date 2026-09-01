# Dispatch

Spot tasks fill leftover included quota. They are interruptible. On-demand (a human, or a job the human started) preempts them.

Healthy leftover communities (CodexBar, OpenUsage.ai, tokscale) **watch**.
ccusage watches the bill. They do not dispatch. Spotticus is the dispatch
layer on top of leftover probes.

Kanbus is the queue. Open chores labeled `spot` are eligible. Spotticus does not own a second backlog.

## When leftover is “spare”

Not “always be agenting.” Spare means the human is **behind the linear pace** of a resetting window.

Example: a weekly window is 50% of the way to reset and only 25% used. Unused 75% will die. That is spare capacity. Dispatch may start.

Sketch (per window, per product):

```
elapsed_frac = time_since_reset / window_length
used_frac    = used_percent / 100
spare        = elapsed_frac - used_frac
```

Dispatch on a pool when `spare` is above a threshold (example: 0.20) **and** remaining percent is above a floor (example: 15%) **and** no on-demand hold.

At 10% elapsed and 5% used, spare is small; wait. At 90% elapsed and 20% used, spare is large; burn.

Thresholds are policy. They will be per-product because clocks differ.

## Per-product clocks

| Product | What “a cycle” means | Dispatch consequence |
| --- | --- | --- |
| Claude | Two windows: 5h session and weekly. Weekly is the one that dies on a calendar. Session can empty while weekly looks healthy | Prefer the window closest to reset that still has leftover. Do not treat session 0% as “Claude is empty” if weekly remains |
| Codex | 5h + weekly | Same dual-window pick |
| Antigravity | Two *tanks* (Gemini vs Claude/GPT), each with 5h until a weekly cap | Switching tanks is a product tactic, not a dispatch bug. Empty Claude-tank is not empty Gemini-tank |
| Cursor | Monthly included, two pools (Cursor Models vs Other Models). No official leftover CLI | Until a curated probe is pinned, Cursor is not a dispatch target. Grok Bot weekly is a separate clock on the same seat |
| Grok Bot | Weekly included; overflow is shared on-demand | Do not dump Grok Bot leftover into Cursor on-demand |

## Managing usage while a spot job runs

A single agentic run can work all night and empty a window. Vendors do not give us a hard remaining-token budget we can enforce mid-turn.

**Safest default: assume one invocation may consume the rest of the window.**

That implies:

1. **One live spot run per pool.** Do not fan out ten Composer workers onto the same weekly bar.
2. **Chores are interruptible.** Default read-only. Writes are explicit on the Kanbus issue.
3. **Preempt is SIGTERM + reopen the Kanbus chore.** On-demand hold does this immediately.
4. **After each chore, re-probe.** If leftover is no longer spare, stop. Do not start the next one on a stale snapshot.
5. **Optional caps are hints, not guarantees:** wall-clock timeout, max turns, “stop at 90% used.” An agent that ignores them can still burn the bar. Caps reduce damage; they do not make overnight swarms safe.

What we will not do:

- Promise “this chore costs 3%.” We cannot know.
- Run uncapped overnight swarms “because leftover exists.”
- Start a second spot job because the first one is “probably small.”

## Hold and preempt

- `hold`: human (or on-demand automation) needs the pool. Kill the spot PID. Set the Kanbus chore back to `open`. Do not start another until `release`.
- `preempt`: same kill path without necessarily setting a lasting hold (window gone, probe failed, remaining below floor).

## Fail closed

No readable leftover → no dispatch. Probe error → no dispatch. Hold set → no dispatch. Already running on that pool → no dispatch.
