from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "ACTIVE_SCOPE.md",
    "PROJECT_MANIFEST.json",
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
]

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

def main() -> None:
    missing = [item for item in REQUIRED if not (ROOT / item).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    manifest = json.loads((ROOT / "PROJECT_MANIFEST.json").read_text(encoding="utf-8"))
    active = manifest["active_documents"]
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

    print(json.dumps({
        "status": "ok",
        "active_documents": len(active),
        "json_files": json_count,
        "jsonl_cases": jsonl_cases,
    }, indent=2))

if __name__ == "__main__":
    main()
