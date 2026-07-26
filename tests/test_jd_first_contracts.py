"""Contract tests for the Day 2 JD-first flow.

These assert the shape of the contracts and the eval cases. No intake, routing,
or pack runtime exists yet, so nothing here tests product behavior.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCE_STATUSES = [
    "official",
    "repeatedly_reported",
    "single_report",
    "inferred_from_jd",
    "unknown",
]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def load_cases() -> list[dict]:
    return [
        json.loads(line)
        for line in (ROOT / "lab/evals/day2_jd_first_cases.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]


def conditions(schema: dict) -> list[dict]:
    """Every if/then pair in a schema, so rules can be asserted individually."""
    found = []
    if isinstance(schema, dict):
        if "if" in schema and "then" in schema:
            found.append(schema)
        for value in schema.values():
            found.extend(conditions(value))
    elif isinstance(schema, list):
        for item in schema:
            found.extend(conditions(item))
    return found


class JdIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = load("schemas/jd_intake.schema.json")

    def test_accepts_only_offline_input_forms(self) -> None:
        forms = self.schema["properties"]["input_form"]["enum"]
        self.assertEqual(
            set(forms),
            {"pasted_text", "user_supplied_url", "screenshot", "uploaded_file"},
        )

    def test_unstated_fields_are_optional_but_unknowns_are_required(self) -> None:
        required = self.schema["required"]
        self.assertIn("unknowns", required)
        for optional in ("team_or_product_area", "track", "level", "location"):
            self.assertIn(optional, self.schema["properties"])
            self.assertNotIn(optional, required)

    def test_requirements_cite_a_jd_location(self) -> None:
        requirement = self.schema["$defs"]["roleRequirement"]
        self.assertIn("jd_location", requirement["required"])


class InterviewContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = load("schemas/interview_context.schema.json")
        self.defs = self.schema["$defs"]

    def test_source_status_scale_has_no_certain_value(self) -> None:
        self.assertEqual(self.defs["sourceStatus"]["enum"], SOURCE_STATUSES)

    def test_three_layers_and_no_culture_fit(self) -> None:
        layers = self.defs["interviewLayer"]["enum"]
        self.assertEqual(
            layers,
            [
                "company_interview_signal",
                "track_team_level_requirement",
                "reported_interview_evidence",
            ],
        )
        for layer in layers:
            self.assertNotIn("culture", layer)
            self.assertNotIn("personality", layer)

    def test_no_presentation_strength_means_guaranteed(self) -> None:
        presented = self.defs["presentedAs"]["enum"]
        self.assertNotIn("certain", presented)
        self.assertNotIn("guaranteed", presented)
        self.assertNotIn("expected", presented)

    def test_single_report_is_capped_at_reported_once(self) -> None:
        rules = conditions(self.defs["interviewQuestion"])
        capped = [
            rule
            for rule in rules
            if rule["if"]["properties"].get("source_status", {}).get("const")
            == "single_report"
        ]
        self.assertEqual(len(capped), 1)
        self.assertEqual(
            capped[0]["then"]["properties"]["presented_as"]["const"], "reported_once"
        )

    def test_stale_reports_cannot_be_presented_as_likely(self) -> None:
        rules = conditions(self.defs["interviewQuestion"])
        stale = [
            rule
            for rule in rules
            if rule["if"]["properties"].get("freshness", {}).get("const") == "stale"
        ]
        self.assertEqual(len(stale), 1)
        self.assertNotIn(
            "likely", stale[0]["then"]["properties"]["presented_as"]["enum"]
        )

    def test_repeatedly_reported_needs_more_than_one_source(self) -> None:
        rules = conditions(self.defs["interviewSignal"])
        repeated = [
            rule
            for rule in rules
            if rule["if"]["properties"].get("source_status", {}).get("const")
            == "repeatedly_reported"
        ]
        self.assertEqual(len(repeated), 1)
        self.assertEqual(repeated[0]["then"]["properties"]["sources"]["minItems"], 2)

    def test_conflicts_keep_both_reports_visible(self) -> None:
        resolutions = self.defs["reportConflict"]["properties"]["resolution"]["enum"]
        self.assertTrue(all(value.endswith("both_shown") for value in resolutions))

    def test_research_origins_require_user_supplied_material(self) -> None:
        origins = self.defs["researchSource"]["properties"]["origin"]["enum"]
        self.assertEqual(
            set(origins),
            {
                "official_company_material",
                "job_description",
                "user_pasted_report",
                "user_uploaded_file",
                "user_own_experience",
            },
        )


class IntakeResultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = load("schemas/intake_result.schema.json")
        self.defs = self.schema["$defs"]

    def test_produces_value_without_a_resume_or_project(self) -> None:
        candidates = self.schema["properties"]["resume_project_candidates"]
        self.assertEqual(candidates["minItems"], 0)
        recommendation = self.schema["properties"]["recommended_project"]
        self.assertTrue(
            any(option.get("type") == "null" for option in recommendation["oneOf"])
        )

    def test_resume_candidates_are_locked_to_self_reported(self) -> None:
        candidate = self.defs["resumeProjectCandidate"]
        self.assertEqual(candidate["properties"]["evidence_status"]["const"], "self_reported")

    def test_all_five_routing_dimensions_are_required(self) -> None:
        self.assertEqual(
            set(self.defs["routingScores"]["required"]),
            {
                "role_relevance",
                "likely_evidence_availability",
                "ownership_clarity",
                "outcome_strength",
                "interview_depth",
            },
        )

    def test_recommendation_always_states_risks(self) -> None:
        recommendation = self.defs["projectRecommendation"]
        self.assertIn("risks", recommendation["required"])
        self.assertEqual(recommendation["properties"]["risks"]["minItems"], 1)

    def test_no_clear_choice_must_offer_alternatives(self) -> None:
        rules = conditions(self.defs["projectRecommendation"])
        self.assertEqual(len(rules), 1)
        self.assertEqual(
            rules[0]["if"]["properties"]["confidence"]["const"], "no_clear_choice"
        )
        self.assertEqual(
            rules[0]["then"]["properties"]["alternatives_considered"]["minItems"], 1
        )

    def test_exactly_one_next_input(self) -> None:
        self.assertEqual(self.schema["properties"]["one_next_input"]["type"], "string")


class ApplicationPackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = load("schemas/application_pack.schema.json")
        self.defs = self.schema["$defs"]
        self.pack = self.defs["interviewPack"]["properties"]

    def test_pack_is_version_2(self) -> None:
        self.assertEqual(self.schema["$id"].rsplit("/", 1)[-1], "2.0.0")
        self.assertEqual(self.schema["properties"]["schema_version"]["const"], "2.0.0")

    def test_bounded_output_counts(self) -> None:
        self.assertEqual(self.pack["priority_questions"]["minItems"], 5)
        self.assertEqual(self.pack["priority_questions"]["maxItems"], 8)
        self.assertEqual(self.pack["answer_drafts"]["minItems"], 3)
        self.assertEqual(self.pack["answer_drafts"]["maxItems"], 3)
        self.assertEqual(self.defs["mockInterviewRound"]["type"], "object")

    def test_every_required_pack_section_is_present(self) -> None:
        for section in (
            "company_track_brief",
            "interview_loop_hypothesis",
            "priority_questions",
            "answer_drafts",
            "questions_to_ask_interviewer",
            "mock_interview_round",
            "unsupported_areas",
        ):
            self.assertIn(section, self.defs["interviewPack"]["required"])

    def test_answer_draft_preserves_the_full_chain(self) -> None:
        self.assertEqual(
            self.defs["answerDraft"]["required"],
            [
                "question_id",
                "question",
                "verified_evidence",
                "answer_ingredients",
                "grounded_draft",
                "claim_safety_review",
                "likely_followups",
            ],
        )

    def test_a_draft_exceeding_its_evidence_cannot_validate(self) -> None:
        review = self.defs["claimSafetyReview"]["properties"]
        self.assertIs(review["exceeds_evidence"]["const"], False)

    def test_answer_evidence_must_be_established_project_evidence(self) -> None:
        statuses = self.defs["verifiedFact"]["properties"]["status"]["enum"]
        self.assertEqual(set(statuses), {"supported", "partially_supported"})

    def test_emphasis_carries_the_invariant_fact_set(self) -> None:
        emphasis = self.defs["emphasisProfile"]
        self.assertEqual(set(emphasis["required"]), {"fact_ids", "emphasis_signal_ids"})

    def test_mock_round_scores_evidence_not_personality(self) -> None:
        dimensions = self.defs["mockInterviewRound"]["properties"]["scoring_dimensions"]
        self.assertEqual(
            set(dimensions["items"]["enum"]),
            {
                "evidence_grounding",
                "claim_boundary_discipline",
                "role_relevance",
                "specificity",
                "followup_recovery",
            },
        )


class Day2EvalCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = load_cases()

    def test_ten_cases_with_stable_unique_ids(self) -> None:
        ids = [case["case_id"] for case in self.cases]
        self.assertEqual(ids, [f"D2-{index:03d}" for index in range(1, 11)])

    def test_every_case_states_what_must_not_happen(self) -> None:
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                self.assertTrue(case["expect"]["must_not"])
                self.assertIn(case["stage"], {"intake", "pack"})

    def test_required_scenarios_are_all_covered(self) -> None:
        names = " ".join(case["name"] for case in self.cases)
        for scenario in (
            "no resume",
            "several resume projects",
            "no project clearly matches",
            "weak evidence availability",
            "unknown company track",
            "conflicting interview reports",
            "stale interview report",
            "single reported question",
            "exceeds project evidence",
            "emphasis changes wording",
        ):
            self.assertIn(scenario, names, f"No case covers: {scenario}")

    def test_cases_reference_registered_schemas(self) -> None:
        contract = load("references/shared_contract.v1.json")
        known = {entry["schema_id"] for entry in contract["schemas"].values()}
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                self.assertIn(case["schema_ref"], known)

    def test_every_case_maps_to_a_day_2_acceptance_criterion(self) -> None:
        journal = (ROOT / "docs/build_journal/DAY_2.md").read_text(encoding="utf-8")
        covered = set()
        for case in self.cases:
            for criterion in case["acceptance_criteria"]:
                self.assertIn(criterion, journal, f"{criterion} is not in DAY_2.md")
                covered.add(criterion)
        self.assertGreaterEqual(len(covered), 10)


class Day2ScopeTests(unittest.TestCase):
    def test_day_2_stays_planned(self) -> None:
        journal = (ROOT / "docs/build_journal/DAY_2.md").read_text(encoding="utf-8")
        self.assertIn("Status: PLANNED", journal)

    def test_excluded_platform_integrations_stay_excluded(self) -> None:
        scope = (ROOT / "ACTIVE_SCOPE.md").read_text(encoding="utf-8").lower()
        for excluded in (
            "job discovery",
            "auto-apply",
            "application tracking",
            "email monitoring",
            "referral automation",
            "multiple deep project analyses",
        ):
            self.assertIn(excluded, scope)

    def test_manifest_routes_the_new_work_order(self) -> None:
        manifest = load("PROJECT_MANIFEST.json")
        self.assertEqual(
            manifest["work_order_to_context"]["WO-05_JD_FIRST_INTAKE"], "jd_intake"
        )
        for path in manifest["context_sets"]["jd_intake"]:
            self.assertTrue((ROOT / path).exists(), f"Missing context file: {path}")


if __name__ == "__main__":
    unittest.main()
