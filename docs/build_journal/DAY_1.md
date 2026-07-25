# Day 1 — Agent Loop

Status: IMPLEMENTED

Not validated. Day 1 verifies loop mechanics only.

## Question

What is the smallest observable loop that can investigate evidence safely?

## Actual implementation scope

A deterministic Evidence Investigator now maps:

```text
Claim + State
→ Action
→ Tool Observation
→ State Update
→ Continue / Adjust / Ask / Stop
```

The slice uses scripted, read-only tools rather than a production model. It has
explicit state, action, observation, and state-update records; separate turn and
tool-call budgets; deterministic visible traces; and terminal reasons for
sufficient evidence, exhausted permitted evidence, unresolved contradiction,
budget exhaustion, confirmation required, and unrecoverable tool failure.

Search results cannot expand the caller's permitted source set. Project document
content remains inert observation data, and persisted traces omit source content.

The one-shot prompt, fixed extract-search-validate workflow, and bounded adaptive
loop retain one comparison interface. No comparative advantage is claimed.

## Files changed

- `src/career_desk/contracts.py`
- `src/career_desk/runtime.py`
- `src/career_desk/tools.py`
- `scripts/validate_repo.py`
- `tests/test_agent_loop.py`
- `tests/test_contracts.py`
- `lab/evals/day1_agent_loop_cases.jsonl`
- `docs/build_journal/traces/day1_success.json`
- `docs/build_journal/traces/day1_tool_failure.json`
- `docs/build_journal/DAY_1.md`
- `docs/13_DECISION_LOG.md`

## Commands and results

- `python3 -m unittest tests.test_agent_loop -v`
  - 13 tests passed in 0.003 seconds.
- `python3 -m unittest
  tests.test_contracts.ContractTests.test_journal_statuses_allow_completed_day1 -v`
  - 1 regression test passed in 0.001 seconds.
- `make validate`
  - Passed with status `ok`, 14 active documents, 14 JSON files, and 41
    JSONL cases.
- `make test`
  - 24 tests passed in 0.007 seconds.
- `git diff --check`
  - Passed with no output.
- Regenerated trace comparison
  - `day1_success.json: MATCH`
  - `day1_tool_failure.json: MATCH`

The initial focused test run failed at import because the loop contract did not
yet exist. The tests passed after the bounded implementation was added.

The first final validation exposed a stale Day 0-only journal gate. A regression
test was added, and the validator now requires Days 0–1 `IMPLEMENTED` while
keeping Days 2–7 `PLANNED`. No verification failures remain.

## Trace evidence

- Successful trace: `docs/build_journal/traces/day1_success.json`
  - search → Continue → read → Supported → Stop (`evidence_sufficient`)
- Failure trace: `docs/build_journal/traces/day1_tool_failure.json`
  - search error → visible failure → Stop (`tool_failure`)

## Bad case or tradeoff

The adaptive path narrows a weak claim after a partial observation, but this does
not prove adaptation is necessary. A fixed workflow could implement the same
branch with less runtime freedom. The loop also treats structured tool
assessments as trusted tool output; production assessment quality is untested.

## Candidate decision checkpoint

- Decision that might require adaptive control: choosing whether to search again,
  narrow a claim after partial evidence, ask for ownership confirmation, or stop
  when later observations change the evidence boundary.
- What a fixed workflow could already handle: ordered search, bounded reads,
  direct/partial/conflicting classification, standard confirmation gates, and all
  current stop conditions.
- Evidence needed to retain the Agent loop: against both baselines, it must improve
  claim-boundary correctness or recovery on labeled cases without unacceptable
  increases in errors, tool calls, latency, or trace ambiguity.
- Replacement trigger: use the fixed workflow if it matches the loop's quality and
  recovery, or if adaptive choices add no measured benefit or create more unsafe
  or unnecessary actions.

No final architecture choice is made before comparison evidence exists.

## What remains unproven

- user value
- product quality
- Agent advantage over a strong one-shot prompt
- Agent advantage over a fixed extract-search-validate workflow
- production model behavior, retrieval quality, latency, or cost
- the full WO-02 project-update cycle

Day 1 is `IMPLEMENTED`, not `VALIDATED`.
