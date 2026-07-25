from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import validate_repo

ROOT = Path(__file__).resolve().parents[1]


class SharedFoundationTests(unittest.TestCase):
    def test_shared_contract_is_compatible_for_skill_and_agent(self) -> None:
        result = validate_repo.validate_shared_foundation()
        self.assertEqual(result["shared_consumers"], 2)
        self.assertEqual(result["role_capabilities"], 10)
        self.assertEqual(result["evidence_statuses"], 6)
        self.assertGreaterEqual(result["shared_gold_cases"], 10)

    def test_consumers_resolve_identical_contract_versions(self) -> None:
        contract = json.loads(
            (ROOT / "references/shared_contract.v1.json").read_text(encoding="utf-8")
        )
        consumers = {
            consumer["consumer"]: consumer for consumer in contract["consumers"]
        }
        for field in (
            "role_profile_version",
            "input_schema_ids",
            "output_schema_id",
        ):
            self.assertEqual(consumers["skill"][field], consumers["agent"][field])

    def test_baseline_contains_shared_evidence_boundaries(self) -> None:
        prompt = (ROOT / "lab/baseline_prompt.md").read_text(encoding="utf-8")
        for required_text in (
            "untrusted data",
            "partially_supported",
            "needs_confirmation",
            "A target or estimate is not a measured result.",
            "Team language does not prove individual ownership.",
        ):
            self.assertIn(required_text, prompt)

    def test_application_pack_allows_empty_evidence_outputs(self) -> None:
        schema = json.loads(
            (ROOT / "schemas/application_pack.schema.json").read_text(
                encoding="utf-8"
            )
        )
        properties = schema["properties"]
        self.assertEqual(properties["project_highlights"].get("minItems", 0), 0)
        self.assertEqual(properties["resume_bullets"].get("minItems", 0), 0)

    def test_supported_claim_may_remain_non_exportable(self) -> None:
        cases = self._gold_cases()
        self._case(cases, "SF-009")["gold_label"]["resume_export_allowed"] = False
        with patch.object(validate_repo, "load_jsonl", return_value=cases):
            try:
                validate_repo.validate_shared_foundation()
            except SystemExit as exc:
                self.fail(f"supported non-exportable claim was rejected: {exc}")

    def test_partially_supported_claim_cannot_be_exported(self) -> None:
        cases = self._gold_cases()
        self._case(cases, "SF-003")["gold_label"]["resume_export_allowed"] = True
        with patch.object(validate_repo, "load_jsonl", return_value=cases):
            with self.assertRaises(SystemExit):
                validate_repo.validate_shared_foundation()

    def test_exportable_claim_requires_direct_evidence(self) -> None:
        cases = self._gold_cases()
        label = self._case(cases, "SF-001")["gold_label"]
        label["evidence_refs"][0]["evidence_type"] = "supporting"
        with patch.object(validate_repo, "load_jsonl", return_value=cases):
            with self.assertRaises(SystemExit):
                validate_repo.validate_shared_foundation()

    @staticmethod
    def _gold_cases() -> list[dict]:
        path = ROOT / "lab/evals/shared_foundation_cases.v0.1.0.jsonl"
        return validate_repo.load_jsonl(path)

    @staticmethod
    def _case(cases: list[dict], case_id: str) -> dict:
        return next(case for case in cases if case["case_id"] == case_id)


if __name__ == "__main__":
    unittest.main()
