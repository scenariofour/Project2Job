---
release: MVP-0
status: locked
updated: 2026-07-25
---

# Active Scope

## Target user

A person preparing to apply within 30 days for an early-career AI PM, Agent PM, or Applied AI Product role who has at least one AI project and is unsure how the project should support the application.

## Primary trigger

The user has a target role or JD and needs to turn one project into useful application and interview evidence.

## Skill MVP input

Required:

- one project corpus
- one target role profile or one JD

Optional:

- resume
- ownership clarification
- time constraint

## Skill MVP output

Output counts below are evidence-dependent targets, not quotas. Return fewer or
none when the permitted evidence cannot support the target. Never fill an output
quota with unsupported claims.

1. Role Fit Map covering 5–7 relevant capability areas
2. up to 3–5 supported Project Highlights
3. up to 2–3 grounded resume bullets
4. Interview Prep Pack:
   - 30-second project introduction
   - three role-relevant follow-up questions
   - source-backed answer ingredients
   - unsupported areas
5. One Next Build
6. user correction prompt

## Agent MVP extension

The Agent performs the same initial analysis, then supports one update cycle:

```text
project changes or new evidence
→ compare versions
→ recheck affected claims
→ update evidence statuses
→ update affected career outputs
→ explain what changed
```

## Role family

P0 uses one versioned role standard:

- Junior AI Product Manager
- Junior Agent Product Manager
- Applied AI Product Manager

A specific JD may override or reweight the standard.

## Primary intents

- `APPLICATION_PACK`: project + role/JD
- `PROJECT_COMPASS`: project only, using the default AI PM role standard
- `UPDATE`: previously analyzed project changed
- `OUT_OF_SCOPE_OR_UNCLEAR`

Resume focus, interview focus, and build focus are modifiers, not separate primary intents.

## Success targets

These are targets, not achieved results:

- first useful Skill output within 5 minutes
- 0–1 questions before first value
- no severe fabricated external-facing claims
- key source precision at least 90% in the labeled set
- blind reviewers prefer the Skill over a strong generic prompt
- stateful update uses fewer repeated reads and questions than a fresh Skill run
- at least one generated asset is judged usable after minor editing

## Explicit exclusions

See root `AGENTS.md`.
