from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "LICENSE",
    "README.md",
    "START_HERE.md",
    "AGENTS.md",
    "ACTIVE_SCOPE.md",
    "PROJECT_MANIFEST.json",
    "PROJECT_STATUS.md",
    "AI_PM_PRODUCT_AND_INTERVIEW_GATE.md",
    "docs/00_PRODUCT_NORTH_STAR.md",
    "docs/01_MVP_PRD.md",
    "docs/02_ROLE_BACKWARDS_EVIDENCE_FRAMEWORK.md",
    "docs/03_AI_PM_ROLE_STANDARD.md",
    "docs/05_SKILL_PRODUCT_SPEC.md",
    "docs/06_AGENT_PRODUCT_SPEC.md",
    "schemas/application_pack.schema.json",
    "skill/career-desk/SKILL.md",
    "lab/evals/skill_cases.jsonl",
    "lab/evals/agent_cases.jsonl",
    "docs/build_journal/README.md",
    "docs/build_journal/IMPLEMENTATION_MAP.md",
    *[f"docs/build_journal/DAY_{day}.md" for day in range(8)],
]

PUBLIC_FIXTURE_ROOTS = [
    "examples",
    "lab/fixtures",
    "skill/career-desk/examples",
]

PRIVATE_PATTERNS = {
    "email address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "macOS local path": re.compile(r"/Users/[^/\s]+/"),
    "Linux local path": re.compile(r"/home/[^/\s]+/"),
}


def validate_json(path: Path) -> None:
    json.loads(path.read_text(encoding="utf-8"))


def validate_jsonl(path: Path) -> int:
    count = 0
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: {exc}") from exc
        count += 1
    return count


def validate_public_fixtures() -> int:
    checked = 0
    for relative_root in PUBLIC_FIXTURE_ROOTS:
        for path in (ROOT / relative_root).rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            for label, pattern in PRIVATE_PATTERNS.items():
                if pattern.search(text):
                    raise SystemExit(f"Public fixture contains {label}: {path}")
            checked += 1
    return checked


def main() -> None:
    missing = [item for item in REQUIRED if not (ROOT / item).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if not license_text.startswith("MIT License\n"):
        raise SystemExit("LICENSE is not the expected MIT License")

    manifest = json.loads((ROOT / "PROJECT_MANIFEST.json").read_text(encoding="utf-8"))
    active = manifest["active_documents"]
    if manifest["active_document_count"] != len(active):
        raise SystemExit("Manifest active_document_count does not match active_documents")
    if len(active) > 15:
        raise SystemExit(f"Too many active documents: {len(active)}")
    for item in active:
        if not (ROOT / item).exists():
            raise SystemExit(f"Active document missing: {item}")

    json_count = 0
    jsonl_cases = 0
    for path in ROOT.rglob("*.json"):
        validate_json(path)
        json_count += 1
    for path in ROOT.rglob("*.jsonl"):
        jsonl_cases += validate_jsonl(path)

    day_0 = (ROOT / "docs/build_journal/DAY_0.md").read_text(encoding="utf-8")
    if "Status: IMPLEMENTED" not in day_0:
        raise SystemExit("Day 0 must be IMPLEMENTED before foundation validation passes")
    for day in range(1, 8):
        path = ROOT / f"docs/build_journal/DAY_{day}.md"
        if "Status: PLANNED" not in path.read_text(encoding="utf-8"):
            raise SystemExit(f"Day {day} must remain PLANNED on Day 0")

    public_fixture_files = validate_public_fixtures()

    print(json.dumps({
        "status": "ok",
        "active_documents": len(active),
        "json_files": json_count,
        "jsonl_cases": jsonl_cases,
        "public_fixture_files": public_fixture_files,
        "journal_days": 8,
        "license": "MIT",
    }, indent=2))


if __name__ == "__main__":
    main()
