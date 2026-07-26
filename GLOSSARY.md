# Glossary

Canonical vocabulary for this repository. This file defines words only. It does
not define scope, permissions, or evidence policy; each term points at the file
that owns the rule.

## Product and program

| Term | Definition | Not to be confused with | Canonical source |
| --- | --- | --- | --- |
| **Project2Job** | The canonical product and repository name. Use it in all new and revised text. | `Career Desk`. | `README.md` |
| **Career Desk** | A legacy internal codename for the same product. Do not introduce it in new text. Several v6-era product documents and the published path `skill/career-desk/` still carry it; those are renamed as each file is next revised, not in one sweep. | The current product name. | `docs/13_DECISION_LOG.md` (D-013) |
| **Skill** | The session-scoped, open-source entry point that runs inside the user's Agent host and holds no product state. | The Agent. A Skill does not persist evidence or run update cycles. | `docs/05_SKILL_PRODUCT_SPEC.md` |
| **Agent** | The stateful product that maintains user-confirmed evidence, applies corrections, and regenerates affected outputs after a project changes. | The Skill, and the Day 1 loop slice. | `docs/06_AGENT_PRODUCT_SPEC.md` |
| **Evidence Investigator** | The bounded loop that turns one claim into an evidence status through Action → Observation → State Update → Continue / Adjust / Ask / Stop. Currently implemented with deterministic scripted read-only tools. | A production model-powered Agent runtime. | `src/career_desk/runtime.py`, `docs/build_journal/DAY_1.md` |
| **Work Order** | The engineering dependency and acceptance unit (`work_orders/`). Defines the context set, deliverables, and acceptance criteria for a slice of implementation. A Work Order is **complete** when every one of its acceptance criteria is implemented and tested; complete does not mean Validated. | A Public Day. Work Orders order engineering; Days order the public narrative. | `PROJECT_MANIFEST.json` |
| **Public Day** | One entry in `docs/build_journal/` describing the public build narrative and its measured evidence. | A Work Order or a release milestone. | `docs/build_journal/README.md` |

## Output vocabulary

| Term | Definition | Not to be confused with | Canonical source |
| --- | --- | --- | --- |
| **Application Pack** | The complete output object: Role Fit Map, Project Highlights, Resume Bullets, Interview Prep Pack, One Next Build, correction prompt, warnings. | A resume, or the Role Fit Map alone. | `schemas/application_pack.schema.json` |
| **Role Fit Map** | Five to seven role capability areas, each with relevance, evidence status, source references, evidence boundary, and interview risk. | A score, a ranking, or a gap list. | `docs/01_MVP_PRD.md` |
| **One Next Build** | Exactly one prioritized next project action derived from the largest evidence gap. | A roadmap or a backlog. | `ACTIVE_SCOPE.md` |

## Evidence vocabulary

`lab/REVIEWER_AND_ANNOTATION_GUIDE.md` is the canonical labeling and
resume-export policy. The definitions below are naming only.

| Term | Definition | Not to be confused with | Canonical source |
| --- | --- | --- | --- |
| **Evidence Status** | The label attached to a claim after investigation. Exactly six values: Supported, Partially Supported, Inferred, Not Found, Conflicting, Needs Confirmation. | A confidence score or a quality rating. | `lab/REVIEWER_AND_ANNOTATION_GUIDE.md` |
| **Supported** | Direct source evidence establishes the claim as written. | Partially Supported. | `lab/REVIEWER_AND_ANNOTATION_GUIDE.md` |
| **Partially Supported** | Source evidence establishes a narrower claim than the one asserted. | Supported, or Inferred. | `lab/REVIEWER_AND_ANNOTATION_GUIDE.md` |
| **Inferred** | A reasonable reading of the sources, without a direct statement. | Source fact. | `lab/REVIEWER_AND_ANNOTATION_GUIDE.md` |
| **Not Found** | The permitted sources were searched and contain no evidence for the claim. | Disproven. Missing material does not prove missing capability. | `lab/REVIEWER_AND_ANNOTATION_GUIDE.md` |
| **Conflicting** | Permitted sources disagree and the conflict was not resolved. | Not Found. | `lab/REVIEWER_AND_ANNOTATION_GUIDE.md` |
| **Needs Confirmation** | Only the user can settle the claim, typically ownership or role. | Inferred. The system must ask rather than guess. | `docs/11_SAFETY_PRIVACY_AND_HITL.md` |
| **Evidence Boundary** | The explicit statement of what the evidence does and does not establish. | A caveat or a disclaimer sentence. | `lab/REVIEWER_AND_ANNOTATION_GUIDE.md` |
| **Source Reference** | A `source_id` plus an exact `location` within that source. | A file name, a URL, or a quotation without a location. | `references/source_registry.json` |

## Acceptance vocabulary

| Term | Definition | Not to be confused with | Canonical source |
| --- | --- | --- | --- |
| **Acceptance Criterion** (AC) | One testable statement that a slice must satisfy before it is accepted. Day 1 ACs use the `D1-AC-nn` form. | An eval case. One AC may be covered by several cases and tests. | `docs/build_journal/DAY_1.md`, `work_orders/` |
| **Eval Case** | One labeled input/expected-behavior record in `lab/evals/`, identified by a stable case ID such as `D1-001`. | A unit test. Cases are data; tests are code. | `lab/evals/` |
| **Unit Test** | Executable code under `tests/` that asserts one behavior of the implementation. | An eval case, or a measure of product value. | `tests/` |
| **Planned** | Specified but not implemented. No runtime behavior exists. | Implemented. | `PROJECT_STATUS.md` |
| **Implemented** | Runtime behavior exists in `src/` and runs. | Tested or Validated. | `PROJECT_STATUS.md` |
| **Tested** | Implemented behavior is covered by passing unit tests and eval cases. | Validated. Passing tests say the mechanics hold, not that the output is useful. | `tests/`, `lab/evals/` |
| **Validated** | Measured evidence from labeled data or real users supports a product claim. Which items are Validated is stated in `PROJECT_STATUS.md`, not here. | Tested. | `docs/10_EVALUATION_AND_POC.md` |
