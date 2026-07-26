from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SKILLS = (
    "p2j",
    "p2j-brief",
    "p2j-audit",
    "p2j-intel",
    "p2j-answer",
    "p2j-mock",
    "p2j-upgrade",
)
SHARED_REFERENCES = (
    "core-contract.md",
    "context-registry.md",
    "gates.md",
    "interview-engine.md",
    "frameworks.md",
)
REQUIRED_BEHAVIOR_CASES = {
    "A01_BRIEF",
    "A02_SIX_GATES",
    "A03_AB_TEST",
    "A04_TECHNICAL",
    "A05_COMPANY_INTEL",
    "A06_NA",
    "A07_README_CAP",
    "A08_OWNERSHIP",
    "A09_STALE_CONFLICT",
    "A10_WEB_INJECTION",
    "A11_NO_EVENT",
    "A12_NEXT_BUILD",
    "A13_MOCK_LABEL",
    "A14_ROUTER_OUTPUTS",
    "A15_BRIEF_MATCH",
    "A16_BRIEF_STORIES",
    "A17_CONTEXT_REUSE",
    "A18_CONTEXT_CHANGE",
    "A19_CONTEXT_CONTROLS",
    "A20_CONTEXT_SAFETY",
}


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def validate(root: Path, require_canonical: bool = False) -> list[str]:
    errors: list[str] = []
    for name in SKILLS:
        skill_dir = root / name
        skill_file = skill_dir / "SKILL.md"
        agent_file = skill_dir / "agents" / "openai.yaml"
        if not skill_file.is_file():
            errors.append(f"{name}: missing SKILL.md")
            continue
        text = skill_file.read_text(encoding="utf-8")
        metadata = frontmatter(text)
        if metadata.get("name") != name:
            errors.append(f"{name}: frontmatter name mismatch")
        if not metadata.get("description"):
            errors.append(f"{name}: missing description")
        if "TODO" in text:
            errors.append(f"{name}: unresolved TODO")
        if len(text.splitlines()) >= 500:
            errors.append(f"{name}: SKILL.md must stay below 500 lines")
        if not agent_file.is_file():
            errors.append(f"{name}: missing agents/openai.yaml")
        else:
            agent_text = agent_file.read_text(encoding="utf-8")
            if f"$%s" % name not in agent_text:
                errors.append(f"{name}: default_prompt does not name ${name}")

    reference_root = root / "p2j" / "references"
    for name in SHARED_REFERENCES:
        if not (reference_root / name).is_file():
            errors.append(f"p2j: missing shared reference {name}")
    for name in (
        "context_registry.py",
        "inventory.py",
        "install_suite.py",
        "stateful_agent.py",
        "validate_output.py",
    ):
        if not (root / "p2j" / "scripts" / name).is_file():
            errors.append(f"p2j: missing script {name}")
    runtime = root / "p2j" / "scripts" / "career_desk"
    if runtime.exists():
        for name in ("capabilities.py", "orchestrator.py", "runtime.py"):
            if not (runtime / name).is_file():
                errors.append(f"p2j: missing bundled runtime {name}")
    for name in ("sample_jd.md", "sample_project.md", "sample_brief.md"):
        if not (root / "p2j" / "examples" / name).is_file():
            errors.append(f"p2j: missing example {name}")

    gate_text = (
        (reference_root / "gates.md").read_text(encoding="utf-8")
        if (reference_root / "gates.md").is_file()
        else ""
    )
    for required in (
        "D1 User and Problem Definition",
        "D10 Communication and Ownership",
        "README-only or self-reported claim",
        "lowest applicable domain score",
        "`N/A`",
    ):
        if required not in gate_text:
            errors.append(f"gates.md: missing {required}")

    engine_text = (
        (reference_root / "interview-engine.md").read_text(encoding="utf-8")
        if (reference_root / "interview-engine.md").is_file()
        else ""
    )
    for required in (
        "Direct Experience",
        "Analogous Experience",
        "Proposed Development-Stage",
        "Project Counterfactual",
        "Technical Concept Applied",
        "Company-Specific Reframing",
        "True No-Direct-Experience",
        "60–90-second",
    ):
        if required not in engine_text:
            errors.append(f"interview-engine.md: missing {required}")

    behavior_path = root / "p2j" / "evals" / "behavior_cases.jsonl"
    if not behavior_path.is_file():
        errors.append("p2j: missing behavior evals")
    else:
        cases = {
            json.loads(line)["id"]
            for line in behavior_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        missing = REQUIRED_BEHAVIOR_CASES - cases
        if missing:
            errors.append(f"p2j: missing behavior cases {sorted(missing)}")

    if require_canonical:
        canonical = reference_root / "canonical"
        for relative in (
            "ACTIVE_SCOPE.md",
            "references/role_profiles/ai_pm_early_career.v0.1.0.json",
            "schemas/application_pack.schema.json",
            "schemas/agent_state.schema.json",
            "schemas/agent_trace.schema.json",
            "schemas/context_registry.schema.json",
            "schemas/interview_context.schema.json",
        ):
            if not (canonical / relative).is_file():
                errors.append(f"installed suite missing canonical/{relative}")
        contract_path = canonical / "references/shared_contract.v1.json"
        if contract_path.is_file():
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            referenced = [
                contract["role_profile"]["path"],
                contract["gold_dataset"]["path"],
                *(
                    item["path"]
                    for item in contract["schemas"].values()
                ),
            ]
            for relative in referenced:
                if not (canonical / relative).is_file():
                    errors.append(
                        f"installed suite missing shared-contract path {relative}"
                    )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Project2Job Skill Suite.")
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Directory containing the seven Skill folders.",
    )
    parser.add_argument("--require-canonical", action="store_true")
    args = parser.parse_args()
    errors = validate(args.root.resolve(), args.require_canonical)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
