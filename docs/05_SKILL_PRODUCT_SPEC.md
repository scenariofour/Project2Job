# Skill Product Specification

## Product role

The Career Desk Skill is the lowest-friction product entry and open-source distribution surface.

It performs a one-session Project-to-Application transformation inside the user's existing Agent host.

## User contract

The user supplies:

- one project
- one role profile or JD

The Skill returns:

- Role Fit Map
- Project Highlights
- Resume Bullets
- Interview Prep Pack
- One Next Build
- source-backed uncertainty

## Why the Skill exists

- no account creation
- local project access
- host model already available
- easy open-source distribution
- first-run value
- strong test surface for Skill design
- user can inspect and modify the method

## Why it is more than a prompt

The Skill package includes:

- versioned role standard
- evidence rubric
- execution sequence
- deterministic inventory script
- output schema
- source rules
- trigger and behavior evals
- examples
- bounded stop conditions

The Skill must still be compared with a strong generic prompt. If it creates no meaningful advantage, it should be reduced or removed.

## Runtime limitations

The Skill cannot guarantee:

- identical models across hosts
- identical tool availability
- persistent state
- consistent token telemetry
- update tracking across sessions
- centralized product analytics

## Execution sequence

1. inspect artifacts with the inventory script
2. route the request
3. load only relevant references
4. extract the top 5–7 role requirements
5. extract project claims
6. verify high-value claims against sources
7. produce the Application Pack
8. ask for correction
9. stop

## Progressive loading

`SKILL.md` remains short.

Load:

- role standard only when role analysis is needed
- evidence rubric for claim verification
- resume reference only for bullet generation
- interview reference only for interview output
- token policy only when project size exceeds the default threshold

## Host fallbacks

- no file tools: accept pasted text
- no web: use bundled role standard or pasted JD
- no code execution: create a manual inventory
- no persistent storage: state the session limitation
- no reliable source location: mark provenance as coarse

## Skill effectiveness

Must pass:

- trigger precision and recall
- behavior adherence
- output schema validation
- source correctness
- unsupported claim checks
- generic-prompt comparison
- cross-host consistency on critical conclusions
