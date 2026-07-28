# Day 4 — Skill, Agent, and Human Control

Status: IMPLEMENTED

Not validated. Day 4 closes the deterministic responsibility, approval,
correction, and update mechanics. It does not establish target-user value,
live-model quality, or a general advantage for an Agent.

## Question

Which responsibilities belong to a reusable Skill, a stateful Agent, or the
user?

## Responsibility boundary

| Owner | Responsibility | Approval or stop point |
| --- | --- | --- |
| Skill | Perform one user-invoked analysis through the shared evidence and output contract. It may reuse compatible Context Registry state after consent. | The user chooses the Project and JD, grants source access, and decides whether to save context. A one-time no-save run needs no registry consent. |
| Agent | On an invoked update, resolve saved context, compare Project/JD versions, select one allowed action, recheck dependency descendants, validate affected outputs, preserve unrelated outputs, and explain the change. | It stops when read permission, correction approval, or factual confirmation is missing. It performs no background monitoring or external action. |
| User | Confirm personal ownership, sensitive or inferred facts, approve corrections, decide whether to persist state, and decide whether an eligible external-facing asset is actually used. | Previewed corrections do not change state. Supported and grounded output is only eligible for external use; Project2Job does not submit or publish it. |

The Context Registry is passive infrastructure, not a fourth product actor. It
stores bounded consented state and fingerprints; it does not choose actions,
monitor files, or regenerate outputs.

## Existing behavior reused

- `StatefulEvidenceAgent` already detects new, unchanged, Project, JD, combined,
  and correction paths under explicit budgets and allowed actions.
- `Project2JobCapabilities` already applies approved corrections, traverses
  dependencies, inspects only changed evidence surfaces, and recomputes affected
  outputs.
- the Context Registry already persists one canonical Agent state atomically and
  restores it in a separate process after consent;
- the external export gate already requires a Supported claim, a direct evidence
  ancestor, and resolved attribution;
- `stateful_agent.py` already reports Before / After / Why, affected and
  preserved outputs, file opens, questions, calls, and stop reason;
- the committed fresh-replay comparison already records the bounded mechanical
  tradeoff.

Day 4 adds no Agent behavior, framework, connector, UI, retrieval layer,
background process, or external action.

## Reproducible evidence

Run:

```bash
python3 -m unittest \
  tests.test_stateful_agent \
  tests.test_integrated_agent \
  tests.test_day3_context.ExternalClaimGroundingTests -v
```

Focused result on 2026-07-27: 35 tests ran, 34 passed, and the optional
`jsonschema` fixture-validation test skipped because that dependency was not
installed.

The focused closeout run executes:

- an initial run that saves dependency-backed outputs and a trace;
- a separate-process restore followed by one real changed-artifact update;
- an unapproved correction that leaves state unchanged;
- an approved correction that updates the named claim and dependent outputs;
- changed and removed evidence paths that preserve unrelated outputs;
- direct-support and resolved-ownership export gates;
- the fresh replay comparison and its limitation statements.

The initial/update path is reproducible in
`test_two_process_restore_and_real_changed_artifact_path`: the initial process
saves state, a later process adds one labeled evidence artifact, opens one file,
updates the three descendants of `c_eval`, and preserves `score_technical`.

## Acceptance traceability

| Acceptance criterion | Eval cases | Executable evidence | Result |
| --- | --- | --- | --- |
| D4-AC-01 Skill, Agent, Registry, and user responsibilities and approval points are distinct | A02_UNCHANGED, A03_CORRECTION_PREVIEW, A12_NO_SAVE | `test_one_time_brief_needs_no_registry_consent_or_agent_runtime`, `test_correction_requires_approval_before_state_changes`, `test_skill_registry_and_agent_have_distinct_responsibilities` | Pass |
| D4-AC-02 Approved corrections propagate to dependent claims and outputs while keeping history visible | A03_CORRECTION_PREVIEW, A04_CORRECTION_APPLY | `test_approved_correction_updates_dependents_and_preserves_unrelated`, `test_approved_correction_persists_only_named_claim_and_dependents` | Pass |
| D4-AC-03 Changed or removed evidence updates only affected outputs and preserves unrelated outputs | A05_PROJECT_ADDED, A06_PROJECT_REMOVED | `test_two_process_restore_and_real_changed_artifact_path`, `test_removed_evidence_and_edges_stay_absent_after_restore` | Pass |
| D4-AC-04 External claims require Supported direct evidence and resolved ownership | D3-001, D3-002, D3-003 | `test_citation_without_direct_support_fails_export_validation`, `test_direct_support_allows_the_external_claim`, `test_unresolved_ownership_fails_external_attribution` | Pass |
| D4-AC-05 One initial run and one later update are reproducible across processes | A01_INITIAL, A02_UNCHANGED, A05_PROJECT_ADDED | `test_two_process_restore_and_real_changed_artifact_path` | Pass |
| D4-AC-06 A stale persistent-claim failure is visible and fails the case | A06_PROJECT_REMOVED | `test_removed_evidence_and_edges_stay_absent_after_restore`, `test_removed_evidence_eval_is_the_visible_stale_state_bad_case` | Pass |
| D4-AC-07 The Agent decision is bounded against fresh replay without claiming user value | A17_COMPARISON | `test_fresh_replay_comparison_supports_only_a_bounded_agent_decision` | Pass |

## Bad case

`A06_PROJECT_REMOVED` is the visible stale-state case. If a supporting evaluation
artifact disappears, retaining the prior Supported claim, evaluation score, or
JD Match fails. The executable path removes both the evidence and dependency
edges, changes only the evaluation descendants, persists the corrected state,
and restores that state unchanged in a later process. Missing support becomes
`not_found`; it does not become proof that the user lacks the capability.

## Architecture decision

Retain the bounded Agent for explicit update cycles, while keeping the Skill the
default one-off product and fresh replay the baseline.

In the one controlled repository comparison, the stateful update opened 1 file
and regenerated 2 outputs; fresh replay opened 6 files and regenerated 23. Both
matched the same 2 expected final values, and the stateful path changed 0
unrelated outputs. This supports selective update mechanics and trace clarity.
It does not show a latency win, token savings, better output quality, target-user
preference, or general Agent superiority. No live model planner ran.

The Agent is therefore justified narrowly by continuity work the Skill alone
does not own: change detection, dependency invalidation, selective regeneration,
and a managed change explanation. If later user or live-model evidence shows no
meaningful benefit, the fixed Skill plus fresh replay remains the simpler
fallback.

See D-027 in `docs/13_DECISION_LOG.md`.

## Maturity

| Label | Day 4 state |
| --- | --- |
| IMPLEMENTED | Responsibility boundary, approval gates, correction propagation, selective update, export validation, persistent restore, and comparison evidence exist. |
| TESTED | Focused deterministic unit and integration coverage passes. |
| DOGFOODED | One controlled repository comparison exists. |
| USER-VALIDATED | No target user has evaluated the update cycle or control model. |
| OUTCOME-PROVEN | No application, interview, or hiring outcome is established. |

## What is not yet proven

- that target users want persistent state;
- that users understand the Skill/Agent boundary or correction controls;
- that a live-model Agent preserves the same correctness and selectivity;
- independent output-quality parity between stateful update and fresh analysis;
- token, latency, or cost advantage;
- advantage over a fixed stateful workflow;
- application, interview, or hiring outcomes.

## Public content notes

- Show the correction preview and explicit approval boundary.
- Show affected and preserved dependency descendants.
- Lead with the stale-state bad case, not the efficiency numbers.
- Describe the Agent decision as a bounded mechanical decision, not validated
  user value.
