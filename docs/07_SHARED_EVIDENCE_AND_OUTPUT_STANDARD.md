# Shared Evidence and Output Standard

The Skill and Agent must use the same definitions.

## Two separate evidence systems

The product carries two kinds of material and must never merge them.

**Project evidence** is what the user's own project sources establish. It uses the
claim types, evidence types, and statuses below, and it is the only material that
may reach a resume bullet or an answer draft's verified evidence.

**Interview research** is what is known about the company, track, and reported
interview experience. It uses the separate source-status scale in
`schemas/interview_context.schema.json` — `official`, `repeatedly_reported`,
`single_report`, `inferred_from_jd`, `unknown` — plus source date and freshness.

Research may decide which verified facts an answer leads with. It may never
become a fact, and no research item is ever labeled Supported.

## Claim types

- role requirement
- project fact
- candidate ownership
- capability claim
- outcome claim
- career output claim
- resume-reported project summary — self-reported until that project's sources are
  read; usable for routing only

## Evidence types

### Direct

The source explicitly establishes the claim.

Examples:

- test result
- code or configuration
- signed-off PRD
- user interview note
- trace
- user-confirmed ownership

### Supporting

The source increases confidence but does not fully establish the claim.

### Self-reported

User statement without independent project artifact.

### Contradictory

Source conflicts with the claim.

### Not found

The permitted material was searched and no supporting source was found.

## Status definitions

### Supported

Direct evidence is sufficient for the bounded claim.

### Partially Supported

Evidence supports part of the claim or a narrower version.

### Inferred

The claim is plausible but not directly established.

### Not Found

No support found in permitted sources.

### Conflicting

Sources disagree.

### Needs Confirmation

A user fact or ownership boundary requires confirmation.

## Evidence path

Every important result stores:

```text
role_requirement_id
→ project_claim_id
→ evidence_id
→ source_id
→ source_location
→ status
→ boundary
→ user_confirmation
```

## Career output policy

### Career-asset packaging

Canonical objective:

> Maximize hiring impact through the strongest defensible interpretation of the
> candidate's facts, decisions, and transferable implications.

Truthful does not mean self-disqualifying. Facts are bounded. Interpretation is
expandable. Framing is strategic.

Apply these distinctions to every copyable resume bullet, introduction, and
interview answer:

1. **Historical fact boundary.** Events, ownership, users, stakeholder
   relationships, metrics, experiments, production status, and outcomes must
   not exceed Supported or user-confirmed facts.
2. **Defensible interpretation.** Synthesize linked facts into capabilities,
   product judgment, causal mechanisms, learning, transferable skills, and
   role relevance when the reasoning chain is defensible and creates no new
   historical event. The capability wording does not need to appear verbatim
   in a source; cite the facts that support the interpretation.
3. **Strategic framing.** Select, reorder, compress, and emphasize the strongest
   role-relevant subset of verified facts. A career asset does not need to
   repeat every known limitation or every fact in the evidence record.
4. **Private risk separation.** Keep unsupported claims, missing validation,
   follow-up risks, and material limitations in `warnings`,
   `unsupported_areas`, `claim_safety_review`, or follow-up defense by default.
   These fields are private preparation material, not sentences to append
   automatically to the copyable asset.
5. **Material disclosure.** Include a limitation in the external asset only
   when the question explicitly asks for it or omission would make the answer
   false or materially misleading. Never hide a boundary that changes what an
   asserted fact means.
6. **Failure stories.** Describe the relevant failure, lead with the
   product/user problem, and end on containment, product change, result,
   judgment, repeat-prevention, or role-relevant capability. Do not end on an
   unrelated disclaimer or unfinished-work list.
7. **Company relevance.** Use the JD to select the strongest story,
   capability, terminology, and emphasis. Do not append a company name or copy
   JD keywords into the conclusion. Company context cannot create or
   strengthen a project fact.
8. **Spoken quality.** Keep answers concise and conversational, with short
   sentences. Frameworks stay internal. Avoid report-style labels, dense
   abstractions, and unnecessary disclaimer sentences.

### Resume bullets

May contain only:

- Supported facts
- user-confirmed facts
- defensible interpretations grounded in linked Supported or user-confirmed
  facts
- current-state limitations only when material disclosure requires them

Must not contain:

- invented metrics
- inferred ownership
- planned work as completed work
- model-estimated outcomes
- unsupported causality

### Interview output

May include:

- supported answer ingredients
- partial areas
- defensible capability and role-relevance interpretations grounded in the
  verified evidence
- likely follow-up questions
- private missing-evidence and risk review

Must not fabricate a polished answer that the project cannot support.

Every answer draft preserves:

```text
question
→ verified evidence
→ answer ingredients
→ grounded draft
→ claim-safety review
→ likely follow-ups
```

The claim-safety review is a private gate, not copy for the answer. A draft that
exceeds its evidence is narrowed or dropped before the pack is emitted; the
rejected wording and remaining risk stay outside the copyable draft.

### Company emphasis

Company and track signals may change:

- which relevant subset of verified facts is selected
- which verified facts an answer leads with
- the order and wording of those facts
- which follow-ups are anticipated

They may never change:

- the verified project-fact pool
- any metric, scope, date, or ownership statement
- a selected fact's evidence boundary
- whether omitting a material limitation would make the answer misleading

Selected fact IDs may differ by question, company, or role emphasis. Every
selected fact ID must resolve to the same verified project-fact pool, and
company research may never supply a missing project fact.

### Interview questions

An interview question inherits the strength of its source, never more:

- one reported experience is presented as reported once, never as expected
- a stale report is never presented as likely
- conflicting reports are shown together with the disagreement stated
- an unknown remains unknown; it is not inferred from the company name

### One Next Build

Must include:

- gap
- why the current Project evidence does not fully satisfy the target JD
- relevant hiring capability category
- exactly one evidence direction
- product and safety boundaries
- bounded handoff steps and evidence acceptance criteria
- expected new evidence for reassessment
- output dependency
- estimated effort band

Project2Job defines the diagnosis and evidence direction. Concrete
implementation subclasses and evaluation mechanics come from downstream
inspection of the Project. Proposed work keeps the current Match; only completed
and sufficient evidence may change it.

## User corrections

A correction must:

- preserve the previous value
- record who changed it
- identify dependent outputs
- invalidate or regenerate affected outputs
- become an eval candidate when it reveals system failure

## Saved context

The Context Registry may reuse a source-linked fact or ownership boundary after
consent, but it is not independent evidence. Current source evidence remains
authoritative. A changed or removed source invalidates every dependent saved
claim or output; unaffected confirmed facts may survive into the new Project
version. A changed JD invalidates role matching and route, not unchanged Project
evidence.
