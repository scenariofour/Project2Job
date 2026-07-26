"""Consistency checks between documents, schemas, and implementation status.

These tests assert specific facts, not whole-document snapshots, so ordinary
editing does not break them.
"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts import validate_repo

ROOT = Path(__file__).resolve().parents[1]

STATUS_DOCUMENTS = ("README.md", "PROJECT_STATUS.md", "START_HERE.md")

STALE_CLAIMS = [
    "Day 0 establishes the repository foundation only",
    "Day 0 repository foundation implemented",
    "Day 0 provides a reproducible repository foundation",
    "No Work Order is complete",
]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def prose(relative: str) -> str:
    """File text normalized so rewrapping or dash style cannot break a test."""
    return " ".join(read(relative).replace("–", "-").split())


def build_repo(root: Path, statuses: list[str], highest_completed: str) -> None:
    journal = root / "docs" / "build_journal"
    journal.mkdir(parents=True)
    for day, status in enumerate(statuses):
        (journal / f"DAY_{day}.md").write_text(
            f"# Day {day}\n\nStatus: {status}\n", encoding="utf-8"
        )
    (root / "PROJECT_STATUS.md").write_text(
        f"# Project Status\n\nHighest completed Day: {highest_completed}\n",
        encoding="utf-8",
    )


class JournalStatusTests(unittest.TestCase):
    """The Day journal gate must be general, not rewritten for each new Day."""

    def check(self, statuses: list[str], highest_completed: str) -> int:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            build_repo(root, statuses, highest_completed)
            return validate_repo.validate_journal_statuses(root)

    def test_current_repository_reports_day_1_completed(self) -> None:
        self.assertEqual(validate_repo.validate_journal_statuses(), 1)

    def test_completed_prefix_passes(self) -> None:
        statuses = ["VALIDATED", "IMPLEMENTED", "PLANNED", "PLANNED"]
        self.assertEqual(self.check(statuses, "1"), 1)

    def test_no_completed_day_passes(self) -> None:
        self.assertEqual(self.check(["PLANNED", "PLANNED"], "none"), -1)

    def test_later_day_completed_while_earlier_planned_fails(self) -> None:
        with self.assertRaises(SystemExit):
            self.check(["IMPLEMENTED", "PLANNED", "IMPLEMENTED"], "2")

    def test_unknown_status_fails(self) -> None:
        with self.assertRaises(SystemExit):
            self.check(["IMPLEMENTED", "DONE", "PLANNED"], "1")

    def test_missing_status_line_fails(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            build_repo(root, ["IMPLEMENTED", "PLANNED"], "0")
            (root / "docs/build_journal/DAY_1.md").write_text(
                "# Day 1\n", encoding="utf-8"
            )
            with self.assertRaises(SystemExit):
                validate_repo.validate_journal_statuses(root)

    def test_gap_in_day_numbers_fails(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            build_repo(root, ["IMPLEMENTED", "IMPLEMENTED"], "1")
            (root / "docs/build_journal/DAY_0.md").unlink()
            with self.assertRaises(SystemExit):
                validate_repo.validate_journal_statuses(root)

    def test_non_numeric_day_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            build_repo(root, ["IMPLEMENTED", "PLANNED"], "0")
            (root / "docs/build_journal/DAY_2_DRAFT.md").write_text(
                "Status: PLANNED\n", encoding="utf-8"
            )
            with self.assertRaises(SystemExit):
                validate_repo.validate_journal_statuses(root)

    def test_project_status_disagreement_fails(self) -> None:
        with self.assertRaises(SystemExit):
            self.check(["IMPLEMENTED", "IMPLEMENTED", "PLANNED"], "0")


class StatusTruthTests(unittest.TestCase):
    def test_no_stale_day_0_only_claims(self) -> None:
        for relative in STATUS_DOCUMENTS:
            text = prose(relative)
            for claim in STALE_CLAIMS:
                self.assertNotIn(claim, text, f"{relative} keeps a stale claim")

    def test_status_documents_state_current_truth(self) -> None:
        for relative in ("README.md", "PROJECT_STATUS.md"):
            text = prose(relative)
            for fact in (
                "WO-00 Shared Foundation is complete",
                "Day 1 bounded Agent Loop is implemented and tested",
                "deterministic scripted read-only tools",
                "not a production model-powered Agent runtime",
                "WO-02",
            ):
                self.assertIn(fact, text, f"{relative} is missing: {fact}")

    def test_unproven_areas_stay_in_the_not_yet_proven_section(self) -> None:
        section = read("PROJECT_STATUS.md").split("## Not yet proven")[1]
        section = section.split("\n## ")[0]
        for area in (
            "user value",
            "product quality",
            "Skill runtime",
            "Web UI and production RAG",
            "production model behavior",
            "latency, token, and cost",
        ):
            self.assertIn(area, section)


class OutputQuantityTests(unittest.TestCase):
    def test_scope_and_prd_make_counts_evidence_dependent(self) -> None:
        for relative in ("ACTIVE_SCOPE.md", "docs/01_MVP_PRD.md"):
            text = prose(relative).lower()
            self.assertIn("evidence-dependent", text)
            self.assertIn("never fill an output quota", text)
            self.assertIn("up to 3-5", text)
            self.assertIn("up to 2-3", text)

    def test_schema_still_allows_zero_highlights_and_bullets(self) -> None:
        schema = json.loads(read("schemas/application_pack.schema.json"))
        properties = schema["properties"]
        self.assertEqual(properties["project_highlights"]["minItems"], 0)
        self.assertEqual(properties["resume_bullets"]["minItems"], 0)


class GlossaryTests(unittest.TestCase):
    REQUIRED_TERMS = [
        "Project2Job",
        "Career Desk",
        "Skill",
        "Agent",
        "Evidence Investigator",
        "Work Order",
        "Public Day",
        "Application Pack",
        "Role Fit Map",
        "Evidence Status",
        "Supported",
        "Partially Supported",
        "Inferred",
        "Not Found",
        "Conflicting",
        "Needs Confirmation",
        "Evidence Boundary",
        "Source Reference",
        "Acceptance Criterion",
        "Eval Case",
        "Unit Test",
        "Implemented",
        "Tested",
        "Validated",
        "Planned",
        "One Next Build",
    ]

    def test_required_terms_are_defined(self) -> None:
        text = prose("GLOSSARY.md")
        for term in self.REQUIRED_TERMS:
            self.assertTrue(f"**{term}**" in text, f"Glossary is missing {term}")

    def test_project2job_is_the_canonical_name(self) -> None:
        glossary = prose("GLOSSARY.md")
        self.assertIn("canonical product and repository name", glossary)
        self.assertIn("legacy internal codename", glossary)
        self.assertIn(
            "Project2Job is the canonical product and repository name",
            prose("README.md"),
        )
        self.assertNotIn("Career Desk produces", prose("AGENTS.md"))


class TraceabilityTests(unittest.TestCase):
    def test_day_1_maps_every_ac_to_cases_and_tests(self) -> None:
        text = read("docs/build_journal/DAY_1.md")
        self.assertIn("## Acceptance traceability", text)
        for index in range(1, 13):
            self.assertIn(f"D1-AC-{index:02d}", text)

        test_names = {
            line.split("def ")[1].split("(")[0]
            for line in read("tests/test_agent_loop.py").splitlines()
            if line.strip().startswith("def test_")
        }
        case_ids = {
            json.loads(line)["case_id"]
            for line in read("lab/evals/day1_agent_loop_cases.jsonl").splitlines()
            if line.strip()
        }
        rows = [line for line in text.splitlines() if line.startswith("| D1-AC-")]
        self.assertEqual(len(rows), 12)
        for row in rows:
            cited_cases = set(re.findall(r"D1-\d{3}", row))
            self.assertTrue(cited_cases, f"Row cites no eval case: {row}")
            self.assertTrue(
                cited_cases <= case_ids,
                f"Row cites unknown eval cases {sorted(cited_cases - case_ids)}: {row}",
            )
            self.assertTrue(
                any(name in row for name in test_names),
                f"Row references no existing unit test: {row}",
            )


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(read("PROJECT_MANIFEST.json"))

    def test_active_document_count_is_unchanged(self) -> None:
        self.assertEqual(self.manifest["active_document_count"], 14)
        self.assertEqual(len(self.manifest["active_documents"]), 14)
        for governance_file in ("GLOSSARY.md", "docs/DOCUMENT_GOVERNANCE.md"):
            self.assertNotIn(governance_file, self.manifest["active_documents"])

    def test_governance_files_are_in_context_sets(self) -> None:
        context_sets = self.manifest["context_sets"]
        for name, files in context_sets.items():
            self.assertIn("GLOSSARY.md", files, f"{name} lacks the glossary")
        self.assertIn(
            "docs/DOCUMENT_GOVERNANCE.md", context_sets["shared_foundation"]
        )


if __name__ == "__main__":
    unittest.main()
