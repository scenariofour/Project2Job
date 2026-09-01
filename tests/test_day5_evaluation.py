from __future__ import annotations

import json
import unittest
from pathlib import Path

from lab.day5_evaluation import (
    PACKAGE,
    build_bad_cases,
    build_evaluation_layers,
    build_results,
    build_taxonomy,
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
            [
                (error["case_id"], error["system"], error["check"])
                for error in results["severe_errors"]
            ],
            [
                ("D5-001", "skill", "key_source_location_resolves"),
                ("D5-001", "skill", "all_source_locations_resolve"),
                ("D5-002", "baseline", "key_source_location_resolves"),
                ("D5-002", "baseline", "all_source_locations_resolve"),
            ],
        )
        self.assertTrue(
            any(
                item["average_override"]
                and item["category"] == "key_source_location_resolves"
                for item in build_bad_cases()
            )
        )

    def test_both_systems_face_the_same_citation_grammar(self) -> None:
        """The grader must not accept from one system what it rejects from the other.

        The first key-source check accepted a prose `sentence 1` anchor, which
        let the baseline clear a gate the Skill had to pass with a line number.
        """
        by_case = {case["case_id"]: case for case in build_results()["case_results"]}
        checks = {
            (case_id, entry["system"]): {
                item["check"]: item["passed"] for item in entry["checks"]
            }
            for case_id, case in by_case.items()
            for entry in case["systems"]
        }
        self.assertFalse(checks[("D5-001", "skill")]["all_source_locations_resolve"])
        self.assertFalse(checks[("D5-002", "baseline")]["all_source_locations_resolve"])
        self.assertTrue(checks[("D5-003", "skill")]["all_source_locations_resolve"])
        self.assertTrue(checks[("D5-003", "baseline")]["all_source_locations_resolve"])

    def test_source_precision_is_observed_for_both_systems(self) -> None:
        """Counted citations, not a claimed rate."""
        precision = build_results()["measurements"]["source_precision"]
        self.assertEqual(
            precision["skill"],
            {
                "total_refs": 24,
                "resolved": 18,
                "blank_span": 6,
                "out_of_range": 0,
                "unparsed_location": 0,
                "unmapped_source": 0,
            },
        )
        self.assertEqual(
            precision["baseline"],
            {
                "total_refs": 60,
                "resolved": 41,
                "blank_span": 0,
                "out_of_range": 0,
                "unparsed_location": 19,
                "unmapped_source": 0,
            },
        )

    def test_bad_case_ids_are_stable_under_new_findings(self) -> None:
        """An enumerated ID renumbers the whole log when one case is added."""
        ids = [item["bad_case_id"] for item in build_bad_cases()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("BC-D5-001-SKILL-KEY-SOURCE-LOCATION-RESOLVES", ids)
        for item in build_bad_cases():
            self.assertTrue(item["bad_case_id"].endswith(
                item["category"].replace("_", "-").upper()
            ))

    def test_every_taxonomy_category_is_backed_by_a_real_artifact(self) -> None:
        """A category may not exist because it sounded complete."""
        categories = build_taxonomy()["categories"]
        self.assertEqual(
            len(categories), len({item["taxonomy_id"] for item in categories})
        )
        for category in categories:
            self.assertTrue(category["observed_in"], category["taxonomy_id"])
            for relative in category["observed_in"]:
                self.assertTrue(
                    (ROOT / relative).exists(),
                    f"{category['taxonomy_id']} cites missing {relative}",
                )
            self.assertTrue(category["product_layer"])
            self.assertTrue(category["product_action"])

    def test_every_emitted_bad_case_maps_to_a_taxonomy_category(self) -> None:
        known = {item["taxonomy_id"] for item in build_taxonomy()["categories"]}
        for item in build_bad_cases():
            self.assertIn(item["taxonomy_id"], known, item["bad_case_id"])

    def test_human_judgement_layers_claim_no_measurement(self) -> None:
        """An automated grader may not stand in for a reviewer."""
        layers = {item["layer"]: item for item in build_evaluation_layers()["layers"]}
        self.assertEqual(sorted(layers), [1, 2, 3, 4, 5])
        self.assertEqual(layers[4]["maturity"], "PROTOCOL ONLY")
        self.assertEqual(layers[5]["maturity"], "NOT STARTED")
        self.assertIn("null", layers[4]["metric"])
        self.assertIsNone(layers[5]["executable"])
        for layer in layers.values():
            self.assertTrue(layer["unmeasured"])

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

    def test_review_protocol_names_who_reviewed_and_what_that_does_not_prove(
        self,
    ) -> None:
        protocol = (PACKAGE / "REVIEW_PROTOCOL.md").read_text(encoding="utf-8")
        lowered = protocol.lower()
        for required in (
            "product owner",
            "product-owner review",
            "target-user validation",
            "blind",
            "accept / revise / reject",
        ):
            self.assertIn(required, lowered)

    def test_product_decisions_cite_evidence_and_use_allowed_verdicts(self) -> None:
        """A decision without a pointer to evidence is an opinion."""
        decisions = json.loads(
            (PACKAGE / "product_decisions.json").read_text(encoding="utf-8")
        )["decisions"]
        self.assertTrue(decisions)
        for decision in decisions:
            self.assertIn(
                decision["verdict"], ("KEEP", "REVISE", "STOP", "UNPROVEN")
            )
            self.assertTrue(decision["reason"])
            self.assertTrue(decision["evidence"])
            for relative in decision["evidence"]:
                self.assertTrue(
                    (ROOT / relative.split("#")[0]).exists(),
                    f"{decision['mechanism']} cites missing {relative}",
                )


if __name__ == "__main__":
    unittest.main()
