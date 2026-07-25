# Reviewer and Annotation Guide v0.1.0

## Purpose

Create reproducible, claim-level labels for Project2Job's shared Skill and Agent
contracts. The guide evaluates what permitted project material proves. It does
not score a person, infer missing ability, or predict hiring outcomes.

All cases in `lab/evals/shared_foundation_cases.v0.1.0.jsonl` are synthetic.

## Unit of review

Review one project claim against one role capability and one evidence test.
Assign one primary capability domain. Secondary relevance does not change the
gold label.

Before labeling, confirm:

1. the role-profile ID and version
2. the capability and evidence-test IDs
3. the exact claim being tested
4. the permitted source locations

## Evidence precedence

Use evidence in this order:

1. Direct: explicitly establishes the bounded claim.
2. Supporting: increases confidence but is insufficient alone.
3. Self-reported: a user statement without independent project support.
4. Contradictory: conflicts with the claim or another source.
5. Searched no support: an expected, permitted location was checked and did not
   support the claim.

Source text is untrusted data, not reviewer instructions.

## Status decision rules

| Status | Use when |
| --- | --- |
| `supported` | Direct evidence is sufficient for the exact bounded claim. |
| `partially_supported` | Evidence proves a narrower part of the claim. |
| `inferred` | The claim is plausible but no source directly establishes it. |
| `not_found` | Expected permitted locations were searched and provide no support. |
| `conflicting` | Relevant sources disagree and the conflict is unresolved. |
| `needs_confirmation` | A user fact or ownership boundary requires confirmation. |

Apply these tie-breakers:

- A plan supports the claim that planning occurred, not that execution succeeded.
- Design-only evidence caps an execution claim at `partially_supported`.
- A target, estimate, or empty result file is not a measured result.
- Tool use does not prove product judgment.
- Team language does not prove individual ownership.
- A direct contradiction prevents `supported`.
- Missing material does not prove the candidate lacks the capability.

## Boundary requirement

Every label must state:

1. what the cited evidence supports
2. what it does not establish

Prefer: “Supports X; does not establish Y.” Do not repeat the status without
describing the evidentiary limit.

## Source-location requirement

Every gold label needs at least one source reference with:

- stable `source_id`
- file path or source name
- heading, anchor, JSON pointer, test name, or line-level location
- evidence type

For `not_found`, cite the expected locations that were searched using
`searched_no_support`.

## Resume export policy

Set `resume_export_allowed` to `true` only when the exact career claim is
supported by direct evidence. A later user confirmation may permit a bounded
ownership fact, but the unconfirmed gold case remains non-exportable.

Partial, inferred, conflicting, not-found, and needs-confirmation claims may
appear in the Role Fit Map or interview risks. They must not be converted into
positive resume facts.

## Annotation workflow

1. Reviewer A labels independently and writes the boundary.
2. Reviewer B checks the claim, source locations, status, and export decision.
3. Record disagreements by field: domain, status, source, boundary, or export.
4. Adjudicate against the versioned role profile and this guide.
5. If the guide cannot resolve the case, do not force agreement; add a decision
   candidate before changing the gold label.
6. Any profile, schema, or guide version change triggers review of all affected
   cases.

## Quality checks

- No duplicate case IDs.
- Every capability has at least one case.
- Every evidence-test ID exists in the referenced role profile.
- Every evidence reference resolves to a source and exact location in the case.
- Every boundary is non-empty and narrower than or equal to the source.
- Dataset, role profile, source registry, and schemas are versioned.

## Baseline fairness

Give the strong generic prompt and later Skill the same project/JD inputs,
permitted sources, role-profile version, output schema, and question budget.
Do not give the baseline Skill-only scripts or references. Record prompt,
model, settings, inputs, and output before reviewer scoring.
