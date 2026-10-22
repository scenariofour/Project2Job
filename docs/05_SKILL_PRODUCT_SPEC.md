# Skill Product Specification

## Product role

The Project2Job Skill is the lowest-friction product entry and open-source
distribution surface.

It is a reusable method that performs a JD-to-Application transformation inside
the user's existing Agent host. With one-time consent, the suite's shared local
Context Registry can reuse bounded Project/company/JD/run state across sessions.

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

Between those two steps the Skill runs one bounded public-web research pass for
company and interview context. It does not search for jobs and does not log into
any platform. Where the host has no web or no browser, the Skill degrades to
user-supplied material and says so.

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
- persistent state when consent or local storage is unavailable
- consistent token telemetry
- background update tracking or change-driven regeneration
- centralized product analytics

## Execution sequence

1. resolve Project/JD identity and compatible local context
2. inventory only new or changed artifacts
3. resolve the three profile states and route the requested asset
4. load only relevant references
5. extract the JD into a `JdIntake`: company, team, role family, track, level,
   location, requirements, likely interview risks, unknowns
6. extract the top 5–7 role requirements as the Role Demand Map
7. reuse fresh company intelligence or run one bounded public-web research pass,
   merging anything the user pasted or uploaded
8. read the optional resume and extract project candidates for routing only
9. recommend one project, then return the `Intake Result` and stop for input
10. reuse the Project Evidence Profile or extract and verify high-value claims
11. generate only the requested asset
12. when the user explicitly requests Full Preparation, produce the complete
    Application and Interview Pack
13. after consent, save only the minimal compatible context
14. ask for correction
15. stop

Step 9 is a real stopping point, not a pause. The Intake Result must stand on its
own if the user never supplies a project.

JD plus Project without a narrower request reuses fresh Company Intelligence or
runs one bounded Intel prerequisite, then returns a concise strategic Brief with
one strongest positioning and one recommended next Skill. It does not
automatically run Brief, Audit, Answer, Mock, and Upgrade.

## Reusable profiles

- **Project Evidence Profile:** deep, source-linked facts, ownership, decisions,
  architecture, results, bad cases, stories, and hiring signals. Build once per
  Project version and update only affected sections.
- **Company Intelligence Profile:** `$p2j-intel` output keyed by exact normalized
  company and track string, including culture, values, product/AI direction,
  role/team priorities, interview signals, sources, and freshness.
- **JD Demand Map:** lightweight per-JD role tasks, stated level, hiring signals,
  must-haves, and preferred qualifications, bound to the resolved Company
  profile key.

## Progressive loading

`SKILL.md` remains short.

Load:

- role standard only when role analysis is needed
- evidence rubric for claim verification
- Context Registry resolver before every run; continue without saving when local
  reuse is unavailable or declined
- profile contract before source retrieval; build only missing or stale profiles
- routing reference only when a resume with several projects is present
- resume reference only for bullet generation
- interview reference only for interview output
- token policy only when project size exceeds the default threshold

## Host fallbacks

- no file tools: accept pasted text
- no web search: set research mode to `unavailable`, use the bundled role
  standard and the pasted JD, and state that company context is user-supplied only
- no browser: keep `read_only_fetch`, record pages needing rendering as
  `render_required`, and list them as gaps rather than guessing their content
- no screenshot reading: ask for the JD as pasted text
- no code execution: create a manual inventory
- no persistent storage or no consent: continue without saving and state the
  session limitation
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
