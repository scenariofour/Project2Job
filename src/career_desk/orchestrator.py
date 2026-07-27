from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from time import perf_counter
from typing import Callable, Protocol


ALLOWED_ACTIONS = {
    "investigate_evidence",
    "refresh_jd_context",
    "produce_brief",
    "produce_interview_answer",
    "pressure_test_answer",
    "recommend_next_build",
    "request_confirmation",
    "stop",
}
ATTRIBUTION_SCOPES = {
    "directly_owned",
    "ai_assisted",
    "collaborator_owned",
    "unresolved",
}


@dataclass(frozen=True)
class AgentBudget:
    max_turns: int = 4
    max_capability_calls: int = 3
    max_repairs: int = 1


@dataclass(frozen=True)
class RunRequest:
    project_version: str
    jd_version: str
    artifacts: dict[str, str]
    project_label: str = ""
    jd_label: str = ""
    correction: dict | None = None
    analyze_from_scratch: bool = False
    permission_to_read: bool = True
    factual_confirmation_required: bool = False


@dataclass
class EvidenceAgentState:
    project_version: str = ""
    jd_version: str = ""
    project_label: str = ""
    jd_label: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    evidence: dict[str, dict] = field(default_factory=dict)
    claims: dict[str, dict] = field(default_factory=dict)
    outputs: dict[str, dict] = field(default_factory=dict)
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    confirmed_facts: dict[str, dict] = field(default_factory=dict)
    unresolved_questions: list[str] = field(default_factory=list)

    def copy(self) -> EvidenceAgentState:
        return deepcopy(self)

    def to_dict(self) -> dict:
        return {
            "project_version": self.project_version,
            "jd_version": self.jd_version,
            "project_label": self.project_label,
            "jd_label": self.jd_label,
            "artifacts": deepcopy(self.artifacts),
            "evidence": deepcopy(self.evidence),
            "claims": deepcopy(self.claims),
            "outputs": deepcopy(self.outputs),
            "dependencies": deepcopy(self.dependencies),
            "confirmed_facts": deepcopy(self.confirmed_facts),
            "unresolved_questions": list(self.unresolved_questions),
        }

    @classmethod
    def from_dict(cls, value: dict) -> EvidenceAgentState:
        fields = {
            "project_version",
            "jd_version",
            "project_label",
            "jd_label",
            "artifacts",
            "evidence",
            "claims",
            "outputs",
            "dependencies",
            "confirmed_facts",
            "unresolved_questions",
        }
        return cls(**{key: deepcopy(value.get(key)) for key in fields if key in value})


class Planner(Protocol):
    def select(self, observation: dict, allowed_actions: tuple[str, ...]) -> str: ...


class CapabilityRuntime(Protocol):
    def execute(self, action: str, context: dict) -> dict: ...


class ScriptedPlanner:
    def __init__(self, actions: list[str]) -> None:
        self.actions = list(actions)

    def select(self, observation: dict, allowed_actions: tuple[str, ...]) -> str:
        if not self.actions:
            return "stop"
        return self.actions.pop(0)


class HostMediatedPlanner:
    """Adapter for a host/model decision function that receives the observation."""

    def __init__(
        self,
        decide: Callable[[dict, tuple[str, ...]], str],
    ) -> None:
        self.decide = decide

    def select(self, observation: dict, allowed_actions: tuple[str, ...]) -> str:
        return self.decide(deepcopy(observation), allowed_actions)


class DependencyGraph:
    def __init__(self, edges: dict[str, list[str]]) -> None:
        self.edges = edges

    def descendants(self, roots: set[str]) -> set[str]:
        found: set[str] = set()
        frontier = list(roots)
        while frontier:
            node = frontier.pop()
            for child in self.edges.get(node, []):
                if child not in found:
                    found.add(child)
                    frontier.append(child)
        return found


def detect_change(previous: EvidenceAgentState | None, request: RunRequest) -> dict:
    if previous is None or request.analyze_from_scratch:
        return {
            "kind": "new",
            "added": sorted(request.artifacts),
            "removed": [],
            "changed": [],
            "project_changed": True,
            "jd_changed": True,
            "correction_present": bool(request.correction),
        }

    previous_paths = set(previous.artifacts)
    current_paths = set(request.artifacts)
    added = sorted(current_paths - previous_paths)
    removed = sorted(previous_paths - current_paths)
    changed = sorted(
        path
        for path in previous_paths & current_paths
        if previous.artifacts[path] != request.artifacts[path]
    )
    project_changed = bool(added or removed or changed) or (
        previous.project_version != request.project_version
    )
    jd_changed = previous.jd_version != request.jd_version
    if request.correction:
        kind = "correction"
    elif project_changed and jd_changed:
        kind = "both"
    elif project_changed:
        kind = "project"
    elif jd_changed:
        kind = "jd"
    else:
        kind = "unchanged"
    return {
        "kind": kind,
        "added": added,
        "removed": removed,
        "changed": changed,
        "project_changed": project_changed,
        "jd_changed": jd_changed,
        "correction_present": bool(request.correction),
    }


