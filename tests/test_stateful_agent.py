from __future__ import annotations

import unittest

from src.career_desk.orchestrator import (
    AgentBudget,
    EvidenceAgentState,
    HostMediatedPlanner,
    RunRequest,
    ScriptedPlanner,
    StatefulEvidenceAgent,
)


class ScriptedCapabilities:
    def __init__(self, results: list[dict]) -> None:
        self.results = list(results)
        self.calls: list[dict] = []

    def execute(self, action: str, context: dict) -> dict:
        self.calls.append({"action": action, "context": context})
        if not self.results:
            raise AssertionError("unexpected capability call")
        return self.results.pop(0)


def existing_state() -> EvidenceAgentState:
    return EvidenceAgentState(
        project_version="project-v1",
        jd_version="jd-v1",
        artifacts={"README.md": "a", "eval.json": "b"},
        evidence={
            "e_api": {"source": "README.md", "summary": "API workflow exists"},
            "e_eval": {"source": "eval.json", "summary": "Evaluation result"},
        },
        claims={
            "c_api": {
                "status": "supported",
                "attribution_scope": "directly_owned",
            },
            "c_eval": {
                "status": "supported",
                "attribution_scope": "ai_assisted",
            },
        },
        outputs={
            "score_technical": {
                "kind": "score",
                "value": 4,
                "depends_on": ["c_api"],
            },
            "score_evaluation": {
                "kind": "score",
                "value": 3,
                "depends_on": ["c_eval"],
            },
            "match_eval": {
                "kind": "jd_match",
                "match": "TRANSFERABLE",
                "depends_on": ["c_eval"],
            },
            "story_api": {
                "kind": "story",
                "content": "API reliability",
                "depends_on": ["c_api"],
            },
        },
        dependencies={
            "README.md": ["e_api"],
            "e_api": ["c_api"],
            "c_api": ["score_technical", "story_api"],
            "eval.json": ["e_eval"],
            "e_eval": ["c_eval"],
            "c_eval": ["score_evaluation", "match_eval"],
            "jd": ["match_eval"],
        },
        confirmed_facts={
            "ownership": {"scope": "directly_owned", "confirmed": True}
        },
    )


