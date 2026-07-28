from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_SECTIONS = (
    "verified_facts",
    "ownership",
    "decisions",
    "architecture",
    "results",
    "bad_cases",
    "stories",
    "hiring_signals",
)
COMPANY_SIGNAL_SECTIONS = (
    "culture_and_values",
    "product_and_ai_direction",
    "role_or_team_priorities",
    "interview_signals",
)
CAPABILITY_ROUTES = {
    "brief": "p2j-brief",
    "company_intelligence": "p2j-intel",
    "evidence_audit": "p2j-audit",
    "interview_answer": "p2j-answer",
    "mock_interview": "p2j-mock",
    "project_upgrade": "p2j-upgrade",
}
ASSET_REQUESTS = {
    "project_highlights",
    "project_introduction",
    "resume_bullets",
}
PROJECT_PROFILE_REQUESTS = {
    *ASSET_REQUESTS,
    "full_preparation",
    "interview_answer",
    "mock_interview",
    "project_upgrade",
}
COMPANY_ADAPTED_REQUESTS = {
    *ASSET_REQUESTS,
    "company_intelligence",
    "full_preparation",
    "interview_answer",
    "mock_interview",
}
JD_REQUESTS = {
    *ASSET_REQUESTS,
    "brief",
    "company_intelligence",
    "evidence_audit",
    "full_preparation",
    "interview_answer",
    "mock_interview",
    "project_upgrade",
}
FULL_PREPARATION_SKILLS = [
    "p2j-brief",
    "p2j-intel",
    "p2j-audit",
    "p2j-answer",
    "p2j-mock",
    "p2j-upgrade",
]
IMPROVEMENT_STORY_FIELDS = (
    "early_signal_or_constraint",
    "diagnosis",
    "deliberate_decision",
    "system_or_product_change",
    "stronger_result",
    "target_hiring_signal",
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Profile timestamps must include a timezone.")
    return parsed


def company_profile_key(company: str, track: str) -> str:
    normalized = " ".join(f"{company}::{track}".lower().split())
    return normalized


def require_fields(value: dict, fields: set[str], label: str) -> None:
    missing = sorted(fields - value.keys())
    if missing:
        raise ValueError(f"{label} is missing: {', '.join(missing)}")


def validate_project_profile(profile: dict) -> None:
    require_fields(
        profile,
        {
            "schema_version",
            "profile_id",
            "project_fingerprint",
            "built_at",
            "sections",
        },
        "Project Evidence Profile",
    )
    if profile["schema_version"] != "1.0.0":
        raise ValueError("Unsupported Project Evidence Profile version.")
    if len(profile["project_fingerprint"]) != 64:
        raise ValueError("Project Evidence Profile needs a SHA-256 fingerprint.")
    parse_time(profile["built_at"])
    sections = profile["sections"]
    if not isinstance(sections, dict) or set(sections) != set(PROJECT_SECTIONS):
        raise ValueError("Project Evidence Profile sections do not match the contract.")
    for name, section in sections.items():
        require_fields(section, {"items", "source_paths"}, f"Project section {name}")
        if not isinstance(section["items"], list) or not isinstance(
            section["source_paths"], list
        ):
            raise ValueError(f"Project section {name} must use bounded arrays.")


def validate_company_profile(profile: dict) -> None:
    require_fields(
        profile,
        {
            "schema_version",
            "profile_key",
            "company",
            "track",
            "researched_at",
            "fresh_until",
            "source_fingerprint",
            "signals",
            "sources",
        },
        "Company Intelligence Profile",
    )
    if profile["schema_version"] != "1.0.0":
        raise ValueError("Unsupported Company Intelligence Profile version.")
    if profile["profile_key"] != company_profile_key(
        profile["company"], profile["track"]
    ):
        raise ValueError("Company Intelligence Profile key does not match company/track.")
    parse_time(profile["researched_at"])
    parse_time(profile["fresh_until"])
    if len(profile["source_fingerprint"]) != 64:
        raise ValueError("Company Intelligence Profile needs a source fingerprint.")
    signals = profile["signals"]
    if not isinstance(signals, dict) or set(signals) != set(COMPANY_SIGNAL_SECTIONS):
        raise ValueError("Company Intelligence Profile signals do not match the contract.")
    if not all(isinstance(value, list) for value in signals.values()):
        raise ValueError("Company Intelligence Profile signals must be arrays.")
    if not isinstance(profile["sources"], list):
        raise ValueError("Company Intelligence Profile sources must be an array.")


def validate_jd_demand_map(profile: dict) -> None:
    require_fields(
        profile,
        {
            "schema_version",
            "map_id",
            "jd_fingerprint",
            "company_profile_key",
            "extracted_at",
            "role_tasks",
            "level",
            "hiring_signals",
            "must_haves",
            "preferred_qualifications",
        },
        "JD Demand Map",
    )
    if profile["schema_version"] != "1.0.0":
        raise ValueError("Unsupported JD Demand Map version.")
    if len(profile["jd_fingerprint"]) != 64:
        raise ValueError("JD Demand Map needs a SHA-256 fingerprint.")
    parse_time(profile["extracted_at"])
    for field in (
        "role_tasks",
        "hiring_signals",
        "must_haves",
        "preferred_qualifications",
    ):
        if not isinstance(profile[field], list):
            raise ValueError(f"JD Demand Map {field} must be an array.")


def profile_states(
    project_profile: dict | None,
    company_profile: dict | None,
    jd_demand_map: dict | None,
    now: datetime,
) -> dict[str, str]:
    states = {
        "project_evidence": "miss",
        "company_intelligence": "miss",
        "jd_demand": "miss",
    }
    if project_profile is not None:
        validate_project_profile(project_profile)
        states["project_evidence"] = "hit"
    if company_profile is not None:
        validate_company_profile(company_profile)
        states["company_intelligence"] = (
            "hit"
            if parse_time(company_profile["fresh_until"]) >= now
            else "stale"
        )
    if jd_demand_map is not None:
        validate_jd_demand_map(jd_demand_map)
        states["jd_demand"] = "hit"
    return states


def add_once(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def plan_request(
    request: str,
    *,
    project_profile: dict | None,
    company_profile: dict | None,
    jd_demand_map: dict | None,
    now: datetime | None = None,
    material_questions: list[str] | None = None,
    company_materially_changed: bool = False,
    affected_project_sections: list[str] | None = None,
) -> dict:
    supported = (
        set(CAPABILITY_ROUTES)
        | ASSET_REQUESTS
        | {"full_preparation"}
    )
    if request not in supported:
        raise ValueError(f"Unsupported Project2Job request: {request}")
    observed_at = now or utc_now()
    states = profile_states(
        project_profile, company_profile, jd_demand_map, observed_at
    )
    if company_materially_changed and company_profile is not None:
        states["company_intelligence"] = "stale"
    if affected_project_sections is not None and project_profile is not None:
        states["project_evidence"] = "partial"
    skills: list[str] = []
    model_tasks: list[str] = []
    deterministic_tasks: list[str] = []
    assets: list[str] = []

    if request == "full_preparation":
        skills = list(FULL_PREPARATION_SKILLS)
        if states["project_evidence"] == "hit":
            skills.remove("p2j-audit")
        if states["company_intelligence"] == "hit":
            skills.remove("p2j-intel")
        assets = [
            "role_fit_map",
            "project_highlights",
            "resume_bullets",
            "interview_prep_pack",
            "one_next_build",
        ]
    elif request in CAPABILITY_ROUTES:
        add_once(skills, CAPABILITY_ROUTES[request])
    else:
        assets = [request]

    if (
        request in PROJECT_PROFILE_REQUESTS
        and states["project_evidence"] != "hit"
    ):
        add_once(skills, "p2j-audit")
        if states["project_evidence"] == "partial":
            deterministic_tasks.append("open_changed_project_artifacts_only")
            model_tasks.append("update_affected_project_profile_sections")
        else:
            deterministic_tasks.append("inventory_changed_project_artifacts")
            model_tasks.append("build_project_evidence_profile")
    if (
        request in COMPANY_ADAPTED_REQUESTS
        and states["company_intelligence"] != "hit"
    ):
        add_once(skills, "p2j-intel")
        deterministic_tasks.append("check_company_profile_freshness")
        model_tasks.append("build_or_refresh_company_intelligence_profile")
    if request in JD_REQUESTS and states["jd_demand"] != "hit":
        deterministic_tasks.append("fingerprint_jd")
        model_tasks.append("extract_lightweight_jd_demand_map")
    if assets or request in {"interview_answer", "mock_interview", "full_preparation"}:
        model_tasks.extend(
            [
                "select_one_strongest_story",
                "adapt_to_company_culture_and_jd",
                "translate_to_product_user_business_and_ai_pm_value",
            ]
        )

    questions = [
        question
        for question in (material_questions or [])
        if isinstance(question, str) and question.strip()
    ][:1]
    return {
        "request": request,
        "mode": (
            "full_preparation" if request == "full_preparation" else "selective"
        ),
        "profile_states": states,
        "skill_invocations": skills,
        "deterministic_tasks": list(dict.fromkeys(deterministic_tasks)),
        "model_tasks": list(dict.fromkeys(model_tasks)),
        "asset_generation": assets,
        "strategy_inputs": {
            "project_profile_id": (
                project_profile.get("profile_id") if project_profile else None
            ),
            "company_profile_key": (
                company_profile.get("profile_key") if company_profile else None
            ),
            "jd_map_id": jd_demand_map.get("map_id") if jd_demand_map else None,
        },
        "questions": questions,
        "affected_project_sections": affected_project_sections or [],
    }


def private_strings(value: object) -> list[str]:
    if isinstance(value, dict):
        return [
            item
            for nested in value.values()
            for item in private_strings(nested)
        ]
    if isinstance(value, list):
        return [item for nested in value for item in private_strings(nested)]
    return [value.strip()] if isinstance(value, str) and value.strip() else []


def validate_external_asset(asset: dict, allowed_fact_ids: set[str]) -> list[str]:
    errors: list[str] = []
    copyable = asset.get("copyable")
    fact_ids = asset.get("fact_ids")
    if not isinstance(copyable, str) or not copyable.strip():
        errors.append("copyable asset is missing")
    if not isinstance(fact_ids, list) or not all(
        isinstance(value, str) for value in fact_ids
    ):
        errors.append("copyable asset fact_ids are invalid")
        fact_ids = []
    if not set(fact_ids).issubset(allowed_fact_ids):
        errors.append("copyable asset references unsupported fact IDs")
    lowered = copyable.lower() if isinstance(copyable, str) else ""
    for heading in (
        "weaknesses:",
        "caveats:",
        "missing validation:",
        "risk warnings:",
    ):
        if heading in lowered:
            errors.append("weakness or caveat list leaked into copyable asset")
            break
    for value in private_strings(asset.get("private_defense", {})):
        if value.lower() in lowered:
            errors.append("private defense leaked into copyable asset")
            break
    return errors


def validate_improvement_story(story: dict) -> list[str]:
    errors = []
    for field in IMPROVEMENT_STORY_FIELDS:
        if not isinstance(story.get(field), str) or not story[field].strip():
            errors.append(f"missing {field}")
    return errors


def usage_report(
    *,
    files_opened: list[str],
    model_calls: int,
    input_tokens: int,
    cached_input_tokens: int,
    output_tokens: int,
    skill_invocations: list[str],
) -> dict:
    numeric = {
        "model_calls": model_calls,
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "output_tokens": output_tokens,
    }
    if any(not isinstance(value, int) or value < 0 for value in numeric.values()):
        raise ValueError("Usage counters must be non-negative integers.")
    if cached_input_tokens > input_tokens:
        raise ValueError("Cached input tokens cannot exceed input tokens.")
    if not all(isinstance(value, str) for value in files_opened):
        raise ValueError("Opened file paths must be strings.")
    if not all(isinstance(value, str) for value in skill_invocations):
        raise ValueError("Skill invocations must be strings.")
    return {
        "files_opened": list(dict.fromkeys(files_opened)),
        "model_calls": model_calls,
        "skill_invocations": list(skill_invocations),
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "uncached_input_tokens": input_tokens - cached_input_tokens,
        "output_tokens": output_tokens,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan one selective Project2Job Skill Suite request."
    )
    parser.add_argument("request")
    parser.add_argument("--profiles", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.profiles.read_text(encoding="utf-8"))
    plan = plan_request(
        args.request,
        project_profile=payload.get("project_evidence_profile"),
        company_profile=payload.get("company_intelligence_profile"),
        jd_demand_map=payload.get("jd_demand_map"),
        material_questions=payload.get("material_questions"),
        company_materially_changed=payload.get(
            "company_materially_changed", False
        ),
        affected_project_sections=payload.get("affected_project_sections"),
    )
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
