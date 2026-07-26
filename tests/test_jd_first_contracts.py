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


def conditions(schema: dict, root: dict | None = None) -> list[dict]:
    """Every if/then pair reachable from a schema, following local $refs.

    Rules shared between definitions live behind a $ref, so a walker that did
    not follow them would silently report zero rules and pass.
    """
    found = []
    if isinstance(schema, dict):
        if "if" in schema and "then" in schema:
            found.append(schema)
        ref = schema.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/") and root is not None:
            node = root
            for part in ref.removeprefix("#/").split("/"):
                node = node[part]
            found.extend(conditions(node, root))
        for key, value in schema.items():
            if key != "$ref":
                found.extend(conditions(value, root))
    elif isinstance(schema, list):
        for item in schema:
            found.extend(conditions(item, root))
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
                rules = conditions(self.defs[definition], self.schema)
                cited = [
                    rule
                    for rule in rules
                    if set(
                        rule["if"].get("properties", {}).get("source_status", {}).get("enum", [])
                    )
                    == {"official", "repeatedly_reported", "single_report"}
                ]
                self.assertEqual(len(cited), 1)
                self.assertEqual(cited[0]["then"]["properties"]["sources"]["minItems"], 1)

    def test_fresh_questions_need_a_dated_source(self) -> None:
        rules = conditions(self.defs["interviewQuestion"], self.schema)
        dated = [
            rule
            for rule in rules
            if set(rule["if"].get("properties", {}).get("freshness", {}).get("enum", []))
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
        rules = conditions(self.defs["interviewQuestion"], self.schema)
        capped = [
            rule
            for rule in rules
            if rule["if"].get("properties", {}).get("source_status", {}).get("const")
            == "single_report"
        ]
        self.assertEqual(len(capped), 1)
        self.assertEqual(
            capped[0]["then"]["properties"]["presented_as"]["const"], "reported_once"
        )

    def test_stale_reports_cannot_be_presented_as_likely(self) -> None:
        rules = conditions(self.defs["interviewQuestion"], self.schema)
        stale = [
            rule
            for rule in rules
            if rule["if"].get("properties", {}).get("freshness", {}).get("const") == "stale"
        ]
        self.assertEqual(len(stale), 1)
        self.assertNotIn(
            "likely", stale[0]["then"]["properties"]["presented_as"]["enum"]
        )

    def test_repeatedly_reported_needs_more_than_one_source(self) -> None:
        rules = conditions(self.defs["interviewSignal"], self.schema)
        repeated = [
            rule
            for rule in rules
            if rule["if"].get("properties", {}).get("source_status", {}).get("const")
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
            {"mode", "usage", "queries", "pages", "stop_reason", "gaps"},
        )

    def test_every_ceiling_has_a_bounded_actual(self) -> None:
        """A declared budget bounds nothing unless the spend is bounded too."""
        ceilings = self.defs["researchBudget"]["properties"]
        usage = self.defs["researchUsage"]["properties"]
        pairs = {
            "max_search_queries": "search_queries",
            "max_pages_fetched": "pages_fetched",
            "max_playwright_pages": "playwright_pages",
            "max_navigation_depth": "navigation_depth_used",
            "max_chars_per_page": None,
            "max_total_tokens": "total_tokens",
            "max_retries_per_page": "retries",
            "max_runtime_seconds": "runtime_seconds",
        }
        self.assertEqual(set(pairs), set(ceilings))
        for ceiling, actual in pairs.items():
            if actual is None:
                continue
            with self.subTest(limit=ceiling):
                self.assertIn(actual, usage)
                self.assertEqual(usage[actual]["maximum"], ceilings[ceiling]["maximum"])
        self.assertEqual(set(usage), set(self.defs["researchUsage"]["required"]))
        # per-page character retention is bounded on the page record itself
        self.assertEqual(
            self.defs["researchPage"]["properties"]["chars_retained"]["maximum"],
            ceilings["max_chars_per_page"]["maximum"],
        )

    def test_run_arrays_cannot_exceed_their_ceilings(self) -> None:
        ceilings = self.defs["researchBudget"]["properties"]
        run = self.defs["researchRun"]["properties"]
        self.assertEqual(
            run["queries"]["maxItems"], ceilings["max_search_queries"]["maximum"]
        )
        self.assertEqual(
            run["pages"]["maxItems"], ceilings["max_pages_fetched"]["maximum"]
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
        rules = conditions(self.defs["researchPage"], self.schema)
        escalated = [
            rule
            for rule in rules
            if rule["if"].get("properties", {}).get("fetch_method", {}).get("const")
            == "playwright"
        ]
        self.assertEqual(len(escalated), 1)
        self.assertEqual(escalated[0]["then"]["required"], ["escalation_reason"])

    def test_only_an_extracted_page_may_retain_content(self) -> None:
        page = self.defs["researchPage"]
        self.assertIn("chars_retained", page["required"])
        rules = conditions(page, self.schema)
        matched = [
            rule
            for rule in rules
            if rule["if"].get("properties", {}).get("outcome", {}).get("not", {}).get("const")
            == "extracted"
        ]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["then"]["properties"]["chars_retained"]["maximum"], 0)

    def test_a_browser_is_never_driven_at_a_wall(self) -> None:
        rules = conditions(self.defs["researchPage"], self.schema)
        matched = [
            rule
            for rule in rules
            if set(rule["if"].get("properties", {}).get("outcome", {}).get("enum", []))
            == {"inaccessible_login_required", "inaccessible_blocked"}
        ]
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0]["then"]["properties"]["fetch_method"]["not"]["const"],
            "playwright",
        )

    def test_web_claims_cite_page_method_and_date(self) -> None:
        rules = conditions(self.defs["researchSource"], self.schema)
        web = [
            rule
            for rule in rules
            if "official_company_page"
            in rule["if"].get("properties", {}).get("origin", {}).get("enum", [])
        ]
        self.assertEqual(len(web), 1)
        self.assertEqual(
            set(web[0]["then"]["required"]), {"url", "fetch_method", "retrieved_on"}
        )

    def test_automatic_research_must_show_its_work(self) -> None:
        rules = conditions(self.defs["researchRun"], self.schema)
        automatic = [
            rule
            for rule in rules
            if rule["if"].get("properties", {}).get("mode", {}).get("const")
            == "automatic_bounded"
        ]
        self.assertEqual(len(automatic), 1)
        for field in ("queries", "pages"):
            self.assertEqual(automatic[0]["then"]["properties"][field]["minItems"], 1)

    def test_a_run_without_research_cannot_claim_sufficiency(self) -> None:
        rules = conditions(self.defs["researchRun"], self.schema)
        skipped = [
            rule
            for rule in rules
            if set(rule["if"].get("properties", {}).get("mode", {}).get("enum", []))
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
            "README.md",
            "PROJECT_STATUS.md",
            "work_orders/WO-05_JD_FIRST_INTAKE.md",
            "docs/01_MVP_PRD.md",
            "docs/05_SKILL_PRODUCT_SPEC.md",
            "docs/09_TOKEN_CONTEXT_AND_COST.md",
            "docs/11_SAFETY_PRIVACY_AND_HITL.md",
            "docs/13_DECISION_LOG.md",
            "docs/build_journal/DAY_2.md",
            "lab/evals/day2_jd_first_cases.jsonl",
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
        self.assertIn("public-web research", scope)
        self.assertIn("required", scope)
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
        rules = conditions(self.defs["projectRecommendation"], self.schema)
        self.assertEqual(len(rules), 1)
        self.assertEqual(
            rules[0]["if"]["properties"]["confidence"]["const"], "no_clear_choice"
        )
        self.assertEqual(
            rules[0]["then"]["properties"]["alternatives_considered"]["minItems"], 1
        )

    def test_cannot_recommend_a_project_with_no_candidates(self) -> None:
        rules = conditions(self.schema, self.schema)
        empty = [
            rule
            for rule in rules
            if rule["if"].get("properties", {})
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
        rules = conditions(self.schema, self.schema)
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
        rules = conditions(self.defs["roleFitItem"], self.schema)
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


try:  # optional: real validation when the library is available locally or in CI
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource

    HAVE_VALIDATOR = True
except ImportError:  # pragma: no cover - the repo has no third-party dependency
    HAVE_VALIDATOR = False


def registry_and(schema_path: str):
    """A validator for one schema, with every sibling schema resolvable."""
    resources = []
    for path in sorted((ROOT / "schemas").glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        if "$id" in schema:
            resources.append(Resource.from_contents(schema))
    registry = Registry().with_resources([(r.id(), r) for r in resources])
    return Draft202012Validator(load(schema_path), registry=registry)


BUDGET = {
    "max_search_queries": 8,
    "max_pages_fetched": 12,
    "max_playwright_pages": 3,
    "max_navigation_depth": 1,
    "max_chars_per_page": 20000,
    "max_total_tokens": 60000,
    "max_retries_per_page": 1,
    "max_runtime_seconds": 120,
}
USAGE = {
    "search_queries": 1,
    "pages_fetched": 1,
    "playwright_pages": 0,
    "navigation_depth_used": 0,
    "total_tokens": 900,
    "retries": 0,
    "runtime_seconds": 12,
}


def a_page(**overrides) -> dict:
    page = {
        "url": "https://example.test/careers/interview",
        "tier": "official",
        "outcome": "extracted",
        "fetch_method": "read_only_fetch",
        "retrieved_on": "2026-07-25",
        "chars_retained": 400,
    }
    page.update(overrides)
    return page


def a_context(**research_overrides) -> dict:
    research = {
        "mode": "automatic_bounded",
        "budget": dict(BUDGET),
        "usage": dict(USAGE),
        "queries": [
            {
                "query": "example interview process",
                "purpose": "official_interview_signals",
                "results_considered": 6,
                "results_kept": 1,
            }
        ],
        "pages": [a_page()],
        "stop_reason": "evidence_sufficient",
        "gaps": [],
    }
    research.update(research_overrides)
    return {
        "schema_version": "1.0.0",
        "company": "Example",
        "research": research,
        "signals": [],
        "questions": [],
        "unknowns": [],
    }


@unittest.skipUnless(HAVE_VALIDATOR, "jsonschema is not installed")
class InstanceValidationTests(unittest.TestCase):
    """Execute the conditional rules instead of only reading them.

    Every other test in this module inspects schema keys, which cannot tell a
    live rule from an unreachable one. These run real instances through a real
    draft-2020-12 validator.
    """

    def setUp(self) -> None:
        self.validator = registry_and("schemas/interview_context.schema.json")

    def assertRejects(self, instance: dict, why: str) -> None:
        self.assertFalse(self.validator.is_valid(instance), f"should be invalid: {why}")

    def test_a_well_formed_research_run_validates(self) -> None:
        errors = sorted(self.validator.iter_errors(a_context()), key=str)
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_a_run_cannot_declare_a_budget_over_the_ceiling(self) -> None:
        self.assertRejects(
            a_context(budget={**BUDGET, "max_pages_fetched": 13}),
            "declared budget exceeds the ceiling",
        )

    def test_a_run_cannot_spend_over_the_ceiling(self) -> None:
        self.assertRejects(
            a_context(usage={**USAGE, "playwright_pages": 4}),
            "spent more Playwright pages than the ceiling allows",
        )
        self.assertRejects(
            a_context(usage={**USAGE, "runtime_seconds": 600}),
            "ran longer than the ceiling allows",
        )
        self.assertRejects(
            a_context(pages=[a_page() for _ in range(13)]),
            "recorded more pages than the ceiling allows",
        )

    def test_only_an_extracted_page_keeps_content(self) -> None:
        for outcome in (
            "inaccessible_login_required",
            "inaccessible_blocked",
            "render_required",
            "fetch_failed",
            "skipped_budget",
            "duplicate_of_kept_page",
        ):
            with self.subTest(outcome=outcome):
                self.assertRejects(
                    a_context(pages=[a_page(outcome=outcome, chars_retained=900)]),
                    f"{outcome} page retained content",
                )

    def test_a_page_cannot_retain_more_than_the_per_page_ceiling(self) -> None:
        self.assertRejects(
            a_context(pages=[a_page(chars_retained=20001)]),
            "retained more characters than the ceiling allows",
        )

    def test_playwright_is_justified_and_never_used_at_a_wall(self) -> None:
        self.assertRejects(
            a_context(pages=[a_page(fetch_method="playwright")]),
            "Playwright fetch with no escalation reason",
        )
        self.assertRejects(
            a_context(
                pages=[
                    a_page(
                        outcome="inaccessible_login_required",
                        chars_retained=0,
                        fetch_method="playwright",
                        escalation_reason="javascript_rendered",
                    )
                ],
                stop_reason="sources_inaccessible",
            ),
            "drove a browser at a login wall",
        )
        self.assertTrue(
            self.validator.is_valid(
                a_context(
                    pages=[
                        a_page(
                            fetch_method="playwright",
                            escalation_reason="javascript_rendered",
                        )
                    ],
                    usage={**USAGE, "playwright_pages": 1},
                )
            )
        )

    def test_a_duplicate_names_what_it_duplicates(self) -> None:
        self.assertRejects(
            a_context(
                pages=[a_page(outcome="duplicate_of_kept_page", chars_retained=0)]
            ),
            "duplicate did not name the page it duplicates",
        )

    def test_research_mode_and_stop_reason_must_agree(self) -> None:
        self.assertRejects(
            a_context(mode="unavailable", queries=[], pages=[]),
            "no research ran yet claimed the evidence was sufficient",
        )
        self.assertRejects(
            a_context(mode="automatic_bounded", stop_reason="research_not_run"),
            "automatic research claimed it never ran",
        )
        self.assertRejects(
            a_context(mode="user_supplied_only", stop_reason="research_not_run"),
            "no-research mode still recorded queries and pages",
        )

    def test_automatic_research_must_show_queries_and_pages(self) -> None:
        self.assertRejects(
            a_context(pages=[]), "automatic research recorded no pages"
        )
        self.assertRejects(
            a_context(queries=[]), "automatic research recorded no queries"
        )

    def test_a_web_claim_must_cite_an_exact_dated_page(self) -> None:
        def with_source(**source) -> dict:
            context = a_context()
            context["signals"] = [
                {
                    "signal_id": "s1",
                    "layer": "company_interview_signal",
                    "statement": "The loop has four stages.",
                    "source_status": "official",
                    "presented_as": "likely",
                    "tier": "official",
                    "sources": [{"origin": "official_company_page", **source}],
                    "freshness": "unknown",
                }
            ]
            return context

        self.assertRejects(
            with_source(reference="careers page"),
            "web claim with no url, fetch method, or retrieval date",
        )
        self.assertRejects(
            with_source(
                reference="careers page",
                url="example.test",
                fetch_method="read_only_fetch",
                retrieved_on="2026-07-25",
            ),
            "cited a bare domain instead of an exact page",
        )
        self.assertRejects(
            with_source(
                reference="careers page",
                url="https://example.test/careers",
                fetch_method="read_only_fetch",
                retrieved_on="last week",
            ),
            "retrieval date is not a date",
        )
        self.assertTrue(
            self.validator.is_valid(
                with_source(
                    reference="careers page#loop",
                    url="https://example.test/careers",
                    fetch_method="read_only_fetch",
                    retrieved_on="2026-07-25",
                )
            )
        )

    def test_a_signal_cannot_outrun_its_source(self) -> None:
        def signal(**overrides) -> dict:
            base = {
                "signal_id": "s1",
                "layer": "reported_interview_evidence",
                "statement": "A take-home is used.",
                "source_status": "single_report",
                "presented_as": "reported_once",
                "tier": "aggregator_or_forum",
                "sources": [{"origin": "user_pasted_report", "reference": "post"}],
                "freshness": "unknown",
            }
            base.update(overrides)
            context = a_context()
            context["signals"] = [base]
            return context

        self.assertRejects(
            signal(presented_as="likely"),
            "one report presented as likely",
        )
        self.assertRejects(
            signal(source_status="repeatedly_reported", presented_as="likely"),
            "repeatedly_reported backed by a single source",
        )
        self.assertRejects(
            signal(freshness="stale", presented_as="likely"),
            "stale report presented as likely",
        )
        self.assertRejects(
            signal(freshness="fresh", presented_as="reported_once"),
            "fresh claim with no dated source",
        )
        self.assertRejects(
            signal(source_status="inferred_from_jd", presented_as="likely"),
            "JD inference presented as likely",
        )


@unittest.skipUnless(HAVE_VALIDATOR, "jsonschema is not installed")
class PackInstanceValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = registry_and("schemas/intake_result.schema.json")

    def test_a_candidate_must_carry_routing_scores(self) -> None:
        intake = {
            "schema_version": "1.0.0",
            "jd_intake": {
                "schema_version": "1.0.0",
                "input_form": "pasted_text",
                "company": "Example",
                "role_family": "ai_product_manager",
                "requirements": [
                    {
                        "role_requirement_id": "r1",
                        "text": "Evaluate retrieval quality",
                        "relevance": "required",
                        "jd_location": "responsibilities",
                    }
                ],
                "likely_interview_risks": [],
                "unknowns": ["track"],
            },
            "role_demand_map": [
                {
                    "role_requirement_id": "r1",
                    "demand": "Can evaluate retrieval",
                    "relevance": "required",
                    "evidence_would_look_like": "a labeled eval set",
                }
            ],
            "interview_context": a_context(),
            "resume_project_candidates": [],
            "recommended_project": None,
            "claims_requiring_verification": [],
            "required_evidence_checklist": [
                {
                    "artifact": "eval_or_test_results",
                    "why_needed": "to verify retrieval evaluation",
                    "required": True,
                }
            ],
            "one_next_input": "the project to analyze",
        }
        self.assertEqual(
            [error.message for error in self.validator.iter_errors(intake)], []
        )

        intake["recommended_project"] = {
            "candidate_id": "c1",
            "reasons": ["closest to the role"],
            "risks": ["summary is self-reported"],
            "confidence": "clear_choice",
            "alternatives_considered": [],
        }
        self.assertFalse(
            self.validator.is_valid(intake),
            "recommended a project when no candidate exists",
        )


if __name__ == "__main__":
    unittest.main()
