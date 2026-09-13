from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from spotticus import __version__
from spotticus.models import ProbeStatus
from spotticus.probes.codexbar import CodexBarProbe
from spotticus.scoring import score_provider


from spotticus.locks import claim_lock, release_lock, hold_lock, unhold_lock


def _matches_target(provider: str, pool_id: str, targets: list[str]) -> bool:
    for t in targets:
        if t == provider or t == f"{provider}.{pool_id}":
            return True
    return False

import dataclasses
from spotticus.routing import resolve_target
import dataclasses
from spotticus.routing import resolve_target
def _prune_report(report, targets: list[str]):
    if not targets:
        return report
        
    new_results = []
    for result in report.results:
        if result.pools:
            new_pools = {
                p_id: windows
                for p_id, windows in result.pools.items()
                if _matches_target(result.provider, p_id, targets)
            }
            new_result = dataclasses.replace(result, pools=new_pools)
            new_results.append(new_result)
        else:
            new_results.append(result)
            
    # Remove providers that have no pools remaining (but keep the failed ones which have no pools natively if we want, or do we? Wait, targets filtering means we only care about targets. But if a probe failed, should we keep it? For now, we only drop results where pools became empty due to filtering.)
    # Actually, if we filter, we only want the targets. If a result has empty pools, we can drop it.
    final_results = [r for r in new_results if r.pools or r.status != "ok"] 
    # Actually, wait, ProbeReport might be frozen too? Let's check `spotticus/models.py`.
    return dataclasses.replace(report, results=[r for r in new_results if r.pools])

def _cmd_status(args: argparse.Namespace) -> int:
    """Probe all providers and display their spare capacity status."""
    probe = CodexBarProbe()
    report = probe.probe(targets=args.target)
    report = _prune_report(report, args.target)

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
                    "pools": {
                        p_id: {
                            "is_eligible": p.is_eligible,
                            "lock_data": p.lock_data,
                            "windows": [
                                {
                                    "window": w.window_name,
                                    "elapsed_frac": w.elapsed_frac,
                                    "used_frac": w.used_frac,
                                    "spare": w.spare,
                                    "remaining_percent": w.remaining_percent,
                                    "is_spare": w.is_spare,
                                }
                                for w in p.window_scores
                            ]
                        }
                        for p_id, p in s.pool_scores.items()
                    }
                }
                for s in provider_scores
            ]
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Spotticus Status (Threshold: {args.threshold}, Floor: {args.floor}%)")
        print("=========================================================")
        for s in provider_scores:
            print(f"\n{s.provider.upper()}:")
            if not s.pool_scores:
                print("  🔴 SKIP: No valid windows / Error")
                continue
            for pool_id, p in s.pool_scores.items():
                if p.lock_data:
                    state = p.lock_data.get("state")
                    product = p.lock_data.get("product", "Unknown")
                    model = p.lock_data.get("model", "Unknown")
                    name = p.lock_data.get("name", "Unknown")
                    if state == "HELD":
                        status_label = f"🔴 SKIP: HELD by {product} ({model}) name: {name}"
                    else:
                        status_label = f"🔴 SKIP: Locked by {product} ({model}) name: {name}"
                elif p.is_eligible:
                    status_label = "🟢 ELIGIBLE"
                elif not p.window_scores:
                    status_label = "🔴 SKIP: No valid windows / Error"
                else:
                    status_label = "🔴 SKIP: Not all windows spare"
                    
                print(f"  {pool_id:<15} {status_label}")
                for w in p.window_scores:
                    spare_str = f"{w.spare:+.2f}"
                    verdict = "spare" if w.is_spare else "not spare"
                    print(
                        f"    - {w.window_name}: "
                        f"elapsed {w.elapsed_frac:.0%}, "
                        f"used {w.used_frac:.0%}, "
                        f"spare {spare_str}, "
                        f"remaining {w.remaining_percent:.0f}% -> {verdict}"
                    )

    return 0 if has_eligible else 1


