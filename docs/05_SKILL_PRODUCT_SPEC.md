# Skill Product Specification

## Product role

The Project2Job Skill is the lowest-friction product entry and open-source distribution surface.

It performs a one-session JD-to-Application transformation inside the user's existing Agent host.

## User contract

The user supplies one target JD, and optionally a resume. The Skill returns an
`Intake Result`: Role Demand Map, company and track signals, resume project
candidates, one recommended project with reasons and risks, claims requiring
verification, a Required Evidence Checklist, and One Next Input.

The user then supplies the selected project's evidence. The Skill returns an
`Application and Interview Pack`:

- Role Fit Map
- Project Highlights
- tailored Resume Bullets
- Interview Pack, including the company and track brief, loop hypothesis,
  5–8 prioritized questions, three grounded answer drafts, questions to ask the
  interviewer, and one mock-interview round specification
- One Next Build
- source-backed uncertainty

The Skill works from pasted text and uploaded files. It does not search for jobs
and does not log into any job platform.

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
4. extract the JD into a `JdIntake`: company, team, role family, track, level,
   location, requirements, likely interview risks, unknowns
5. extract the top 5–7 role requirements as the Role Demand Map
6. read the optional resume and extract project candidates for routing only
7. recommend one project, then return the `Intake Result` and stop for input
8. extract project claims from the selected project
9. verify high-value claims against sources
10. produce the Application and Interview Pack
11. ask for correction
12. stop

Step 7 is a real stopping point, not a pause. The Intake Result must stand on its
own if the user never supplies a project.

## Progressive loading

`SKILL.md` remains short.

Load:

- role standard only when role analysis is needed
- evidence rubric for claim verification
- routing reference only when a resume with several projects is present
- resume reference only for bullet generation
- interview reference only for interview output
- token policy only when project size exceeds the default threshold

## Host fallbacks

- no file tools: accept pasted text
- no web: use the bundled role standard and the pasted JD; a user-supplied URL is
  an optional convenience, never a requirement
- no screenshot reading: ask for the JD as pasted text
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
