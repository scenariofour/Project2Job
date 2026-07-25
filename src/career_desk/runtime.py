from __future__ import annotations

from .contracts import (
    ActionKind,
    ActionRecord,
    AgentDecision,
    AgentState,
    EvidenceStatus,
    InvestigationRequest,
    InvestigationRun,
    ObservationRecord,
    RunBudget,
    StateUpdateRecord,
    StopReason,
    TraceStep,
)
from .tools import EvidenceTools


class EvidenceInvestigator:
    comparison_approaches = (
        "strong_one_shot_prompt",
        "fixed_extract_search_validate",
        "bounded_adaptive_agent_loop",
    )

    def __init__(self, tools: EvidenceTools, budget: RunBudget) -> None:
        self.tools = tools
        self.budget = budget

    async def investigate(self, request: InvestigationRequest) -> InvestigationRun:
        state = AgentState(
            claim_id=request.claim_id,
            original_claim=request.text,
            active_claim=request.text,
            allowed_source_ids=tuple(request.allowed_source_ids),
            budget=self.budget,
        )
        trace: list[TraceStep] = []

        while state.stop_reason is None:
            if self._budget_reached(state):
                state.stop_reason = StopReason.BUDGET_EXHAUSTED
                break

            state_before = state.snapshot()
            action = self._select_action(request, state)
            state.turns_used += 1
            state.tool_calls_used += 1

            try:
                data = self._call_tool(action)
                observation = ObservationRecord(
                    turn=action.turn,
                    tool_name=action.tool_name,
                    ok=True,
                    data=data,
                )
                update = self._apply_observation(state, action, observation)
            except Exception as error:
                observation = ObservationRecord(
                    turn=action.turn,
                    tool_name=action.tool_name,
                    ok=False,
                    data={},
                    error=str(error),
                )
                state.stop_reason = StopReason.TOOL_FAILURE
                update = self._state_update(
                    state,
                    AgentDecision.STOP,
                    "Unrecoverable tool failure is visible; prior state is preserved.",
                )

            trace.append(
                TraceStep(
                    state_before=state_before,
                    action=action,
                    observation=observation,
                    state_update=update,
                )
            )

        return InvestigationRun(state=state, trace=tuple(trace))

    @staticmethod
    def _budget_reached(state: AgentState) -> bool:
        return (
            state.turns_used >= state.budget.max_turns
            or state.tool_calls_used >= state.budget.max_tool_calls
        )

    def _select_action(
        self,
        request: InvestigationRequest,
        state: AgentState,
    ) -> ActionRecord:
        turn = state.turns_used + 1
        if request.requires_confirmation:
            return ActionRecord(
                turn=turn,
                kind=ActionKind.ASK,
                tool_name="request_confirmation",
                arguments={
                    "question": f"Please confirm: {state.active_claim}",
                    "context": {"claim_id": state.claim_id},
                },
            )
        if state.pending_matches:
            match = state.pending_matches[0]
            return ActionRecord(
                turn=turn,
                kind=ActionKind.READ,
                tool_name="read_source",
                arguments={
                    "source_id": match["source_id"],
                    "location": match["location"],
                    "max_chars": state.budget.max_source_chars_per_call,
                },
            )
        return ActionRecord(
            turn=turn,
            kind=ActionKind.SEARCH,
            tool_name="search_sources",
            arguments={
                "query": state.active_claim,
                "source_ids": list(state.allowed_source_ids),
                "limit": max(1, len(state.allowed_source_ids)),
            },
        )

    def _call_tool(self, action: ActionRecord) -> dict:
        arguments = action.arguments
        if action.tool_name == "search_sources":
            return self.tools.search_sources(**arguments)
        if action.tool_name == "read_source":
            return self.tools.read_source(**arguments)
        if action.tool_name == "request_confirmation":
            return self.tools.request_confirmation(**arguments)
        raise RuntimeError(f"unsupported tool: {action.tool_name}")

    def _apply_observation(
        self,
        state: AgentState,
        action: ActionRecord,
        observation: ObservationRecord,
    ) -> StateUpdateRecord:
        if action.kind == ActionKind.SEARCH:
            return self._apply_search(state, observation.data)
        if action.kind == ActionKind.READ:
            return self._apply_read(state, observation.data)
        if action.kind == ActionKind.ASK:
            state.status = EvidenceStatus.NEEDS_CONFIRMATION
            state.stop_reason = StopReason.CONFIRMATION_REQUIRED
            return self._state_update(
                state,
                AgentDecision.ASK,
                "Personal ownership requires user confirmation.",
            )
        raise RuntimeError(f"unsupported action kind: {action.kind}")

    def _apply_search(self, state: AgentState, data: dict) -> StateUpdateRecord:
        matches = data.get("matches", [])
        state.sources_exhausted = bool(data.get("exhausted", False))
        if matches:
            state.pending_matches.extend(matches)
            return self._state_update(
                state,
                AgentDecision.CONTINUE,
                "Candidate evidence found; read the permitted source.",
            )
        if state.sources_exhausted:
            state.status = EvidenceStatus.NOT_FOUND
            state.stop_reason = StopReason.EVIDENCE_EXHAUSTED
            return self._state_update(
                state,
                AgentDecision.STOP,
                "Permitted evidence was exhausted without support.",
            )
        return self._state_update(
            state,
            AgentDecision.CONTINUE,
            "No evidence in this observation; permitted search remains.",
        )

    def _apply_read(self, state: AgentState, data: dict) -> StateUpdateRecord:
        if state.pending_matches:
            state.pending_matches.pop(0)
        assessment = data.get("assessment")
        evidence = {
            key: data[key]
            for key in ("source_id", "location", "assessment")
            if key in data
        }

        if assessment == "direct":
            state.evidence.append(evidence)
            state.status = EvidenceStatus.SUPPORTED
            state.stop_reason = StopReason.EVIDENCE_SUFFICIENT
            return self._state_update(
                state,
                AgentDecision.STOP,
                "Direct evidence is sufficient for the bounded claim.",
            )

        if assessment == "partial":
            narrowed_claim = data.get("narrowed_claim")
            if not isinstance(narrowed_claim, str) or not narrowed_claim.strip():
                raise RuntimeError("partial evidence requires a narrowed claim")
            state.evidence.append(evidence)
            state.active_claim = narrowed_claim
            state.status = EvidenceStatus.PARTIALLY_SUPPORTED
            state.pending_matches.clear()
            state.sources_exhausted = False
            return self._state_update(
                state,
                AgentDecision.ADJUST,
                "Weak claim narrowed to the boundary supported by the observation.",
            )

        if assessment == "contradictory":
            state.evidence.append(evidence)
            state.status = EvidenceStatus.CONFLICTING
            state.stop_reason = StopReason.UNRESOLVED_CONTRADICTION
            return self._state_update(
                state,
                AgentDecision.STOP,
                "Contradictory evidence requires user resolution.",
            )

        if assessment == "irrelevant":
            if not state.pending_matches and state.sources_exhausted:
                state.status = EvidenceStatus.NOT_FOUND
                state.stop_reason = StopReason.EVIDENCE_EXHAUSTED
                return self._state_update(
                    state,
                    AgentDecision.STOP,
                    "Read content was inert data and did not support the claim.",
                )
            return self._state_update(
                state,
                AgentDecision.CONTINUE,
                "Observation was irrelevant; another permitted candidate remains.",
            )

        raise RuntimeError("tool returned an unknown evidence assessment")

    @staticmethod
    def _state_update(
        state: AgentState,
        decision: AgentDecision,
        note: str,
    ) -> StateUpdateRecord:
        return StateUpdateRecord(
            turn=state.turns_used,
            decision=decision,
            active_claim=state.active_claim,
            status=state.status,
            stop_reason=state.stop_reason,
            note=note,
        )
