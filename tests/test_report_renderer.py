from __future__ import annotations

import json
import unittest
from html import unescape
from pathlib import Path

from apps.web.render_report import render

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "apps" / "web" / "fixtures"


class ReportRendererTests(unittest.TestCase):
    def load(self, name: str) -> tuple[dict, str]:
        data = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
        return data, render(data)

    def test_all_four_states_render_from_structured_fixtures(self) -> None:
        expected = {
            "initial_analysis.json": "Preliminary Project Scores",
            "evidence_inspection.json": "Preview before approval",
            "project_updated.json": "Selective Update Summary",
            "no_relevant_changes.json": "No relevant changes found",
        }
        for fixture, marker in expected.items():
            with self.subTest(fixture=fixture):
                data, document = self.load(fixture)
                self.assertIn(marker, document)
                self.assertIn("Agent Activity", document)
                self.assertIn(data["project"]["name"], document)

    def test_update_count_and_preserved_outputs_match_trace(self) -> None:
        data, document = self.load("project_updated.json")
        visible_text = unescape(document)
        self.assertIn(
            f"{len(data['trace']['affected_outputs'])} updated", document
        )
        for output_id in data["trace"]["preserved_outputs"]:
            if output_id in data["state"]["outputs"]:
                label = data["state"]["outputs"][output_id].get(
                    "label", output_id
                )
                self.assertIn(label, visible_text)

    def test_update_has_before_after_and_why(self) -> None:
        _, document = self.load("project_updated.json")
        self.assertIn("Before", document)
        self.assertIn("After", document)
        self.assertIn("Why:", document)

    def test_inspection_requires_approval_and_shows_evidence_boundary(self) -> None:
        _, document = self.load("evidence_inspection.json")
        for marker in (
            "Supporting sources",
            "Attribution scope",
            "Affected outputs",
            "Human correction",
            "Approve &amp; Apply Correction",
        ):
            self.assertIn(marker, document)

    def test_normal_reports_hide_implementation_language(self) -> None:
        forbidden = (
            "registry state",
            "cached artifact",
            "internal id",
            "raw scoring",
            "D1 ",
            "D2 ",
            "Execute Build",
        )
        for path in FIXTURES.glob("*.json"):
            document = render(json.loads(path.read_text(encoding="utf-8")))
            for phrase in forbidden:
                self.assertNotIn(phrase, document)


if __name__ == "__main__":
    unittest.main()
