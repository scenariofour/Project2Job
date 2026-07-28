# Project Status

Updated: 2026-07-27

Highest completed Day: 3

## Current stage

**WO-00 Shared Foundation is complete. The Day 1 bounded Agent Loop is
implemented and tested. Day 2 JD-first intake and Day 3 context/evidence
behavior are implemented and tested. Stateful Agent V0 mechanics are
implemented and deterministically tested. A seven-Skill host-native Alpha is
implemented and installable.**

Loop mechanics and Skill contracts are covered by unit tests and eval cases.
The Alpha has been dogfooded in Codex, but product quality and user value are
not yet validated with target users.

## Implemented

Repository foundation:

- existing Git history, `origin`, public repository, and MIT license preserved
- v6 package integrated at the repository root
- manifest-scoped product documents and Work Orders
- deterministic validation, contract-test, and inventory commands
- public Day 0–Day 7 journal

WO-00 Shared Foundation:

- versioned role profile, source registry, and shared contract
- application pack, project evidence, role profile, and gold case schemas
- ten labeled shared gold cases covering every capability domain and every
  evidence status
- reviewer and annotation guidance

Day 1 bounded Agent Loop:

- a deterministic Evidence Investigator with explicit state, action,
  observation, and state-update records
- Continue / Adjust / Ask / Stop decisions with separate turn and tool-call
  budgets and guaranteed termination
- terminal reasons for sufficient evidence, exhausted evidence, unresolved
  contradiction, budget exhaustion, required confirmation, and tool failure
- a permitted-source boundary that tool results cannot expand
- deterministic visible traces committed under `docs/build_journal/traces/`

Day 1 still uses **deterministic scripted read-only tools**. The new V0 layer
adds the WO-02 Project/JD update mechanics, but it is not a production
model-powered Agent runtime.

Stateful Agent V0:

- consent-gated local Project/JD context with cross-process reuse
- Project and JD version/change detection
- explicit allowed-action orchestrator with scripted and host-mediated planners
- dependency-aware correction, removal, Project-update, and JD-update paths
- selective output preservation, one bounded repair, visible stop conditions,
  and privacy-safe structured traces
- one real changed-artifact path through the existing Evidence Investigator;
  scores and JD Matches are recomputed but change only when evidence adds the
  corresponding capability
- one shared local renderer for Initial Analysis, Evidence Inspection, Project
  Updated, and No Relevant Changes
- observed execution-cost and replay-consistency comparison between a stateful
  update and fresh host replay

Host-native Skill Alpha:

- `$p2j` low-friction router
- `$p2j-brief`, `$p2j-audit`, `$p2j-intel`, `$p2j-answer`, `$p2j-mock`, and
  `$p2j-upgrade` specialists
- six strict 0–5 Gates projected from the canonical 10 domains, with hard caps
  and N/A handling
- bounded project forensics and public company research contracts
- ranked interview-answer reconstruction with explicit factual framing
- installer, portable archive builder, suite validator, and behavior evals
- consent-gated local Context Registry for one Project, one JD, and compatible
  Analysis Run history, including selective reuse and invalidation

The Alpha runs inside a compatible Agent host. It depends on that host for file,
Git, search, fetch, browser, and local-storage capabilities; it is not a
standalone runtime and does not monitor or regenerate in the background.

Day 2 JD-first intake (WO-05):

- deterministic JD extraction that records every unstated field as unknown
- Role Demand Map derived from the versioned role profile
- one bounded research pass over a host-supplied search / read-only fetch /
  Playwright capability, with canonical-URL and page-body deduplication,
  official-tier-first ordering, escalation reasons, blocked-page abandonment,
  budget accounting, and one recorded stop reason on every path
- resume candidate extraction that stays `self_reported`, five routing bands,
  an evidence-availability gate that keyword overlap cannot pass, and
  `no_clear_choice` instead of a weak winner
- Required Evidence Checklist and exactly one next input
- a cross-object output validator and an executable runner for the
  intake-stage Day 2 eval cases

Day 3 context, provenance, and evidence:

