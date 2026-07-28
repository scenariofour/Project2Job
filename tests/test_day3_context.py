from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from lab.day3_context_comparison import build_report
from src.career_desk.orchestrator import EvidenceAgentState, validate_state


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs" / "build_journal" / "traces" / "day3_context_comparison.json"


class Day3ContextComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = build_report()
        self.by_name = {
            strategy["strategy"]: strategy
            for strategy in self.report["strategies"]
        }

    def test_committed_result_matches_the_deterministic_runner(self) -> None:
        committed = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(committed, self.report)

    def test_manifest_preserves_correctness_with_less_opened_context(self) -> None:
        broad = self.by_name["broad_full_project"]
        manifest = self.by_name["manifest_scoped"]
        self.assertEqual(
            manifest["claim_to_source_correct"],
            broad["claim_to_source_correct"],
        )
        self.assertEqual(manifest["critical_sources_missed"], 0)
        self.assertLess(manifest["file_open_events"], broad["file_open_events"])
        self.assertLess(manifest["content_chars_opened"], broad["content_chars_opened"])
        self.assertLess(
            manifest["irrelevant_file_open_events"],
            broad["irrelevant_file_open_events"],
        )

    def test_targeted_selection_records_the_boundary_miss(self) -> None:
        targeted = self.by_name["targeted_filename_selection"]
        self.assertEqual(targeted["critical_sources_missed"], 1)
        self.assertEqual(targeted["claim_to_source_correct"], 2)
        missed = next(
            case for case in targeted["cases"] if case["case_id"] == "D3-003"
        )
        self.assertEqual(missed["status"], "unsafe_boundary_missed")
        self.assertEqual(missed["critical_sources_missed"], ["docs/team.md"])

    def test_citation_alone_remains_unsupported(self) -> None:
        for strategy in self.report["strategies"]:
            case = next(
                item for item in strategy["cases"] if item["case_id"] == "D3-002"
            )
            self.assertEqual(case["status"], "unsupported")
            self.assertIsNone(case["grounded_source"])
            self.assertFalse(case["citation_supports_claim"])

    def test_decision_defers_retrieval(self) -> None:
        self.assertEqual(
            self.report["decision"]["selected_architecture"],
            "manifest_scoped_context",
        )
        self.assertEqual(
            self.report["decision"]["retrieval_layer"],
            "deferred",
        )


class ExternalClaimGroundingTests(unittest.TestCase):
    @staticmethod
    def state() -> EvidenceAgentState:
        return EvidenceAgentState(
            evidence={
                "e1": {
                    "source": "README.md",
                    "location": "README.md:3",
                    "summary": "A citation exists but does not support the claim.",
                    "assessment": "irrelevant",
                }
            },
            claims={
                "c1": {
                    "status": "supported",
                    "attribution_scope": "directly_owned",
                }
            },
            outputs={
                "resume": {
                    "kind": "resume_bullet",
                    "content": "Launched the product to 100 users.",
                    "depends_on": ["c1"],
                    "exported": True,
                }
            },
            dependencies={
                "README.md": ["e1"],
                "e1": ["c1"],
                "c1": ["resume"],
            },
        )

    def test_citation_without_direct_support_fails_export_validation(self) -> None:
        failures = validate_state(self.state(), {"resume"})
        self.assertIn("ungrounded_export", {item["code"] for item in failures})

    def test_direct_support_allows_the_external_claim(self) -> None:
        state = self.state()
        state.evidence["e1"]["assessment"] = "direct"
        self.assertEqual(validate_state(state, {"resume"}), [])

    def test_unresolved_ownership_fails_external_attribution(self) -> None:
        state = self.state()
        state.evidence["e1"]["assessment"] = "direct"
        state.claims["c1"]["attribution_scope"] = "unresolved"
        failures = validate_state(state, {"resume"})
        self.assertIn(
            "unresolved_attribution_export",
            {item["code"] for item in failures},
        )

    def test_export_without_a_claim_dependency_is_not_grounded(self) -> None:
        state = self.state()
        state.outputs["resume"]["depends_on"] = ["README.md"]
        failures = validate_state(state, {"resume"})
        self.assertIn("ungrounded_export", {item["code"] for item in failures})

    def test_export_repair_preserves_internal_output_and_disables_export(self) -> None:
        from src.career_desk.orchestrator import repair_state

        state = self.state()
        original = deepcopy(state.outputs["resume"])
        repaired = repair_state(state, validate_state(state, {"resume"}))
        self.assertEqual(repaired, {"resume"})
        self.assertFalse(state.outputs["resume"]["exported"])
        self.assertEqual(state.outputs["resume"]["content"], original["content"])


if __name__ == "__main__":
    unittest.main()
