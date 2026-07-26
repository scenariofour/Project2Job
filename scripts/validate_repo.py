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
    "GLOSSARY.md",
    "AI_PM_PRODUCT_AND_INTERVIEW_GATE.md",
    "docs/DOCUMENT_GOVERNANCE.md",
    "docs/00_PRODUCT_NORTH_STAR.md",
    "docs/01_MVP_PRD.md",
    "docs/02_ROLE_BACKWARDS_EVIDENCE_FRAMEWORK.md",
    "docs/03_AI_PM_ROLE_STANDARD.md",
    "docs/05_SKILL_PRODUCT_SPEC.md",
    "docs/06_AGENT_PRODUCT_SPEC.md",
    "schemas/application_pack.schema.json",
    "schemas/jd_intake.schema.json",
    "schemas/interview_context.schema.json",
    "schemas/intake_result.schema.json",
    "schemas/project_evidence.schema.json",
    "schemas/role_profile.schema.json",
    "schemas/gold_case.schema.json",
    "references/source_registry.json",
    "references/role_profiles/ai_pm_early_career.v0.1.0.json",
    "references/shared_contract.v1.json",
    "lab/evals/shared_foundation_cases.v0.1.0.jsonl",
    "lab/REVIEWER_AND_ANNOTATION_GUIDE.md",
    "lab/baseline_prompt.md",
    "skill/career-desk/SKILL.md",
    "lab/evals/skill_cases.jsonl",
    "lab/evals/agent_cases.jsonl",
    "docs/build_journal/README.md",
    "docs/build_journal/IMPLEMENTATION_MAP.md",
    "work_orders/WO-05_JD_FIRST_INTAKE.md",
    "lab/evals/day2_jd_first_cases.jsonl",
    *[f"docs/build_journal/DAY_{day}.md" for day in range(8)],
]

PUBLIC_FIXTURE_ROOTS = [
    "examples",
    "lab/fixtures",
    "skill/career-desk/examples",
]

