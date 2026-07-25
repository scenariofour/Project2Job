from __future__ import annotations

"""
WO-02 implementation target.

The first version should use one Evidence Investigator and read-only tools.
Framework-specific code should remain behind this interface.
"""

from career_desk.contracts import EvidenceResult, RunBudget
from career_desk.tools import EvidenceTools


class EvidenceInvestigator:
    def __init__(self, tools: EvidenceTools, budget: RunBudget) -> None:
        self.tools = tools
        self.budget = budget

    async def investigate(
        self,
        *,
        requirement: dict,
        claim: dict,
        state_summary: dict,
    ) -> EvidenceResult:
        raise NotImplementedError(
            "Implement under WO-02_AGENT_POC after shared schemas and gold cases are approved."
        )
