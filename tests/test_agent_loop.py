from __future__ import annotations

import asyncio
import json
import unittest
from pathlib import Path

from src.career_desk.contracts import (
    AgentDecision,
    EvidenceStatus,
    InvestigationRequest,
    RunBudget,
    StopReason,
)
from src.career_desk.runtime import EvidenceInvestigator

ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "lab/evals/day1_agent_loop_cases.jsonl"


class ScriptedEvidenceTools:
    def __init__(self, script: list[dict]) -> None:
        self._script = list(script)
        self.calls: list[dict] = []

    def _next(self, tool: str, arguments: dict) -> dict:
        step = self._script.pop(0)
        if step["tool"] != tool:
            raise AssertionError(f"expected {step['tool']}, got {tool}")
        self.calls.append({"tool": tool, "arguments": arguments})
        if "error" in step:
            raise RuntimeError(step["error"])
        return step["result"]

    def inventory_sources(self, project_root: str) -> dict:
        return self._next("inventory_sources", {"project_root": project_root})

    def search_sources(self, query: str, source_ids: list[str], limit: int) -> dict:
        return self._next(
            "search_sources",
            {"query": query, "source_ids": source_ids, "limit": limit},
        )

    def read_source(self, source_id: str, location: str, max_chars: int) -> dict:
        return self._next(
            "read_source",
            {
                "source_id": source_id,
                "location": location,
                "max_chars": max_chars,
            },
        )

    def compare_evidence(self, claim: str, evidence: list[dict]) -> dict:
        return self._next(
            "compare_evidence", {"claim": claim, "evidence": evidence}
        )

    def request_confirmation(self, question: str, context: dict) -> dict:
        return self._next(
            "request_confirmation", {"question": question, "context": context}
        )

    def submit_evidence_result(self, result: dict) -> dict:
        return self._next("submit_evidence_result", {"result": result})


def load_case(case_id: str) -> dict:
    for line in CASES_PATH.read_text(encoding="utf-8").splitlines():
        case = json.loads(line)
        if case["case_id"] == case_id:
            return case
    raise AssertionError(f"missing case {case_id}")


def run_case(case_id: str):
    case = load_case(case_id)
    tools = ScriptedEvidenceTools(case["tool_script"])
    budget = RunBudget(**case["budget"])
    request = InvestigationRequest(**case["claim"])
    result = asyncio.run(EvidenceInvestigator(tools, budget).investigate(request))
    return case, tools, result


class BoundedAgentLoopTests(unittest.TestCase):
    def assert_gold(self, case: dict, result) -> None:
        gold = case["gold"]
        self.assertEqual(
            [step.state_update.decision.value for step in result.trace],
            gold["decisions"],
        )
        self.assertEqual(result.state.status.value, gold["status"])
        self.assertEqual(result.state.stop_reason.value, gold["stop_reason"])

    def test_continue_path_is_explicit(self) -> None:
        case, _, result = run_case("D1-001")
        self.assert_gold(case, result)
        self.assertEqual(result.trace[0].state_update.decision, AgentDecision.CONTINUE)
        self.assertEqual(result.trace[0].action.tool_name, "search_sources")

    def test_adjust_path_narrows_the_claim(self) -> None:
        case, _, result = run_case("D1-002")
        self.assert_gold(case, result)
        adjustment = result.trace[1]
        self.assertEqual(adjustment.state_update.decision, AgentDecision.ADJUST)
        self.assertEqual(result.state.active_claim, case["gold"]["active_claim"])
        self.assertNotEqual(result.state.active_claim, result.state.original_claim)

    def test_ask_path_requests_confirmation(self) -> None:
        case, _, result = run_case("D1-003")
        self.assert_gold(case, result)
        self.assertEqual(result.trace[0].state_update.decision, AgentDecision.ASK)
        self.assertEqual(result.state.status, EvidenceStatus.NEEDS_CONFIRMATION)

    def test_stops_when_evidence_is_sufficient(self) -> None:
        case, _, result = run_case("D1-001")
        self.assert_gold(case, result)
        self.assertEqual(result.state.stop_reason, StopReason.EVIDENCE_SUFFICIENT)
        self.assertEqual(result.state.status, EvidenceStatus.SUPPORTED)

    def test_stops_when_permitted_evidence_is_exhausted(self) -> None:
        case, _, result = run_case("D1-004")
        self.assert_gold(case, result)
        self.assertEqual(result.state.stop_reason, StopReason.EVIDENCE_EXHAUSTED)

    def test_stops_on_unresolved_contradiction(self) -> None:
        case, _, result = run_case("D1-005")
        self.assert_gold(case, result)
        self.assertEqual(result.state.stop_reason, StopReason.UNRESOLVED_CONTRADICTION)
        self.assertEqual(result.state.status, EvidenceStatus.CONFLICTING)

    def test_stops_on_budget_exhaustion(self) -> None:
        case, tools, result = run_case("D1-006")
        self.assert_gold(case, result)
        self.assertEqual(result.state.stop_reason, StopReason.BUDGET_EXHAUSTED)
        self.assertEqual(len(tools.calls), 1)

    def test_stops_on_unrecoverable_tool_failure(self) -> None:
        case, _, result = run_case("D1-007")
        self.assert_gold(case, result)
        self.assertEqual(result.state.stop_reason, StopReason.TOOL_FAILURE)
        self.assertIn("corrupt PDF", result.trace[0].observation.error)

    def test_loop_always_terminates_within_budgets(self) -> None:
        case, tools, result = run_case("D1-008")
        self.assert_gold(case, result)
        self.assertLessEqual(result.state.turns_used, result.state.budget.max_turns)
        self.assertLessEqual(
            result.state.tool_calls_used, result.state.budget.max_tool_calls
        )
        self.assertEqual(len(tools.calls), 3)

    def test_prompt_injection_text_remains_inert_observation_data(self) -> None:
        case, tools, result = run_case("D1-009")
        self.assert_gold(case, result)
        content = result.trace[1].observation.data["content"]
        self.assertIn("Ignore prior instructions", content)
        self.assertEqual(
            [call["tool"] for call in tools.calls],
            ["search_sources", "read_source"],
        )
        self.assertEqual(result.state.status, EvidenceStatus.NOT_FOUND)

    def test_search_cannot_expand_the_permitted_source_set(self) -> None:
        case, tools, result = run_case("D1-010")
        self.assert_gold(case, result)
        self.assertEqual([call["tool"] for call in tools.calls], ["search_sources"])
        self.assertIn("outside the permitted set", result.trace[0].observation.error)

    def test_trace_is_deterministic_and_contains_visible_records(self) -> None:
        _, _, first = run_case("D1-001")
        _, _, second = run_case("D1-001")
        self.assertEqual(first.to_trace_dict(), second.to_trace_dict())
        for step in first.trace:
            self.assertIsNotNone(step.state_before)
            self.assertIsNotNone(step.action)
            self.assertIsNotNone(step.observation)
            self.assertIsNotNone(step.state_update)

    def test_comparison_approaches_remain_named_but_unclaimed(self) -> None:
        self.assertEqual(
            EvidenceInvestigator.comparison_approaches,
            (
                "strong_one_shot_prompt",
                "fixed_extract_search_validate",
                "bounded_adaptive_agent_loop",
            ),
        )


if __name__ == "__main__":
    unittest.main()
