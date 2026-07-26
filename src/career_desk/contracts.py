from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import NotRequired, Protocol, TypedDict


class EvidenceStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    INFERRED = "inferred"
    NOT_FOUND = "not_found"
    CONFLICTING = "conflicting"
    NEEDS_CONFIRMATION = "needs_confirmation"


class AgentDecision(str, Enum):
    CONTINUE = "continue"
    ADJUST = "adjust"
    ASK = "ask"
    STOP = "stop"


class StopReason(str, Enum):
    EVIDENCE_SUFFICIENT = "evidence_sufficient"
    EVIDENCE_EXHAUSTED = "evidence_exhausted"
    CONFIRMATION_REQUIRED = "confirmation_required"
    UNRESOLVED_CONTRADICTION = "unresolved_contradiction"
    BUDGET_EXHAUSTED = "budget_exhausted"
    TOOL_FAILURE = "tool_failure"


class ActionKind(str, Enum):
    SEARCH = "search"
    READ = "read"
    ASK = "ask"


class SourceRef(TypedDict):
    source_id: str
    location: str
    excerpt: NotRequired[str]


class EvidenceResult(TypedDict):
    claim_id: str
    status: EvidenceStatus
    source_refs: list[SourceRef]
    boundary: str
    stop_reason: str


@dataclass(frozen=True)
class RunBudget:
    max_turns: int
    max_tool_calls: int
    max_source_chars_per_call: int


@dataclass(frozen=True)
class InvestigationRequest:
    claim_id: str
    text: str
    allowed_source_ids: list[str]
    requires_confirmation: bool = False


@dataclass(frozen=True)
class AgentStateSnapshot:
    claim_id: str
    active_claim: str
    status: EvidenceStatus
    turns_used: int
    tool_calls_used: int
    remaining_candidates: int
    sources_exhausted: bool


@dataclass(frozen=True)
class ActionRecord:
    turn: int
    kind: ActionKind
    tool_name: str
    arguments: dict


@dataclass(frozen=True)
class ObservationRecord:
    turn: int
    tool_name: str
    ok: bool
    data: dict
    error: str | None = None


@dataclass(frozen=True)
class StateUpdateRecord:
    turn: int
    decision: AgentDecision
    active_claim: str
    status: EvidenceStatus
    stop_reason: StopReason | None
    note: str


@dataclass(frozen=True)
class TraceStep:
    state_before: AgentStateSnapshot
    action: ActionRecord
    observation: ObservationRecord
    state_update: StateUpdateRecord


@dataclass
class AgentState:
    claim_id: str
    original_claim: str
    active_claim: str
    allowed_source_ids: tuple[str, ...]
    budget: RunBudget
    status: EvidenceStatus = EvidenceStatus.INFERRED
    turns_used: int = 0
    tool_calls_used: int = 0
    stop_reason: StopReason | None = None
    evidence: list[dict] = field(default_factory=list)
    pending_matches: list[dict] = field(default_factory=list)
    sources_exhausted: bool = False

    def snapshot(self) -> AgentStateSnapshot:
        return AgentStateSnapshot(
            claim_id=self.claim_id,
            active_claim=self.active_claim,
            status=self.status,
            turns_used=self.turns_used,
            tool_calls_used=self.tool_calls_used,
            remaining_candidates=len(self.pending_matches),
            sources_exhausted=self.sources_exhausted,
        )


@dataclass(frozen=True)
class InvestigationRun:
    state: AgentState
    trace: tuple[TraceStep, ...]

    def to_trace_dict(self) -> dict:
        steps = [_plain_data(asdict(step)) for step in self.trace]
        for step in steps:
            step["state"] = step.pop("state_before")
            data = step["observation"]["data"]
            content = data.pop("content", None)
            if isinstance(content, str):
                data["content_chars"] = len(content)
        final_state = {
            key: _plain_data(getattr(self.state, key))
            for key in (
                "claim_id",
                "original_claim",
                "active_claim",
                "status",
                "turns_used",
                "tool_calls_used",
                "stop_reason",
            )
        }
        return {
            "final_state": final_state,
            "steps": steps,
        }


def _plain_data(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _plain_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain_data(item) for item in value]
    return value


class InvestigationApproach(Protocol):
    async def investigate(self, request: InvestigationRequest) -> InvestigationRun: ...


class Telemetry(TypedDict, total=False):
    files_discovered: int
    files_opened: int
    repeated_reads: int
    model_calls: int
    tool_calls: int
    agent_turns: int
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    latency_ms: int
    estimated_cost: float
    stop_reason: str
