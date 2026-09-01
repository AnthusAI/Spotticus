from __future__ import annotations

import argparse
import sys

from spotticus import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="spotticus",
        description=(
            "Fill leftover included coding-agent quota with interruptible "
            "Kanbus chores. Interactive work is on-demand. Spot tasks preempt."
        ),
    )
    parser.add_argument("--version", action="version", version=f"spotticus {__version__}")
    parser.parse_args(argv)
    parser.print_help()
    print(
        "\nSpotticus is pre-1.0. Leftover probes and dispatch policy live in docs/ "
        "and Kanbus. No dispatch yet.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
