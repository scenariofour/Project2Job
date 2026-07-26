# Document Governance

How this repository keeps documents, schemas, and code from disagreeing. This
is not a PRD and defines no product behavior.

## Canonical responsibilities

One question, one owner. If two files answer the same question, the owner wins
and the other file links to it.

| File or system | Owns |
| --- | --- |
| `ACTIVE_SCOPE.md` | current product scope and explicit exclusions |
| `schemas/` | machine-enforced contracts |
| `PROJECT_STATUS.md` | current implementation truth |
| `work_orders/` | engineering dependencies and acceptance criteria |
| `docs/build_journal/` | public Day narrative and measured evidence |
| `docs/13_DECISION_LOG.md` | approved product and architecture decisions |
| `GLOSSARY.md` | canonical vocabulary |
| `docs/11_SAFETY_PRIVACY_AND_HITL.md` | permissions, data boundaries, human control |
| `lab/REVIEWER_AND_ANNOTATION_GUIDE.md` | evidence labeling and resume-export policy |
| Git commits and pull requests | incremental change history |

## Change rule

There are no `baseline/`, `increments/`, or `review/` folders. Git history is
the increment record.

A meaningful product-contract change must update every affected item:

- the canonical document that owns the question
- the schema, when the contract is machine-enforced
- the acceptance criterion or eval case that proves the new behavior
- `docs/13_DECISION_LOG.md`, when the decision itself changed
- `PROJECT_STATUS.md` or the Day journal, when implementation truth changed

A change that touches only wording needs none of the above.

## Review checklist

Before merging a documentation or contract change, check for:

- scope creep and missing explicit exclusions
- terminology inconsistent with `GLOSSARY.md`
- permission, visibility, or data-scope conflicts
- source and metric definitions that disagree between files
- dependency assumptions that no Work Order guarantees
- unhandled empty, timeout, corrupt, unauthorized, and conflicting states
- acceptance criteria that a later decision has overridden
- schema and prose disagreement
- status, document, and code disagreement
- implementation or user-value claims that no test or measurement supports

`make validate` and `make test` enforce the mechanical parts of this list.
Everything else is a human read.

## Diagram rule

- Use Mermaid only when a process, state machine, or sequence is materially
  clearer than the prose it replaces.
- Use ASCII wireframes only while implementing a UI surface.
- Do not add diagrams for decoration.
- Executable traces and tests remain stronger evidence than any diagram.
