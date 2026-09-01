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

1. Curate leftover probes for products Anthus uses. Follow **CodexBar**
   first for live leftover (`codexbar usage --json`). Next leftover
   communities: OpenUsage.ai, then tokscale `usage --json`. **ccusage** is
   historical spend from local logs, not remaining-%. aiuse and aiquota are
   real glue, not the community. Do not invent scrapers. Products we do
   not run land only via a working PR plus verification help. Keep
   [docs/related-tools.md](docs/related-tools.md) current. Dump new
   findings into
   [docs/research/leftover-tool-landscape.md](docs/research/leftover-tool-landscape.md).
2. Dispatch interruptible chores when leftover is behind linear pace.
   The healthy leftover repos watch; they do not dispatch. That gap is
   Spotticus. Assume one agentic invocation may burn the rest of a
   window. One live spot run per pool. Re-probe after each chore. Fail
   closed.

Read `docs/leftover.md` and `docs/dispatch.md` before changing probe or
dispatch behavior.

## Git

This repository is its own git repo. Do not commit Spotticus into the
parent `~/Projects` checkout.

`develop` is the continuous-integration branch. Merge accepted, green work
there as soon as it is ready. Do not park completed work on long-lived
feature branches waiting for `main`.

`main` is the release branch. Semantic-release runs only from `main`.
Do not treat a merge to `develop` as a production release. The release
workflow is local to this repo and authenticates with `GITHUB_TOKEN`;
do not call the platform-ci reusable workflow, which requires an
`anthusbot_gh_token` this repository does not have.

Open pull requests against `develop`. Merge them there as soon as
sub-agent review is addressed and CI is green. Do not park completed
work on feature branches. Humans promote `develop` to `main` when they
intend a release, not as the daily integration path.

## Pull request review

No human GitHub reviewer will show up. Review is done in this session with
**Composer 2.5** (and Bugbot when a branch diff should be checked)
sub-agents. Do not mark a PR ready and wait. Launch a reviewer against
`develop`, treat request-changes as blocking, and have a second agent
apply fixes. Approval from that loop is the merge gate, not a person on
the PR.

No emojis. No second issue store beside Kanbus.

