"""JD-first intake: one target JD to one Intake Result (WO-05, Day 2).

The runtime is deterministic and host-native. It parses only what the JD
states, records everything else as unknown, and depends on the host for web
capability through the `ResearchHost` protocol in `research.py`. Nothing here
verifies a project: resume material stays `self_reported`, and interview
research never becomes project evidence.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .research import (
    BoundedResearch,
    canonical_url,
    unavailable_context,
    usage_exceeding_budget,
    user_supplied_context,
)

ROOT = Path(__file__).resolve().parents[2]
ROLE_PROFILE_PATH = ROOT / "references/role_profiles/ai_pm_early_career.v0.1.0.json"

SCHEMA_VERSION = "1.0.0"

#: JD header fields the parser reads verbatim. Anything absent is unknown.
STATED_FIELDS = {
    "company": ("company",),
    "team_or_product_area": ("team", "product area", "team or product area"),
    "track": ("track",),
    "level": ("level", "seniority"),
    "location": ("location",),
}

ROLE_FAMILIES = (
    ("agent product manager", "agent_product_manager"),
    ("agent pm", "agent_product_manager"),
    ("applied ai product manager", "applied_ai_product_manager"),
    ("applied ai pm", "applied_ai_product_manager"),
    ("ai product manager", "ai_product_manager"),
    ("ai pm", "ai_product_manager"),
)

REQUIRED_HEADINGS = ("responsibilities", "requirements", "qualifications", "you will")
SUPPORTING_HEADINGS = ("preferred", "nice to have", "bonus", "plus")

#: Capability keywords from the versioned role profile's ten domains.
CAPABILITY_KEYWORDS = {
    "D1": ("user", "problem", "customer", "pain", "discovery"),
    "D2": ("scope", "prioriti", "roadmap", "tradeoff", "prd", "spec", "requirement"),
    "D3": ("model", "llm", "prompt", "ai fit", "fine-tune", "capability boundary"),
    "D4": ("agent", "workflow", "orchestrat", "stop condition", "tool call"),
    "D5": ("retriev", "rag", "context", "data", "index", "embedding"),
    "D6": ("eval", "quality", "error analysis", "bad case", "regression", "test"),
    "D7": ("safety", "reliab", "guardrail", "human in the loop", "permission", "risk"),
    "D8": ("metric", "cost", "latency", "token", "performance", "kpi"),
    "D9": ("ship", "launch", "cross-functional", "stakeholder", "deliver", "engineering"),
    "D10": ("communicat", "write", "present", "ownership", "document"),
}

CAPABILITY_ARTIFACTS = {
    "D1": "user_or_stakeholder_feedback",
    "D2": "prd_or_spec",
    "D3": "repository_or_code",
    "D4": "repository_or_code",
    "D5": "repository_or_code",
    "D6": "eval_or_test_results",
    "D7": "prd_or_spec",
    "D8": "metrics_or_analytics",
    "D9": "prd_or_spec",
    "D10": "prd_or_spec",
}

GENERIC_EVIDENCE = (
    "A dated project artifact that shows this requirement was met in practice."
)


#: Phrases that name an artifact a reviewer could actually open. Naming the
#: topic of the JD is not the same as having something to show for it.
ARTIFACT_TERMS = (
    "repository",
    "repo",
    "github",
    "source code",
    "prd",
    "spec",
    "design doc",
    "eval set",
    "eval harness",
    "labeled",
    "test suite",
    "regression test",
    "dashboard",
    "metrics",
    "analytics",
    "user feedback",
    "interview notes",
    "survey",
    "demo",
    "dataset",
    "notebook",
)

OWNERSHIP_STRONG = ("i led", "i owned", "i designed", "i built", "i wrote", "sole", "solo")
OWNERSHIP_ADEQUATE = ("co-led", "with a partner", "i contributed", "my part")
OWNERSHIP_WEAK = ("we ", "team", "our ")

OUTCOME_WORDS = (
    "reduced",
    "improved",
    "increased",
    "cut ",
    "raised",
    "shipped",
    "adopted",
    "launched",
)
OUTCOME_WEAK = ("planned", "prototype", "in progress", "wip", "unfinished")

DEPTH_TERMS = (
    "tradeoff",
    "trade-off",
    "decision",
    "iterat",
    "bad case",
    "failure",
    "root cause",
    "alternative",
    "rejected",
    "stop condition",
    "error analysis",
)

BAND_ORDER = {"strong": 3, "adequate": 2, "weak": 1, "unknown": 0}
#: A candidate whose evidence is unlikely to exist cannot be recommended,
#: however well its wording matches the JD.
ROUTABLE_EVIDENCE_BANDS = ("strong", "adequate")


def _role_profile() -> dict:
    return json.loads(ROLE_PROFILE_PATH.read_text(encoding="utf-8"))


def _pass_conditions() -> dict[str, str]:
    return {
        capability["capability_id"]: capability["evidence_tests"][0]["pass_condition"]
        for capability in _role_profile()["capabilities"]
    }


def _capability_for(text: str) -> str | None:
    lowered = text.lower()
    for capability_id, keywords in CAPABILITY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return capability_id
    return None


def _relevance_for(heading: str) -> str:
    lowered = heading.lower()
    if any(word in lowered for word in SUPPORTING_HEADINGS):
        return "supporting"
    if any(word in lowered for word in REQUIRED_HEADINGS):
        return "required"
    return "important"


def extract_jd(
    jd_text: str,
    *,
    input_form: str = "pasted_text",
    jd_reference: str | None = None,
) -> dict:
    """Extract what the JD states. Everything it does not state is unknown.

    The parser reads `Field: value` headers and bulleted sections. It never
    infers a team, track, or level from the company name or the role title.
    """
    stated: dict[str, str] = {}
    requirements: list[dict] = []
    heading = "unlabeled"
    title = ""

    for raw_line in jd_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("-", "*", "•")):
            text = line.lstrip("-*• ").strip()
            if not text:
                continue
            requirements.append(
                {
                    "role_requirement_id": f"r{len(requirements) + 1}",
                    "text": text,
                    "relevance": _relevance_for(heading),
                    "jd_location": heading,
                }
            )
            continue
        label, separator, value = line.partition(":")
        label_key = label.strip().lower()
        value = value.strip()
        if separator and value:
            if label_key in ("role", "title", "position"):
                title = value
                continue
            for field, aliases in STATED_FIELDS.items():
                if label_key in aliases:
                    stated[field] = value
                    break
            continue
        if separator and not value:
            heading = label.strip()

    role_family = "other_or_unsupported"
    lowered_title = title.lower()
    for marker, family in ROLE_FAMILIES:
        if marker in lowered_title:
            role_family = family
            break

    unknowns = [field for field in STATED_FIELDS if field not in stated]
    if not title:
        unknowns.append("role_title")
    capabilities = _pass_conditions()
    for requirement in requirements:
        capability_id = _capability_for(requirement["text"])
        if capability_id in capabilities:
            requirement["capability_id"] = capability_id

    intake = {
        "schema_version": SCHEMA_VERSION,
        "input_form": input_form,
        "company": stated.get("company", "unstated"),
        "role_family": role_family,
        "requirements": requirements,
        "likely_interview_risks": [
            f"The JD states “{requirement['text']}”; expect the loop to probe it."
            for requirement in requirements
            if requirement["relevance"] == "required"
        ][:3],
        "unknowns": unknowns,
    }
    for field in ("team_or_product_area", "track", "level", "location"):
        if field in stated:
            intake[field] = stated[field]
    if jd_reference:
        intake["jd_reference"] = jd_reference
    return intake


def role_demand_map(jd_intake: dict) -> list[dict]:
    """What the role demands, and what evidence would satisfy each demand."""
    conditions = _pass_conditions()
    demands = []
    for requirement in jd_intake["requirements"]:
        text = requirement["text"]
        capability_id = requirement.get("capability_id")
        demands.append(
            {
                "role_requirement_id": requirement["role_requirement_id"],
                "demand": f"Can {text[0].lower()}{text[1:]}",
                "relevance": requirement["relevance"],
                "evidence_would_look_like": conditions.get(
                    capability_id or "", GENERIC_EVIDENCE
                ),
            }
        )
    return demands


def required_evidence_checklist(jd_intake: dict, ownership_clear: bool) -> list[dict]:
    """Which artifacts the user must supply before deep analysis can run."""
    checklist: list[dict] = []
    seen: set[str] = set()
    for requirement in jd_intake["requirements"]:
        artifact = CAPABILITY_ARTIFACTS.get(
            requirement.get("capability_id", ""), "repository_or_code"
        )
        if artifact in seen:
            continue
        seen.add(artifact)
        checklist.append(
            {
                "artifact": artifact,
                "why_needed": f"To verify: {requirement['text']}",
                "required": requirement["relevance"] == "required",
            }
        )
    if not checklist:
        checklist.append(
            {
                "artifact": "repository_or_code",
                "why_needed": "To verify any claim about the selected project.",
                "required": True,
            }
        )
    checklist = checklist[:5]
    if not ownership_clear:
        checklist.append(
            {
                "artifact": "ownership_clarification",
                "why_needed": "The resume summary does not establish who did the work.",
                "required": True,
            }
        )
    return checklist


def extract_resume_candidates(resume_text: str) -> list[dict]:
    """Extract project summaries from a resume, for routing only.

    Nothing extracted here is evidence. Every candidate is `self_reported`
    until the project's own sources are read.
    """
    candidates: list[dict] = []
    heading = "resume"
    for raw_line in resume_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("-", "*", "•")):
            summary = line.lstrip("-*• ").strip()
            if summary:
                candidates.append(
                    {
                        "candidate_id": f"c{len(candidates) + 1}",
                        "summary": summary,
                        "resume_location": heading,
                        "evidence_status": "self_reported",
                    }
                )
            continue
        if line.endswith(":"):
            heading = line.rstrip(":").strip().lower() or heading
            continue
        if candidates:  # a wrapped continuation of the previous bullet
            candidates[-1]["summary"] = f"{candidates[-1]['summary']} {line}"
    return candidates


def _band(count: int, strong: int, adequate: int) -> str:
    if count >= strong:
        return "strong"
    if count >= adequate:
        return "adequate"
    return "weak"


def routing_scores(summary: str, jd_intake: dict) -> dict:
    """Five coarse bands. Keyword overlap is one of them, never the decider."""
    text = summary.lower()
    demanded = {
        requirement["capability_id"]
        for requirement in jd_intake["requirements"]
        if requirement.get("capability_id")
    }
    matched_capabilities = sum(
        1
        for capability_id in demanded
        if any(keyword in text for keyword in CAPABILITY_KEYWORDS[capability_id])
    )
    # Relative to what this JD demands, so a short JD does not make every
    # candidate look weak and a long one does not make every candidate strong.
    covered = matched_capabilities / len(demanded) if demanded else 0.0
    artifacts = sum(1 for term in ARTIFACT_TERMS if term in text)
    depth = sum(1 for term in DEPTH_TERMS if term in text)

    if len(text.split()) < 6:
        availability = "unknown"
    else:
        availability = _band(artifacts, 3, 2)

    if any(term in text for term in OWNERSHIP_STRONG):
        ownership = "strong"
    elif any(term in text for term in OWNERSHIP_ADEQUATE):
        ownership = "adequate"
    elif any(term in text for term in OWNERSHIP_WEAK):
        ownership = "weak"
    else:
        ownership = "unknown"

    has_outcome = any(term in text for term in OUTCOME_WORDS)
    if has_outcome and re.search(r"\d", text):
        outcome = "strong"
    elif has_outcome:
        outcome = "adequate"
    elif any(term in text for term in OUTCOME_WEAK):
        outcome = "weak"
    else:
        outcome = "unknown"

    if not demanded:
        relevance = "unknown"
    elif covered >= 2 / 3:
        relevance = "strong"
    elif covered >= 1 / 3:
        relevance = "adequate"
    else:
        relevance = "weak"

    return {
        "role_relevance": relevance,
        "likely_evidence_availability": availability,
        "ownership_clarity": ownership,
        "outcome_strength": outcome,
        "interview_depth": _band(depth, 2, 1),
    }


def _rank_key(candidate: dict) -> tuple[int, ...]:
    scores = candidate["scores"]
    return tuple(
        BAND_ORDER[scores[dimension]]
        for dimension in (
            "likely_evidence_availability",
            "role_relevance",
            "ownership_clarity",
            "outcome_strength",
            "interview_depth",
        )
    )


def recommend_project(candidates: list[dict]) -> dict | None:
    """Recommend exactly one project, or decline with `no_clear_choice`."""
    if not candidates:
        return None

    every_id = [candidate["candidate_id"] for candidate in candidates]
    routable = [
        candidate
        for candidate in candidates
        if candidate["scores"]["likely_evidence_availability"] in ROUTABLE_EVIDENCE_BANDS
    ]
    ranked = sorted(routable, key=lambda candidate: (_rank_key(candidate), candidate["candidate_id"]), reverse=True)

    declined_reasons = ["No candidate is a defensible choice from resume text alone."]
    risks = [
        "Routing used self-reported resume summaries; none of it is verified evidence."
    ]
    if not ranked:
        return {
            "candidate_id": None,
            "reasons": [
                *declined_reasons,
                "Every candidate's likely evidence availability is weak or unknown.",
            ],
            "risks": risks,
            "confidence": "no_clear_choice",
            "alternatives_considered": every_id,
        }
    if len(ranked) > 1 and _rank_key(ranked[0]) == _rank_key(ranked[1]):
        return {
            "candidate_id": None,
            "reasons": [*declined_reasons, "Two candidates rank identically."],
            "risks": risks,
            "confidence": "no_clear_choice",
            "alternatives_considered": every_id,
        }

    winner = ranked[0]
    scores = winner["scores"]
    reasons = [
        "Likely evidence availability is "
        f"{scores['likely_evidence_availability']}: the summary names artifacts a "
        "reviewer could open.",
        f"Role relevance against this JD is {scores['role_relevance']}.",
    ]
    if any(
        BAND_ORDER[candidate["scores"]["role_relevance"]]
        >= BAND_ORDER[scores["role_relevance"]]
        for candidate in candidates
        if candidate["candidate_id"] != winner["candidate_id"]
    ):
        reasons.append(
            "Candidates were ranked on likely evidence availability first: "
            "evidence availability outranks keyword overlap."
        )
    if scores["ownership_clarity"] != "strong":
        risks.append("The summary does not establish who did the work.")
    if scores["outcome_strength"] in ("weak", "unknown"):
        risks.append("The summary states no measured outcome.")

    runner_up = _rank_key(ranked[1]) if len(ranked) > 1 else (0, 0, 0, 0, 0)
    winner_key = _rank_key(winner)
    # A clear choice needs both a margin over the field and a strong candidate
    # of its own. Winning a weak field is a narrow choice, not a clear one.
    clear = (
        scores["likely_evidence_availability"] == "strong"
        and (winner_key[0] > runner_up[0] or sum(winner_key) - sum(runner_up) >= 3)
    )
    return {
        "candidate_id": winner["candidate_id"],
        "reasons": reasons,
        "risks": risks,
        "confidence": "clear_choice" if clear else "narrow_choice",
        "alternatives_considered": [
            candidate_id for candidate_id in every_id if candidate_id != winner["candidate_id"]
        ],
    }


def jd_inferred_signals(jd_intake: dict) -> list[dict]:
    """Signals derived from the JD alone.

    A JD inference is never a report. It stays `inferred_from_jd`, is presented
    as speculative, and always sits in the company layer: a track requirement
    would need a track the JD did not state.
    """
    signals = []
    for requirement in jd_intake["requirements"]:
        if requirement["relevance"] != "required":
            continue
        signals.append(
            {
                "signal_id": f"jd-{requirement['role_requirement_id']}",
                "layer": "company_interview_signal",
                "statement": (
                    f"The JD asks for: {requirement['text']}. "
                    "The loop may probe it; no source confirms how."
                ),
                "source_status": "inferred_from_jd",
                "presented_as": "speculative",
                "tier": "unknown",
                "sources": [
                    {
                        "origin": "job_description",
                        "reference": requirement["jd_location"],
                    }
                ],
                "freshness": "unknown",
                "company": jd_intake["company"],
            }
        )
    return signals[:3]


def cross_reference_errors(intake_result: dict) -> list[str]:
    """Checks that span objects, which one JSON Schema document cannot express.

    Schema validation and these checks are complementary: a document can be
    schema-valid and still recommend a candidate that does not exist, cite a
    page the run never read, or report spending more than it declared.
    """
    errors: list[str] = []
    candidates = {
        candidate["candidate_id"] for candidate in intake_result["resume_project_candidates"]
    }
    recommendation = intake_result.get("recommended_project")
    if recommendation and recommendation["candidate_id"] is not None:
        if recommendation["candidate_id"] not in candidates:
            errors.append(
                f"recommended candidate_id {recommendation['candidate_id']} "
                "is not one of the extracted candidates"
            )
        if recommendation["candidate_id"] in recommendation["alternatives_considered"]:
            errors.append("the recommended candidate is also listed as an alternative")

    context = intake_result["interview_context"]
    research = context["research"]
    errors.extend(usage_exceeding_budget(research))

    extracted: dict[str, dict] = {}
    for page in research["pages"]:
        canonical = page.get("canonical_url", page["url"])
        if page["outcome"] == "extracted":
            if canonical in extracted:
                errors.append(f"two extracted pages share the canonical URL {canonical}")
            extracted[canonical] = page
        if page["outcome"] == "duplicate_of_kept_page" and page["duplicate_of"] not in {
            other.get("canonical_url", other["url"])
            for other in research["pages"]
            if other["outcome"] == "extracted"
        }:
            errors.append(
                f"duplicate page names {page['duplicate_of']}, which no kept page uses"
            )

    for item in [*context["signals"], *context["questions"]]:
        for source in item["sources"]:
            url = source.get("url")
            if url and canonical_url(url) not in extracted:
                errors.append(f"claim cites {url}, which this run did not extract")

    conflict_ids = {
        item_id for conflict in context.get("conflicts", []) for item_id in conflict["item_ids"]
    }
    known_ids = {signal["signal_id"] for signal in context["signals"]} | {
        question["question_id"] for question in context["questions"]
    }
    errors.extend(
        f"conflict names unknown item {item_id}"
        for item_id in sorted(conflict_ids - known_ids)
    )
    return errors


def _one_next_input(recommendation: dict | None, candidates: list[dict]) -> str:
    if recommendation is None:
        return "Send one project to analyze: its repository, PRD, evals, or feedback."
    if recommendation["candidate_id"] is None:
        return (
            "Choose which project to analyze, then send its repository or files; "
            "no candidate is defensible from resume text alone."
        )
    chosen = next(
        candidate
        for candidate in candidates
        if candidate["candidate_id"] == recommendation["candidate_id"]
    )
    name = chosen["summary"].split(":")[0].strip()
    return f"Send the repository or files for one project: {name}."


def interview_context(
    jd: dict,
    *,
    research_host=None,
    pasted_reports: list | None = None,
    budget: dict | None = None,
    today: date,
) -> dict:
    """Company and interview research for this JD. Never project evidence."""
    if research_host is not None:
        run = BoundedResearch(
            jd["company"],
            research_host,
            today=today,
            budget=budget,
            track=jd.get("track"),
        ).run()
    elif pasted_reports:
        run = user_supplied_context(jd["company"], pasted_reports, today)
    else:
        run = unavailable_context()

    context = {
        "schema_version": SCHEMA_VERSION,
        "company": jd["company"],
        "research": run.research,
        "signals": [*run.signals, *jd_inferred_signals(jd)],
        "questions": run.questions,
        "unknowns": [*jd["unknowns"], *run.research["gaps"]],
    }
    for field in ("track", "level", "location"):
        if field in jd:
            context[field] = jd[field]
    if run.conflicts:
        context["conflicts"] = run.conflicts
    return context


def run_intake(
    jd_text: str,
    *,
    input_form: str = "pasted_text",
    jd_reference: str | None = None,
    resume_text: str | None = None,
    research_host=None,
    pasted_reports: list | None = None,
    research_budget: dict | None = None,
    today: date | None = None,
) -> dict:
    """Run the JD-first intake and return one Intake Result instance."""
    today = today or date.today()
    jd = extract_jd(jd_text, input_form=input_form, jd_reference=jd_reference)
    demands = role_demand_map(jd)
    candidates = extract_resume_candidates(resume_text) if resume_text else []
    for candidate in candidates:
        candidate["scores"] = routing_scores(candidate["summary"], jd)
    recommendation = recommend_project(candidates)
    ownership_clear = bool(recommendation) and recommendation["candidate_id"] is not None and next(
        candidate["scores"]["ownership_clarity"]
        for candidate in candidates
        if candidate["candidate_id"] == recommendation["candidate_id"]
    ) == "strong"
    context = interview_context(
        jd,
        research_host=research_host,
        pasted_reports=pasted_reports,
        budget=research_budget,
        today=today,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "jd_intake": jd,
        "role_demand_map": demands,
        "interview_context": context,
        "resume_project_candidates": candidates,
        "recommended_project": recommendation,
        "claims_requiring_verification": [
            f"Self-reported: {candidate['summary']}" for candidate in candidates
        ],
        "required_evidence_checklist": required_evidence_checklist(jd, ownership_clear),
        "one_next_input": _one_next_input(recommendation, candidates),
    }
