from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skill" / "p2j" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import context_registry  # noqa: E402
import profile_router  # noqa: E402


class SelectiveSkillRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "README.md").write_text(
            "A source-grounded AI product workflow.\n", encoding="utf-8"
        )
        self.jd_one = self.root / "jd-one.txt"
        self.jd_two = self.root / "jd-two.txt"
        self.jd_one.write_text(
            "Lead AI evaluation and reliability decisions.\n", encoding="utf-8"
        )
        self.jd_two.write_text(
            "Ship agent workflows and improve adoption.\n", encoding="utf-8"
        )
        identity = context_registry.project_identity(self.project)
        self.project_snapshot = context_registry.project_snapshot(identity)
        self.project_profile = {
            "schema_version": "1.0.0",
            "profile_id": "project-profile-1",
            "project_fingerprint": self.project_snapshot["fingerprint"],
            "built_at": "2026-07-28T12:00:00+00:00",
            "sections": {
                name: {"items": [], "source_paths": ["README.md"]}
                for name in profile_router.PROJECT_SECTIONS
            },
        }
        self.company_profile = {
            "schema_version": "1.0.0",
            "profile_key": profile_router.company_profile_key(
                "OpenAI", "AI product"
            ),
            "company": "OpenAI",
            "track": "AI product",
            "researched_at": "2026-07-28T12:00:00+00:00",
            "fresh_until": "2026-08-27T12:00:00+00:00",
            "source_fingerprint": "a" * 64,
            "signals": {
                "culture_and_values": [],
                "product_and_ai_direction": [],
                "role_or_team_priorities": [],
                "interview_signals": [],
            },
            "sources": [],
        }
        self.jd_map_one = self.jd_map(self.jd_one)
        self.jd_map_two = self.jd_map(self.jd_two)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def jd_map(self, path: Path) -> dict:
        snapshot = context_registry.jd_snapshot(path)
        return {
            "schema_version": "1.0.0",
            "map_id": f"map-{path.stem}",
            "jd_fingerprint": snapshot["fingerprint"],
            "company_profile_key": self.company_profile["profile_key"],
            "extracted_at": "2026-07-28T12:00:00+00:00",
            "role_tasks": ["Build reliable AI products"],
            "level": "unknown",
            "hiring_signals": ["AI evaluation judgment"],
            "must_haves": ["Product judgment"],
            "preferred_qualifications": [],
        }

    def test_capability_preservation_and_explicit_full_preparation(self) -> None:
        plan = profile_router.plan_request(
            "full_preparation",
            project_profile=None,
            company_profile=None,
            jd_demand_map=None,
        )
        self.assertEqual(
            plan["skill_invocations"],
            [
                "p2j-brief",
                "p2j-intel",
                "p2j-audit",
                "p2j-answer",
                "p2j-mock",
                "p2j-upgrade",
            ],
        )
        self.assertEqual(
            set(profile_router.CAPABILITY_ROUTES),
            {
                "brief",
                "company_intelligence",
                "evidence_audit",
                "interview_answer",
                "mock_interview",
                "project_upgrade",
            },
        )

    def test_normal_resume_request_invokes_no_specialist_when_profiles_are_fresh(self) -> None:
        plan = profile_router.plan_request(
            "resume_bullets",
            project_profile=self.project_profile,
            company_profile=self.company_profile,
            jd_demand_map=self.jd_map_one,
            now=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        self.assertEqual(plan["skill_invocations"], [])
        self.assertEqual(plan["asset_generation"], ["resume_bullets"])
        self.assertIn("select_one_strongest_story", plan["model_tasks"])
        self.assertEqual(plan["questions"], [])

    def test_default_brief_builds_company_context_without_forcing_audit(self) -> None:
        plan = profile_router.plan_request(
            "brief",
            project_profile=None,
            company_profile=None,
            jd_demand_map=None,
        )
        self.assertEqual(plan["skill_invocations"], ["p2j-intel", "p2j-brief"])
        self.assertNotIn("p2j-audit", plan["skill_invocations"])
        self.assertIn(
            "build_or_refresh_company_intelligence_profile", plan["model_tasks"]
        )

        reused = profile_router.plan_request(
            "brief",
            project_profile=None,
            company_profile=self.company_profile,
            jd_demand_map=self.jd_map_one,
            now=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        self.assertEqual(reused["skill_invocations"], ["p2j-brief"])
        self.assertIn("adapt_to_company_culture_and_jd", reused["model_tasks"])

    def test_project_only_brief_uses_default_role_without_company_research(self) -> None:
        plan = profile_router.plan_request(
            "brief",
            project_profile=None,
            company_profile=None,
            jd_demand_map=None,
            company_context_required=False,
        )
        self.assertEqual(plan["skill_invocations"], ["p2j-brief"])
        self.assertNotIn("p2j-intel", plan["skill_invocations"])
        self.assertNotIn("fingerprint_jd", plan["deterministic_tasks"])
        self.assertNotIn("adapt_to_company_culture_and_jd", plan["model_tasks"])

    def test_project_profile_reuses_across_jds_without_reopening_files(self) -> None:
        registry = context_registry.empty_registry()
        jd = context_registry.jd_snapshot(self.jd_one)
        analysis = {"project_evidence_profile": self.project_profile}
        saved, _ = context_registry.save_run(
            registry, self.project_snapshot, jd, "p2j-audit", analysis
        )
        with patch("inventory.sha256", side_effect=AssertionError("reread")):
            unchanged = context_registry.project_snapshot(
                context_registry.project_identity(self.project),
                saved["projects"][0],
            )
        resolved = context_registry.resolve_context(
            saved,
            unchanged,
            context_registry.jd_snapshot(self.jd_two),
            company="OpenAI",
            track="AI product",
            now=datetime(2026, 7, 28, tzinfo=timezone.utc),
        )
        self.assertEqual(resolved["profiles"]["project_evidence"]["state"], "hit")
        self.assertEqual(
            resolved["profiles"]["project_evidence"]["profile"]["profile_id"],
            "project-profile-1",
        )

    def test_changed_project_returns_only_affected_profile_sections(self) -> None:
        registry = context_registry.empty_registry()
        saved, _ = context_registry.save_run(
            registry,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_one),
            "p2j-audit",
            {"project_evidence_profile": self.project_profile},
        )
        (self.project / "README.md").write_text(
            "The source-grounded workflow changed.\n", encoding="utf-8"
        )
        changed_snapshot = context_registry.project_snapshot(
            context_registry.project_identity(self.project),
            saved["projects"][0],
        )
        resolved = context_registry.resolve_context(
            saved,
            changed_snapshot,
            context_registry.jd_snapshot(self.jd_one),
        )
        project = resolved["profiles"]["project_evidence"]
        self.assertEqual(project["state"], "partial")
        self.assertEqual(project["changed_source_paths"], ["README.md"])
        self.assertEqual(
            project["affected_sections"], sorted(profile_router.PROJECT_SECTIONS)
        )

    def test_added_project_file_requires_surface_inspection_for_all_sections(self) -> None:
        registry = context_registry.empty_registry()
        saved, _ = context_registry.save_run(
            registry,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_one),
            "p2j-audit",
            {"project_evidence_profile": self.project_profile},
        )
        evals = self.project / "evals"
        evals.mkdir()
        (evals / "new-results.json").write_text(
            '{"severe_bad_cases": 0}\n', encoding="utf-8"
        )
        changed_snapshot = context_registry.project_snapshot(
            context_registry.project_identity(self.project),
            saved["projects"][0],
        )
        resolved = context_registry.resolve_context(
            saved,
            changed_snapshot,
            context_registry.jd_snapshot(self.jd_one),
        )
        project = resolved["profiles"]["project_evidence"]
        self.assertEqual(project["state"], "partial")
        self.assertEqual(project["added_source_paths"], ["evals/new-results.json"])
        self.assertTrue(project["surface_inspection_required"])
        self.assertEqual(
            project["affected_sections"], sorted(profile_router.PROJECT_SECTIONS)
        )

        plan = profile_router.plan_request(
            "project_introduction",
            project_profile=project["profile"],
            company_profile=self.company_profile,
            jd_demand_map=self.jd_map_one,
            affected_project_sections=project["affected_sections"],
            added_project_sources=project["added_source_paths"],
        )
        self.assertIn(
            "inspect_added_project_evidence_surfaces",
            plan["deterministic_tasks"],
        )
        self.assertIn(
            "update_potentially_affected_project_profile_sections",
            plan["model_tasks"],
        )

    def test_company_profile_reuses_across_jds_until_stale(self) -> None:
        registry = context_registry.empty_registry()
        saved, _ = context_registry.save_run(
            registry,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_one),
            "p2j-intel",
            {
                "company_intelligence_profile": self.company_profile,
                "jd_demand_map": self.jd_map_one,
            },
        )
        fresh = context_registry.resolve_context(
            saved,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_two),
            company="OpenAI",
            track="AI product",
            now=datetime(2026, 7, 29, tzinfo=timezone.utc),
        )
        self.assertEqual(fresh["profiles"]["company_intelligence"]["state"], "hit")
        self.assertEqual(fresh["profiles"]["jd_demand"]["state"], "miss")

        stale = context_registry.resolve_context(
            saved,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_two),
            company="OpenAI",
            track="AI product",
            now=datetime(2026, 9, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(stale["profiles"]["company_intelligence"]["state"], "stale")

        changed = context_registry.resolve_context(
            saved,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_two),
            company="OpenAI",
            track="AI product",
            company_source_fingerprint="b" * 64,
            now=datetime(2026, 7, 29, tzinfo=timezone.utc),
        )
        self.assertEqual(
            changed["profiles"]["company_intelligence"]["state"], "stale"
        )
        self.assertEqual(
            changed["profiles"]["company_intelligence"]["reason"],
            "material_change",
        )

    def test_company_profile_reuse_requires_exact_normalized_track(self) -> None:
        registry = context_registry.empty_registry()
        saved, _ = context_registry.save_run(
            registry,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_one),
            "p2j-intel",
            {"company_intelligence_profile": self.company_profile},
        )
        exact = context_registry.resolve_context(
            saved,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_two),
            company="  openai ",
            track=" AI   PRODUCT ",
            now=datetime(2026, 7, 29, tzinfo=timezone.utc),
        )
        self.assertEqual(exact["profiles"]["company_intelligence"]["state"], "hit")

        different = context_registry.resolve_context(
            saved,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_two),
            company="OpenAI",
            track="API infrastructure",
            now=datetime(2026, 7, 29, tzinfo=timezone.utc),
        )
        self.assertEqual(
            different["profiles"]["company_intelligence"]["state"], "miss"
        )

    def test_jd_map_reuse_requires_resolved_company_profile_key(self) -> None:
        registry = context_registry.empty_registry()
        saved, _ = context_registry.save_run(
            registry,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_one),
            "p2j-intel",
            {"company_intelligence_profile": self.company_profile},
        )
        mismatched_map = dict(self.jd_map_one)
        mismatched_map["company_profile_key"] = profile_router.company_profile_key(
            "OpenAI", "API infrastructure"
        )
        saved, _ = context_registry.save_run(
            saved,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_one),
            "p2j",
            {"jd_demand_map": mismatched_map},
        )
        resolved = context_registry.resolve_context(
            saved,
            self.project_snapshot,
            context_registry.jd_snapshot(self.jd_one),
            company="OpenAI",
            track="AI product",
            now=datetime(2026, 7, 29, tzinfo=timezone.utc),
        )
        self.assertEqual(resolved["profiles"]["company_intelligence"]["state"], "hit")
        self.assertEqual(resolved["profiles"]["jd_demand"]["state"], "mismatch")
        self.assertEqual(
            resolved["profiles"]["jd_demand"]["reason"],
            "company_profile_key_mismatch",
        )

        plan = profile_router.plan_request(
            "project_introduction",
            project_profile=self.project_profile,
            company_profile=self.company_profile,
            jd_demand_map=mismatched_map,
        )
        self.assertEqual(plan["profile_states"]["jd_demand"], "mismatch")
        self.assertIn("extract_lightweight_jd_demand_map", plan["model_tasks"])
        orphaned = profile_router.plan_request(
            "project_introduction",
            project_profile=self.project_profile,
            company_profile=None,
            jd_demand_map=self.jd_map_one,
        )
        self.assertEqual(orphaned["profile_states"]["jd_demand"], "miss")

    def test_registry_rejects_saving_mixed_company_and_jd_profile_keys(self) -> None:
        mismatched_map = dict(self.jd_map_one)
        mismatched_map["company_profile_key"] = profile_router.company_profile_key(
            "OpenAI", "API infrastructure"
        )
        with self.assertRaisesRegex(
            context_registry.RegistryError,
            "must match the saved Company Intelligence Profile",
        ):
            context_registry.save_run(
                context_registry.empty_registry(),
                self.project_snapshot,
                context_registry.jd_snapshot(self.jd_one),
                "p2j-intel",
                {
                    "company_intelligence_profile": self.company_profile,
                    "jd_demand_map": mismatched_map,
                },
            )

    def test_same_evidence_uses_distinct_jd_strategy_inputs(self) -> None:
        first = profile_router.plan_request(
            "interview_answer",
            project_profile=self.project_profile,
            company_profile=self.company_profile,
            jd_demand_map=self.jd_map_one,
        )
        second = profile_router.plan_request(
            "interview_answer",
            project_profile=self.project_profile,
            company_profile=self.company_profile,
            jd_demand_map=self.jd_map_two,
        )
        self.assertEqual(
            first["strategy_inputs"]["project_profile_id"],
            second["strategy_inputs"]["project_profile_id"],
        )
        self.assertNotEqual(
            first["strategy_inputs"]["jd_map_id"],
            second["strategy_inputs"]["jd_map_id"],
        )
        self.assertIn("adapt_to_company_culture_and_jd", first["model_tasks"])

    def test_external_asset_keeps_private_defense_private(self) -> None:
        asset = {
            "copyable": (
                "I diagnosed an unsafe export path, added a source gate, and "
                "turned the bad case into a regression that now blocks release."
            ),
            "fact_ids": ["fact-gate", "fact-regression"],
            "private_defense": {
                "unsupported_claims": ["Measured hiring impact"],
                "difficult_follow_ups": ["Was this used in production?"],
                "fallback_language": ["I have not measured production adoption."],
            },
        }
        self.assertEqual(
            profile_router.validate_external_asset(
                asset, {"fact-gate", "fact-regression"}
            ),
            [],
        )
        leaked = dict(asset)
        leaked["copyable"] = (
            asset["copyable"] + " I have not measured production adoption."
        )
        self.assertIn(
            "private defense leaked into copyable asset",
            profile_router.validate_external_asset(
                leaked, {"fact-gate", "fact-regression"}
            ),
        )
        weakness_list = dict(asset)
        weakness_list["copyable"] = "Weaknesses: no production validation."
        self.assertIn(
            "weakness or caveat list leaked into copyable asset",
            profile_router.validate_external_asset(
                weakness_list, {"fact-gate", "fact-regression"}
            ),
        )
        broad_missing = dict(asset)
        broad_missing["copyable"] = (
            "| JD requirement | Match | Evidence | Missing |\n"
            "| Reliability | GAP | None | Production validation |"
        )
        self.assertIn(
            "weakness or caveat list leaked into copyable asset",
            profile_router.validate_external_asset(
                broad_missing, {"fact-gate", "fact-regression"}
            ),
        )
        limitation = dict(asset)
        limitation["copyable"] = "The most important limitation is adoption."
        self.assertIn(
            "weakness or caveat list leaked into copyable asset",
            profile_router.validate_external_asset(
                limitation, {"fact-gate", "fact-regression"}
            ),
        )

    def test_bad_case_contract_ends_on_improvement_and_hiring_signal(self) -> None:
        story = {
            "early_signal_or_constraint": "An exact-source check failed.",
            "diagnosis": "The aggregate score hid a severe unsafe case.",
            "deliberate_decision": "Treat severe cases as release overrides.",
            "system_or_product_change": "Added a blocking export gate.",
            "stronger_result": "The bad case now prevents unsafe release.",
            "target_hiring_signal": "AI product judgment and reliability ownership.",
        }
        self.assertEqual(profile_router.validate_improvement_story(story), [])
        incomplete = dict(story)
        incomplete.pop("target_hiring_signal")
        self.assertIn(
            "missing target_hiring_signal",
            profile_router.validate_improvement_story(incomplete),
        )

    def test_fabricated_fact_and_second_question_are_rejected(self) -> None:
        asset = {
            "copyable": "I launched the product to 10,000 users.",
            "fact_ids": ["invented-launch"],
            "private_defense": {},
        }
        self.assertIn(
            "copyable asset references unsupported fact IDs",
            profile_router.validate_external_asset(asset, {"fact-gate"}),
        )
        plan = profile_router.plan_request(
            "resume_bullets",
            project_profile=None,
            company_profile=self.company_profile,
            jd_demand_map=self.jd_map_one,
            material_questions=["Who owned the launch?", "What was the result?"],
        )
        self.assertEqual(len(plan["questions"]), 1)

    def test_usage_report_requires_complete_token_and_file_accounting(self) -> None:
        usage = profile_router.usage_report(
            files_opened=["README.md", "evals/results.json", "README.md"],
            model_calls=2,
            input_tokens=1200,
            cached_input_tokens=800,
            output_tokens=300,
            skill_invocations=["p2j-answer"],
        )
        self.assertEqual(usage["files_opened"], ["README.md", "evals/results.json"])
        self.assertEqual(usage["uncached_input_tokens"], 400)
        self.assertEqual(usage["output_tokens"], 300)
        with self.assertRaises(ValueError):
            profile_router.usage_report(
                files_opened=[],
                model_calls=1,
                input_tokens=100,
                cached_input_tokens=101,
                output_tokens=20,
                skill_invocations=[],
            )

    def test_stateful_agent_declares_host_native_planner_boundary(self) -> None:
        script = (SCRIPTS / "stateful_agent.py").read_text(encoding="utf-8")
        router = (ROOT / "skill" / "p2j" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Persisted output-update runtime, not the selective Skill planner",
            script,
        )
        self.assertIn(
            "does not choose a normal selective Skill",
            router,
        )

    def test_two_jd_dogfood_records_reuse_and_measured_replay_boundary(self) -> None:
        report = json.loads(
            (
                ROOT
                / "docs"
                / "dogfood"
                / "SELECTIVE_ROUTING_TWO_JD_DOGFOOD.json"
            ).read_text(encoding="utf-8")
        )
        profile_router.validate_project_profile(report["project_evidence_profile"])
        profile_router.validate_company_profile(
            report["company_intelligence_profile"]
        )
        for demand_map in report["jd_demand_maps"]:
            profile_router.validate_jd_demand_map(demand_map)
        self.assertEqual(
            len({item["map_id"] for item in report["jd_demand_maps"]}), 2
        )
        runs = report["actual_selective_runs"]
        self.assertEqual(len(runs), 2)
        self.assertEqual(
            runs[0]["profiles"]["saved"],
            [
                "project_evidence_profile",
                "company_intelligence_profile",
                "jd_demand_map",
            ],
        )
        self.assertEqual(
            runs[1]["profiles"]["reused"],
            ["project_evidence_profile", "company_intelligence_profile"],
        )
        allowed_fact_ids = {
            item["fact_id"]
            for section in report["project_evidence_profile"]["sections"].values()
            for item in section["items"]
            if isinstance(item, dict) and isinstance(item.get("fact_id"), str)
        }
        observed_at = datetime(2026, 7, 28, 20, 0, tzinfo=timezone.utc)
        expected_prerequisites = [
            profile_router.plan_request(
                "project_introduction",
                project_profile=None,
                company_profile=None,
                jd_demand_map=None,
                now=observed_at,
            ),
            profile_router.plan_request(
                "project_introduction",
                project_profile=report["project_evidence_profile"],
                company_profile=report["company_intelligence_profile"],
                jd_demand_map=None,
                now=observed_at,
            ),
        ]
        for run, demand_map, expected_prerequisite in zip(
            runs, report["jd_demand_maps"], expected_prerequisites
        ):
            self.assertEqual(
                run["prerequisite_route_plan"], expected_prerequisite
            )
            self.assertEqual(
                run["route_plan"],
                profile_router.plan_request(
                    "project_introduction",
                    project_profile=report["project_evidence_profile"],
                    company_profile=report["company_intelligence_profile"],
                    jd_demand_map=demand_map,
                    now=observed_at,
                ),
            )
            self.assertEqual(run["route_plan"]["request"], "project_introduction")
            self.assertEqual(
                run["route_plan"]["asset_generation"], ["project_introduction"]
            )
            artifact_path = ROOT / run["output_artifact"]
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
            self.assertEqual(
                profile_router.validate_external_asset(
                    artifact, allowed_fact_ids
                ),
                [],
            )
            self.assertGreaterEqual(len(artifact["copyable"].split()), 100)
            self.assertLessEqual(len(artifact["copyable"].split()), 180)
            self.assertIn("files_opened", run["usage"])
        old = report["execution_comparison"]["old_path"]
        new = report["execution_comparison"]["new_path"]
        self.assertLess(
            new["two_jd_specialist_invocations"],
            old["two_jd_specialist_invocations"],
        )
        self.assertEqual(
            new["two_jd_project_file_opens"],
            old["two_jd_project_file_opens"],
        )
        tokens = report["deterministic_token_replay"]
        self.assertEqual(
            tokens["old_path_input_tokens"] - tokens["new_path_input_tokens"],
            tokens["input_token_savings"],
        )
        self.assertIsNone(report["live_telemetry"]["cached_input_tokens"])
        self.assertIn("billed production usage", tokens["boundary"])


if __name__ == "__main__":
    unittest.main()
