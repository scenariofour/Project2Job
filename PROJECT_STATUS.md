# Project Status

Updated: 2026-07-26

Highest completed Day: 1

## Current stage

**WO-00 Shared Foundation is complete. The Day 1 bounded Agent Loop is
implemented and tested. Stateful Agent V0 mechanics are implemented and
deterministically tested. A seven-Skill host-native Alpha is implemented and
installable.**

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

See `docs/build_journal/DAY_1.md` for Agent-loop traceability and
`docs/dogfood/SKILL_ALPHA_DOGFOOD.md` for the Alpha inspection report.

## Planned

- WO-05 JD-first intake and project routing: contracts, eval cases, and
  acceptance criteria are defined; the host-native Skill now exercises them,
  but no standalone runtime exists
- target-user testing and cross-host behavior comparison
- production retrieval comparison and failure injection beyond deterministic
  fixtures
- evaluation runs, model decision, target-user pilot, and measured results

## Not yet proven

- user value or adoption
- product quality
- Skill runtime outside fresh Codex dogfood, including cross-host behavior;
  install validation succeeded in Codex and Claude Code locations, but the
  Claude invocation was blocked by an expired host OAuth token
- production Web UI and production RAG behavior; the local report is a
  demonstration surface only
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

## Next required action

Run the first target-user Alpha test and a live-model planner comparison; do not
expand the local report into a production Web application.
