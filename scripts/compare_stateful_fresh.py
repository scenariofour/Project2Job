from __future__ import annotations

import json
import sys
import argparse
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_agent_demo import OneResultCapabilities, initial_payload  # noqa: E402
from src.career_desk.orchestrator import (  # noqa: E402
    HostMediatedPlanner,
    RunRequest,
    ScriptedPlanner,
    StatefulEvidenceAgent,
)


class SequenceCapabilities:
    def __init__(self, results: list[dict]) -> None:
        self.results = list(results)

    def execute(self, action: str, context: dict) -> dict:
        return self.results.pop(0)


def values(outputs: dict) -> dict:
    return {
        output_id: {
            key: output.get(key)
            for key in ("value", "match", "content")
            if key in output
        }
        for output_id, output in outputs.items()
    }


def usage(trace: dict, key: str) -> int:
    return sum(step.get("usage", {}).get(key, 0) for step in trace["steps"])


def compare(host_action: str | None = None) -> dict:
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
    base_state = initial["state"]
    updated = initial_payload()
    updated["evidence"]["evidence_eval_result"] = {
        "source": "eval_results.csv",
        "location": "summary rows",
        "summary": "Executed evaluation met its threshold.",
    }
    updated["claims"]["claim_evaluation"]["status"] = "supported"
    updated["outputs"]["score_evaluation"].update(
        {
            "value": 4,
            "before": 3,
            "why": "Executed evaluation evidence was added.",
        }
    )
    updated["outputs"]["match_eval"].update(
        {
            "match": "EXACT MATCH",
            "before": "TRANSFERABLE",
            "why": "The revised evidence directly demonstrates the competency.",
        }
    )
    updated["dependencies"]["eval_results.csv"] = ["evidence_eval_result"]
    updated["dependencies"]["evidence_eval_result"] = ["claim_evaluation"]

    selective = deepcopy(updated)
    selective["affected_outputs"] = ["score_evaluation", "match_eval"]
    selective["usage"] = {
        "files_read": 1,
        "repeated_questions": 0,
        "tokens": 0,
    }

    observations: list[dict] = []

    def decide(observation: dict, allowed: tuple[str, ...]) -> str:
        observations.append(observation)
        if host_action is not None:
            if host_action not in allowed:
                raise ValueError(f"host action is not allowed: {host_action}")
            return host_action
        return (
            "investigate_evidence"
            if observation["detected_change"] == "project"
            else "stop"
        )

    stateful = StatefulEvidenceAgent(
        HostMediatedPlanner(decide),
        OneResultCapabilities(selective),
    ).run(
        RunRequest(
            project_version="project-v2",
            jd_version="jd-v1",
            artifacts={**artifacts_v1, "eval_results.csv": "e"},
        ),
        base_state,
    )

    fresh = deepcopy(updated)
    fresh["affected_outputs"] = sorted(fresh["outputs"])
    fresh["usage"] = {
        "files_read": 5,
        "repeated_questions": 0,
        "tokens": 0,
    }
    fresh_run = StatefulEvidenceAgent(
        ScriptedPlanner(["request_confirmation", "produce_brief"]),
        SequenceCapabilities(
            [
                {
                    "observation_summary": "Ownership confirmation requested again.",
                    "usage": {
                        "files_read": 0,
                        "repeated_questions": 1,
                        "tokens": 0,
                    },
                },
                fresh,
            ]
        ),
    ).run(
        RunRequest(
            project_version="project-v2",
            jd_version="jd-v1",
            artifacts={**artifacts_v1, "eval_results.csv": "e"},
        )
    )

    base_values = values(base_state.outputs)
    expected_values = values(updated["outputs"])
    expected_changed = sorted(
        key for key in expected_values if expected_values[key] != base_values.get(key)
    )
    expected_preserved = sorted(set(base_values) - set(expected_changed))

    def metrics(result: dict) -> dict:
        result_values = values(result["state"].outputs)
        return {
            "files_read": usage(result["trace"], "files_read"),
            "repeated_questions": usage(result["trace"], "repeated_questions"),
            "capability_calls": result["trace"]["usage"]["capability_calls"],
            "affected_outputs_correctly_updated": sum(
                result_values.get(key) == expected_values[key]
                for key in expected_changed
            ),
            "unaffected_outputs_incorrectly_changed": sum(
                result_values.get(key) != base_values[key]
                for key in expected_preserved
            ),
            "outputs_regenerated": len(result["trace"]["affected_outputs"]),
            "latency_ms": result["trace"]["usage"]["latency_ms"],
            "token_usage": usage(result["trace"], "tokens"),
            "trace_clarity": {
                "has_detected_change": bool(result["trace"]["detected_change"]),
                "has_stop_reason": bool(result["trace"]["stop_reason"]),
                "steps_with_validation": sum(
                    bool(step.get("validation_result"))
                    for step in result["trace"]["steps"]
                ),
            },
        }

    return {
        "comparison_type": "deterministic_scripted_dogfood",
        "expected_changed_outputs": expected_changed,
        "expected_preserved_outputs": expected_preserved,
        "stateful_agent_update": metrics(stateful),
        "fresh_skill_rerun": metrics(fresh_run),
        "host_mediated_decision": {
            "observation": observations[0],
            "selected_action": stateful["trace"]["steps"][0]["selected_action"],
            "decision_source": (
                "host_supplied_after_observation"
                if host_action is not None
                else "deterministic_observation_policy"
            ),
        },
        "conclusion": (
            "The scripted stateful update read fewer files, repeated no confirmed "
            "question, and regenerated only expected outputs while preserving "
            "the same deterministic output correctness."
        ),
        "limitations": [
            "This is scripted repository dogfood, not target-user validation.",
            "Token usage is unavailable because no model call was made.",
            "Sub-millisecond local latency is not representative of a live model path.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host-action")
    args = parser.parse_args()
    output = ROOT / "docs" / "dogfood" / "STATEFUL_AGENT_V0_COMPARISON.json"
    output.write_text(
        json.dumps(compare(args.host_action), indent=2) + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
