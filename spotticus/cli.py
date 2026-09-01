from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from spotticus import __version__
from spotticus.models import ProbeStatus
from spotticus.probes.codexbar import CodexBarProbe
from spotticus.scoring import score_provider


def _cmd_status(args: argparse.Namespace) -> int:
    """Probe all providers and display their spare capacity status."""
    probe = CodexBarProbe()
    report = probe.probe()

    if report.status == ProbeStatus.FAILED:
        if args.json:
            print(json.dumps({"error": report.error}, indent=2))
        else:
            print(f"Probe failed: {report.error}", file=sys.stderr)
        return 1

    now = datetime.now(timezone.utc)
    provider_scores = []
    
    for result in report.results:
        score = score_provider(
            result, 
            now, 
            spare_threshold=args.threshold, 
            remaining_floor=args.floor
        )
        provider_scores.append(score)

    has_eligible = any(score.is_eligible for score in provider_scores)

    if args.json:
        output = {
            "now": now.isoformat(),
            "threshold": args.threshold,
            "floor": args.floor,
            "providers": [
                {
                    "provider": s.provider,
                    "is_eligible": s.is_eligible,
                    "windows": [
                        {
                            "window": w.window_name,
                            "elapsed_frac": w.elapsed_frac,
                            "used_frac": w.used_frac,
                            "spare": w.spare,
                            "remaining_percent": w.remaining_percent,
                            "is_spare": w.is_spare,
                        }
                        for w in s.window_scores
                    ]
                }
                for s in provider_scores
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Spotticus Status (Threshold: {args.threshold}, Floor: {args.floor}%)")
        print("=========================================================")
        for s in provider_scores:
            if s.is_eligible:
                status_label = "🟢 ELIGIBLE"
            elif not s.window_scores:
                status_label = "🔴 SKIP: No valid windows / Error"
            else:
                status_label = "🔴 SKIP: Not all windows spare"
                
            print(f"\n{s.provider.upper():<15} {status_label}")
            for w in s.window_scores:
                spare_str = f"{w.spare:+.2f}"
                verdict = "spare" if w.is_spare else "not spare"
                print(
                    f"  - {w.window_name}: "
                    f"elapsed {w.elapsed_frac:.0%}, "
                    f"used {w.used_frac:.0%}, "
                    f"spare {spare_str}, "
                    f"remaining {w.remaining_percent:.0f}% -> {verdict}"
                )

    return 0 if has_eligible else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Spotticus fills leftover included coding-agent quota with interruptible "
            "Kanbus chores. Interactive work is on-demand. Spot tasks preempt."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"spotticus {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command")

    # -- status --
    status_parser = subparsers.add_parser(
        "status",
        help="Check spare-pace status across all providers.",
    )
    status_parser.add_argument(
        "--json", action="store_true", help="Output as JSON."
    )
    status_parser.add_argument(
        "--threshold",
        type=float,
        default=0.20,
        help="Spare threshold (default: 0.20).",
    )
    status_parser.add_argument(
        "--floor",
        type=float,
        default=15.0,
        help="Remaining-percent floor (default: 15.0).",
    )

    args = parser.parse_args(argv)

    if args.command == "status":
        return _cmd_status(args)
    else:
        parser.print_help()
        print(
            "\nSpotticus is pre-1.0. Try: spotticus status",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
