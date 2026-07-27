from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.career_desk.orchestrator import (
    EvidenceAgentState,
    HostMediatedPlanner,
    RunRequest,
    ScriptedPlanner,
    StatefulEvidenceAgent,
)

FIXTURES = ROOT / "apps" / "web" / "fixtures"


class OneResultCapabilities:
    def __init__(self, result: dict) -> None:
        self.result = result

    def execute(self, action: str, context: dict) -> dict:
        return self.result


def initial_payload() -> dict:
    claims = {
        "claim_problem": {
            "status": "supported",
            "attribution_scope": "directly_owned",
        },
        "claim_product": {
            "status": "supported",
            "attribution_scope": "directly_owned",
        },
        "claim_technical": {
            "status": "supported",
            "attribution_scope": "ai_assisted",
        },
        "claim_evaluation": {
            "status": "partially_supported",
            "attribution_scope": "directly_owned",
        },
        "claim_delivery": {
            "status": "supported",
            "attribution_scope": "directly_owned",
        },
    }
    evidence = {
        "evidence_problem": {
            "source": "README.md",
            "location": "Problem statement",
            "summary": "A concrete reliability problem and affected workflow are documented.",
        },
        "evidence_product": {
            "source": "decision_log.md",
            "location": "Decision 2",
            "summary": "The project records a bounded reliability-first product decision.",
        },
        "evidence_technical": {
            "source": "src/workflow.py",
            "location": "workflow controls",
            "summary": "The implementation contains the described workflow and fallback.",
        },
        "evidence_evaluation": {
            "source": "eval_plan.md",
            "location": "Acceptance criteria",
            "summary": "Evaluation is planned, but no executed result is present yet.",
        },
        "evidence_delivery": {
            "source": "decision_log.md",
            "location": "Learning notes",
            "summary": "Delivery decisions and one learning loop are recorded.",
        },
    }
    outputs = {
        "score_problem": {
            "kind": "score",
            "label": "Problem & User Evidence",
            "value": 3,
            "explanation": "The problem and workflow are clear; direct user evidence is limited.",
            "depends_on": ["claim_problem"],
        },
        "score_product": {
            "kind": "score",
            "label": "Product Judgment",
            "value": 4,
            "explanation": "The project records a bounded reliability-first tradeoff.",
            "depends_on": ["claim_product"],
        },
        "score_technical": {
            "kind": "score",
            "label": "Technical System",
            "value": 4,
            "explanation": "The workflow, fallback, and control boundaries are inspectable.",
            "depends_on": ["claim_technical"],
        },
        "score_evaluation": {
            "kind": "score",
            "label": "Evaluation & Reliability",
            "value": 3,
            "explanation": "Evaluation criteria exist, but executed comparative evidence is thin.",
            "depends_on": ["claim_evaluation"],
        },
        "score_delivery": {
            "kind": "score",
            "label": "Delivery & Learning Loop",
            "value": 3,
            "explanation": "Delivery and learning are visible; measured adoption is not.",
            "depends_on": ["claim_delivery"],
        },
        "match_api": {
            "kind": "jd_match",
            "label": "AI workflow reliability",
            "match": "EXACT MATCH",
            "evidence": "Implemented workflow controls and fallback.",
            "missing": "None for this competency.",
            "depends_on": ["claim_technical"],
        },
        "match_eval": {
            "kind": "jd_match",
            "label": "Evaluation design",
            "match": "TRANSFERABLE",
            "evidence": "Inspectible evaluation plan and criteria.",
            "missing": "Executed comparative results.",
            "depends_on": ["claim_evaluation"],
        },
        "match_commercial": {
            "kind": "jd_match",
            "label": "Commercial marketplace impact",
            "match": "GAP",
            "evidence": "No direct commercial outcome evidence.",
            "missing": "Seller workflow or revenue outcome.",
            "depends_on": ["claim_problem"],
        },
        "story_reliability": {
            "kind": "story",
            "label": "Designing a bounded AI workflow",
            "content": "Shows technical product judgment and reliability tradeoffs.",
            "depends_on": ["claim_product", "claim_technical"],
        },
        "story_failure": {
            "kind": "story",
            "label": "Turning a failure into a control",
            "content": "Shows diagnosis, prioritization, and learning.",
            "depends_on": ["claim_delivery"],
        },
        "route": {
            "kind": "route",
            "label": "Recommended Route",
            "route": "$p2j-upgrade",
            "content": "Review one bounded evaluation build because executed evidence is the largest role-relevant gap.",
            "depends_on": ["claim_evaluation"],
        },
    }
    dependencies: dict[str, list[str]] = {
        "README.md": ["evidence_problem"],
        "decision_log.md": ["evidence_product", "evidence_delivery"],
        "src/workflow.py": ["evidence_technical"],
        "eval_plan.md": ["evidence_evaluation"],
        "evidence_problem": ["claim_problem"],
        "evidence_product": ["claim_product"],
        "evidence_technical": ["claim_technical"],
        "evidence_evaluation": ["claim_evaluation"],
        "evidence_delivery": ["claim_delivery"],
        "claim_problem": ["score_problem", "match_commercial"],
        "claim_product": ["score_product", "story_reliability"],
        "claim_technical": ["score_technical", "match_api", "story_reliability"],
        "claim_evaluation": ["score_evaluation", "match_eval", "route"],
        "claim_delivery": ["score_delivery", "story_failure"],
        "jd": ["match_api", "match_eval", "match_commercial", "route"],
    }
    return {
        "evidence": evidence,
        "claims": claims,
        "outputs": outputs,
        "dependencies": dependencies,
        "affected_outputs": sorted(outputs),
        "observation_summary": "Project evidence was mapped to the target role and validated.",
        "usage": {
            "files_read": 4,
            "repeated_questions": 0,
            "tokens": 0,
        },
        "stop": True,
    }


