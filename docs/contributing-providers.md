# Adding a provider we do not use

Anthus will curate leftover probes for products we actually run. Other products can land if you:

1. Open a pull request with a working probe (command + JSON shape + windows + reset).
2. Stay on the PR until we can reproduce it, or until you provide a recorded fixture (`--json` output plus redacted creds path) we can regression-test.
3. Document last-verified date and failure mode (fail closed, never dispatch on garbage).

We may not have a seat on that product. “It works on my machine” is not enough without a fixture or a co-maintainer who can re-verify when the vendor URL moves.

## What a provider module must include

- How credentials are found (file path, not a scraped cookie if a file exists).
- The exact command or HTTP call.
- JSON pointer to used %, remaining %, `resets_at`, window name.
- Which clock it is (5h, weekly, monthly, dual tank).
- Last verified date.
- A test with a checked-in **redacted** sample payload.

Do not add browser-cookie decryptors. Do not add `api2.cursor.sh` scraping unless that is already the documented method for a named wrapper we call, and the PR pins that wrapper’s version.

Existing named wrappers (not ours): [cclimits](https://github.com/cruzanstx/cclimits), [CodexBar](https://github.com/steipete/CodexBar), [aiquota](https://github.com/kohii/aiquota). Desk gauges at [aiquota.app](https://aiquota.app) are a different product from the aiquota CLI. [aiuse](https://github.com/djbclark/aiuse) aggregates those CLIs; it is not a probe to wrap. See [related-tools.md](related-tools.md) and the unsorted dump in [research/leftover-tool-landscape.md](research/leftover-tool-landscape.md).

## Kanbus

File a story under the leftover-probes epic. Label it with the product name. Do not start from a drive-by README edit.
