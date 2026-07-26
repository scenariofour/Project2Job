# WO-02 Agent PoC

Context set: `agent_poc`

Implementation status: implemented and deterministically tested on
2026-07-26; target-user value remains unvalidated.

## Goal

Implement one stateful Evidence Investigator and one project-update cycle.

## Deliver

- six read-only tools
- Agent loop
- project state
- file hashing
- user correction
- dependency invalidation
- update comparison
- traces
- token and tool telemetry

## Acceptance

- Agent respects budgets and stop conditions
- tool failures remain visible
- user correction updates dependent outputs
- changed files are prioritized
- fresh Skill rerun comparison completed
- no multi-agent or Deep Agent

## Evidence

- `src/career_desk/runtime.py` retains the bounded per-claim Evidence
  Investigator and six read-only tool interfaces.
- `skill/p2j/scripts/context_registry.py` provides consent-gated identity,
  version, fingerprint, correction-context, canonical Agent-state persistence,
  and cross-process reuse.
- `src/career_desk/orchestrator.py` provides the allowed-action policy,
  scripted and host-mediated planners, dependency traversal, one repair, and
  privacy-safe run trace.
- `src/career_desk/capabilities.py` and
  `skill/p2j/scripts/stateful_agent.py` connect the registry, orchestrator,
  changed-surface Evidence Investigator, validators, and atomic save path.
- `tests/test_context_registry.py`, `tests/test_stateful_agent.py`,
  `tests/test_integrated_agent.py`, and
  `lab/evals/agent_cases.jsonl` cover the accepted stateful paths.
- `docs/dogfood/STATEFUL_AGENT_V0_COMPARISON.json` records the fresh-rerun
  comparison from observed integrated adapter events. It supports a bounded
  repository-dogfood conclusion only.
