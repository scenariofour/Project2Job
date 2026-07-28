"""Regenerate the committed Day 2 JD-first dogfood artifact.

The dogfood runs the intake over the repository's own committed fixtures: one
JD that never states a company, and a resume assembled from the four project
fixtures plus the prompt-injection fixture. Nothing is invented for it, so the
result is reproducible and the artifact can be pinned by a test.

    python3 scripts/build_day2_dogfood.py [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.career_desk.jd_intake import cross_reference_errors, run_intake  # noqa: E402

ARTIFACT = ROOT / "docs/build_journal/traces/day2_jd_first_dogfood.json"
JD_FIXTURE = ROOT / "lab/fixtures/fixture_ai_pm_jd.md"
RUN_DATE = date(2026, 7, 27)

#: One resume bullet per committed project fixture, using that fixture's own
#: words. The injection fixture is included to check that its text routes
#: nothing: it is candidate material, not an instruction.
RESUME_FIXTURES = [
    ("Agent Project", "lab/fixtures/fixture_project_plan_only.md"),
    ("AI Agent", "lab/fixtures/fixture_project_with_code_no_users.md"),
    ("Team Project", "lab/fixtures/fixture_team_project.md"),
    ("Career Evidence Agent", "lab/fixtures/fixture_project_without_jd.md"),
    ("Injection Fixture", "lab/fixtures/fixture_prompt_injection.md"),
]


def resume_text() -> str:
    lines = ["Projects:"]
    for name, relative in RESUME_FIXTURES:
        body = (ROOT / relative).read_text(encoding="utf-8").splitlines()
        prose = " ".join(
            line.strip()
            for line in body
            if line.strip() and not line.startswith("#")
        )
        lines.append(f"- {name}: {prose}")
    return "\n".join(lines)


def build() -> dict:
    result = run_intake(
        JD_FIXTURE.read_text(encoding="utf-8"),
        resume_text=resume_text(),
        jd_reference=str(JD_FIXTURE.relative_to(ROOT)),
        today=RUN_DATE,
    )
    return {
        "run_date": RUN_DATE.isoformat(),
        "jd_fixture": str(JD_FIXTURE.relative_to(ROOT)),
        "resume_fixtures": [relative for _, relative in RESUME_FIXTURES],
        "research_mode": result["interview_context"]["research"]["mode"],
        "cross_reference_errors": cross_reference_errors(result),
        "intake_result": result,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare with the committed artifact instead of rewriting it.",
    )
    args = parser.parse_args()

    payload = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        current = ARTIFACT.read_text(encoding="utf-8")
        print("MATCH" if current == payload else "DIFFERS")
        raise SystemExit(0 if current == payload else 1)
    ARTIFACT.write_text(payload, encoding="utf-8")
    print(f"Wrote {ARTIFACT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
