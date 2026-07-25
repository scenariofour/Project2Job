from __future__ import annotations

from enum import Enum
from typing import NotRequired, TypedDict


class EvidenceStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    INFERRED = "inferred"
    NOT_FOUND = "not_found"
    CONFLICTING = "conflicting"
    NEEDS_CONFIRMATION = "needs_confirmation"


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


class RunBudget(TypedDict):
    max_turns: int
    max_tool_calls: int
    max_source_chars_per_call: int


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