def eligible_actions(observation: dict) -> tuple[str, ...]:
    """Return only actions that are valid for the observed state."""
    if observation.get("factual_confirmation_required"):
        return ("request_confirmation",)
    if observation.get("correction_present") and not observation.get(
        "correction_approved"
    ):
        return ("stop",)

    actions_taken = set(observation.get("actions_taken", []))
    project_changed = bool(observation.get("project_changed"))
    jd_changed = bool(observation.get("jd_changed"))
    detected = observation.get("detected_change")

    if detected == "unchanged":
        return ("stop",)
    if detected == "new":
        if "refresh_jd_context" not in actions_taken:
            return (
                "refresh_jd_context",
                "investigate_evidence",
                "produce_brief",
            )
        if "produce_brief" not in actions_taken:
            return ("produce_brief",)
        return ("stop",)
    if observation.get("correction_present") and observation.get(
        "correction_approved"
    ) and "investigate_evidence" not in actions_taken:
        return ("investigate_evidence",)
    if project_changed and "investigate_evidence" not in actions_taken:
        return ("investigate_evidence",)
    if jd_changed and "refresh_jd_context" not in actions_taken:
        return ("refresh_jd_context",)
    return ("stop",)


def affected_output_ids(state: EvidenceAgentState, roots: set[str]) -> set[str]:
    descendants = DependencyGraph(state.dependencies).descendants(roots)
    return {item for item in descendants if item in state.outputs}


def has_evidence_ancestor(state: EvidenceAgentState, output_id: str) -> bool:
    parents: dict[str, set[str]] = {}
    for parent, children in state.dependencies.items():
        for child in children:
            parents.setdefault(child, set()).add(parent)
    frontier = [output_id]
    seen: set[str] = set()
    while frontier:
        node = frontier.pop()
        if node in state.evidence:
            return True
        if node in seen:
            continue
        seen.add(node)
        frontier.extend(parents.get(node, set()))
    return False


def validate_state(state: EvidenceAgentState, output_ids: set[str]) -> list[dict]:
    failures: list[dict] = []
    for output_id in sorted(output_ids):
        output = state.outputs[output_id]
        dependencies = set(output.get("depends_on", []))
        if (
            output.get("kind") == "score"
            and output.get("value", 1) > 1
            and not has_evidence_ancestor(state, output_id)
        ):
            failures.append(
                {"output_id": output_id, "code": "score_without_evidence"}
            )
        if output.get("match") == "EXACT MATCH":
            claims = [
                state.claims[item]
                for item in dependencies
                if item in state.claims
            ]
            if not claims or any(
                claim.get("status") != "supported" for claim in claims
            ):
                failures.append(
                    {"output_id": output_id, "code": "overstrong_exact_match"}
                )
        if output.get("exported"):
            unsupported = [
                item
                for item in dependencies
                if item in state.claims
                and state.claims[item].get("status") != "supported"
            ]
            if unsupported:
                failures.append(
                    {"output_id": output_id, "code": "unsupported_export"}
                )
        for claim_id in dependencies:
            claim = state.claims.get(claim_id)
            if claim and claim.get("attribution_scope") not in ATTRIBUTION_SCOPES:
                failures.append(
                    {"output_id": output_id, "code": "invalid_attribution"}
                )
        if output.get("evidence_system") == "mixed":
            failures.append(
                {"output_id": output_id, "code": "mixed_evidence_systems"}
            )
        if output.get("kind") == "route" and not output.get("route"):
            failures.append({"output_id": output_id, "code": "missing_route"})
    return failures


def repair_state(state: EvidenceAgentState, failures: list[dict]) -> set[str]:
    repaired: set[str] = set()
    for failure in failures:
        output = state.outputs.get(failure["output_id"])
        if not output:
            continue
        if failure["code"] == "overstrong_exact_match":
            output["before"] = output.get("match")
            output["match"] = "TRANSFERABLE"
            output["why"] = "Direct competency evidence was not available."
            repaired.add(failure["output_id"])
        elif failure["code"] == "unsupported_export":
            output["before"] = output.get("content", "")
            output["exported"] = False
            output["why"] = "The claim is not supported for external use."
            repaired.add(failure["output_id"])
    return repaired


