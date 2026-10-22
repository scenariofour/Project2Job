"""Print or verify the deterministic Day 5 evaluation artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab.day5_evaluation import (  # noqa: E402
    build_blind_packet,
    check_committed,
    write_committed,
    serialized_bad_cases,
    serialized_layers,
    serialized_results,
    serialized_taxonomy,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument(
        "--print",
        choices=("results", "bad-cases", "blind-packet", "taxonomy", "layers"),
    )
    args = parser.parse_args()

    if args.check:
        stale = check_committed()
        if stale:
            raise SystemExit(f"Committed Day 5 artifacts are stale: {stale}")
        print("Day 5 evaluation artifacts match the recorded outputs.")
        return

    if args.write:
        for path in write_committed():
            print(f"Wrote {path.relative_to(ROOT)}")
        return

    printers = {
        "results": serialized_results,
        "bad-cases": serialized_bad_cases,
        "blind-packet": build_blind_packet,
        "taxonomy": serialized_taxonomy,
        "layers": serialized_layers,
    }
    print(printers[args.print](), end="")


if __name__ == "__main__":
    main()
