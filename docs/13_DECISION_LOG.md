# Decision Log

## D-001: Two products, one standard

Decision:

- build an open-source Skill
- build a stateful Agent
- share standards, schemas, and evals

Reason:

The Skill provides low-friction value and distribution. The Agent creates update and continuity value.

## D-002: One project and one role

Decision:

MVP analyzes one project against one role profile or JD.

Reason:

Multi-project selection increases input cost, tokens, explanation difficulty, and evaluation complexity.

## D-003: Application Pack output

Decision:

MVP produces grounded resume and interview assets in addition to evidence analysis.

Reason:

Users need directly usable career outputs, not an internal audit report.

## D-004: Agent value is update value

Decision:

The full Agent must detect project changes and update dependent evidence and outputs.

Reason:

A Web wrapper around the Skill would not justify a stateful Agent product.

## D-005: Role-Backwards Evidence Framework

Decision:

Use RBEF as the shared method.

Reason:

The product should connect role reality, hiring signals, project artifacts, evidence boundaries, and career outputs.

## D-006: No broad integrations in MVP

Decision:

No Gmail, job APIs, application tracking, or broad MCP set.

Reason:

They do not prove the core product promise and increase failure surface.

## D-007: Strong generic prompt as baseline

Decision:

Treat a high-quality prompt as the primary Skill competitor.

Reason:

The Skill must create value through reusable standards, scripts, references, schemas, and eval-tested behavior.

## D-008: Frameworks follow evidence

Decision:

Do not require LangGraph, multi-agent, or Deep Agent.

Reason:

Framework use must solve observed runtime problems.

## D-009: Import v6 into the existing repository

Decision:

Integrate the v6 Build System at the existing Project2Job repository root while
preserving its Git history, `origin`, `main` lineage, and MIT license.

Reason:

The repository is the public system of record. Reinitializing or nesting the
package would break provenance and make the documented paths inaccurate.

## D-010: Separate public Days from engineering dependencies

Decision:

Use `docs/build_journal/` for the Day 0–Day 7 learning narrative and retain
`work_orders/` as the technical dependency system.

Reason:

Content order and engineering order serve different purposes. Keeping both
explicit prevents the journal from becoming a duplicate roadmap or PRD.

## D-011: Exclude the generated Skill ZIP

Decision:

Do not track `dist/career-desk-project-to-application-skill_v1.zip` on Day 0.

Reason:

The package README identifies it as generated but does not provide a reproducible
rebuild command. Source files remain authoritative until a release process is
documented and verified.

## D-012: Keep the bounded Agent loop provisional

Decision:

Implement one deterministic bounded Evidence Investigator behind the same
comparison interface as the strong one-shot prompt and fixed
extract-search-validate workflow. Do not select the Agent loop as the final
architecture before comparative evidence exists.

Reason:

Adaptive control may help choose when to narrow, ask, continue, or stop as
evidence changes. The current Day 1 branches are also expressible as a fixed
workflow. Retain the loop only if labeled comparison shows better evidence
boundaries or recovery at acceptable safety, cost, latency, and trace clarity;
replace it with the fixed workflow if those benefits do not materialize.

## D-013: One vocabulary, one governance note, testable consistency

Decision:

- `Project2Job` is the canonical product and repository name. `Career Desk` is a
  legacy internal codename kept only in clearly historical records and already
  published paths such as `skill/career-desk/`.
- Change history stays in Git, pull requests, Work Orders, and
  `docs/13_DECISION_LOG.md`. Do not add `baseline/`, `increments/`, or `review/`
  folders that duplicate them.
- Add exactly two supporting files: `GLOSSARY.md` for vocabulary and
  `docs/DOCUMENT_GOVERNANCE.md` for which document owns which question. Neither
  becomes an active product document.
- Documentation consistency is enforced by tests
  (`tests/test_document_consistency.py`), not by review habit, and the Day
  journal gate is a general prefix rule rather than a per-Day constant.
- Diagrams are added only when a process, state machine, or sequence is
  materially clearer than prose. Traces and tests remain the stronger evidence.

Reason:

The drift found before this change was two names for one product, a Day 0-only
status after Day 1 shipped, output counts that contradicted the schema, and a
validator that needed editing for every new Day. Naming and ownership rules
prevent the first three; a general rule and a test suite prevent them from
returning silently.