def _cmd_claim(args: argparse.Namespace) -> int:
    success = claim_lock(
        target=args.target,
        product=args.product,
        model=args.model,
        name=args.name,
        pid=args.pid,
        session_id=args.session_id
    )
    if success:
        print(f"Lock claimed for target {args.target}.")
        return 0
    else:
        print(f"Failed to claim lock. Target {args.target} is already locked.", file=sys.stderr)
        return 1


def _cmd_release(args: argparse.Namespace) -> int:
    success, reason = release_lock(
        target=args.target,
        pid=args.pid
    )
    if success:
        print(f"Lock released for target {args.target}.")
        return 0
    else:
        print(f"Failed to release lock. {reason}", file=sys.stderr)
        return 1


def _cmd_hold(args: argparse.Namespace) -> int:
    hold_lock(args.target)
    print(f"Lock preempted and held for target {args.target}.")
    return 0


def _cmd_unhold(args: argparse.Namespace) -> int:
    unhold_lock(args.target)
    print(f"Lock unconditionally removed for target {args.target}.")
    return 0


def _cmd_resolve(args: argparse.Namespace) -> int:
    try:
        from pathlib import Path
        config_path = Path(args.config) if args.config else Path.home() / ".spotticus.yml"
        result = resolve_target(
            class_name=args.cls,
            specific_app=args.app,
            config_path=config_path,
            threshold=args.threshold,
            floor=args.floor,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"Error resolving target: {e}", file=sys.stderr)
        return 1


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
        "--target",
        action="append",
        default=[],
        help="Specific pools to query (e.g. antigravity.gemini). Can be passed multiple times.",
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

    # -- claim --
    claim_parser = subparsers.add_parser("claim", help="Claim spare capacity for a target.")
    claim_parser.add_argument("target", help="Target to claim (e.g., provider.pool).")
    claim_parser.add_argument("--product", required=True, help="Product name.")
    claim_parser.add_argument("--model", required=True, help="Model name.")
    claim_parser.add_argument("--name", required=True, help="Bot or session name.")
    claim_parser.add_argument("--pid", type=int, required=True, help="Process ID of the agent.")
    claim_parser.add_argument("--session-id", help="Optional session ID.")

    # -- release --
    release_parser = subparsers.add_parser("release", help="Release a claimed target.")
    release_parser.add_argument("target", help="Target to release (e.g., provider.pool).")
    release_parser.add_argument("--pid", type=int, required=True, help="Process ID of the agent releasing.")

    # -- hold --
    hold_parser = subparsers.add_parser("hold", help="Preempt and hold a target lock.")
    hold_parser.add_argument("target", help="Target to hold (e.g., provider.pool).")

    # -- resolve --
    resolve_parser = subparsers.add_parser("resolve", help="Resolve a model class to an app/model.")
    resolve_parser.add_argument("--cls", required=True, help="The model class (e.g. smart, cheap).")
    resolve_parser.add_argument("--app", help="Optional specific app to override the class priority.")
    resolve_parser.add_argument("--config", help="Path to config yaml.")
    resolve_parser.add_argument("--threshold", type=float, default=0.20, help="Spare threshold.")
    resolve_parser.add_argument("--floor", type=float, default=15.0, help="Remaining-percent floor.")

    # -- unhold --
    unhold_parser = subparsers.add_parser("unhold", help="Unconditionally remove a target's lock (even if HELD).")
    unhold_parser.add_argument("target", help="Target to unhold (e.g., provider.pool).")

    args = parser.parse_args(argv)

    if args.command == "status":
        return _cmd_status(args)
    elif args.command == "claim":
        return _cmd_claim(args)
    elif args.command == "release":
        return _cmd_release(args)
    elif args.command == "hold":
        return _cmd_hold(args)
    elif args.command == "resolve":
        return _cmd_resolve(args)

    elif args.command == "unhold":
        return _cmd_unhold(args)
    else:
        parser.print_help()
        print(
            "\nSpotticus is pre-1.0. Try: spotticus status",
            file=sys.stderr,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
