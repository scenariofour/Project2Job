from __future__ import annotations

import json
import unittest
from pathlib import Path

from lab.day5_evaluation import (
    PACKAGE,
    build_bad_cases,
    build_results,
    check_committed,
    load_jsonl,
)

ROOT = Path(__file__).resolve().parents[1]


class Day5EvaluationTests(unittest.TestCase):
    def test_committed_artifacts_match_recorded_outputs(self) -> None:
        self.assertEqual(check_committed(), [])

    def test_gold_cases_are_complete_and_reuse_existing_cases(self) -> None:
        cases = load_jsonl(PACKAGE / "cases.jsonl")
        self.assertEqual(
            [case["source_case_id"] for case in cases],
            ["S01", "S02", "S05", "A17_COMPARISON"],
        )
        for case in cases:
            gold = case["gold"]
            for field in (
                "expected_statuses",
                "source_location",
                "evidence_boundary",
                "acceptable_alternative",
                "reviewer_notes",
            ):
                self.assertTrue(gold[field])

    def test_three_pairs_are_schema_valid_at_capture(self) -> None:
        manifest = json.loads(
            (PACKAGE / "capture_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(manifest["runs"]), 6)
        self.assertEqual(
            {(run["case_id"], run["system"]) for run in manifest["runs"]},
            {
                (case_id, system)
                for case_id in ("D5-001", "D5-002", "D5-003")
                for system in ("baseline", "skill")
            },
        )
        self.assertTrue(
            all(run["schema_validation"]["valid"] for run in manifest["runs"])
        )
        self.assertEqual(
            manifest["reused_artifacts"]["existing_skill_output"],
            "skill/p2j/examples/sample_brief.md",
        )

    def test_severe_error_is_not_hidden_by_aggregate_scores(self) -> None:
        results = build_results()
        self.assertFalse(results["automated_gate_passed"])
        self.assertEqual(
            results["severe_errors"],
            [
                {
                    "case_id": "D5-001",
                    "system": "skill",
                    "check": "key_source_location_resolves",
                }
            ],
        )
        self.assertTrue(
            any(
                item["average_override"]
                and item["category"] == "key_source_location_resolves"
                for item in build_bad_cases()
            )
        )

    def test_unobservable_measurements_and_human_results_stay_null(self) -> None:
        results = build_results()
        self.assertIsNone(results["measurements"]["provider_cost"])
        self.assertEqual(
            results["measurements"]["runtime"]["baseline"]["observed_runs"], 2
        )
        self.assertEqual(
            results["measurements"]["runtime"]["baseline"]["total_runs"], 3
        )
        self.assertTrue(
            all(value is None for value in results["human_results"].values())
        )

    def test_agent_comparison_remains_bounded(self) -> None:
        checks = build_results()["agent_comparison"]["checks"]
        self.assertTrue(all(check["passed"] for check in checks))
        self.assertTrue(all(check["severe"] for check in checks))

    def test_human_templates_contain_no_fabricated_review(self) -> None:
        reviews = load_jsonl(PACKAGE / "human_review.template.jsonl")
        self.assertEqual(len(reviews), 3)
        for review in reviews:
            self.assertIsNone(review["reviewer_id"])
            self.assertIsNone(review["preference"])
            for label in ("A", "B"):
                self.assertTrue(
                    all(value is None for value in review["scores"][label].values())
                )


if __name__ == "__main__":
    unittest.main()