class StatefulEvidenceAgent:
    def __init__(
        self,
        planner: Planner,
        capabilities: CapabilityRuntime,
        budget: AgentBudget | None = None,
    ) -> None:
        self.planner = planner
        self.capabilities = capabilities
        self.budget = budget or AgentBudget()

    def run(
        self,
        request: RunRequest,
        previous: EvidenceAgentState | None = None,
    ) -> dict:
        started = perf_counter()
        state = previous.copy() if previous else EvidenceAgentState()
        before_outputs = deepcopy(state.outputs)
        change = detect_change(previous, request)
        invalidated = self._invalidated(state, request, change)
        observation = {
            "detected_change": change["kind"],
            "project_changed": change["project_changed"],
            "jd_changed": change["jd_changed"],
            "correction_present": change["correction_present"],
            "changed_artifacts": {
                key: change[key] for key in ("added", "removed", "changed")
            },
            "invalidated_outputs": sorted(invalidated),
            "correction_approved": bool(
                request.correction and request.correction.get("approved")
            ),
            "factual_confirmation_required": request.factual_confirmation_required,
            "actions_taken": [],
        }
        trace: list[dict] = []
        affected: set[str] = set()
        stop_reason = ""
        repairs = 0
        capability_calls = 0
        events: list[dict] = []

        if not request.permission_to_read and change["kind"] != "unchanged":
            stop_reason = "permission_required"
        elif (
            request.correction
            and not request.correction.get("approved", False)
        ):
            stop_reason = "correction_approval_required"
        elif change["kind"] == "unchanged":
            stop_reason = "no_relevant_changes"

        turn = 0
        while not stop_reason:
            if (
                turn >= self.budget.max_turns
                or capability_calls >= self.budget.max_capability_calls
            ):
                stop_reason = "budget_exhausted"
                break
            turn += 1
            allowed = eligible_actions(observation)
            action = self.planner.select(
                deepcopy(observation), allowed
            )
            if action not in ALLOWED_ACTIONS or action not in allowed:
                stop_reason = "policy_stop"
                trace.append(
                    self._trace_step(
                        turn,
                        observation,
                        action,
                        "Rejected action outside the allowed policy.",
                        [],
                        [],
                        "failed",
                    )
                )
                break
            if action == "stop":
                stop_reason = "complete"
                break

            capability_calls += 1
            result = self.capabilities.execute(
                action,
                {
                    "change": deepcopy(change),
                    "invalidated_outputs": sorted(invalidated),
                    "state": state.to_dict(),
                    "request": {
                        "project_version": request.project_version,
                        "jd_version": request.jd_version,
                        "correction": deepcopy(request.correction),
                    },
                },
            )
            candidate = state.copy()
            self._apply_result(candidate, result)
            changed_outputs = set(result.get("affected_outputs", []))
            failures = validate_state(candidate, changed_outputs)
            validation = "passed"
            if failures:
                if repairs < self.budget.max_repairs:
                    repaired = repair_state(candidate, failures)
                    repairs += 1
                    changed_outputs.update(repaired)
                    failures = validate_state(candidate, changed_outputs)
                    validation = "repaired" if not failures else "failed"
                else:
                    validation = "failed"
            if not failures:
                state = candidate
                affected.update(changed_outputs)
            events.extend(deepcopy(result.get("events", [])))
            preserved = set(state.outputs) - affected
            trace.append(
                self._trace_step(
                    turn,
                    observation,
                    action,
                    result.get("observation_summary", ""),
                    sorted(changed_outputs),
                    sorted(preserved),
                    validation,
                    self._event_usage(result.get("events", [])),
                    result.get("capability", action),
                    result.get("events", []),
                )
            )
            observation = {
                "detected_change": change["kind"],
                "project_changed": change["project_changed"],
                "jd_changed": change["jd_changed"],
                "correction_present": change["correction_present"],
                "correction_approved": bool(
                    request.correction and request.correction.get("approved")
                ),
                "factual_confirmation_required": request.factual_confirmation_required,
                "last_action": action,
                "actions_taken": [
                    *observation.get("actions_taken", []),
                    action,
                ],
                "validation": validation,
                "validation_failures": failures,
                "affected_outputs": sorted(affected),
            }
            if failures:
                stop_reason = "validation_failed"
            elif result.get("stop"):
                stop_reason = result.get("stop_reason", "complete")

        if stop_reason not in {
            "validation_failed",
            "permission_required",
            "correction_approval_required",
            "policy_stop",
        }:
            state.project_version = request.project_version
            state.jd_version = request.jd_version
            state.project_label = request.project_label or state.project_label
            state.jd_label = request.jd_label or state.jd_label
            state.artifacts = dict(request.artifacts)
        preserved = sorted(
            output_id
            for output_id, value in state.outputs.items()
            if output_id not in affected and before_outputs.get(output_id) == value
        )
        return {
            "state": state,
            "trace": {
                "state_summary": {
                    "project_version": request.project_version,
                    "jd_version": request.jd_version,
                    "project_changed": change["project_changed"],
                    "jd_changed": change["jd_changed"],
                    "correction_present": change["correction_present"],
                    "evidence_count": len(state.evidence),
                    "claim_count": len(state.claims),
                    "output_count": len(state.outputs),
                },
                "detected_change": change["kind"],
                "steps": trace,
                "affected_outputs": sorted(affected),
                "preserved_outputs": preserved,
                "stop_reason": stop_reason,
                "budgets": {
                    "max_turns": self.budget.max_turns,
                    "max_capability_calls": self.budget.max_capability_calls,
                    "max_repairs": self.budget.max_repairs,
                },
                "usage": {
                    "turns": turn,
                    "capability_calls": capability_calls,
                    "repairs": repairs,
                    "latency_ms": round((perf_counter() - started) * 1000, 3),
                    **self._event_usage(events),
                },
            },
        }

    @staticmethod
    def _invalidated(
        state: EvidenceAgentState,
        request: RunRequest,
        change: dict,
    ) -> set[str]:
        roots = set(change["added"] + change["removed"] + change["changed"])
        if request.correction:
            roots.add(request.correction.get("claim_id", ""))
        if change["jd_changed"]:
            roots.add("jd")
        return affected_output_ids(state, roots)

    @staticmethod
    def _apply_result(state: EvidenceAgentState, result: dict) -> None:
        removed_evidence = set(result.get("removed_evidence", []))
        for evidence_id in removed_evidence:
            state.evidence.pop(evidence_id, None)
        removed_nodes = set(result.get("removed_dependency_nodes", []))
        for node in removed_nodes:
            state.dependencies.pop(node, None)
        if removed_nodes:
            for parent, children in list(state.dependencies.items()):
                state.dependencies[parent] = [
                    child for child in children if child not in removed_nodes
                ]
        for collection in ("evidence", "claims", "outputs"):
            getattr(state, collection).update(deepcopy(result.get(collection, {})))
        for parent, children in result.get("dependencies", {}).items():
            state.dependencies[parent] = list(dict.fromkeys(children))
        state.confirmed_facts.update(deepcopy(result.get("confirmed_facts", {})))

    @staticmethod
    def _trace_step(
        turn: int,
        observation: dict,
        action: str,
        summary: str,
        affected: list[str],
        preserved: list[str],
        validation: str,
        usage: dict | None = None,
        capability: str | None = None,
        events: list[dict] | None = None,
    ) -> dict:
        return {
            "turn": turn,
            "state_summary": {
                "detected_change": observation.get("detected_change"),
                "last_action": observation.get("last_action"),
            },
            "selected_action": action,
            "capability_used": capability or action,
            "observation_summary": summary,
            "validation_result": validation,
            "affected_outputs": affected,
            "preserved_outputs": preserved,
            "usage": deepcopy(usage or {}),
            "events": deepcopy(events or []),
        }

    @staticmethod
    def _event_usage(events: list[dict]) -> dict:
        opened: set[str] = set()
        usage = {
            "files_opened": 0,
            "questions_asked": 0,
            "tool_calls": 0,
        }
        token_usage = 0
        tokens_available = False
        for event in events:
            kind = event.get("kind")
            if kind == "file_opened":
                opened.add(str(event.get("path", "")))
            if kind == "question_asked":
                usage["questions_asked"] += 1
            if kind == "tool_call":
                usage["tool_calls"] += 1
            if kind == "token_usage" and isinstance(event.get("tokens"), int):
                token_usage += event["tokens"]
                tokens_available = True
        usage["token_usage"] = token_usage if tokens_available else None
        usage["files_opened"] = len(opened)
        return usage
