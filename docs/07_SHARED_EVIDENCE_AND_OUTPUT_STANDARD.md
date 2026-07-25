# Shared Evidence and Output Standard

The Skill and Agent must use the same definitions.

## Claim types

- role requirement
- project fact
- candidate ownership
- capability claim
- outcome claim
- career output claim

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
