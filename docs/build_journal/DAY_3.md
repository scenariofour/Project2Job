# Day 3 — Context, RAG, and Evidence

Status: IMPLEMENTED

## Question

How much context should be read, and when does retrieval improve evidence quality?

## User value

Outputs stay traceable to permitted sources without repeatedly loading an entire
project.

## Core concepts

Context budgets, retrieval, provenance, evidence boundaries, source registry,
and RAG comparison.

## Product and implementation scope

The repository keeps the existing chain:

```text
Source / Artifact
→ Evidence
→ Claim
→ Output
→ Dependency
```

Artifact manifests and fingerprints remain the Project source registry. Evidence
records carry source and location, claims carry status and attribution scope,
outputs name their dependencies, and the deterministic graph invalidates
descendants after a change or removal.

Day 3 adds no index, vector database, embedding model, RAG service, Agent
framework, or new source connector.

## Context-selection comparison

`scripts/run_day3_context_comparison.py` executes three labeled synthetic cases
against the same seven-file Project fixture:

1. a supported evaluation-result claim;
2. a citation-only launch claim that remains unsupported;
3. an ownership claim whose separate team-boundary artifact is critical.

Each strategy is rerun for each case, so file-open events and content characters
are observed counts, not estimates. They count opened Project artifact bodies,
not the case definitions or manifest control file. Targeted selection ranks
manifest paths by exact filename-term overlap; it is not semantic retrieval.

| Strategy | File-open events | Unique files | Characters opened | Relevant sources found | Critical sources missed | Irrelevant opens | Claim/source correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Broad full Project | 21 | 7 | 2,841 | 3 | 0 | 18 | 3/3 |
| Manifest-scoped | 12 | 4 | 1,815 | 3 | 0 | 9 | 3/3 |
| Targeted filename selection | 3 | 3 | 435 | 2 | 1 | 1 | 2/3 |

The targeted selector found `eval/design.md` but missed `docs/team.md`, the only
artifact establishing that individual ownership was unresolved. This is the
required missed-evidence bad case.

The run did not measure tokens, latency, cost, model quality, or user value.
`content_chars_opened` is the only content-volume measurement.

Reproduce or verify the committed result:

```bash
python3 scripts/run_day3_context_comparison.py --check
python3 -m unittest tests.test_day3_context -v
```

The machine-readable result is
`docs/build_journal/traces/day3_context_comparison.json`.

## Architecture decision

Retain manifest-scoped context and defer retrieval/RAG.

Manifest scope matched the broad baseline on all three claim/source judgments
and all critical sources while opening 1,026 fewer characters and nine fewer
file events. The narrower selector saved more context but failed the ownership
boundary case. This small synthetic comparison does not show enough benefit to
justify a retrieval layer.

See D-026 in `docs/13_DECISION_LOG.md`.

## Behavior added

External export validation now requires:

- every dependent claim to remain Supported;
- a direct evidence ancestor through the dependency graph;
- resolved ownership attribution.

A citation node with `irrelevant`, `partial`, or contradictory assessment cannot
ground the external claim. The existing one-repair policy disables export while
preserving the internal output for review. Changed evidence records now retain
their structured assessment so this check is inspectable.

Existing behavior is reused for:

- Project and JD manifests, fingerprints, and cross-process state;
- changed/removed detection, dependency invalidation, cleanup, and selective
  recompute;
- preservation of unrelated outputs;
- separate Project-evidence and interview-research status systems;
- inert untrusted text, fixed tool permissions, and a fixed source frontier;
- research items created only from the host's bounded `ExtractedItem` contract;
- structured traces and observed file-open telemetry.

## Acceptance traceability

| Acceptance criterion | Eval cases | Executable evidence | Result |
| --- | --- | --- | --- |
| D3-AC-01 External claims have direct source support or stay unexported | D3-001, D3-002 | `test_citation_without_direct_support_fails_export_validation`, `test_direct_support_allows_the_external_claim` | Pass |
| D3-AC-02 Citation presence alone does not establish grounding | D3-002 | `test_citation_alone_remains_unsupported` | Pass |
| D3-AC-03 Project evidence and interview research remain separate truth systems | D2-017, A08_BOTH_CHANGED | `test_the_two_evidence_scales_stay_separate`, `test_research_never_reaches_a_candidate_or_a_verification_claim` | Pass |
| D3-AC-04 Untrusted text cannot instruct, add tools, expand permission, or enlarge the source frontier | D1-009, D1-010, D2-017, A14_INJECTION | `test_prompt_injection_text_remains_inert_observation_data`, `test_search_cannot_expand_the_permitted_source_set`, `test_fetched_page_text_cannot_cause_a_fetch_or_a_claim` | Pass |
| D3-AC-05 Web facts become research items only through bounded structured extraction | D2-017 | `test_fetched_page_text_cannot_cause_a_fetch_or_a_claim`, `test_a_cited_page_must_be_one_the_run_extracted` | Pass |
| D3-AC-06 Changed or removed sources invalidate dependent evidence, claims, and outputs | A05_PROJECT_ADDED, A06_PROJECT_REMOVED | `test_two_process_restore_and_real_changed_artifact_path`, `test_removed_evidence_and_edges_stay_absent_after_restore` | Pass |
| D3-AC-07 Unrelated outputs remain preserved | A05_PROJECT_ADDED, A06_PROJECT_REMOVED, A17_COMPARISON | `test_removed_evidence_and_edges_stay_absent_after_restore`, `test_manifest_preserves_correctness_with_less_opened_context` | Pass |
| D3-AC-08 Uncertain ownership prevents direct personal attribution | D1-003, D3-003 | `test_unresolved_ownership_fails_external_attribution`, `test_targeted_selection_records_the_boundary_miss` | Pass |

## Maturity

| Label | Day 3 state |
| --- | --- |
| IMPLEMENTED | Comparison runner, fixtures, committed result, export gate, schema field, and decision record exist. |
| TESTED | Ten focused Day 3 tests pass; reused Day 1–3 regression coverage passes. |
| DOGFOODED | No. The comparison uses synthetic deterministic fixtures. |
| USER-VALIDATED | No target user has evaluated this Day 3 behavior. |
| OUTCOME-PROVEN | No application, interview, or hiring outcome is established. |

## What is not yet proven

- production retrieval or RAG quality;
- behavior on a live, large, heterogeneous Project corpus;
- model token use, latency, or cost;
- that manifest scope is best for every Project;
- target-user comprehension or value;
- hiring or application outcomes.

## Bad case or tradeoff

Narrow retrieval can lower context volume while omitting the one artifact needed
to bound a claim. Day 3 therefore stops at the evidence-backed architecture
decision and does not implement RAG.

## Public content notes

- Visualize provenance and evidence boundaries.
- Report only the observed file and character counts as measurements.
- Keep Transformer/Attention notes tied to product impact.
