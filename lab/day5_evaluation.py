"""Deterministic checks and review artifacts for the Day 5 evaluation package."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skill" / "p2j" / "scripts"))

from source_resolution import resolve_refs, summarize  # noqa: E402

PACKAGE = ROOT / "lab" / "day5"
RESULT_PATH = PACKAGE / "results.json"
BAD_CASE_PATH = PACKAGE / "bad_cases.jsonl"
BLIND_PACKET_PATH = PACKAGE / "blind_review_packet.md"
TAXONOMY_PATH = PACKAGE / "bad_case_taxonomy.json"
LAYER_PATH = PACKAGE / "evaluation_layers.json"

# Every observed Day 5 failure maps to one taxonomy entry and one product layer.
# A category earns a row only when a real recorded case produced it.
SOURCE_CHECKS = ("key_source_location_resolves", "all_source_locations_resolve")

TAXONOMY = {
    # A source failure splits by how the citation failed, because the two modes
    # need different product fixes: one convention, one format.
    "blank_span": "T-SOURCE-GRAMMAR",
    "out_of_range": "T-SOURCE-GRAMMAR",
    "unparsed_location": "T-UNVERIFIABLE-LOCATION",
    "unmapped_source": "T-UNVERIFIABLE-LOCATION",
    "first_person_team_affiliation": "T-OWNERSHIP-AMBIGUITY",
    "skill_catalog_isolation": "T-HARNESS-ISOLATION",
    "runtime_not_instrumented": "T-HARNESS-INSTRUMENTATION",
    "canonical_output_shape": "T-OUTPUT-SHAPE",
    "expected_evidence_statuses_present": "T-EVIDENCE-STATUS",
    "unsupported_resume_export_blocked": "T-UNSUPPORTED-EXPORT",
    "answer_claim_safety_gate_closed": "T-UNSUPPORTED-EXPORT",
    "forbidden_external_claim_absent": "T-UNSUPPORTED-EXPORT",
    "one_next_build_targets_gold_gap": "T-NEXT-BUILD",
}


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


def _source_map(case_id: str) -> dict[str, Path]:
    """The permitted sources the capture presented, keyed by their cited names."""
    files = load_json(PACKAGE / "capture_manifest.json")["capture_source_files"]
    return {name: ROOT / relative for name, relative in files[case_id].items()}


def _resolve_key_source(
    case: dict[str, Any], output: dict[str, Any], sources: dict[str, Path]
) -> bool:
    """Resolve at least one key-highlight citation to the expected source phrase.

    Both systems are held to the one canonical location grammar. An earlier
    version of this check also accepted prose anchors such as `sentence 1`,
    which let an unverifiable baseline citation pass a gate the Skill had to
    clear with a line number. That accommodation is recorded as
    `T-GRADER-ACCOMMODATION` and removed.
    """
    phrase = case["gold"]["key_source_phrase"].casefold()
    for highlight in output["project_highlights"]:
        if phrase not in highlight["text"].casefold():
            continue
        for ref in resolve_refs({"source_refs": highlight["source_refs"]}, sources):
            if ref["status"] == "resolved" and phrase in ref["excerpt"].casefold():
                return True
    return False


def _portable(resolution: dict[str, Any]) -> dict[str, Any]:
    """Rewrite resolved paths relative to the repository.

    An absolute path makes the committed record machine-specific and leaks a
    local home directory into a public artifact.
    """
    for record in resolution["unresolved"]:
        if "resolved_path" in record:
            record["resolved_path"] = str(
                Path(record["resolved_path"]).relative_to(ROOT)
            )
    return resolution


def _case_checks(
    case: dict[str, Any], output: dict[str, Any], resolution: dict[str, Any]
) -> list[dict[str, Any]]:
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
            "passed": _resolve_key_source(
                case, output, _source_map(case["case_id"])
            ),
            "severe": True,
        },
        {
            # Schema validity says a citation exists. Only resolution says it
            # points at text a reader or a recruiter could check.
            "check": "all_source_locations_resolve",
            "passed": resolution["all_resolve"],
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
        sources = _source_map(case["case_id"])
        for run in sorted(runs_by_case[case["case_id"]], key=lambda item: item["system"]):
            output_path = ROOT / run["output"]
            output = load_json(output_path)
            resolution = _portable(summarize(resolve_refs(output, sources)))
            checks = _case_checks(case, output, resolution)
            systems.append(
                {
                    "system": run["system"],
                    "output": run["output"],
                    "output_sha256": sha256(output_path),
                    "schema_valid_at_capture": run["schema_validation"]["valid"],
                    "source_resolution": resolution,
                    "checks": checks,
                }
            )
            unresolved_statuses = sorted(
                {item["status"] for item in resolution["unresolved"]}
            )
            for check in checks:
                if not (check["severe"] and not check["passed"]):
                    continue
                error = {
                    "case_id": case["case_id"],
                    "system": run["system"],
                    "check": check["check"],
                }
                if check["check"] in SOURCE_CHECKS:
                    error["unresolved_statuses"] = unresolved_statuses
                severe_errors.append(error)
        case_results.append(
            {
                "case_id": case["case_id"],
                "source_case_id": case["source_case_id"],
                "systems": systems,
            }
        )

    source_precision = {
        system: {
            "total_refs": 0,
            "resolved": 0,
            "blank_span": 0,
            "out_of_range": 0,
            "unparsed_location": 0,
            "unmapped_source": 0,
        }
        for system in ("baseline", "skill")
    }
    for case in case_results:
        for entry in case["systems"]:
            bucket = source_precision[entry["system"]]
            bucket["total_refs"] += entry["source_resolution"]["total_refs"]
            for status, count in entry["source_resolution"]["counts"].items():
                bucket[status] += count

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
            "source_precision": source_precision,
            "source_precision_note": (
                "Observed citation resolution over 3 cases per system. It "
                "measures whether an exported citation points at real text, "
                "not whether the claim is a good one."
            ),
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


def _bad_case_id(case_id: str, system: str, category: str) -> str:
    """A stable ID derived from content.

    An enumerated ID renumbers every existing bad case as soon as one more is
    found, which breaks the traceability the log exists to provide.
    """
    slug = category.replace("_", "-").upper()
    return f"BC-{case_id}-{system.upper()}-{slug}"


def _taxonomy_for(error: dict[str, Any]) -> str:
    """A source failure is classified by how it failed, not by which gate saw it."""
    if error["check"] in SOURCE_CHECKS:
        statuses = error.get("unresolved_statuses") or []
        return TAXONOMY[statuses[0]] if statuses else "T-SOURCE-GRAMMAR"
    return TAXONOMY[error["check"]]


def build_bad_cases() -> list[dict[str, Any]]:
    results = build_results()
    bad_cases = [
        {
            "bad_case_id": _bad_case_id(
                error["case_id"], error["system"], error["check"]
            ),
            "case_id": error["case_id"],
            "system": error["system"],
            "severity": "severe",
            "category": error["check"],
            "taxonomy_id": _taxonomy_for(error),
            "status": "open",
            "evidence": error,
            "average_override": True,
        }
        for error in results["severe_errors"]
    ]
    bad_cases.extend(
        [
            {
                "bad_case_id": _bad_case_id(
                    "D5-002", "both", "first_person_team_affiliation"
                ),
                "case_id": "D5-002",
                "system": "both",
                "severity": "pending_human_review",
                "category": "first_person_team_affiliation",
                "taxonomy_id": TAXONOMY["first_person_team_affiliation"],
                "status": "needs_adjudication",
                "evidence": "Both outputs use first-person team framing while individual ownership remains unconfirmed.",
                "average_override": True,
            },
            {
                "bad_case_id": _bad_case_id(
                    "measurement", "baseline", "skill_catalog_isolation"
                ),
                "case_id": "measurement",
                "system": "baseline",
                "severity": "measurement_limitation",
                "category": "skill_catalog_isolation",
                "taxonomy_id": TAXONOMY["skill_catalog_isolation"],
                "status": "open",
                "evidence": load_json(PACKAGE / "capture_manifest.json")["baseline"][
                    "isolation_limitation"
                ],
                "average_override": False,
            },
            {
                "bad_case_id": _bad_case_id(
                    "D5-001", "baseline", "runtime_not_instrumented"
                ),
                "case_id": "D5-001",
                "system": "baseline",
                "severity": "measurement_limitation",
                "category": "runtime_not_instrumented",
                "taxonomy_id": TAXONOMY["runtime_not_instrumented"],
                "status": "open",
                "evidence": "The first baseline wall time is unavailable and is not backfilled.",
                "average_override": False,
            },
        ]
    )
    return bad_cases


# Only a category a recorded case actually produced earns a row. Every entry
# names the product layer that has to change, so the log stays actionable
# instead of descriptive.
BAD_CASE_TAXONOMY = [
    {
        "taxonomy_id": "T-SOURCE-GRAMMAR",
        "name": "Cited line span resolves to no text",
        "product_layer": "output_contract_and_provenance",
        "observed_in": ["lab/day5/outputs/skill/S01.json"],
        "observation": (
            "The Skill run numbered non-empty body lines, so six citations for "
            "the 20-case plan point at blank absolute line 2 instead of line 3. "
            "The claim is inside the permitted source; its citation is not."
        ),
        "product_action": (
            "Define one absolute line grammar in the shared standard and the "
            "core contract, and resolve every citation before export."
        ),
        "status": "fixed_at_gate",
    },
    {
        "taxonomy_id": "T-UNVERIFIABLE-LOCATION",
        "name": "Citation format no reader or checker can resolve",
        "product_layer": "output_contract_and_provenance",
        "observed_in": ["lab/day5/outputs/baseline/S02.json"],
        "observation": (
            "All 19 baseline citations use prose anchors such as "
            "'Team Project, sentence 1' and 'Responsibilities, bullet 2'. They "
            "are schema-valid and unverifiable."
        ),
        "product_action": (
            "Reject a location that names no absolute line span; the gate "
            "applies to both systems."
        ),
        "status": "fixed_at_gate",
    },
    {
        "taxonomy_id": "T-GRADER-ACCOMMODATION",
        "name": "Grader applied a laxer standard to one system",
        "product_layer": "rubric_and_grader",
        "observed_in": ["lab/day5_evaluation.py"],
        "observation": (
            "The first key-source check carried a 'sentence 1' branch that let "
            "an unverifiable baseline citation pass a gate the Skill had to "
            "clear with a line number, tilting the comparison toward the "
            "baseline."
        ),
        "product_action": (
            "Hold both systems to the one canonical grammar and re-record the "
            "affected results."
        ),
        "status": "fixed",
    },
    {
        "taxonomy_id": "T-OWNERSHIP-AMBIGUITY",
        "name": "First-person team framing with unconfirmed contribution",
        "product_layer": "ownership_and_claim_classification",
        "observed_in": [
            "lab/day5/outputs/skill/S02.json",
            "lab/day5/outputs/baseline/S02.json",
        ],
        "observation": (
            "Both systems keep the correct team-level status while using "
            "first-person wording. Whether that stays inside the boundary is a "
            "human judgement no deterministic check can make."
        ),
        "product_action": (
            "Keep the case open for reviewer adjudication; do not resolve it "
            "with an automated rule."
        ),
        "status": "needs_adjudication",
    },
    {
        "taxonomy_id": "T-ASSET-RISK-LEAKAGE",
        "name": "Private evidence risk leaked into a copyable asset",
        "product_layer": "career_asset_packaging",
        "observed_in": [
            "docs/dogfood/PROJECT2JOB_DAY5_CAREER_ASSET_DOGFOOD.md"
        ],
        "observation": (
            "Accurate warnings entered a spoken interview answer and made "
            "pending validation more memorable than the supported achievement."
        ),
        "product_action": (
            "Separate the external script from Private Defense; recorded as "
            "D-029 with behavioral regressions."
        ),
        "status": "fixed",
    },
    {
        "taxonomy_id": "T-CONTEXT-SELECTION-MISS",
        "name": "Targeted selection drops the artifact that bounds a claim",
        "product_layer": "context_selection",
        "observed_in": ["lab/evals/day3_context_cases.jsonl"],
        "observation": (
            "D3-003: narrow selection lowered context volume while omitting "
            "the separate ownership boundary."
        ),
        "product_action": (
            "Retain manifest-scoped context and defer retrieval; recorded as "
            "D-026."
        ),
        "status": "accepted_tradeoff",
    },
    {
        "taxonomy_id": "T-STALE-PERSISTENT-CLAIM",
        "name": "Removed evidence survives in persisted state",
        "product_layer": "orchestration_and_state",
        "observed_in": ["lab/evals/agent_cases.jsonl"],
        "observation": (
            "A06_PROJECT_REMOVED is the visible stale-state case: a claim whose "
            "source is gone must not survive a restore."
        ),
        "product_action": (
            "Dependency-aware invalidation on removal, covered by regression."
        ),
        "status": "fixed",
    },
    {
        "taxonomy_id": "T-HARNESS-ISOLATION",
        "name": "Baseline isolation not observable",
        "product_layer": "eval_harness",
        "observed_in": ["lab/day5/capture_manifest.json"],
        "observation": (
            "The host loaded the global Skill catalog despite "
            "--ignore-user-config, so token overhead cannot be attributed "
            "cleanly to Project2Job instructions."
        ),
        "product_action": (
            "Do not claim a token-overhead comparison until a capture proves "
            "isolation."
        ),
        "status": "open",
    },
    {
        "taxonomy_id": "T-HARNESS-INSTRUMENTATION",
        "name": "A measurement was never instrumented",
        "product_layer": "eval_harness",
        "observed_in": ["lab/day5/capture_manifest.json"],
        "observation": (
            "The first baseline run was not wrapped with /usr/bin/time, so one "
            "of six wall times does not exist."
        ),
        "product_action": (
            "Leave the value null and report runtime as an incomplete set; "
            "never backfill."
        ),
        "status": "open",
    },
]

# The layers separate what a machine can decide from what only a person can.
# A layer is `unmeasured` until an executable artifact or a signed record exists.
EVALUATION_LAYERS = [
    {
        "layer": 1,
        "name": "Deterministic contract checks",
        "what_exists": (
            "Application Pack schema validation, citation resolution, forbidden "
            "export phrases, resume-bullet count, answer claim-safety gate, and "
            "expected evidence statuses."
        ),
        "executable": "python3 scripts/run_day5_evaluation.py --check",
        "metric": "severe check pass/fail per case per system; citation counts",
        "unmeasured": "nothing at this layer",
        "maturity": "TESTED",
    },
    {
        "layer": 2,
        "name": "Component quality",
        "what_exists": (
            "Day 2 intake extraction and routing cases, Day 3 context selection "
            "comparison, Context Registry reuse and invalidation, selective "
            "routing, and Skill behavior cases."
        ),
        "executable": "python3 -m unittest discover -s tests -t .",
        "metric": "per-component assertions and eval-case checks",
        "unmeasured": (
            "component behavior against a live host, live model, or real "
            "project corpus"
        ),
        "maturity": "TESTED",
    },
    {
        "layer": 3,
        "name": "End-to-end task success",
        "what_exists": (
            "Three recorded strong-prompt versus Project2Job Application Pack "
            "pairs on the S01/S02/S05 boundary cases, plus the Agent "
            "update-versus-fresh-replay mechanics comparison."
        ),
        "executable": "python3 scripts/run_day5_evaluation.py --print results",
        "metric": (
            "severe-gate pass rate and citation resolution rate over 3 cases "
            "per system"
        ),
        "unmeasured": (
            "task success on unseen projects; n=3 supports direction, not a "
            "rate"
        ),
        "maturity": "TESTED",
    },
    {
        "layer": 4,
        "name": "Human product judgement",
        "what_exists": (
            "A blind packet, a 0-3 rubric, blank two-reviewer forms, a "
            "disagreement form, and a written protocol. One product-owner "
            "target-user dogfood session is recorded separately."
        ),
        "executable": "python3 -m unittest tests.test_day5_evaluation -v",
        "metric": "none recorded; every score field is null",
        "unmeasured": (
            "reviewer scores, preference, disagreement, and every subjective "
            "rubric dimension"
        ),
        "maturity": "PROTOCOL ONLY",
    },
    {
        "layer": 5,
        "name": "Real user and outcome evidence",
        "what_exists": "A blank bounded target-user pilot record.",
        "executable": None,
        "metric": "none",
        "unmeasured": (
            "adoption, external use, application results, and hiring outcomes"
        ),
        "maturity": "NOT STARTED",
    },
]


def build_taxonomy() -> dict[str, Any]:
    return {
        "note": (
            "Every category is backed by a recorded case in this repository. "
            "No category exists because it sounded complete."
        ),
        "categories": BAD_CASE_TAXONOMY,
    }


def build_evaluation_layers() -> dict[str, Any]:
    return {
        "note": (
            "Deterministic correctness and subjective product quality are "
            "separate layers. An automated grader never stands in for layer 4."
        ),
        "layers": EVALUATION_LAYERS,
    }


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


def serialized_taxonomy() -> str:
    return json.dumps(build_taxonomy(), indent=2, ensure_ascii=False) + "\n"


def serialized_layers() -> str:
    return json.dumps(build_evaluation_layers(), indent=2, ensure_ascii=False) + "\n"


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
        TAXONOMY_PATH: serialized_taxonomy(),
        LAYER_PATH: serialized_layers(),
    }
    return [
        str(path.relative_to(ROOT))
        for path, content in expected.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]


def write_committed() -> list[Path]:
    """Rewrite every generated artifact from the recorded outputs."""
    expected = {
        RESULT_PATH: serialized_results(),
        BAD_CASE_PATH: serialized_bad_cases(),
        BLIND_PACKET_PATH: build_blind_packet(),
        TAXONOMY_PATH: serialized_taxonomy(),
        LAYER_PATH: serialized_layers(),
    }
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
    return list(expected)