- a deterministic broad/full versus manifest-scoped versus targeted-selection
  comparison over three synthetic cases and seven focused artifacts
- an inspectable committed result with observed file-open, character,
  relevance, critical-miss, irrelevant-open, claim/source, and provenance counts
- one targeted-selection bad case that misses the separate ownership boundary
- an external-export gate requiring Supported claims, a direct evidence
  ancestor, and resolved attribution
- the measured decision to retain manifest-scoped context and defer retrieval/RAG

The intake runtime opens no socket of its own and does not generate an
Application and Interview Pack. Its `runtime_seconds` and `total_tokens` are a
deterministic cost model, not measurements.

## Tested

- 13 Day 1 Agent-loop unit tests and 10 `D1-001`–`D1-010` eval cases
- required repository paths exist and the active document count is bounded
- JSON and JSONL files parse
- Day journal statuses form a valid completed prefix that agrees with this file
- documentation consistency checks in `tests/test_document_consistency.py`
- sample project inventory is deterministic
- seven Skill packages pass structural validation and install validation
- twenty Skill behavior cases cover routing, Brief UX, shared context, Gates,
  Answer Lab, research,
  N/A, source caps, ownership, conflict, injection, no-event recovery, and One
  Next Build, plus visibly labeled mock practice
- twenty Context Registry unit tests cover consent, cross-process and
  cross-Skill reuse, versioning, incremental invalidation, controls, identity,
  privacy, and corrupt-state failure
- integrated tests cover separate-process restore, the real changed-artifact
  path, all Project/JD/correction flag combinations, invalid action rejection,
  and the Upgrade handoff boundary
- fresh Codex host dogfood produced a concise Brief and a grounded Answer Lab
  without executing the inspected project
- 43 Day 2 intake behavior tests, plus the 17 intake-stage `D2-0xx` eval cases
  executed end to end with 85 checks and no failure
- every Intake Result the eval cases produce validates against
  `schemas/intake_result.schema.json` and passes the cross-reference validator
- one JD-first dogfood over committed fixtures, pinned to the runtime
- ten focused Day 3 tests cover the deterministic comparison, citation-only
  grounding failure, direct evidence, unresolved attribution, and bounded repair

See `docs/build_journal/DAY_1.md` for Agent-loop traceability,
`docs/build_journal/DAY_2.md` for intake traceability,
`docs/dogfood/SKILL_ALPHA_DOGFOOD.md` for the Alpha inspection report, and
`docs/dogfood/DAY2_JD_FIRST_DOGFOOD.md` for the JD-first dogfood.

## Planned

- WO-05 pack handoff: the Intake Result is produced but no pack generator
  consumes it, so the three `pack`-stage Day 2 cases stay unexecuted
- a live-host research pass; every executed case uses a fixture host
- target-user testing and cross-host behavior comparison
- live-corpus and live-model context comparison beyond deterministic fixtures
- evaluation runs, model decision, target-user pilot, and measured results

## Not yet proven

- user value or adoption
- product quality
- Skill runtime outside fresh Codex dogfood, including cross-host behavior;
  install validation succeeded in Codex and Claude Code locations, but the
  Claude invocation was blocked by an expired host OAuth token
- production Web UI and production RAG behavior; the local report is a
  demonstration surface only
- production retrieval quality; Day 3 intentionally defers a retrieval layer
- model token use, latency, and cost for the Day 3 context strategies; only file
  opens and characters were observed
- production model behavior
- Skill advantage over a strong generic prompt
- Agent advantage beyond the single observed execution-cost and
  replay-consistency comparison
- latency, token, and cost targets
- role-standard relationship to hiring outcomes
- that the JD-first ordering matches how users actually work
- that the project recommendation beats the user's own instinct
- that public evidence plus optional user-supplied material will support a useful
  company brief
- intake behavior against a live host: search results, page structure, latency,
  and token cost are all fixture-level
- that the routing bands agree with a human reviewer on real resume prose

## Next required action

Run the first target-user Alpha test and a live-model planner comparison. Day 4
and later implementation remain separate tasks; do not expand the local report
or add retrieval without new evidence.
