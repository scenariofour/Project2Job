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

    def test_sample_output_has_sources(self) -> None:
        output = json.loads(
            (ROOT / "skill/career-desk/examples/sample_output.json").read_text()
        )
        for bullet in output["resume_bullets"]:
            self.assertTrue(bullet["source_refs"])

    def test_changed_paths(self) -> None:
        result = changed_paths(
            {"a.md": "1", "b.md": "2"},
            {"a.md": "1", "b.md": "3", "c.md": "4"},
        )
        self.assertEqual(result["changed"], ["b.md"])
        self.assertEqual(result["added"], ["c.md"])
        self.assertEqual(result["unchanged"], ["a.md"])

    def test_journal_statuses_allow_completed_day1(self) -> None:
        self.assertEqual(validate_repo.validate_journal_statuses(), 1)


if __name__ == "__main__":
    unittest.main()
