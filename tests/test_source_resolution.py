"""Regression coverage for the Day 5 exact-source failure.

Day 5 recorded a Project2Job run whose exported Project Highlight cited
`S01_project.md:2` for a claim that sits on absolute line 3. The run numbered
non-empty body lines instead of file lines, every citation in it was internally
consistent, and JSON Schema validation passed, so nothing caught it. These tests
pin the gate that now does.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "p2j" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from source_resolution import (  # noqa: E402
    BLANK_SPAN,
    OUT_OF_RANGE,
    RESOLVED,
    UNMAPPED_SOURCE,
    UNPARSED_LOCATION,
    parse_location,
    parse_source_arguments,
    resolve_refs,
    summarize,
)

PLAN_ONLY = ROOT / "lab" / "fixtures" / "fixture_project_plan_only.md"
SAMPLE_BRIEF = ROOT / "skill" / "p2j" / "examples" / "sample_brief.md"
SAMPLE_PROJECT = ROOT / "skill" / "p2j" / "examples" / "sample_project.md"
RECORDED_SKILL_S01 = ROOT / "lab" / "day5" / "outputs" / "skill" / "S01.json"
RECORDED_BASELINE_S02 = ROOT / "lab" / "day5" / "outputs" / "baseline" / "S02.json"
TEAM_PROJECT = ROOT / "lab" / "fixtures" / "fixture_team_project.md"


def ref(location: str, source_id: str = "SRC-PROJECT") -> dict[str, object]:
    return {"source_refs": [{"source_id": source_id, "location": location}]}


class LocationGrammarTests(unittest.TestCase):
    def lines(self, location: str) -> tuple[str | None, int, int]:
        parsed = parse_location(location)
        self.assertIsNotNone(parsed, location)
        self.assertEqual(parsed["kind"], "lines")
        return parsed["file"], parsed["start"], parsed["end"]

    def test_canonical_forms_parse(self) -> None:
        self.assertEqual(self.lines("S01_project.md:2"), ("S01_project.md", 2, 2))
        self.assertEqual(self.lines("S01_project.md:1-3"), ("S01_project.md", 1, 3))
        self.assertEqual(self.lines("line 3"), (None, 3, 3))
        self.assertEqual(self.lines("lines 3-5"), (None, 3, 5))
        self.assertEqual(self.lines("3"), (None, 3, 3))

    def test_en_dash_range_is_accepted(self) -> None:
        """Hosts rewrite hyphens; a rewritten range is still a real citation."""
        self.assertEqual(self.lines("lines 5–7"), (None, 5, 7))

    def test_reversed_range_is_normalized(self) -> None:
        self.assertEqual(self.lines("notes.md:7-5"), ("notes.md", 5, 7))

    def test_heading_anchors_parse(self) -> None:
        """A heading is a real anchor a reader can find.

        The first version of this gate accepted only line spans and would have
        rejected every citation in the Skill's own shipped Brief.
        """
        self.assertEqual(
            parse_location("sample_project.md#Problem and scope"),
            {
                "file": "sample_project.md",
                "kind": "heading",
                "heading": "Problem and scope",
            },
        )
        self.assertEqual(
            parse_location("#Technical plan"),
            {"file": None, "kind": "heading", "heading": "Technical plan"},
        )

    def test_prose_anchors_do_not_parse_as_line_numbers(self) -> None:
        """A trailing ordinal is not a line number.

        An earlier grammar read `Responsibilities, bullet 2` as line 2 and
        silently resolved a citation to unrelated text.
        """
        for location in (
            "Responsibilities, bullet 2",
            "Team Project, sentence 1",
            "Team Project, sentences 1–2",
            "Team Project, entire document",
        ):
            self.assertIsNone(parse_location(location), location)


class ResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = {"S01_project.md": PLAN_ONLY, "SRC-PROJECT": PLAN_ONLY}

    def status(self, location: str) -> str:
        return resolve_refs(ref(location), self.sources)[0]["status"]

    def test_blank_line_citation_does_not_resolve(self) -> None:
        """The exact BC-D5-001 failure mode, at the smallest scale."""
        self.assertEqual(self.status("S01_project.md:2"), BLANK_SPAN)

    def test_correct_absolute_line_resolves_to_the_claim(self) -> None:
        result = resolve_refs(ref("S01_project.md:3"), self.sources)[0]
        self.assertEqual(result["status"], RESOLVED)
        self.assertIn("20 cases", result["excerpt"])

    def test_line_span_covering_the_blank_line_still_resolves(self) -> None:
        """A range carrying real text is fine; only an empty span is not."""
        self.assertEqual(self.status("S01_project.md:1-3"), RESOLVED)

    def test_line_past_the_end_of_the_file_does_not_resolve(self) -> None:
        self.assertEqual(self.status("S01_project.md:99"), OUT_OF_RANGE)

    def test_prose_location_does_not_resolve(self) -> None:
        self.assertEqual(self.status("Team Project, sentence 1"), UNPARSED_LOCATION)

    def test_unknown_source_does_not_resolve(self) -> None:
        self.assertEqual(self.status("unknown_file.md:3"), UNMAPPED_SOURCE)

    def test_source_id_names_the_file_when_the_location_does_not(self) -> None:
        self.assertEqual(self.status("line 3"), RESOLVED)


class HeadingAnchorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = {"sample_project.md": SAMPLE_PROJECT}

    def resolve(self, location: str) -> dict:
        return resolve_refs(ref(location, "sample_project.md"), self.sources)[0]

    def test_heading_resolves_to_its_whole_section(self) -> None:
        result = self.resolve("sample_project.md#Problem and scope")
        self.assertEqual(result["status"], RESOLVED)
        self.assertIn("rejects automatic job", result["excerpt"])
        self.assertNotIn("Technical plan", result["excerpt"])

    def test_heading_match_ignores_case(self) -> None:
        self.assertEqual(
            self.resolve("sample_project.md#problem AND scope")["status"], RESOLVED
        )

    def test_absent_heading_does_not_resolve(self) -> None:
        self.assertEqual(
            self.resolve("sample_project.md#No Such Heading")["status"], OUT_OF_RANGE
        )

    def test_shipped_brief_citations_all_resolve(self) -> None:
        """Dogfood: the gate must not reject the product's own real output."""
        citations = re.findall(
            r"`([^`]+\.md#[^`]+)`", SAMPLE_BRIEF.read_text(encoding="utf-8")
        )
        self.assertEqual(len(citations), 7)
        summary = summarize(
            resolve_refs(
                {
                    "source_refs": [
                        {"source_id": item.split("#")[0], "location": item}
                        for item in citations
                    ]
                },
                self.sources,
            )
        )
        self.assertTrue(summary["all_resolve"], summary["unresolved"])

    def test_every_ref_is_reported_with_its_json_pointer(self) -> None:
        """A failure has to name the exported field, not just a count."""
        instance = {
            "project_highlights": [
                {"source_refs": [{"source_id": "SRC-PROJECT", "location": "S01_project.md:2"}]}
            ]
        }
        result = resolve_refs(instance, self.sources)[0]
        self.assertEqual(result["pointer"], "/project_highlights/0/source_refs/0")