def serialize(result: dict, view: str, extra: dict | None = None) -> dict:
    trace = deepcopy(result["trace"])
    trace["usage"]["latency_ms"] = 0
    payload = {
        "view": view,
        "project": {"name": "Sample AI Reliability Lab", "version": "1.1"},
        "jd": {"label": "Applied AI Product Manager"},
        "state": result["state"].to_dict(),
        "trace": trace,
    }
    if extra:
        payload.update(extra)
    return payload


def build_fixtures() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    artifacts_v1 = {
        "README.md": "a",
        "decision_log.md": "b",
        "src/workflow.py": "c",
        "eval_plan.md": "d",
    }
    initial = StatefulEvidenceAgent(
        ScriptedPlanner(["produce_brief"]),
        OneResultCapabilities(initial_payload()),
    ).run(
        RunRequest(
            project_version="project-v1",
            jd_version="jd-v1",
            artifacts=artifacts_v1,
        )
    )
    base_state: EvidenceAgentState = initial["state"]
    inspection = StatefulEvidenceAgent(
        ScriptedPlanner(["investigate_evidence"]),
        OneResultCapabilities({}),
    ).run(
        RunRequest(
            project_version="project-v1",
            jd_version="jd-v1",
            artifacts=artifacts_v1,
            correction={
                "claim_id": "claim_technical",
                "attribution_scope": "ai_assisted",
                "approved": False,
            },
        ),
        base_state,
    )
    update_result = {
        "evidence": {
            "evidence_eval_result": {
                "source": "eval_results.csv",
                "location": "summary rows",
                "summary": "Executed cases now show the workflow meeting its reliability threshold.",
            }
        },
        "claims": {
            "claim_evaluation": {
                "status": "supported",
                "attribution_scope": "directly_owned",
            }
        },
        "outputs": {
            "score_evaluation": {
                "kind": "score",
                "label": "Evaluation & Reliability",
                "value": 4,
                "before": 3,
                "explanation": "Executed evaluation results now support the reliability boundary.",
                "why": "A new results artifact provides executed evidence.",
                "depends_on": ["claim_evaluation"],
            },
            "match_eval": {
                "kind": "jd_match",
                "label": "Evaluation design",
                "match": "EXACT MATCH",
                "before": "TRANSFERABLE",
                "evidence": "Executed evaluation results and acceptance criteria.",
                "missing": "None for this competency.",
                "why": "The competency is now directly demonstrated.",
                "depends_on": ["claim_evaluation"],
            },
        },
        "dependencies": {
            "eval_results.csv": ["evidence_eval_result"],
            "evidence_eval_result": ["claim_evaluation"],
            "claim_evaluation": ["score_evaluation", "match_eval", "route"],
        },
        "affected_outputs": ["score_evaluation", "match_eval"],
        "observation_summary": "The new evaluation artifact directly supports two outputs.",
        "usage": {
            "files_read": 1,
            "repeated_questions": 0,
            "tokens": 0,
        },
        "stop": True,
    }

    observed: list[dict] = []

    def decide(observation: dict, allowed: tuple[str, ...]) -> str:
        observed.append(observation)
        return (
            "investigate_evidence"
            if observation["detected_change"] == "project"
            else "stop"
        )

    updated = StatefulEvidenceAgent(
        HostMediatedPlanner(decide),
        OneResultCapabilities(update_result),
    ).run(
        RunRequest(
            project_version="project-v2",
            jd_version="jd-v1",
            artifacts={**artifacts_v1, "eval_results.csv": "e"},
        ),
        base_state,
    )
    unchanged = StatefulEvidenceAgent(
        ScriptedPlanner(["produce_brief"]),
        OneResultCapabilities({}),
    ).run(
        RunRequest(
            project_version="project-v1",
            jd_version="jd-v1",
            artifacts=artifacts_v1,
        ),
        base_state,
    )

    fixtures = {
        "initial_analysis.json": serialize(initial, "initial_analysis"),
        "evidence_inspection.json": serialize(
            inspection,
            "evidence_inspection",
            {
                "inspection": {
                    "claim": "Designed and operated a reliable AI workflow.",
                    "sources": [
                        {
                            "label": "src/workflow.py — workflow controls",
                            "summary": "Shows the implemented workflow and fallback boundary.",
                        },
                        {
                            "label": "decision_log.md — Decision 2",
                            "summary": "Explains why reliability was prioritized.",
                        },
                    ],
                    "attribution_scope": "AI-assisted",
                    "affected_outputs": ["Technical System", "AI workflow reliability"],
                    "correction": {
                        "prompt": "Describe what you directly owned and what AI assisted with.",
                        "preview": [
                            {
                                "before": "Designed and operated a reliable AI workflow.",
                                "after": "Designed the workflow boundary and used AI assistance during implementation.",
                                "why": "The wording should preserve the confirmed attribution boundary.",
                            }
                        ],
                    },
                }
            },
        ),
        "project_updated.json": serialize(
            updated,
            "project_updated",
            {"host_observation_used": observed[0]},
        ),
        "no_relevant_changes.json": serialize(
            unchanged, "no_relevant_changes"
        ),
    }
    for name, payload in fixtures.items():
        (FIXTURES / name).write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    build_fixtures()
