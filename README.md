# Spotticus

Spotticus fills leftover **included** coding-agent quota with interruptible chores. Interactive work is on-demand. Spot tasks preempt when a human needs the pool.

It is not Fast. It is not on-demand spend. It is not “always be agenting.”

```
leftover included quota  →  spare capacity (spot)
human interactive work   →  on-demand
Kanbus chores            →  the queue
```

## Two jobs

1. **Leftover probes.** A curated catalog of ways to read *current* session and weekly (or monthly) usage for the products Anthus actually uses. We wrap and verify existing tools. We do not invent scrapers. Products we do not run ourselves can land if someone sends a working pull request and helps verify it. See [docs/leftover.md](docs/leftover.md), [docs/related-tools.md](docs/related-tools.md), and [docs/contributing-providers.md](docs/contributing-providers.md).

   Live leftover: follow [CodexBar](https://github.com/steipete/CodexBar) first, then [OpenUsage.ai](https://www.openusage.ai) and [tokscale](https://github.com/junhoyeo/tokscale) `usage --json`. Historical spend: [ccusage](https://github.com/ccusage/ccusage) (not remaining-%). Glue notes: [aiquota](https://github.com/kohii/aiquota), [aiquota.app](https://aiquota.app), [aiuse](https://github.com/djbclark/aiuse). Dump: [docs/research/leftover-tool-landscape.md](docs/research/leftover-tool-landscape.md).

2. **Dispatch.** When leftover is spare enough, relative to how far the refresh cycle has run, start interruptible Kanbus chores on that pool. Preempt when on-demand work needs the pool. Per-product clocks and burn behavior are first-class. See [docs/dispatch.md](docs/dispatch.md).

The queue is **Kanbus**. Open chores labeled `spot` are the backlog. Spotticus does not keep a second issue store.

## Status

Pre-1.0. Ideas are in Kanbus and `docs/`. The CLI is a versioned stub until the leftover catalog and dispatch policy have specs.

## Install (later)

```bash
pip install spotticus
```

Until a release exists, clone this repository. Integration is `develop`.
`main` is release only. Open pull requests against `develop`.

## License

MIT. See [LICENSE](LICENSE).