DAY_STATUSES = ("PLANNED", "IMPLEMENTED", "VALIDATED")
COMPLETED_STATUSES = ("IMPLEMENTED", "VALIDATED")
STATUS_LINE = re.compile(r"^Status: (\S+)$", re.MULTILINE)

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


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def validate_journal_statuses(root: Path = ROOT) -> int:
    """Check Day statuses form a completed prefix and return the highest one.

    Completed Days (IMPLEMENTED or VALIDATED) must come first and without gaps,
    every PLANNED Day must follow them, and PROJECT_STATUS.md must name the same
    highest completed Day. Returns -1 when no Day is complete. Adding a Day
    therefore needs no change here.
    """
    day_paths = []
    for path in (root / "docs/build_journal").glob("DAY_*.md"):
        number = path.stem.removeprefix("DAY_")
        if not number.isdigit():
            raise SystemExit(f"Journal file is not DAY_<number>.md: {path.name}")
        day_paths.append((int(number), path))

    highest_completed = -1
    for day, path in sorted(day_paths):
        found = STATUS_LINE.findall(path.read_text(encoding="utf-8"))
        if len(found) != 1 or found[0] not in DAY_STATUSES:
            raise SystemExit(
                f"Day {day} must have exactly one status line from {DAY_STATUSES}"
            )
        status = found[0]
        if status not in COMPLETED_STATUSES:
            continue
        if day != highest_completed + 1:
            raise SystemExit(
                f"Day {day} is {status} while an earlier Day is missing or PLANNED"
            )
        highest_completed = day

    reported = highest_completed if highest_completed >= 0 else "none"
    expected = f"Highest completed Day: {reported}"
    project_status = (root / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    if not re.search(rf"^{expected}$", project_status, re.MULTILINE):
        raise SystemExit(f"PROJECT_STATUS.md must state '{expected}' on its own line")
    return highest_completed


def iter_refs(node) -> list[str]:
    if isinstance(node, dict):
        found = [node["$ref"]] if isinstance(node.get("$ref"), str) else []
        for value in node.values():
            found.extend(iter_refs(value))
        return found
    if isinstance(node, list):
        return [ref for item in node for ref in iter_refs(item)]
    return []


def validate_schema_refs() -> int:
    """Every $ref must resolve to a local $def or another schema in schemas/.

    Nothing in this repository resolves $ref at runtime, so an unresolvable
    reference would otherwise be an invisible break in a published contract.
    """
    loaded = [
        (path, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted((ROOT / "schemas").glob("*.schema.json"))
    ]
    schemas = {
        schema["$id"]: (path, schema) for path, schema in loaded if "$id" in schema
    }

    checked = 0
    for path, schema in loaded:
        for ref in iter_refs(schema):
            target_id, _, fragment = ref.partition("#")
            target = schema if not target_id else None
            if target_id:
                if target_id not in schemas:
                    raise SystemExit(f"{path.name}: $ref to unknown schema {ref}")
                target = schemas[target_id][1]
            if fragment and fragment != "/":
                node = target
                for part in fragment.strip("/").split("/"):
                    if not isinstance(node, dict) or part not in node:
                        raise SystemExit(f"{path.name}: $ref does not resolve: {ref}")
                    node = node[part]
            checked += 1
    return checked


def validate_shared_foundation() -> dict[str, int]:
    contract = json.loads(
        (ROOT / "references/shared_contract.v1.json").read_text(encoding="utf-8")
    )
    profile_path = ROOT / contract["role_profile"]["path"]
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    registry = json.loads(
        (ROOT / "references/source_registry.json").read_text(encoding="utf-8")
    )
    cases = load_jsonl(ROOT / contract["gold_dataset"]["path"])

    if not re.fullmatch(r"\d+\.\d+\.\d+", contract["version"]):
        raise SystemExit("Shared contract version must be semver")
    history = [entry["version"] for entry in contract["version_history"]]
    if history[-1] != contract["version"]:
        raise SystemExit("Shared contract version is not the latest version_history entry")
    if profile["role_id"] != contract["role_profile"]["role_id"]:
        raise SystemExit("Shared contract role_id does not match role profile")
    if profile["version"] != contract["role_profile"]["version"]:
        raise SystemExit("Shared contract role version does not match role profile")
    if profile["source_registry_version"] != registry["registry_version"]:
        raise SystemExit("Role profile and source registry versions do not match")

    schema_ids = set()
    for name, schema_ref in contract["schemas"].items():
        schema_path = ROOT / schema_ref["path"]
        if not schema_path.exists():
            raise SystemExit(f"Shared schema missing for {name}: {schema_path}")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        if schema.get("$id") != schema_ref["schema_id"]:
            raise SystemExit(f"Shared schema ID mismatch for {name}")
        schema_ids.add(schema_ref["schema_id"])

    registry_by_id = {source["id"]: source for source in registry["sources"]}
    registry_ids = set(registry_by_id)
    if not set(profile["source_ids"]).issubset(registry_ids):
        raise SystemExit("Role profile references an unknown source ID")
    if set(profile["source_ids"]) != set(registry["role_profile_source_ids"]):
        raise SystemExit("Role profile sources do not match registry review scope")
    for source_id in profile["source_ids"]:
        source = registry_by_id[source_id]
        if source.get("status") != "accessible" or not source.get("verified_on"):
            raise SystemExit(f"Role profile source is not verified: {source_id}")

    capability_ids = set()
    evidence_test_ids = set()
    evidence_test_domains = {}
    for capability in profile["capabilities"]:
        capability_id = capability["capability_id"]
        if capability_id in capability_ids:
            raise SystemExit(f"Duplicate capability ID: {capability_id}")
        capability_ids.add(capability_id)
        if not capability["evidence_tests"]:
            raise SystemExit(f"Capability has no evidence tests: {capability_id}")
        if not set(capability["source_ids"]).issubset(registry_ids):
            raise SystemExit(f"Capability references unknown source: {capability_id}")
        for evidence_test in capability["evidence_tests"]:
            test_id = evidence_test["evidence_test_id"]
            if test_id in evidence_test_ids:
                raise SystemExit(f"Duplicate evidence test ID: {test_id}")
            evidence_test_ids.add(test_id)
            evidence_test_domains[test_id] = capability_id

    if len(capability_ids) != 10:
        raise SystemExit(f"Expected 10 capability domains, found {len(capability_ids)}")
    if len(cases) < 10:
        raise SystemExit(f"Expected at least 10 shared gold cases, found {len(cases)}")

    case_ids = set()
    covered_capabilities = set()
    covered_statuses = set()
    for case in cases:
        case_id = case["case_id"]
        if case_id in case_ids:
            raise SystemExit(f"Duplicate shared case ID: {case_id}")
        case_ids.add(case_id)
        if case["dataset_version"] != contract["gold_dataset"]["version"]:
            raise SystemExit(f"Gold dataset version mismatch: {case_id}")
        if case["role_profile_ref"] != {
            "role_id": profile["role_id"],
            "version": profile["version"],
        }:
            raise SystemExit(f"Gold case role profile mismatch: {case_id}")
        if case["capability_id"] not in capability_ids:
            raise SystemExit(f"Gold case capability missing from profile: {case_id}")
        if case["evidence_test_id"] not in evidence_test_ids:
            raise SystemExit(f"Gold case evidence test missing from profile: {case_id}")
        if evidence_test_domains[case["evidence_test_id"]] != case["capability_id"]:
            raise SystemExit(f"Gold case evidence test belongs to another domain: {case_id}")

        source_locations = {
            (source["source_id"], source["location"]) for source in case["sources"]
        }
        label = case["gold_label"]
        if not label["boundary"].strip():
            raise SystemExit(f"Gold case boundary is empty: {case_id}")
        if not label["evidence_refs"]:
            raise SystemExit(f"Gold case has no evidence references: {case_id}")
        for evidence_ref in label["evidence_refs"]:
            key = (evidence_ref["source_id"], evidence_ref["location"])
            if key not in source_locations:
                raise SystemExit(f"Gold evidence location does not resolve: {case_id}")
        if label["resume_export_allowed"]:
            if label["status"] != "supported":
                raise SystemExit(
                    f"Resume export requires supported status: {case_id}"
                )
            if not any(
                evidence_ref["evidence_type"] == "direct"
                for evidence_ref in label["evidence_refs"]
            ):
                raise SystemExit(
                    f"Resume export requires direct evidence: {case_id}"
                )
        covered_capabilities.add(case["capability_id"])
        covered_statuses.add(label["status"])

    if covered_capabilities != capability_ids:
        missing = sorted(capability_ids - covered_capabilities)
        raise SystemExit(f"Capability domains without gold cases: {missing}")
    expected_statuses = {
        "supported",
        "partially_supported",
        "inferred",
        "not_found",
        "conflicting",
        "needs_confirmation",
    }
    if covered_statuses != expected_statuses:
        missing = sorted(expected_statuses - covered_statuses)
        raise SystemExit(f"Evidence statuses without gold cases: {missing}")

    consumers = {item["consumer"]: item for item in contract["consumers"]}
    if set(consumers) != {"skill", "agent"}:
        raise SystemExit("Shared contract must declare exactly Skill and Agent consumers")
    skill_contract = {
        "role_profile_version": consumers["skill"]["role_profile_version"],
        "input_schema_ids": consumers["skill"]["input_schema_ids"],
        "intermediate_schema_id": consumers["skill"]["intermediate_schema_id"],
        "output_schema_id": consumers["skill"]["output_schema_id"],
    }
    agent_contract = {
        "role_profile_version": consumers["agent"]["role_profile_version"],
        "input_schema_ids": consumers["agent"]["input_schema_ids"],
        "intermediate_schema_id": consumers["agent"]["intermediate_schema_id"],
        "output_schema_id": consumers["agent"]["output_schema_id"],
    }
    if skill_contract != agent_contract:
        raise SystemExit("Skill and Agent contract declarations differ")
    if skill_contract["role_profile_version"] != profile["version"]:
        raise SystemExit("Consumer role profile version does not resolve")
    if not set(skill_contract["input_schema_ids"]).issubset(schema_ids):
        raise SystemExit("Consumer input schema ID does not resolve")
    if skill_contract["intermediate_schema_id"] not in schema_ids:
        raise SystemExit("Consumer intermediate schema ID does not resolve")
    if skill_contract["output_schema_id"] not in schema_ids:
        raise SystemExit("Consumer output schema ID does not resolve")

    return {
        "role_capabilities": len(capability_ids),
        "evidence_tests": len(evidence_test_ids),
        "shared_gold_cases": len(cases),
        "evidence_statuses": len(covered_statuses),
        "shared_consumers": len(consumers),
    }


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

    highest_completed_day = validate_journal_statuses()

    public_fixture_files = validate_public_fixtures()
    schema_refs = validate_schema_refs()
    shared_foundation = validate_shared_foundation()

    print(json.dumps({
        "status": "ok",
        "active_documents": len(active),
        "json_files": json_count,
        "jsonl_cases": jsonl_cases,
        "public_fixture_files": public_fixture_files,
        "journal_days": len(list((ROOT / "docs/build_journal").glob("DAY_*.md"))),
        "highest_completed_day": highest_completed_day,
        "schema_refs": schema_refs,
        "license": "MIT",
        "shared_foundation": shared_foundation,
    }, indent=2))


if __name__ == "__main__":
    main()
