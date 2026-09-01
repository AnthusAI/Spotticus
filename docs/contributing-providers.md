# Adding a provider we do not use

Anthus will curate leftover probes for products we actually run. Other products can land if you:

1. Open a pull request **against `develop`** with a working probe (command + JSON shape + windows + reset).
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

Default leftover community to wrap: [CodexBar](https://github.com/steipete/CodexBar). Next: [OpenUsage.ai](https://github.com/robinebers/openusage), [tokscale](https://github.com/junhoyeo/tokscale) `usage --json`. Spend-only: [ccusage](https://github.com/ccusage/ccusage). Glue, not hubs: [aiquota](https://github.com/kohii/aiquota), [aiuse](https://github.com/djbclark/aiuse). See [related-tools.md](related-tools.md) and [research/leftover-tool-landscape.md](research/leftover-tool-landscape.md).

## Kanbus

File a story under the leftover-probes epic. Label it with the product name. Do not start from a drive-by README edit.
