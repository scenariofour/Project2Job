from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import context_registry

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if (REPOSITORY_ROOT / "PROJECT_MANIFEST.json").is_file():
    sys.path.insert(0, str(REPOSITORY_ROOT))

try:
    from src.career_desk.capabilities import (
        Project2JobCapabilities,
        execution_handoff,
    )
    from src.career_desk.orchestrator import (
        EvidenceAgentState,
        HostMediatedPlanner,
        RunRequest,
        StatefulEvidenceAgent,
    )
except ModuleNotFoundError:
    from career_desk.capabilities import Project2JobCapabilities, execution_handoff
    from career_desk.orchestrator import (
        EvidenceAgentState,
        HostMediatedPlanner,
        RunRequest,
        StatefulEvidenceAgent,
    )


def observed_metrics(trace: dict, expected: set[str]) -> dict:
    affected = set(trace["affected_outputs"])
    file_paths = {
        event.get("path")
        for step in trace["steps"]
        for event in step.get("events", [])
        if event.get("kind") == "file_opened"
    }
    usage = trace["usage"]
    return {
        "files_opened": len(file_paths),
        "questions_asked": usage.get("questions_asked", 0),
        "capability_calls": usage["capability_calls"],
        "outputs_regenerated": len(affected),
        "outputs_preserved": len(trace["preserved_outputs"]),
        "expected_outputs_correctly_updated": len(affected & expected),
        "unrelated_outputs_incorrectly_changed": len(affected - expected),
        "latency_ms": usage["latency_ms"],
        "token_usage": usage.get("token_usage"),
    }


def public_changes(state: EvidenceAgentState, affected: list[str]) -> list[dict]:
    changes = []
    for output_id in affected:
        output = state.outputs[output_id]
        before = output.get("before")
        after = output.get("value", output.get("match"))
        if after is None:
            after = (
                output.get("route")
                if output.get("kind") == "route"
                else output.get("summary")
            )
        changes.append(
            {
                "output": output.get("label", output_id),
                "before": before,
                "after": after,
                "why": output.get("why", "Its supporting evidence changed."),
            }
        )
    return changes


