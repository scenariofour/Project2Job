"""Run or verify the deterministic Day 3 context comparison."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab.day3_context_comparison import build_report  # noqa: E402


COMMITTED_RESULT = (
    ROOT / "docs" / "build_journal" / "traces" / "day3_context_comparison.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report()
    rendered = json.dumps(report, indent=2) + "\n"

    if args.check:
        if not COMMITTED_RESULT.is_file():
            raise SystemExit(f"Missing committed result: {COMMITTED_RESULT}")
        if COMMITTED_RESULT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Committed Day 3 comparison result is stale.")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
