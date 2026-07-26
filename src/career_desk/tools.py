from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import EvidenceResult


@dataclass(frozen=True)
class ToolError:
    code: str
    message: str
    retryable: bool


class EvidenceTools(Protocol):
    def inventory_sources(self, project_root: str) -> dict: ...
    def search_sources(self, query: str, source_ids: list[str], limit: int) -> dict: ...
    def read_source(self, source_id: str, location: str, max_chars: int) -> dict: ...
    def compare_evidence(self, claim: str, evidence: list[dict]) -> dict: ...
    def request_confirmation(self, question: str, context: dict) -> dict: ...
    def submit_evidence_result(self, result: EvidenceResult) -> dict: ...
