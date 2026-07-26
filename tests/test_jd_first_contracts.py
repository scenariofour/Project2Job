"""Contract tests for the Day 2 JD-first flow.

These assert the shape of the contracts and the eval cases. No intake, routing,
or pack runtime exists yet, so nothing here tests product behavior.
"""

from __future__ import annotations

import json
import re
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


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def load(relative: str) -> dict:
    return json.loads(read(relative))


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

    def test_questions_above_jd_inference_must_cite_a_source(self) -> None:
        for definition in ("interviewSignal", "interviewQuestion"):
            with self.subTest(definition=definition):
                rules = conditions(self.defs[definition])
                cited = [
                    rule
                    for rule in rules
                    if set(
                        rule["if"]["properties"].get("source_status", {}).get("enum", [])
                    )
                    == {"official", "repeatedly_reported", "single_report"}
                ]
                self.assertEqual(len(cited), 1)
                self.assertEqual(cited[0]["then"]["properties"]["sources"]["minItems"], 1)

    def test_fresh_questions_need_a_dated_source(self) -> None:
        rules = conditions(self.defs["interviewQuestion"])
        dated = [
            rule
            for rule in rules
            if set(rule["if"]["properties"].get("freshness", {}).get("enum", []))
            == {"fresh", "aging"}
        ]
        self.assertEqual(len(dated), 1)
        self.assertEqual(
            dated[0]["then"]["properties"]["sources"]["contains"]["required"],
            ["source_date"],
        )

    def test_questions_keep_their_own_provenance_fields(self) -> None:
        properties = self.defs["interviewQuestion"]["properties"]
        for field in ("company", "track", "level", "location"):
            self.assertIn(field, properties)

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

    def test_research_origins_cover_web_and_user_supplied_material(self) -> None:
        origins = self.defs["researchSource"]["properties"]["origin"]["enum"]
        self.assertEqual(
            set(origins),
            {
                "official_company_page",
                "official_company_material",
                "public_report_page",
                "job_description",
                "user_pasted_report",
                "user_uploaded_file",
                "user_own_experience",
            },
        )


