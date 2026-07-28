"""Deterministic checks and review artifacts for the Day 5 evaluation package."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "lab" / "day5"
RESULT_PATH = PACKAGE / "results.json"
BAD_CASE_PATH = PACKAGE / "bad_cases.jsonl"
BLIND_PACKET_PATH = PACKAGE / "blind_review_packet.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _export_claim_text(output: dict[str, Any]) -> str:
    texts = [item["text"] for item in output["project_highlights"]]
    texts.extend(item["text"] for item in output["resume_bullets"])
    return "\n".join(texts)


def _resolve_key_source(case: dict[str, Any], output: dict[str, Any]) -> bool:
    """Resolve at least one key-highlight citation to the expected source phrase."""
    source_path = ROOT / case["input"]["project"]
    lines = source_path.read_text(encoding="utf-8").splitlines()
    phrase = case["gold"]["key_source_phrase"].casefold()

    for highlight in output["project_highlights"]:
        if phrase not in highlight["text"].casefold():
            continue
        for ref in highlight["source_refs"]:
            location = ref["location"]
            match = re.search(r"(?:line(?:s)?\s+|:)(\d+)(?:-(\d+))?", location)
            if match:
                start = int(match.group(1))
                end = int(match.group(2) or start)
                excerpt = "\n".join(lines[start - 1 : end])
                if phrase in excerpt.casefold():
                    return True
            if "sentence 1" in location.casefold():
                body = " ".join(line.strip() for line in lines if line.strip() and not line.startswith("#"))
                first_sentence = body.split(".", 1)[0]
                if phrase in first_sentence.casefold():
                    return True
    return False


def _case_checks(case: dict[str, Any], output: dict[str, Any]) -> list[dict[str, Any]]:
    gold = case["gold"]
    statuses = {item["status"] for item in output["role_fit_map"]}
    export_text = _export_claim_text(output).casefold()
    next_build_text = json.dumps(output["next_build"]).casefold()

    checks = [
        {
            "check": "canonical_output_shape",
            "passed": (
                output.get("schema_version") == "2.0.0"
                and 5 <= len(output.get("role_fit_map", [])) <= 7
                and len(output.get("interview_pack", {}).get("answer_drafts", [])) == 3
            ),
            "severe": True,
        },
        {
            "check": "expected_evidence_statuses_present",
            "passed": set(gold["expected_statuses"]).issubset(statuses),
            "severe": True,
        },
        {
            "check": "unsupported_resume_export_blocked",
            "passed": len(output["resume_bullets"]) == gold["expected_resume_bullet_count"],
            "severe": True,
        },
        {
            "check": "answer_claim_safety_gate_closed",
            "passed": all(
                not draft["claim_safety_review"]["exceeds_evidence"]
                for draft in output["interview_pack"]["answer_drafts"]
            ),
            "severe": True,
        },
        {
            "check": "forbidden_external_claim_absent",
            "passed": not any(
                phrase.casefold() in export_text
                for phrase in gold["forbidden_export_phrases"]
            ),
            "severe": True,
        },
        {
            "check": "key_source_location_resolves",
            "passed": _resolve_key_source(case, output),
            "severe": True,
        },
        {
            "check": "one_next_build_targets_gold_gap",
            "passed": all(
                term.casefold() in next_build_text for term in gold["next_build_terms"]
            ),
            "severe": False,
        },
    ]
    return checks


def _agent_checks() -> list[dict[str, Any]]:
    comparison = load_json(
        ROOT / "docs" / "dogfood" / "STATEFUL_AGENT_V0_COMPARISON.json"
    )
    stateful = comparison["stateful_agent_update"]
    fresh = comparison["fresh_skill_rerun"]
    limitations = " ".join(comparison["limitations"]).casefold()
    return [
        {
            "check": "expected_final_values_match",
            "passed": (
                stateful["expected_final_values_matched"] == 2
                and fresh["expected_final_values_matched"] == 2
            ),
            "severe": True,
        },
        {
            "check": "no_unrelated_output_changed",
            "passed": (
                stateful["unrelated_outputs_changed"] == 0
                and fresh["unrelated_outputs_changed"] == 0
            ),
            "severe": True,
        },
        {
            "check": "token_unavailability_visible",
            "passed": (
                stateful["token_usage"] is None
                and fresh["token_usage"] is None
                and "token usage is unavailable" in limitations
            ),
            "severe": True,
        },
        {
            "check": "agent_superiority_not_claimed",
            "passed": (
                "not an independent quality comparison" in limitations
                and "not target-user validation" in limitations
            ),
            "severe": True,
        },
    ]


def build_results() -> dict[str, Any]:
    cases = load_jsonl(PACKAGE / "cases.jsonl")
    manifest = load_json(PACKAGE / "capture_manifest.json")
    runs_by_case: dict[str, list[dict[str, Any]]] = {}
    for run in manifest["runs"]:
        runs_by_case.setdefault(run["case_id"], []).append(run)

    case_results = []
    severe_errors = []
    for case in cases[:3]:
        systems = []
        for run in sorted(runs_by_case[case["case_id"]], key=lambda item: item["system"]):
            output_path = ROOT / run["output"]
            checks = _case_checks(case, load_json(output_path))
            systems.append(
                {
                    "system": run["system"],
                    "output": run["output"],
                    "output_sha256": sha256(output_path),
                    "schema_valid_at_capture": run["schema_validation"]["valid"],
                    "checks": checks,
                }
            )
            for check in checks:
                if check["severe"] and not check["passed"]:
                    severe_errors.append(
                        {
                            "case_id": case["case_id"],
                            "system": run["system"],
                            "check": check["check"],
                        }
                    )
        case_results.append(
            {
                "case_id": case["case_id"],
                "source_case_id": case["source_case_id"],
                "systems": systems,
            }
        )

    agent_checks = _agent_checks()
    for check in agent_checks:
        if check["severe"] and not check["passed"]:
            severe_errors.append(
                {"case_id": "D5-004", "system": "agent_comparison", "check": check["check"]}
            )

    token_totals: dict[str, dict[str, int]] = {}
    observed_runtime: dict[str, dict[str, Any]] = {}
    for system in ("baseline", "skill"):
        runs = [run for run in manifest["runs"] if run["system"] == system]
        token_totals[system] = {
            key: sum(run["usage"][key] for run in runs)
            for key in (
                "input_tokens",
                "cached_input_tokens",
                "cache_write_input_tokens",
                "output_tokens",
                "reasoning_output_tokens",
            )
        }
        measured = [
            run["runtime_seconds"] for run in runs if run["runtime_seconds"] is not None
        ]
        observed_runtime[system] = {
            "observed_runs": len(measured),
            "total_runs": len(runs),
            "observed_wall_seconds_total": round(sum(measured), 2),
            "not_comparable_as_complete_set": len(measured) != len(runs),
        }

    return {
        "package_version": manifest["package_version"],
        "status": "pending_human_review",
        "comparison": "strong_generic_prompt_vs_project2job_skill",
        "reused_artifacts": manifest["reused_artifacts"],
        "case_results": case_results,
        "agent_comparison": {
            "source": "docs/dogfood/STATEFUL_AGENT_V0_COMPARISON.json",
            "checks": agent_checks,
        },
        "severe_errors": severe_errors,
        "automated_gate_passed": not severe_errors,
        "measurements": {
            "tokens": token_totals,
            "runtime": observed_runtime,
            "provider_cost": None,
            "provider_cost_note": "The host exposed no provider price or billed cost.",
        },
        "human_results": {
            "scores": None,
            "preference": None,
            "reviewer_disagreement": None,
            "target_user_feedback": None,
            "product_value": None,
        },
    }


def build_bad_cases() -> list[dict[str, Any]]:
    results = build_results()
    bad_cases = [
        {
            "bad_case_id": f"BC-{index:03d}",
            "case_id": error["case_id"],
            "system": error["system"],
            "severity": "severe",
            "category": error["check"],
            "status": "open",
            "evidence": error,
            "average_override": True,
        }
        for index, error in enumerate(results["severe_errors"], start=1)
    ]
    next_id = len(bad_cases) + 1
    bad_cases.extend(
        [
            {
                "bad_case_id": f"BC-{next_id:03d}",
                "case_id": "D5-002",
                "system": "both",
                "severity": "pending_human_review",
                "category": "first_person_team_affiliation",
                "status": "needs_adjudication",
                "evidence": "Both outputs use first-person team framing while individual ownership remains unconfirmed.",
                "average_override": True,
            },
            {
                "bad_case_id": f"BC-{next_id + 1:03d}",
                "case_id": "measurement",
                "system": "baseline",
                "severity": "measurement_limitation",
                "category": "skill_catalog_isolation",
                "status": "open",
                "evidence": load_json(PACKAGE / "capture_manifest.json")["baseline"][
                    "isolation_limitation"
                ],
                "average_override": False,
            },
            {
                "bad_case_id": f"BC-{next_id + 2:03d}",
                "case_id": "D5-001",
                "system": "baseline",
                "severity": "measurement_limitation",
                "category": "runtime_not_instrumented",
                "status": "open",
                "evidence": "The first baseline wall time is unavailable and is not backfilled.",
                "average_override": False,
            },
        ]
    )
    return bad_cases


def _review_projection(output: dict[str, Any]) -> dict[str, Any]:
    return {
        "role_fit_map": output["role_fit_map"],
        "project_highlights": output["project_highlights"],
        "resume_bullets": output["resume_bullets"],
        "intro_30_seconds": output["interview_pack"]["intro_30_seconds"],
        "answer_drafts": [
            {
                "question": draft["question"],
                "verified_evidence": draft["verified_evidence"],
                "answer_ingredients": draft["answer_ingredients"],
                "grounded_draft": draft["grounded_draft"],
                "claim_safety_review": draft["claim_safety_review"],
                "likely_followups": draft["likely_followups"],
            }
            for draft in output["interview_pack"]["answer_drafts"]
        ],
        "next_build": output["next_build"],
        "warnings": output["warnings"],
    }


def build_blind_packet() -> str:
    cases = {case["case_id"]: case for case in load_jsonl(PACKAGE / "cases.jsonl")}
    manifest = load_json(PACKAGE / "capture_manifest.json")
    runs = {
        (run["case_id"], run["system"]): load_json(ROOT / run["output"])
        for run in manifest["runs"]
    }
    sections = [
        "# Day 5 Blind Human Review Packet",
        "",
        "Review only this packet. Do not open `capture_manifest.json`, which contains the label key.",
        "Score each output 0–3 using `lab/scoring_rubric.md`. A severe fabricated",
        "external-facing claim fails the output regardless of its other scores.",
        "Record two independent reviews in copies of `human_review.template.jsonl`.",
        "Adjudicate a score delta greater than 1 or any severe-error disagreement",
        "with `reviewer_disagreement.template.jsonl`.",
    ]
    for case_id in ("D5-001", "D5-002", "D5-003"):
        case = cases[case_id]
        sections.extend(
            [
                "",
                f"## {case_id}: {case['name']}",
                "",
                "### Project input",
                "",
                "```text",
                (ROOT / case["input"]["project"]).read_text(encoding="utf-8").rstrip(),
                "```",
                "",
                "### Target JD",
                "",
                "```text",
                (ROOT / case["input"]["jd"]).read_text(encoding="utf-8").rstrip(),
                "```",
            ]
        )
        for label in ("A", "B"):
            system = manifest["blind_labels"][case_id][label]
            projection = _review_projection(runs[(case_id, system)])
            sections.extend(
                [
                    "",
                    f"### Output {label}",
                    "",
                    "```json",
                    json.dumps(projection, indent=2, ensure_ascii=False),
                    "```",
                ]
            )
    sections.append("")
    return "\n".join(sections)


def serialized_results() -> str:
    return json.dumps(build_results(), indent=2, ensure_ascii=False) + "\n"


def serialized_bad_cases() -> str:
    return "".join(
        json.dumps(item, ensure_ascii=False) + "\n" for item in build_bad_cases()
    )


def check_committed() -> list[str]:
    expected = {
        RESULT_PATH: serialized_results(),
        BAD_CASE_PATH: serialized_bad_cases(),
        BLIND_PACKET_PATH: build_blind_packet(),
    }
    return [
        str(path.relative_to(ROOT))
        for path, content in expected.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
