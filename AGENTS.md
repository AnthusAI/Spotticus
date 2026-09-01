# Agent Instructions

## Project management with Kanbus

Use Kanbus for task management.
Why: Kanbus task management is MANDATORY here; every task must live in Kanbus.
When: Create/update the Kanbus task before coding; close it only after the change lands.
How: See CONTRIBUTING_AGENT.md for the Kanbus workflow, hierarchy, status rules, priorities, command examples, and the sins to avoid. Never inspect project/ or issue JSON directly (including with cat or jq); use Kanbus commands only.
Performance: Prefer kbs (Rust) when available; kanbus (Python) is equivalent but slower.
Warning: Editing project/ directly is a sin against The Way. Do not read or write anything in project/; work only through Kanbus.

## What this project is

Spotticus treats unused included coding-agent quota as spare capacity (spot
tasks). Interactive work is on-demand and preempts spot work. Kanbus chores
labeled `spot` are the queue.

Two jobs:

1. Curate leftover probes for products Anthus uses. Wrap existing CLIs
   (`cclimits`, `codexbar`, `aiquota`, later others). Do not invent scrapers.
   Products we do not run land only via a working PR plus verification help.
   Keep [docs/related-tools.md](docs/related-tools.md) current
   (`https://github.com/kohii/aiquota`, `https://aiquota.app`,
   `https://github.com/djbclark/aiuse`). Dump new findings into
   [docs/research/leftover-tool-landscape.md](docs/research/leftover-tool-landscape.md);
   do not silently pick a wrap target.
2. Dispatch interruptible chores when leftover is behind linear pace.
   Assume one agentic invocation may burn the rest of a window. One live
   spot run per pool. Re-probe after each chore. Fail closed.

Read `docs/leftover.md` and `docs/dispatch.md` before changing probe or
dispatch behavior.

This repository is its own git repo. Do not commit Spotticus into the
parent `~/Projects` checkout.

`develop` is the integration branch if one exists; `main` is release.
Semantic-release runs from `main`. Do not merge to `main` as daily
integration. Git Flow details (Chattic-style `develop` as CI, PRs against
`develop`, humans promote to `main`) are not copied here yet; discuss
before stealing that policy.

No emojis. No second issue store beside Kanbus.

