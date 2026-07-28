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
        self.assertEqual(len(cases), 38)
        self.assertEqual(len({case["id"] for case in cases}), 38)
        no_event = next(case for case in cases if case["id"] == "A11_NO_EVENT")
        self.assertIn("select strongest", no_event["must"])
        self.assertIn("dead end", no_event["must_not"])
        mock = next(case for case in cases if case["id"] == "A13_MOCK_LABEL")
        self.assertIn("Mock Interview — simulated practice", mock["must"])
        router = next(case for case in cases if case["id"] == "A14_ROUTER_OUTPUTS")
        self.assertIn(
            "JD_INTAKE returns canonical Intake Result",
            router["must"],
        )
        selective = next(
            case for case in cases if case["id"] == "A29_SELECTIVE_INVOCATION"
        )
        self.assertIn("zero specialist invocations", selective["must"])
        full = next(
            case for case in cases if case["id"] == "A28_CAPABILITY_PRESERVATION"
        )
        for skill in SKILLS[1:]:
            self.assertIn(skill, full["must"])
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

    def test_career_asset_packaging_regressions_cover_the_dogfood_failure(self) -> None:
        path = ROOT / "skill" / "p2j" / "evals" / "behavior_cases.jsonl"
        cases = {
            case["id"]: case
            for case in (
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        }
        expected = {
            "A21_LIMITATION_SEPARATION",
            "A22_PRIVATE_WARNING_PRESERVATION",
            "A23_DEFENSIBLE_CAPABILITY",
            "A24_DERIVATION_BOUNDARY",
            "A25_DAY5_FAILURE_ENDING",
            "A26_COMPANY_SUBSET",
            "A27_SPOKEN_USABILITY",
        }
        self.assertTrue(expected.issubset(cases))
        for case_id in expected:
            with self.subTest(case=case_id):
                self.assertTrue(cases[case_id]["must"])
                self.assertTrue(cases[case_id]["must_not"])

        leakage = cases["A21_LIMITATION_SEPARATION"]
        self.assertIn(
            "pending human review, missing production validation, and absent user impact stay outside the main script",
            leakage["must"],
        )
        private = cases["A22_PRIVATE_WARNING_PRESERVATION"]
        self.assertIn("delete the risk from the pack", private["must_not"])
        derived = cases["A23_DEFENSIBLE_CAPABILITY"]
        self.assertIn(
            "derive a defensible AI PM capability from linked facts",
            derived["must"],
        )
        fabrication = cases["A24_DERIVATION_BOUNDARY"]["must_not"]
        for prohibited in (
            "claim production launch",
            "claim user outcome",
            "invent a metric",
            "invent a stakeholder relationship",
            "assign personal ownership",
        ):
            self.assertIn(prohibited, fabrication)
        failure = cases["A25_DAY5_FAILURE_ENDING"]
        self.assertEqual(
            failure["origin"],
            "docs/dogfood/PROJECT2JOB_DAY5_CAREER_ASSET_DOGFOOD.md",
        )
        self.assertIn(
            "end on containment, product decision, resulting control, repeat-prevention, or AI PM judgment",
            failure["must"],
        )
        self.assertIn(
            "claim independent user validation or hiring impact",
            failure["must_not"],
        )
        company = cases["A26_COMPANY_SUBSET"]
        self.assertIn("company may change selected verified fact subset", company["must"])
        self.assertIn("require identical selected fact IDs", company["must_not"])
        spoken = cases["A27_SPOKEN_USABILITY"]
        self.assertIn("concise conversational language", spoken["must"])
        self.assertIn("multiple disclaimer sentences", spoken["must_not"])

    def test_shared_packaging_policy_is_canonical_and_consumed(self) -> None:
        standard = (
            ROOT / "docs" / "07_SHARED_EVIDENCE_AND_OUTPUT_STANDARD.md"
        ).read_text(encoding="utf-8")
        for rule in (
            "Maximize hiring impact through the strongest defensible interpretation",
            "Historical fact boundary",
            "Defensible interpretation",
            "Strategic framing",
            "Private risk separation",
            "Material disclosure",
            "Failure stories",
            "Company relevance",
            "Spoken quality",
        ):
            self.assertIn(rule, standard)

        core = (
            ROOT / "skill" / "p2j" / "references" / "core-contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "`docs/07_SHARED_EVIDENCE_AND_OUTPUT_STANDARD.md`",
            core,
        )
        for skill_name in ("p2j-answer", "p2j-mock"):
            text = (ROOT / "skill" / skill_name / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("career-asset packaging policy", text)

    def test_answer_engine_removes_self_disqualifying_rules(self) -> None:
        engine = (
            ROOT / "skill" / "p2j" / "references" / "interview-engine.md"
        ).read_text(encoding="utf-8")
        self.assertIn("strongest relevant subset of verified", engine)
        self.assertIn("Private Defense", engine)
        self.assertIn("false or materially misleading", engine)
        self.assertIn("short, conversational sentences", engine)
        self.assertNotIn("Preserve limitations.", engine)
        self.assertNotIn("same verified fact IDs", engine)

        frameworks = (
            ROOT / "skill" / "p2j" / "references" / "frameworks.md"
        ).read_text(encoding="utf-8")
        normalized_frameworks = " ".join(frameworks.split())
        self.assertIn(
            "End on that mechanism, decision, result, or capability",
            normalized_frameworks,
        )
        self.assertIn(
            "strongest current achievement, decision, or control",
            normalized_frameworks,
        )

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

    def test_profile_contract_and_schemas_ship_with_the_suite(self) -> None:
        contract = (
            ROOT / "skill" / "p2j" / "references" / "profile-contract.md"
        ).read_text(encoding="utf-8")
        for term in (
            "Project Evidence Profile",
            "Company Intelligence Profile",
            "JD Demand Map",
            "Full Preparation",
            "Private Defense",
        ):
            self.assertIn(term, contract)
        for name in (
            "project_evidence_profile.schema.json",
            "company_intelligence_profile.schema.json",
            "jd_demand_map.schema.json",
        ):
            self.assertTrue((ROOT / "schemas" / name).is_file())
        self.assertTrue((SCRIPTS / "profile_router.py").is_file())


if __name__ == "__main__":
    unittest.main()
