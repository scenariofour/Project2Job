from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.validate_repo import validate_shared_foundation

ROOT = Path(__file__).resolve().parents[1]


class SharedFoundationTests(unittest.TestCase):
    def test_shared_contract_is_compatible_for_skill_and_agent(self) -> None:
        result = validate_shared_foundation()
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


if __name__ == "__main__":
    unittest.main()