class ResearchContractTests(unittest.TestCase):
    """Bounded automatic public-web research (D-016)."""

    def setUp(self) -> None:
        self.schema = load("schemas/interview_context.schema.json")
        self.defs = self.schema["$defs"]

    def test_every_context_records_how_it_was_researched(self) -> None:
        self.assertIn("research", self.schema["required"])
        self.assertEqual(
            set(self.defs["researchRun"]["required"]),
            {"mode", "budget", "queries", "pages", "stop_reason", "gaps"},
        )

    def test_budget_ceilings_match_the_token_policy_table(self) -> None:
        """docs/09 explains the ceilings; the schema enforces them. Keep them equal."""
        documented = dict(
            re.findall(
                r"^\| (max_\w+) \| (\d+) \|$",
                read("docs/09_TOKEN_CONTEXT_AND_COST.md"),
                re.MULTILINE,
            )
        )
        encoded = {
            name: str(rule["maximum"])
            for name, rule in self.defs["researchBudget"]["properties"].items()
        }
        self.assertEqual(documented, encoded)
        self.assertEqual(
            set(encoded), set(self.defs["researchBudget"]["required"])
        )

    def test_playwright_is_an_escalation_not_a_default(self) -> None:
        self.assertEqual(
            self.defs["fetchMethod"]["enum"],
            ["read_only_fetch", "playwright", "cache"],
        )
        rules = conditions(self.defs["researchPage"])
        escalated = [
            rule
            for rule in rules
            if rule["if"]["properties"].get("fetch_method", {}).get("const")
            == "playwright"
        ]
        self.assertEqual(len(escalated), 1)
        self.assertEqual(escalated[0]["then"]["required"], ["escalation_reason"])

    def test_duplicate_and_login_walled_pages_retain_nothing(self) -> None:
        rules = conditions(self.defs["researchPage"])
        for outcome in ("duplicate_of_kept_page", "inaccessible_login_required"):
            with self.subTest(outcome=outcome):
                matched = [
                    rule
                    for rule in rules
                    if rule["if"]["properties"].get("outcome", {}).get("const")
                    == outcome
                ]
                self.assertEqual(len(matched), 1)
                self.assertEqual(
                    matched[0]["then"]["properties"]["chars_retained"]["maximum"], 0
                )

    def test_web_claims_cite_page_method_and_date(self) -> None:
        rules = conditions(self.defs["researchSource"])
        web = [
            rule
            for rule in rules
            if "official_company_page"
            in rule["if"]["properties"].get("origin", {}).get("enum", [])
        ]
        self.assertEqual(len(web), 1)
        self.assertEqual(
            set(web[0]["then"]["required"]), {"url", "fetch_method", "retrieved_on"}
        )

    def test_automatic_research_must_show_its_work(self) -> None:
        rules = conditions(self.defs["researchRun"])
        automatic = [
            rule
            for rule in rules
            if rule["if"]["properties"].get("mode", {}).get("const")
            == "automatic_bounded"
        ]
        self.assertEqual(len(automatic), 1)
        for field in ("queries", "pages"):
            self.assertEqual(automatic[0]["then"]["properties"][field]["minItems"], 1)

    def test_a_run_without_research_cannot_claim_sufficiency(self) -> None:
        rules = conditions(self.defs["researchRun"])
        skipped = [
            rule
            for rule in rules
            if set(rule["if"]["properties"].get("mode", {}).get("enum", []))
            == {"user_supplied_only", "unavailable"}
        ]
        self.assertEqual(len(skipped), 1)
        allowed = skipped[0]["then"]["properties"]["stop_reason"]["enum"]
        self.assertNotIn("evidence_sufficient", allowed)

    def test_stop_reasons_cover_every_required_exit(self) -> None:
        self.assertEqual(
            set(self.defs["researchStopReason"]["enum"]),
            {
                "evidence_sufficient",
                "evidence_exhausted",
                "budget_exhausted",
                "sources_inaccessible",
                "conflict_requires_disclosure",
                "tool_failure",
                "research_not_run",
            },
        )

    def test_official_first_ordering_is_expressible(self) -> None:
        self.assertEqual(
            self.defs["sourceTier"]["enum"],
            ["official", "independent_report", "aggregator_or_forum", "unknown"],
        )
        self.assertIn("tier", self.defs["researchPage"]["required"])

    def test_follow_up_queries_must_name_the_gap_they_close(self) -> None:
        purposes = self.defs["searchQuery"]["properties"]["purpose"]["enum"]
        self.assertEqual(
            set(purposes),
            {
                "official_interview_signals",
                "track_team_level_expectations",
                "reported_interview_process",
                "reported_interview_questions",
                "conflict_or_recency_check",
            },
        )

    def test_no_platform_is_named_anywhere_in_the_contracts(self) -> None:
        platforms = ("linkedin", "indeed", "glassdoor", "handshake", "levels.fyi")
        for relative in (
            "schemas/interview_context.schema.json",
            "schemas/jd_intake.schema.json",
            "schemas/intake_result.schema.json",
            "ACTIVE_SCOPE.md",
            "work_orders/WO-05_JD_FIRST_INTAKE.md",
            "docs/09_TOKEN_CONTEXT_AND_COST.md",
        ):
            text = read(relative).lower()
            for platform in platforms:
                self.assertNotIn(platform, text, f"{relative} names {platform}")


