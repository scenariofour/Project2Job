from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "p2j" / "scripts" / "context_registry.py"
sys.path.insert(0, str(SCRIPT.parent))
import context_registry as registry_module  # noqa: E402


class ContextRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.home = self.root / "p2j-home"
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "README.md").write_text(
            "A bounded AI workflow with an evaluation plan.\n", encoding="utf-8"
        )
        self.jd = self.root / "jd.txt"
        self.jd.write_text("Build reliable AI product workflows.\n", encoding="utf-8")
        self.analysis = self.root / "analysis.json"
        self.analysis.write_text(
            json.dumps(
                {
                    "confirmed_facts": [
                        {
                            "fact_id": "fact-workflow",
                            "text": "The project implements a bounded workflow.",
                            "status": "supported",
                            "source_paths": ["README.md"],
                        },
                        {
                            "fact_id": "fact-owner",
                            "text": "The user confirmed ownership of product scoping.",
                            "status": "supported",
                            "source_paths": [],
                        },
                    ],
                    "ownership_boundaries": [
                        {
                            "claim_id": "ownership-scope",
                            "boundary": "Product scoping is confirmed; implementation is shared.",
                            "status": "confirmed",
                            "source_paths": [],
                        }
                    ],
                    "resolved_question_ids": ["ownership-scope"],
                    "unresolved_questions": [],
                    "known_gaps": [
                        {
                            "gap_id": "gap-users",
                            "text": "No primary user research is present.",
                            "source_paths": ["README.md"],
                        }
                    ],
                    "evidence": [
                        {
                            "path": "README.md",
                            "source_id": "source-readme",
                            "location": "README.md:1",
                            "status": "supported",
                        }
                    ],
                    "scores": {"Problem & User Evidence": 2},
                    "matches": [
                        {
                            "requirement": "Reliable AI workflows",
                            "match": "EXACT MATCH",
                        }
                    ],
                    "reused_fact_ids": [],
                    "output_references": ["outputs/brief.json"],
                    "recommended_route": "$p2j-audit",
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def command(
        self,
        *arguments: str,
        check: bool = True,
        home: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["P2J_HOME"] = str(home or self.home)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            check=check,
            capture_output=True,
            text=True,
            env=environment,
        )

    def save(self, *, consent: bool = False, skill: str = "p2j-brief") -> dict:
        arguments = [
            "save-run",
            "--project",
            str(self.project),
            "--jd-file",
            str(self.jd),
            "--skill",
            skill,
            "--analysis",
            str(self.analysis),
        ]
        if consent:
            arguments.append("--consent")
        return json.loads(self.command(*arguments).stdout)

    def resolve(self, *extra: str, project: Path | None = None) -> dict:
        return json.loads(
            self.command(
                "resolve",
                "--project",
                str(project or self.project),
                "--jd-file",
                str(self.jd),
                *extra,
            ).stdout
        )

    def registry(self) -> dict:
        return json.loads(
            (self.home / "context-registry.json").read_text(encoding="utf-8")
        )

    def test_first_saved_run_requires_consent_and_creates_three_record_types(self) -> None:
        failed = self.command(
            "save-run",
            "--project",
            str(self.project),
            "--jd-file",
            str(self.jd),
            "--skill",
            "p2j-brief",
            "--analysis",
            str(self.analysis),
            check=False,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("one-time consent", failed.stderr)
        self.assertFalse(self.home.exists())

        result = self.save(consent=True)
        self.assertTrue(result["saved"])
        registry = self.registry()
        self.assertEqual(len(registry["projects"]), 1)
        self.assertEqual(len(registry["jds"]), 1)
        self.assertEqual(len(registry["analysis_runs"]), 1)

    def test_unchanged_context_and_brief_are_reused_in_a_separate_process(self) -> None:
        self.save(consent=True)
        result = self.resolve()
        self.assertEqual(result["context_state"], "unchanged")
        self.assertTrue(result["reuse_notice"])
        self.assertEqual(result["compatible_runs"][0]["skill"], "p2j-brief")
        self.assertEqual(result["project_version"], 1)
        self.assertEqual(result["jd_version"], 1)

    def test_unchanged_files_reuse_cached_fingerprints(self) -> None:
        self.save(consent=True)
        stored = registry_module.load_registry(self.home)
        identity = registry_module.project_identity(self.project)
        project = stored["projects"][0]
        with patch("inventory.sha256", side_effect=AssertionError("rehash")):
            snapshot = registry_module.project_snapshot(identity, project)
        self.assertEqual(
            snapshot["fingerprint"], project["versions"][-1]["fingerprint"]
        )

    def test_confirmed_ownership_is_reused_without_repeating_a_question(self) -> None:
        self.save(consent=True)
        result = self.resolve()
        self.assertEqual(
            result["reusable"]["ownership_boundaries"][0]["status"], "confirmed"
        )
        self.assertEqual(result["reusable"]["unresolved_questions"], [])

    def test_audit_can_continue_from_prior_brief_context(self) -> None:
        self.save(consent=True)
        result = self.resolve()
        skills = {run["skill"] for run in result["compatible_runs"]}
        self.assertIn("p2j-brief", skills)

    def test_project_run_can_reuse_prior_jd_only_intelligence(self) -> None:
        self.command(
            "save-run",
            "--jd-file",
            str(self.jd),
            "--skill",
            "p2j-intel",
            "--analysis",
            str(self.analysis),
            "--consent",
        )
        result = self.resolve()
        skills = {run["skill"] for run in result["compatible_runs"]}
        self.assertIn("p2j-intel", skills)

    def test_moved_git_repository_with_same_remote_has_same_identity(self) -> None:
        remote = "https://github.com/example/project2job-context-test.git"
        for project in (self.project, self.root / "moved-project"):
            project.mkdir(exist_ok=True)
            if not (project / "README.md").exists():
                (project / "README.md").write_text(
                    "A bounded AI workflow with an evaluation plan.\n",
                    encoding="utf-8",
                )
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            subprocess.run(["git", "remote", "add", "origin", remote], cwd=project, check=True)

        self.save(consent=True)
        result = self.resolve(project=self.root / "moved-project")
        self.assertEqual(result["context_state"], "unchanged")
        self.assertTrue(result["reuse_notice"])

    def test_multiple_git_remotes_without_origin_are_identity_ambiguous(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        subprocess.run(
            ["git", "remote", "add", "one", "https://example.invalid/one.git"],
            cwd=self.project,
            check=True,
        )
        subprocess.run(
            ["git", "remote", "add", "two", "https://example.invalid/two.git"],
            cwd=self.project,
            check=True,
        )
        result = self.resolve()
        self.assertEqual(result["context_state"], "identity_ambiguous")
        self.assertEqual(result["compatible_runs"], [])

    def test_project_and_jd_changes_create_new_versions(self) -> None:
        self.save(consent=True)
        (self.project / "evals.json").write_text('{"passed": 3}\n', encoding="utf-8")
        self.jd.write_text(
            "Build reliable AI product workflows and lead evaluation.\n",
            encoding="utf-8",
        )
        changed = self.resolve()
        self.assertEqual(changed["context_state"], "both_changed")
        self.assertIn("evals.json", changed["changes"]["added"])
        self.assertIn("jd_match", changed["recompute"])

        saved = self.save()
        self.assertEqual(saved["project_version"], 2)
        self.assertEqual(saved["jd_version"], 2)

    def test_same_jd_url_with_changed_content_creates_a_new_version(self) -> None:
        url = "https://jobs.example.invalid/roles/ai-pm"
        first = self.command(
            "save-run",
            "--project",
            str(self.project),
            "--jd-file",
            str(self.jd),
            "--jd-url",
            url,
            "--skill",
            "p2j-brief",
            "--analysis",
            str(self.analysis),
            "--consent",
        )
        self.assertEqual(json.loads(first.stdout)["jd_version"], 1)
        self.jd.write_text("Lead evaluation for AI workflows.\n", encoding="utf-8")
        second = self.command(
            "save-run",
            "--project",
            str(self.project),
            "--jd-file",
            str(self.jd),
            "--jd-url",
            url,
            "--skill",
            "p2j-brief",
            "--analysis",
            str(self.analysis),
        )
        self.assertEqual(json.loads(second.stdout)["jd_version"], 2)
        self.assertEqual(len(self.registry()["jds"]), 1)

    def test_unaffected_facts_survive_and_changed_artifacts_invalidate_dependents(self) -> None:
        self.save(consent=True)
        (self.project / "README.md").write_text(
            "The workflow design changed.\n", encoding="utf-8"
        )
        changed = self.resolve()
        fact_ids = {
            fact["fact_id"] for fact in changed["reusable"]["confirmed_facts"]
        }
        self.assertNotIn("fact-workflow", fact_ids)
        self.assertIn("fact-owner", fact_ids)
        self.assertEqual(
            changed["invalidated_output_references"], ["outputs/brief.json"]
        )
        self.assertIn("dependent_scores", changed["recompute"])

    def test_removed_artifact_invalidates_dependent_output(self) -> None:
        self.save(consent=True)
        (self.project / "README.md").unlink()
        changed = self.resolve()
        self.assertEqual(changed["changes"]["removed"], ["README.md"])
        self.assertEqual(
            changed["invalidated_output_references"], ["outputs/brief.json"]
        )

    def test_analyze_from_scratch_bypasses_reuse_without_deleting_history(self) -> None:
        self.save(consent=True)
        result = self.resolve("--mode", "fresh")
        self.assertEqual(result["compatible_runs"], [])
        self.assertEqual(result["reusable"]["confirmed_facts"], [])
        self.assertEqual(len(self.registry()["analysis_runs"]), 1)

    def test_refresh_recomputes_results_but_retains_confirmed_facts(self) -> None:
        self.save(consent=True)
        result = self.resolve("--mode", "refresh")
        self.assertEqual(result["compatible_runs"], [])
        fact_ids = {
            fact["fact_id"] for fact in result["reusable"]["confirmed_facts"]
        }
        self.assertIn("fact-owner", fact_ids)
        self.assertIn("project_scores", result["recompute"])
        self.assertEqual(len(self.registry()["analysis_runs"]), 1)

    def test_do_not_save_writes_nothing(self) -> None:
        result = json.loads(
            self.command(
                "save-run",
                "--project",
                str(self.project),
                "--jd-file",
                str(self.jd),
                "--skill",
                "p2j-brief",
                "--analysis",
                str(self.analysis),
                "--do-not-save",
            ).stdout
        )
        self.assertFalse(result["saved"])
        self.assertFalse(self.home.exists())

    def test_forget_removes_only_selected_project_context(self) -> None:
        self.save(consent=True)
        result = json.loads(
            self.command("forget", "--project", str(self.project)).stdout
        )
        self.assertEqual(result["forgotten"]["projects"], 1)
        registry = self.registry()
        self.assertEqual(registry["projects"], [])
        self.assertEqual(registry["analysis_runs"], [])
        self.assertEqual(len(registry["jds"]), 1)

    def test_corrupted_context_fails_safely_and_visibly(self) -> None:
        self.home.mkdir()
        path = self.home / "context-registry.json"
        path.write_text("{not-json", encoding="utf-8")
        result = self.command(
            "resolve",
            "--project",
            str(self.project),
            "--jd-file",
            str(self.jd),
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("corrupted or unreadable", result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), "{not-json")

    def test_structurally_corrupt_context_is_not_reused_or_overwritten(self) -> None:
        self.home.mkdir()
        path = self.home / "context-registry.json"
        malformed = {
            "schema_version": "1.0.0",
            "projects": [{}],
            "jds": [],
            "analysis_runs": [],
        }
        path.write_text(json.dumps(malformed), encoding="utf-8")
        result = self.command(
            "resolve",
            "--project",
            str(self.project),
            "--jd-file",
            str(self.jd),
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid projects record", result.stderr)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), malformed)

    def test_registry_rejects_secrets_and_never_persists_source_bodies(self) -> None:
        secret_analysis = self.root / "secret-analysis.json"
        secret_analysis.write_text(
            json.dumps(
                {
                    "confirmed_facts": [
                        {
                            "fact_id": "secret",
                            "text": "Token sk-abcdefghijklmnopqrstuvwxyz123456",
                            "status": "supported",
                            "source_paths": ["README.md"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        rejected = self.command(
            "save-run",
            "--project",
            str(self.project),
            "--jd-file",
            str(self.jd),
            "--skill",
            "p2j-brief",
            "--analysis",
            str(secret_analysis),
            "--consent",
            check=False,
        )
        self.assertNotEqual(rejected.returncode, 0)
        self.assertFalse((self.home / "context-registry.json").exists())
        self.assertFalse((self.home / "consent.json").exists())

        self.save(consent=True)
        stored = (self.home / "context-registry.json").read_text(encoding="utf-8")
        self.assertNotIn(
            "A bounded AI workflow with an evaluation plan.", stored
        )
        self.assertNotIn("Build reliable AI product workflows.", stored)

    def test_p2j_home_isolates_context(self) -> None:
        self.save(consent=True)
        other = self.root / "other-home"
        result = self.command(
            "resolve",
            "--project",
            str(self.project),
            "--jd-file",
            str(self.jd),
            home=other,
        )
        self.assertEqual(json.loads(result.stdout)["context_state"], "new")
        self.assertFalse(other.exists())


if __name__ == "__main__":
    unittest.main()