class StatefulAgentTests(unittest.TestCase):
    def test_initial_run_saves_dependency_backed_outputs_and_trace(self) -> None:
        capabilities = ScriptedCapabilities(
            [
                {
                    "evidence": {
                        "e1": {"source": "README.md", "summary": "Observed fact"}
                    },
                    "claims": {
                        "c1": {
                            "status": "supported",
                            "attribution_scope": "directly_owned",
                        }
                    },
                    "outputs": {
                        "score_problem": {
                            "kind": "score",
                            "value": 3,
                            "depends_on": ["c1"],
                        }
                    },
                    "dependencies": {
                        "README.md": ["e1"],
                        "e1": ["c1"],
                        "c1": ["score_problem"],
                    },
                    "affected_outputs": ["score_problem"],
                    "observation_summary": "The project evidence supports the score.",
                    "usage": {"files_read": 1, "tokens": 0},
                    "stop": True,
                }
            ]
        )
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["produce_brief"]), capabilities
        ).run(
            RunRequest(
                project_version="project-v1",
                jd_version="jd-v1",
                artifacts={"README.md": "a"},
            )
        )
        self.assertEqual(result["trace"]["detected_change"], "new")
        self.assertEqual(result["trace"]["affected_outputs"], ["score_problem"])
        self.assertEqual(result["trace"]["stop_reason"], "complete")
        self.assertEqual(
            result["state"].dependencies["README.md"], ["e1"]
        )

    def test_no_change_rerun_reads_nothing_and_regenerates_nothing(self) -> None:
        capabilities = ScriptedCapabilities([])
        state = existing_state()
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["produce_brief"]), capabilities
        ).run(
            RunRequest(
                project_version=state.project_version,
                jd_version=state.jd_version,
                artifacts=state.artifacts,
            ),
            state,
        )
        self.assertEqual(result["trace"]["stop_reason"], "no_relevant_changes")
        self.assertEqual(result["trace"]["usage"]["capability_calls"], 0)
        self.assertEqual(result["trace"]["affected_outputs"], [])
        self.assertEqual(
            result["trace"]["preserved_outputs"], sorted(state.outputs)
        )

    def test_correction_requires_approval_before_state_changes(self) -> None:
        state = existing_state()
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["investigate_evidence"]), ScriptedCapabilities([])
        ).run(
            RunRequest(
                project_version=state.project_version,
                jd_version=state.jd_version,
                artifacts=state.artifacts,
                correction={
                    "claim_id": "c_api",
                    "attribution_scope": "collaborator_owned",
                    "approved": False,
                },
            ),
            state,
        )
        self.assertEqual(
            result["trace"]["stop_reason"], "correction_approval_required"
        )
        self.assertEqual(
            result["state"].claims["c_api"]["attribution_scope"],
            "directly_owned",
        )

    def test_approved_correction_updates_dependents_and_preserves_unrelated(self) -> None:
        state = existing_state()
        capabilities = ScriptedCapabilities(
            [
                {
                    "claims": {
                        "c_api": {
                            "status": "partially_supported",
                            "attribution_scope": "collaborator_owned",
                        }
                    },
                    "outputs": {
                        "score_technical": {
                            "kind": "score",
                            "value": 3,
                            "depends_on": ["c_api"],
                            "before": 4,
                            "why": "Ownership was corrected.",
                        },
                        "story_api": {
                            "kind": "story",
                            "content": "Team API reliability contribution",
                            "depends_on": ["c_api"],
                            "before": "API reliability",
                            "why": "Ownership was corrected.",
                        },
                    },
                    "affected_outputs": ["score_technical", "story_api"],
                    "observation_summary": "Approved ownership correction applied.",
                    "stop": True,
                }
            ]
        )
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["investigate_evidence"]), capabilities
        ).run(
            RunRequest(
                project_version=state.project_version,
                jd_version=state.jd_version,
                artifacts=state.artifacts,
                correction={
                    "claim_id": "c_api",
                    "attribution_scope": "collaborator_owned",
                    "approved": True,
                },
            ),
            state,
        )
        self.assertEqual(
            result["trace"]["affected_outputs"],
            ["score_technical", "story_api"],
        )
        self.assertIn("score_evaluation", result["trace"]["preserved_outputs"])
        self.assertEqual(
            result["state"].outputs["score_technical"]["before"], 4
        )

    def test_removed_evidence_invalidates_only_dependent_outputs(self) -> None:
        state = existing_state()
        capabilities = ScriptedCapabilities(
            [
                {
                    "claims": {
                        "c_eval": {
                            "status": "not_found",
                            "attribution_scope": "ai_assisted",
                        }
                    },
                    "outputs": {
                        "score_evaluation": {
                            "kind": "score",
                            "value": 1,
                            "depends_on": ["c_eval"],
                            "before": 3,
                            "why": "The supporting evaluation artifact was removed.",
                        },
                        "match_eval": {
                            "kind": "jd_match",
                            "match": "GAP",
                            "depends_on": ["c_eval"],
                            "before": "TRANSFERABLE",
                            "why": "The supporting evaluation artifact was removed.",
                        },
                    },
                    "affected_outputs": ["score_evaluation", "match_eval"],
                    "observation_summary": "Removed evidence was rechecked.",
                    "stop": True,
                }
            ]
        )
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["investigate_evidence"]), capabilities
        ).run(
            RunRequest(
                project_version="project-v2",
                jd_version=state.jd_version,
                artifacts={"README.md": "a"},
            ),
            state,
        )
        self.assertEqual(
            result["trace"]["affected_outputs"],
            ["match_eval", "score_evaluation"],
        )
        self.assertIn("score_technical", result["trace"]["preserved_outputs"])

    def test_jd_update_reuses_project_evidence(self) -> None:
        state = existing_state()
        capabilities = ScriptedCapabilities(
            [
                {
                    "outputs": {
                        "match_eval": {
                            "kind": "jd_match",
                            "match": "EXACT MATCH",
                            "depends_on": ["c_eval"],
                            "before": "TRANSFERABLE",
                            "why": "The revised JD now asks for direct evaluation work.",
                        }
                    },
                    "affected_outputs": ["match_eval"],
                    "observation_summary": "JD requirements were refreshed.",
                    "usage": {"files_read": 0, "project_evidence_reused": 2},
                    "stop": True,
                }
            ]
        )
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["refresh_jd_context"]), capabilities
        ).run(
            RunRequest(
                project_version=state.project_version,
                jd_version="jd-v2",
                artifacts=state.artifacts,
            ),
            state,
        )
        self.assertEqual(
            capabilities.calls[0]["action"], "refresh_jd_context"
        )
        self.assertEqual(result["state"].evidence, state.evidence)
        self.assertEqual(result["trace"]["affected_outputs"], ["match_eval"])

    def test_one_bounded_repair_downgrades_overstrong_exact_match(self) -> None:
        capabilities = ScriptedCapabilities(
            [
                {
                    "claims": {
                        "c1": {
                            "status": "partially_supported",
                            "attribution_scope": "directly_owned",
                        }
                    },
                    "outputs": {
                        "m1": {
                            "kind": "jd_match",
                            "match": "EXACT MATCH",
                            "depends_on": ["c1"],
                        }
                    },
                    "affected_outputs": ["m1"],
                    "observation_summary": "A match was proposed.",
                    "stop": True,
                }
            ]
        )
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["produce_brief"]), capabilities
        ).run(
            RunRequest(
                project_version="p1",
                jd_version="j1",
                artifacts={"README.md": "a"},
            )
        )
        self.assertEqual(result["state"].outputs["m1"]["match"], "TRANSFERABLE")
        self.assertEqual(result["trace"]["usage"]["repairs"], 1)
        self.assertEqual(
            result["trace"]["steps"][0]["validation_result"], "repaired"
        )

    def test_unrecoverable_validation_failure_stops_visibly(self) -> None:
        capabilities = ScriptedCapabilities(
            [
                {
                    "outputs": {
                        "score_bad": {"kind": "score", "value": 5}
                    },
                    "affected_outputs": ["score_bad"],
                    "observation_summary": "An invalid score was proposed.",
                }
            ]
        )
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["produce_brief"]), capabilities
        ).run(
            RunRequest(
                project_version="p1",
                jd_version="j1",
                artifacts={"README.md": "a"},
            )
        )
        self.assertEqual(result["trace"]["stop_reason"], "validation_failed")
        self.assertEqual(
            result["trace"]["steps"][0]["validation_result"], "failed"
        )

    def test_budget_guarantees_termination(self) -> None:
        capabilities = ScriptedCapabilities(
            [
                {"observation_summary": "continue"},
                {"observation_summary": "continue"},
            ]
        )
        result = StatefulEvidenceAgent(
            ScriptedPlanner(["investigate_evidence", "produce_brief"]),
            capabilities,
            AgentBudget(max_turns=1, max_capability_calls=1, max_repairs=1),
        ).run(
            RunRequest(
                project_version="p1",
                jd_version="j1",
                artifacts={"README.md": "a"},
            )
        )
        self.assertEqual(result["trace"]["stop_reason"], "budget_exhausted")
        self.assertEqual(len(capabilities.calls), 1)

    def test_host_mediated_path_selects_from_live_observation(self) -> None:
        seen: list[dict] = []

        def decide(observation: dict, allowed: tuple[str, ...]) -> str:
            seen.append(observation)
            if observation["detected_change"] == "project":
                return "investigate_evidence"
            return "stop"

        state = existing_state()
        capabilities = ScriptedCapabilities(
            [
                {
                    "affected_outputs": [],
                    "observation_summary": "Changed artifact inspected.",
                    "stop": True,
                }
            ]
        )
        result = StatefulEvidenceAgent(
            HostMediatedPlanner(decide), capabilities
        ).run(
            RunRequest(
                project_version="project-v2",
                jd_version=state.jd_version,
                artifacts={**state.artifacts, "notes.md": "c"},
            ),
            state,
        )
        self.assertEqual(seen[0]["detected_change"], "project")
        self.assertEqual(
            result["trace"]["steps"][0]["selected_action"],
            "investigate_evidence",
        )


if __name__ == "__main__":
    unittest.main()
