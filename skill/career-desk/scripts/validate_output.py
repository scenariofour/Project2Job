from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = {
    "run_type",
    "intent",
    "role_fit_map",
    "project_highlights",
    "resume_bullets",
    "interview_pack",
    "next_build",
    "warnings",
}

def validate(data: dict) -> list[str]:
    errors = []
    missing = sorted(REQUIRED - data.keys())
    if missing:
        errors.append(f"Missing fields: {', '.join(missing)}")
    if len(data.get("resume_bullets", [])) > 3:
        errors.append("No more than 3 resume bullets are allowed.")
    for index, bullet in enumerate(data.get("resume_bullets", []), start=1):
        if not bullet.get("source_refs"):
            errors.append(f"Resume bullet {index} has no source references.")
    next_build = data.get("next_build", {})
    for field in ("gap", "why_now", "steps", "acceptance_criteria", "expected_evidence"):
        if field not in next_build:
            errors.append(f"Next Build missing: {field}")
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: validate_output.py output.json")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        raise SystemExit(1)
    print(json.dumps({"valid": True}, indent=2))
