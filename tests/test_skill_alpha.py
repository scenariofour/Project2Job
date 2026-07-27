from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "p2j" / "scripts"
SKILLS = (
    "p2j",
    "p2j-brief",
    "p2j-audit",
    "p2j-intel",
    "p2j-answer",
    "p2j-mock",
    "p2j-upgrade",
)

sys.path.insert(0, str(SCRIPTS))
from inventory import inventory  # noqa: E402
from validate_suite import validate  # noqa: E402


class SkillSuiteTests(unittest.TestCase):
    def test_source_suite_validates(self) -> None:
        self.assertEqual(validate(ROOT / "skill"), [])

    def test_specialists_share_one_contract_owner(self) -> None:
        for name in SKILLS[1:]:
            text = (ROOT / "skill" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("../p2j/references/", text)
            self.assertNotIn("### D1.", text)
            self.assertNotIn("max_search_queries", text)

    def test_inventory_is_read_only_and_exposes_git_as_a_lead(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "inventory.py"),
                str(ROOT / "examples" / "sample_project"),
                "--summary",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        output = json.loads(result.stdout)
        self.assertGreater(output["file_count"], 0)
        self.assertIn("not proof", output["notice"])
        self.assertIn("git", output)
        self.assertIn("evidence_candidates", output)
        self.assertNotIn("files", output)

    def test_inventory_scopes_git_history_to_project_subdirectory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            project = repository / "project"
            sibling = repository / "sibling"
            project.mkdir()
            sibling.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(
                ["git", "config", "user.name", "Project2Job Test"],
                cwd=repository,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=repository,
                check=True,
            )
            (project / "project.txt").write_text("project\n", encoding="utf-8")
            subprocess.run(["git", "add", "project"], cwd=repository, check=True)
            subprocess.run(
                ["git", "commit", "-qm", "project evidence"],
                cwd=repository,
                check=True,
            )
            (sibling / "sibling.txt").write_text("sibling\n", encoding="utf-8")
            subprocess.run(["git", "add", "sibling"], cwd=repository, check=True)
            subprocess.run(
                ["git", "commit", "-qm", "unrelated sibling"],
                cwd=repository,
                check=True,
            )
            subjects = [
                item["subject"]
                for item in inventory(project)["git"]["recent_commits"]
            ]
            self.assertEqual(subjects, ["project evidence"])

    def test_install_is_self_contained_and_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "skills"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "install_suite.py"),
                    "--dest",
                    str(destination),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(validate(destination, require_canonical=True), [])
            self.assertTrue(
                (
                    destination
                    / "p2j"
                    / "references"
                    / "canonical"
                    / "schemas"
                    / "application_pack.schema.json"
                ).is_file()
            )
            contract = json.loads(
                (
                    destination
                    / "p2j"
                    / "references"
                    / "canonical"
                    / "references"
                    / "shared_contract.v1.json"
                ).read_text(encoding="utf-8")
            )
            referenced = [
                contract["role_profile"]["path"],
                contract["gold_dataset"]["path"],
                *(item["path"] for item in contract["schemas"].values()),
            ]
            for relative in referenced:
                self.assertTrue(
                    (
                        destination
                        / "p2j"
                        / "references"
                        / "canonical"
                        / relative
                    ).is_file(),
                    relative,
                )
            self.assertTrue(
                (destination / "p2j" / "scripts" / "validate_output.py").is_file()
            )
            self.assertTrue(
                (destination / "p2j" / "scripts" / "context_registry.py").is_file()
            )
            for name in ("sample_jd.md", "sample_project.md", "sample_brief.md"):
                self.assertTrue(
                    (destination / "p2j" / "examples" / name).is_file(),
                    name,
                )

    def test_archive_contains_all_invocable_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "suite.zip"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "install_suite.py"),
                    "--archive",
                    str(archive),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            with zipfile.ZipFile(archive) as bundle:
                names = set(bundle.namelist())
            for skill in SKILLS:
                self.assertIn(
                    f"project2job-skill-suite/{skill}/SKILL.md",
                    names,
                )
            self.assertFalse(
                any("__pycache__" in name or name.endswith((".pyc", ".pyo")) for name in names)
            )

    def test_behavior_eval_covers_user_contract(self) -> None:
        path = ROOT / "skill" / "p2j" / "evals" / "behavior_cases.jsonl"
        cases = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(cases), 20)
        self.assertEqual(len({case["id"] for case in cases}), 20)
        no_event = next(case for case in cases if case["id"] == "A11_NO_EVENT")
        self.assertIn("select strongest", no_event["must"])
        self.assertIn("dead end", no_event["must_not"])
        mock = next(case for case in cases if case["id"] == "A13_MOCK_LABEL")
        self.assertIn("Mock Interview — simulated practice", mock["must"])
        router = next(case for case in cases if case["id"] == "A14_ROUTER_OUTPUTS")
        self.assertIn(
            "APPLICATION_PACK leads with concise Brief then completes canonical pack",
            router["must"],
        )
        upgrade = next(case for case in cases if case["id"] == "A12_NEXT_BUILD")
        for behavior in (
            "gap and JD mismatch diagnosis",
            "one evidence direction",
            "capability category may use JD or company evidence",
            "concrete subclasses come from Project inspection",
            "bounded product-fit exploration",
            "human-reviewed evidence for subjective quality",
            "proposed work preserves current Match",
            "EXACT MATCH, TRANSFERABLE, and GAP only",
        ):
            self.assertIn(behavior, upgrade["must"])

    def test_brief_contract_is_project_focused_and_hides_internal_scoring(self) -> None:
        text = (ROOT / "skill" / "p2j-brief" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("at most eight", text)
        self.assertIn("Do not run project tests, builds, or", text)
        for section in (
            "Project Verdict",
            "Preliminary Project Scores",
            "JD Match",
            "Interview Value",
            "Recommended Route",
        ):
            self.assertIn(section, text)
        for dimension in (
            "Problem & User Evidence",
            "Product Judgment",
            "Technical System",
            "Evaluation & Reliability",
            "Delivery &",
            "Learning Loop",
        ):
            self.assertIn(dimension, text)
        self.assertIn("`**EXACT MATCH**`", text)
        self.assertIn("`TRANSFERABLE`", text)
        self.assertIn("`` `GAP` ``", text)
        self.assertIn("return as many as the evidence", text)
        self.assertIn("select exactly one of", text)
        self.assertIn("absent ownership metadata", text)
        self.assertNotIn("Preliminary Gate Scores", text)
        self.assertNotIn("Highest-Priority Questions", text)

    def test_all_skills_resolve_shared_context(self) -> None:
        router = (ROOT / "skill" / "p2j" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("context_registry.py", router)
        for name in SKILLS[1:]:
            text = (ROOT / "skill" / name / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Resolve shared context", text)

    def test_sample_brief_uses_only_public_project_language(self) -> None:
        text = (ROOT / "skill" / "p2j" / "examples" / "sample_brief.md").read_text(
            encoding="utf-8"
        )
        for section in (
            "## Project Verdict",
            "## Preliminary Project Scores",
            "## JD Match",
            "## Interview Value",
            "## Recommended Route",
        ):
            self.assertIn(section, text)
        self.assertNotIn("Preliminary Gate Scores", text)
        self.assertNotRegex(text, r"\bG[1-6]\b")
        self.assertNotRegex(text, r"\bD(?:10|[1-9])\b")

    def test_answer_and_audit_bound_forensics(self) -> None:
        audit = (ROOT / "skill" / "p2j-audit" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        answer = (ROOT / "skill" / "p2j-answer" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("no more than six evidence searches", audit)
        self.assertIn("no more than twenty line-targeted", audit)
        self.assertIn("Do not concatenate whole files", audit)
        self.assertIn("do not execute project tests or code", audit)
        self.assertIn("at most twelve line-targeted sections", answer)
        self.assertIn("Do not execute project code or", answer)
        self.assertIn("reserve at least one section for the implementation", answer)
        self.assertIn("do not turn that search omission", answer)

    def test_intel_keeps_operating_headroom_below_schema_ceiling(self) -> None:
        engine = (
            ROOT / "skill" / "p2j" / "references" / "interview-engine.md"
        ).read_text(encoding="utf-8")
        self.assertIn("6 queries", engine)
        self.assertIn("8 fetched pages", engine)
        self.assertIn("45,000", engine)
        self.assertIn("including total tokens and runtime", engine)


if __name__ == "__main__":
    unittest.main()
