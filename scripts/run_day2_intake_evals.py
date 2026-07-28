"""Execute the Day 2 JD-first intake eval cases and print the report.

Usage:

    python3 scripts/run_day2_intake_evals.py [--output PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab.day2_intake_eval import run_all  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write the report as JSON.")
    args = parser.parse_args()

    report = run_all()
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if report["failed_cases"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