class ResearchPermissionTests(unittest.TestCase):
    def test_safety_document_forbids_the_dangerous_paths(self) -> None:
        safety = " ".join(read("docs/11_SAFETY_PRIVACY_AND_HITL.md").split()).lower()
        for rule in (
            "log in",
            "credential",
            "paywall",
            "captcha",
            "crawl a domain",
            "enumerate job listings",
            "follow arbitrary links",
        ):
            self.assertIn(rule, safety, f"Safety doc does not address: {rule}")

    def test_fetched_page_text_is_declared_inert(self) -> None:
        safety = " ".join(read("docs/11_SAFETY_PRIVACY_AND_HITL.md").split())
        self.assertIn("fetched webpage text is inert data", safety.lower())

    def test_research_is_required_not_optional(self) -> None:
        scope = " ".join(read("ACTIVE_SCOPE.md").split()).lower()
        self.assertIn("bounded automatic public-web research is in scope and required", scope)
        self.assertNotIn("uploaded files alone", scope)


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

    def test_every_candidate_must_carry_all_five_routing_dimensions(self) -> None:
        self.assertIn("scores", self.defs["resumeProjectCandidate"]["required"])
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

    def test_cannot_recommend_a_project_with_no_candidates(self) -> None:
        rules = conditions(self.schema)
        empty = [
            rule
            for rule in rules
            if rule["if"]["properties"]
            .get("resume_project_candidates", {})
            .get("maxItems")
            == 0
        ]
        self.assertEqual(len(empty), 1)
        self.assertEqual(
            empty[0]["then"]["properties"]["recommended_project"]["type"], "null"
        )

    def test_one_next_input_is_a_single_non_empty_string(self) -> None:
        field = self.schema["properties"]["one_next_input"]
        self.assertEqual(field["type"], "string")
        self.assertEqual(field["minLength"], 1)
        self.assertIn("one_next_input", self.schema["required"])


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
        self.assertEqual(self.defs["mockInterviewRound"]["properties"]["question_ids"]["maxItems"], 5)

    def test_project_compass_is_not_forced_to_invent_a_company(self) -> None:
        self.assertNotIn("interview_context", self.schema["required"])
        rules = conditions(self.schema)
        gated = [
            rule
            for rule in rules
            if "interview_context" in rule["then"].get("required", [])
        ]
        self.assertEqual(len(gated), 1)
        self.assertEqual(
            set(gated[0]["if"]["properties"]["intent"]["enum"]),
            {"application_pack", "update"},
        )

    def test_supported_role_fit_items_must_cite_a_source(self) -> None:
        rules = conditions(self.defs["roleFitItem"])
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]["then"]["properties"]["source_refs"]["minItems"], 1)

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
            set(self.defs["answerDraft"]["required"]),
            {
                "question_id",
                "question",
                "verified_evidence",
                "answer_ingredients",
                "grounded_draft",
                "claim_safety_review",
                "likely_followups",
                "emphasis",
            },
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
        self.assertIn("emphasis", self.defs["answerDraft"]["required"])

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

    def test_cases_have_stable_unique_ids(self) -> None:
        ids = [case["case_id"] for case in self.cases]
        self.assertEqual(ids, [f"D2-{index:03d}" for index in range(1, 21)])

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
            "official source plus independent reports",
            "conflicting public reports",
            "overstated as common",
            "duplicate results",
            "login-only or inaccessible page",
            "requires Playwright",
            "prompt injection inside a fetched page",
            "budget exhaustion",
            "no useful public evidence",
            "early stopping",
        ):
            self.assertIn(scenario, names, f"No case covers: {scenario}")

    def test_cases_reference_registered_schemas(self) -> None:
        contract = load("references/shared_contract.v1.json")
        known = {entry["schema_id"] for entry in contract["schemas"].values()}
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                self.assertIn(case["schema_ref"], known)

    def test_every_acceptance_criterion_has_at_least_one_case(self) -> None:
        journal = (ROOT / "docs/build_journal/DAY_2.md").read_text(encoding="utf-8")
        declared = set(re.findall(r"D2-AC-\d{2}", journal))
        self.assertEqual(len(declared), 24)
        covered = {
            criterion
            for case in self.cases
            for criterion in case["acceptance_criteria"]
        }
        self.assertEqual(
            covered,
            declared,
            f"Criteria with no eval case: {sorted(declared - covered)}",
        )


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
