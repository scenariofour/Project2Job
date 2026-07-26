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

## Acceptance traceability

Every Day 1 acceptance criterion, its labeled eval cases, the unit test that
executes it, and the committed evidence. Eval case IDs `D1-001`–`D1-010` are
stable and unchanged.

These criteria cover loop mechanics only. Passing them does not validate output
quality, user value, or any Agent advantage.

| AC | Criterion | Eval cases | Unit test (`tests/test_agent_loop.py`) | Evidence | Result |
| --- | --- | --- | --- | --- | --- |
| D1-AC-01 | Explicit state, action, observation, and state-update records | D1-001, D1-002 | `test_trace_is_deterministic_and_contains_visible_records` | `traces/day1_success.json` | Pass |
| D1-AC-02 | Continue path | D1-001, D1-008 | `test_continue_path_is_explicit` | `traces/day1_success.json` | Pass |
| D1-AC-03 | Adjust path narrows the claim | D1-002 | `test_adjust_path_narrows_the_claim` | eval case gold `active_claim` | Pass |
| D1-AC-04 | Ask path requests human confirmation | D1-003 | `test_ask_path_requests_confirmation` | eval case gold `needs_confirmation` | Pass |
| D1-AC-05 | Stop on sufficient evidence | D1-001, D1-002 | `test_stops_when_evidence_is_sufficient` | `traces/day1_success.json` | Pass |
| D1-AC-06 | Stop when permitted evidence is exhausted | D1-004, D1-009 | `test_stops_when_permitted_evidence_is_exhausted` | eval case gold `evidence_exhausted` | Pass |
| D1-AC-07 | Stop on unresolved contradiction | D1-005 | `test_stops_on_unresolved_contradiction` | eval case gold `conflicting` | Pass |
| D1-AC-08 | Budget stop and guaranteed termination | D1-006, D1-008 | `test_stops_on_budget_exhaustion`, `test_loop_always_terminates_within_budgets` | eval case gold `budget_exhausted` | Pass |
| D1-AC-09 | Tool failure is visible and terminal | D1-007, D1-010 | `test_stops_on_unrecoverable_tool_failure` | `traces/day1_tool_failure.json` | Pass |
| D1-AC-10 | Prompt injection text remains inert observation data | D1-009 | `test_prompt_injection_text_remains_inert_observation_data` | eval case gold `content_remains_data` | Pass |
| D1-AC-11 | Tool results cannot expand the permitted source set | D1-010 | `test_search_cannot_expand_the_permitted_source_set` | eval case gold `must_not_read_unpermitted_source` | Pass |
| D1-AC-12 | Traces are deterministic across runs | D1-001, D1-007 | `test_trace_is_deterministic_and_contains_visible_records` | `traces/day1_success.json`, `traces/day1_tool_failure.json` | Pass |

`test_comparison_approaches_remain_named_but_unclaimed` is not an acceptance
criterion. It asserts that no comparative advantage is claimed yet.

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
- `GLOSSARY.md`
- `docs/DOCUMENT_GOVERNANCE.md`
- `tests/test_document_consistency.py`
- `README.md`, `PROJECT_STATUS.md`, `ACTIVE_SCOPE.md`, `docs/01_MVP_PRD.md`

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
test was added and the gate was advanced to Day 1.

## Governance follow-up

A later pass on this same pull request removed the documentation drift Day 1
created. `README.md` and `PROJECT_STATUS.md` had kept a Day 0-only status,
`ACTIVE_SCOPE.md` and the MVP PRD had stated output counts as quotas while the
schema allowed zero, and the product carried two names.

- `GLOSSARY.md` and `docs/DOCUMENT_GOVERNANCE.md` were added. Neither is an
  active product document; `active_document_count` remains 14.
- The Day journal gate was replaced with a general rule: statuses must be
  recognized, completed Days must form a contiguous prefix, and
  `PROJECT_STATUS.md` must state the same highest completed Day. Adding Day 2
  will not require editing `scripts/validate_repo.py`.
- `tests/test_document_consistency.py` now enforces these document facts.

Results after the follow-up:

- `python3 -m unittest discover -s tests -p test_agent_loop.py -v` — 13 tests passed.
- `python3 -m unittest discover -s tests -p test_document_consistency.py -v` — 17 tests passed.
- `make validate` — status `ok`, 14 active documents, `highest_completed_day: 1`.
- `make test` — 41 tests passed.
- `make inventory` and `git diff --check` — passed.

No verification failures remain.

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