class RecordedOutputTests(unittest.TestCase):
    """The two recorded Day 5 source failures stay reproducible."""

    def test_recorded_skill_s01_reproduces_the_blank_line_failure(self) -> None:
        instance = json.loads(RECORDED_SKILL_S01.read_text(encoding="utf-8"))
        summary = summarize(resolve_refs(instance, {"S01_project.md": PLAN_ONLY}))
        self.assertFalse(summary["all_resolve"])
        self.assertEqual(summary["total_refs"], 8)
        self.assertEqual(summary["counts"][BLANK_SPAN], 6)
        self.assertIn(
            "/project_highlights/0/source_refs/0",
            [item["pointer"] for item in summary["unresolved"]],
        )

    def test_recorded_baseline_s02_reproduces_the_unverifiable_format(self) -> None:
        instance = json.loads(RECORDED_BASELINE_S02.read_text(encoding="utf-8"))
        summary = summarize(resolve_refs(instance, {"S02_project.md": TEAM_PROJECT}))
        self.assertFalse(summary["all_resolve"])
        self.assertEqual(summary["counts"][UNPARSED_LOCATION], 19)
        self.assertEqual(summary["counts"][RESOLVED], 0)

    def test_rewriting_the_recorded_citations_to_absolute_lines_passes(self) -> None:
        """The fix is the convention, not the evidence.

        Re-anchoring the same recorded claims to absolute lines resolves every
        citation, which is what shows the failure was a location grammar
        mismatch rather than an unsupported claim.
        """
        raw = RECORDED_SKILL_S01.read_text(encoding="utf-8")
        corrected = json.loads(
            raw.replace("S01_project.md:2", "S01_project.md:3").replace(
                "S01_project.md:3-", "S01_project.md:4-"
            )
        )
        summary = summarize(resolve_refs(corrected, {"S01_project.md": PLAN_ONLY}))
        self.assertTrue(summary["all_resolve"], summary["unresolved"])


class ValidatorCommandTests(unittest.TestCase):
    """Schema validity and citation resolution must stay separate gates."""

    def run_validator(self, output: Path, *sources: str) -> tuple[int, dict]:
        command = [
            sys.executable,
            str(SCRIPTS / "validate_output.py"),
            str(output),
            "--schema",
            "application_pack",
        ]
        for source in sources:
            command.extend(["--source", source])
        completed = subprocess.run(command, capture_output=True, text=True)
        return completed.returncode, json.loads(completed.stdout)

    def test_schema_valid_output_still_fails_on_an_unresolved_citation(self) -> None:
        code, report = self.run_validator(
            RECORDED_SKILL_S01, f"S01_project.md={PLAN_ONLY}"
        )
        self.assertEqual(report["errors"], [])
        self.assertFalse(report["source_resolution"]["all_resolve"])
        self.assertEqual(code, 1)

    def test_resolution_is_skipped_when_no_source_is_supplied(self) -> None:
        """Pasted-excerpt runs have no file to resolve against."""
        code, report = self.run_validator(RECORDED_SKILL_S01)
        self.assertNotIn("source_resolution", report)
        self.assertEqual(code, 0)

    def test_a_missing_source_file_is_an_argument_error(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            code, report = self.run_validator(
                RECORDED_SKILL_S01, f"S01_project.md={Path(name) / 'absent.md'}"
            )
        self.assertEqual(code, 2)
        self.assertFalse(report["valid"])

    def test_source_arguments_accept_a_bare_path(self) -> None:
        sources = parse_source_arguments([str(PLAN_ONLY)])
        self.assertEqual(sources, {PLAN_ONLY.name: PLAN_ONLY})


if __name__ == "__main__":
    unittest.main()
