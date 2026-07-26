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

### Resume bullets

May contain only:

- Supported facts
- user-confirmed facts
- explicitly labeled current-state limitations when useful

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
- likely follow-up questions
- explicit missing evidence

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

The claim-safety review is a gate, not a note. A draft that exceeds its evidence
is narrowed or dropped before the pack is emitted.

### Company emphasis

Company and track signals may change:

- which verified facts an answer leads with
- the order and wording of those facts
- which follow-ups are anticipated

They may never change:

- the fact set behind the answer
- any metric, scope, date, or ownership statement
- the evidence boundary

Two runs of the same question against the same project must resolve to the same
fact IDs regardless of company emphasis.

### Interview questions

An interview question inherits the strength of its source, never more:

- one reported experience is presented as reported once, never as expected
- a stale report is never presented as likely
- conflicting reports are shown together with the disagreement stated
- an unknown remains unknown; it is not inferred from the company name

### One Next Build

Must include:

- gap
- why now
- steps
- acceptance criteria
- expected new evidence
- output dependency
- estimated effort band

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