def run(args: argparse.Namespace) -> dict:
    home = context_registry.registry_home()
    registry = context_registry.load_registry(home)
    identity = context_registry.project_identity(args.project)
    prior_project = context_registry.find_record(
        registry["projects"], "project_id", identity["project_id"]
    )
    project = context_registry.project_snapshot(identity, prior_project)
    jd = context_registry.jd_snapshot(args.jd_file, None, args.jd_key, False)
    resolved = context_registry.resolve_context(registry, project, jd, args.mode)
    previous = (
        EvidenceAgentState.from_dict(resolved["previous_agent_state"])
        if resolved["previous_agent_state"]
        else None
    )
    seed = (
        json.loads(args.seed.read_text(encoding="utf-8"))
        if args.seed
        else {}
    )
    correction = (
        json.loads(args.correction.read_text(encoding="utf-8"))
        if args.correction
        else None
    )
    artifacts = {
        item["path"]: item["fingerprint"] for item in project["artifacts"]
    }
    project_label = (
        seed.get("report", {}).get("project_name")
        or (previous.project_label if previous else "")
        or args.project.name
    )
    jd_label = (
        seed.get("report", {}).get("jd_label")
        or (previous.jd_label if previous else "")
        or "Target role"
    )
    host_decisions: list[dict] = []

    def decide(observation: dict, allowed: tuple[str, ...]) -> str:
        if observation["detected_change"] == "new":
            proposal = (
                "produce_brief"
                if observation.get("last_action") == "refresh_jd_context"
                else "refresh_jd_context"
            )
        elif (
            observation.get("project_changed")
            or observation.get("correction_present")
        ) and observation.get("last_action") != "investigate_evidence":
            proposal = "investigate_evidence"
        elif (
            observation.get("jd_changed")
            and observation.get("last_action") != "refresh_jd_context"
        ):
            proposal = "refresh_jd_context"
        elif observation.get("factual_confirmation_required"):
            proposal = "request_confirmation"
        else:
            proposal = "stop"
        selected = proposal if proposal in allowed else allowed[0]
        host_decisions.append(
            {
                "observation": {
                    key: observation.get(key)
                    for key in (
                        "detected_change",
                        "project_changed",
                        "jd_changed",
                        "correction_present",
                        "last_action",
                    )
                },
                "proposed_action": proposal,
                "eligible_actions": list(allowed),
                "selected_action": selected,
            }
        )
        return selected

    result = StatefulEvidenceAgent(
        HostMediatedPlanner(decide),
        Project2JobCapabilities(args.project, seed),
    ).run(
        RunRequest(
            project_version=f"project-v{resolved['project_version']}",
            jd_version=f"jd-v{resolved['jd_version']}",
            artifacts=artifacts,
            project_label=project_label,
            jd_label=jd_label,
            correction=correction,
            analyze_from_scratch=args.mode == "fresh",
            factual_confirmation_required=args.confirmation_required,
        ),
        previous,
    )
    trace = result["trace"]
    expected = (
        set(trace["affected_outputs"])
        if trace["detected_change"] == "new"
        else set(
            args.expected_output
            or seed.get("expected_changed_outputs", trace["affected_outputs"])
        )
    )
    metrics = observed_metrics(trace, expected)
    payload = {
        "project": {
            "name": result["state"].project_label
        },
        "jd": {
            "label": result["state"].jd_label
        },
        "result": {
            "stop_reason": trace["stop_reason"],
            "changed_outputs": len(trace["affected_outputs"]),
            "preserved_outputs": len(trace["preserved_outputs"]),
            "changes": public_changes(result["state"], trace["affected_outputs"]),
        },
        "state": result["state"].to_dict(),
        "trace": trace,
        "metrics": metrics,
        "host_mediated_decisions": host_decisions,
    }
    if args.upgrade_build:
        build = json.loads(args.upgrade_build.read_text(encoding="utf-8"))
        payload["upgrade_handoff"] = execution_handoff(
            result["state"].project_label,
            build,
        )
    if (
        not args.do_not_save
        and trace["stop_reason"]
        not in {
            "validation_failed",
            "permission_required",
            "correction_approval_required",
            "policy_stop",
        }
    ):
        analysis = {
            "agent_state": payload["state"],
            "agent_trace": trace,
            "observed_metrics": metrics,
            "evidence": [
                {"path": item["source"], "location": item.get("location", "")}
                for item in result["state"].evidence.values()
            ],
            "output_references": sorted(result["state"].outputs),
            "recommended_route": next(
                (
                    output.get("route")
                    for output in result["state"].outputs.values()
                    if output.get("kind") == "route"
                ),
                None,
            ),
        }
        updated, saved = context_registry.save_run(
            registry, project, jd, "p2j", analysis
        )
        context_registry.ensure_consent(home, args.consent)
        context_registry.atomic_write(
            home / context_registry.REGISTRY_FILE, updated
        )
        payload["saved"] = True
        payload["run_id"] = saved["run_id"]
    else:
        payload["saved"] = False
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the bounded stateful Project2Job vertical slice."
    )
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--jd-file", type=Path, required=True)
    parser.add_argument("--jd-key")
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--upgrade-build", type=Path)
    parser.add_argument("--expected-output", action="append", default=[])
    parser.add_argument("--correction", type=Path)
    parser.add_argument("--confirmation-required", action="store_true")
    parser.add_argument(
        "--mode", choices=("normal", "refresh", "fresh"), default="normal"
    )
    parser.add_argument("--consent", action="store_true")
    parser.add_argument("--do-not-save", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        payload = run(args)
        rendered = json.dumps(payload, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
    except (OSError, ValueError, context_registry.RegistryError) as error:
        raise SystemExit(f"Project2Job Agent error: {error}") from error


if __name__ == "__main__":
    main()
