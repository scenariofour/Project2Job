"""Deterministic Day 3 context-selection comparison.

The comparison opens synthetic fixture files and observes only file events,
characters opened, labeled source recall, claim-to-source correctness, and
critical boundary misses. It does not model tokens, latency, or model quality.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "lab" / "fixtures" / "day3_context"
CASES_PATH = ROOT / "lab" / "evals" / "day3_context_cases.jsonl"


def load_cases() -> list[dict]:
    return [
        json.loads(line)
        for line in CASES_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def fixture_paths() -> list[str]:
    return sorted(
        path.relative_to(FIXTURE_ROOT).as_posix()
        for path in FIXTURE_ROOT.rglob("*.md")
    )


def manifest_paths() -> list[str]:
    manifest = json.loads(
        (FIXTURE_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    return list(manifest["project_sources"])


def targeted_paths(case: dict, candidates: list[str]) -> list[str]:
    terms = {term.casefold() for term in case["claim"]["target_terms"]}

    def rank(path: str) -> tuple[int, str]:
        path_terms = set(re.findall(r"[a-z0-9]+", path.casefold()))
        return (-len(terms & path_terms), path)

    top_k = case["claim"]["target_top_k"]
    return sorted(candidates, key=rank)[:top_k]


def assess_case(case: dict, opened: list[str]) -> dict:
    supporting = case["gold"]["supporting_sources"]
    critical = case["gold"]["critical_boundary_sources"]
    supporting_found = [path for path in supporting if path in opened]
    critical_found = [path for path in critical if path in opened]
    critical_missed = [path for path in critical if path not in opened]

    if supporting_found and critical_missed:
        status = "unsafe_boundary_missed"
    elif supporting_found and critical:
        status = "needs_confirmation"
    elif supporting_found:
        status = "supported"
    else:
        status = "unsupported"

    citation = case["claim"]["citation"]
    citation_supports = citation in supporting_found
    grounded_source = citation if status == "supported" and citation_supports else None
    expected = case["gold"]["expected_status"]
    claim_to_source_correct = (
        status == expected
        and (
            (status == "supported" and grounded_source is not None)
            or (status == "unsupported" and grounded_source is None)
            or (
                status == "needs_confirmation"
                and not critical_missed
                and grounded_source is None
            )
        )
    )
    relevant = set(supporting) | set(critical)
    return {
        "case_id": case["case_id"],
        "opened_files": opened,
        "status": status,
        "expected_status": expected,
        "supporting_sources_found": supporting_found,
        "critical_sources_found": critical_found,
        "critical_sources_missed": critical_missed,
        "citation": citation,
        "citation_supports_claim": citation_supports,
        "grounded_source": grounded_source,
        "claim_to_source_correct": claim_to_source_correct,
        "irrelevant_files_opened": [
            path for path in opened if path not in relevant
        ],
    }


def run_strategy(name: str, cases: list[dict]) -> dict:
    all_paths = fixture_paths()
    manifest = manifest_paths()
    results = []
    content_chars_opened = 0
    opened_events: list[str] = []

    for case in cases:
        if name == "broad_full_project":
            selected = all_paths
        elif name == "manifest_scoped":
            selected = manifest
        elif name == "targeted_filename_selection":
            selected = targeted_paths(case, manifest)
        else:  # pragma: no cover - strategies are fixed above
            raise ValueError(f"Unknown strategy: {name}")
        for path in selected:
            content_chars_opened += len(
                (FIXTURE_ROOT / path).read_text(encoding="utf-8")
            )
            opened_events.append(path)
        results.append(assess_case(case, selected))

    supported = [case for case in results if case["status"] == "supported"]
    grounded = [case for case in supported if case["grounded_source"]]
    return {
        "strategy": name,
        "case_count": len(results),
        "file_open_events": len(opened_events),
        "unique_files_opened": sorted(set(opened_events)),
        "content_chars_opened": content_chars_opened,
        "relevant_sources_found": sum(
            len(case["supporting_sources_found"])
            + len(case["critical_sources_found"])
            for case in results
        ),
        "critical_sources_missed": sum(
            len(case["critical_sources_missed"]) for case in results
        ),
        "irrelevant_file_open_events": sum(
            len(case["irrelevant_files_opened"]) for case in results
        ),
        "claim_to_source_correct": sum(
            case["claim_to_source_correct"] for case in results
        ),
        "provenance_coverage": {
            "source_linked_supported_claims": len(grounded),
            "supported_claims": len(supported),
        },
        "cases": results,
    }


def build_report() -> dict:
    cases = load_cases()
    strategies = [
        run_strategy(name, cases)
        for name in (
            "broad_full_project",
            "manifest_scoped",
            "targeted_filename_selection",
        )
    ]
    by_name = {item["strategy"]: item for item in strategies}
    broad = by_name["broad_full_project"]
    manifest = by_name["manifest_scoped"]
    targeted = by_name["targeted_filename_selection"]
    return {
        "schema_version": "1.0.0",
        "comparison": "day3_context_selection",
        "measurements": [
            "file_open_events",
            "unique_files_opened",
            "content_chars_opened",
            "relevant_sources_found",
            "critical_sources_missed",
            "irrelevant_file_open_events",
            "claim_to_source_correct",
            "provenance_coverage",
        ],
        "measurement_notes": [
            (
                "File-open events count Project artifact bodies opened per case; "
                "case definitions and the manifest control file are not context."
            ),
            (
                "Content characters are Python string lengths of opened fixture "
                "bodies, not token estimates."
            ),
            (
                "Targeted selection ranks manifest paths by exact filename-term "
                "overlap; it is not semantic retrieval or production RAG."
            ),
        ],
        "not_measured": ["runtime", "tokens", "cost", "model_quality", "user_value"],
        "strategies": strategies,
        "decision": {
            "selected_architecture": "manifest_scoped_context",
            "retrieval_layer": "deferred",
            "evidence": {
                "manifest_matches_broad_claim_to_source_correctness": (
                    manifest["claim_to_source_correct"]
                    == broad["claim_to_source_correct"]
                ),
                "manifest_opens_fewer_chars_than_broad": (
                    manifest["content_chars_opened"]
                    < broad["content_chars_opened"]
                ),
                "targeted_critical_boundary_misses": targeted[
                    "critical_sources_missed"
                ],
            },
            "boundary": (
                "This deterministic synthetic comparison supports the repository "
                "context choice only; it does not establish production retrieval "
                "quality or user value."
            ),
        },
    }
