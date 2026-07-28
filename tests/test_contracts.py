from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import validate_repo
from src.career_desk.state import changed_paths

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_active_docs_are_limited(self) -> None:
        manifest = json.loads((ROOT / "PROJECT_MANIFEST.json").read_text())
        self.assertLessEqual(len(manifest["active_documents"]), 15)

    def test_installed_pack_contract_requires_sources(self) -> None:
        schema = json.loads(
            (ROOT / "schemas/application_pack.schema.json").read_text()
        )
        bullet = schema["$defs"]["resumeBullet"]
        grounded_text = schema["$defs"]["groundedText"]
        self.assertIn("source_refs", bullet["required"])
        self.assertEqual(bullet["properties"]["source_refs"]["minItems"], 1)
        self.assertIn("source_refs", grounded_text["required"])
        self.assertEqual(grounded_text["properties"]["source_refs"]["minItems"], 1)

    def test_changed_paths(self) -> None:
        result = changed_paths(
            {"a.md": "1", "b.md": "2"},
            {"a.md": "1", "b.md": "3", "c.md": "4"},
        )
        self.assertEqual(result["changed"], ["b.md"])
        self.assertEqual(result["added"], ["c.md"])
        self.assertEqual(result["unchanged"], ["a.md"])

    def test_journal_statuses_allow_completed_day2(self) -> None:
        self.assertEqual(validate_repo.validate_journal_statuses(), 2)


if __name__ == "__main__":
    unittest.main()
