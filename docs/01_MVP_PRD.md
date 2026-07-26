# MVP PRD

## Target user

A person applying within 30 days for a Junior AI PM, Agent PM, or Applied AI Product role who has at least one AI project and lacks confidence about how the project should support the application.

## Trigger

The user has one target JD and one or more projects that may be relevant, and does not know which project to put forward or how far it can be defended.

## Core user task

Choose the right project for this JD, then transform it into a company- and track-specific Application and Interview Pack without overstating what the project proves.

## Inputs

Required to start:

- one target JD as pasted text, a user-supplied URL, a screenshot, or an uploaded file

Required before deep analysis:

- one selected project corpus

Optional:

- resume, read only to route between candidate projects
- pasted or uploaded company material and interview reports
- ownership clarification
- project time constraint

## Progressive flow

`ACTIVE_SCOPE.md` owns the eight-step flow. In PRD terms the run has two output points: an `Intake Result` as soon as the JD is understood, and an `Application and Interview Pack` once one selected project's evidence is verified. The user must get real value at the first point without supplying a project.

Resume projects are extracted for routing only. Their summaries are self-reported claims and carry no evidence status until that project's own sources are read. Exactly one project may enter deep analysis.

Accepted project inputs may include:

- local folder
- repository
- ZIP
- README
- PRD
- architecture notes
- eval results
- user research
- demo notes

## Output contract

Project Highlight and Resume Bullet counts are evidence-dependent targets, not
quotas. Return fewer items or none when the permitted evidence cannot support
the target, and never fill an output quota with unsupported claims.
`schemas/application_pack.schema.json` therefore allows zero Project Highlights
and zero Resume Bullets.

The Role Fit Map is the exception. It always covers 5–7 capability areas, as the
schema requires; an area without evidence is reported with a `not_found` or
`needs_confirmation` status rather than dropped.

### 1. Role Fit Map

For 5–7 role capability areas:

- relevance to the target role
- current project evidence status
- source references
- evidence boundary
- interview risk

### 2. Project Highlights

Up to 3–5 supported project highlights selected for the target role.

### 3. Resume Bullets

Up to 2–3 editable bullets using supported facts only.

Each bullet includes:

- text
- source references
- risk note
- missing information that would strengthen it

### 4. Interview Pack

- 30-second project introduction
- company and track brief, drawn only from labeled interview context
- interview-loop hypothesis, each stage carrying its own source status
- 5–8 prioritized P0/P1 questions
- three grounded answer drafts
- likely follow-up questions for each draft
- questions to ask the interviewer
- one mock-interview round specification
- unsupported or weak areas

Each answer draft preserves `question → verified evidence → answer ingredients → grounded draft → claim-safety review → likely follow-ups`. A draft whose claim-safety review finds it exceeds the evidence must be narrowed or dropped; it may not ship.

Company emphasis may reorder or reword an answer. It may not change the fact set behind it.

### 5. One Next Build

- problem to solve
- why it is highest priority
- concrete steps
- acceptance criteria
- expected new evidence
- interview question it unlocks

### 6. Correction path

The user can correct:

- ownership
- factual errors
- metric meaning
- source interpretation
- evidence status

## Intake Result contract

Returned before any project evidence exists, so the run has value from one JD alone:

- Role Demand Map
- Company and Track Signals
- Resume Project Candidates, each marked self-reported
- Recommended Project, with reasons, risks, and confidence
- claims requiring verification
- Required Evidence Checklist
- One Next Input

When no candidate clearly fits, the recommendation confidence is `no_clear_choice` and the product asks the user to choose. It does not assert a winner.

## Interview context

Three labeled layers — Company Interview Signals, track/team/level requirements, and Reported Interview Evidence — with no personality-based culture fit. Every item carries one of `official`, `repeatedly_reported`, `single_report`, `inferred_from_jd`, `unknown`, plus source date, reference, stage, and freshness where available.

Interview context is gathered by one bounded automatic public-web research pass
plus anything the user supplies. `ACTIVE_SCOPE.md` owns the tool path and stop
conditions, `docs/09_TOKEN_CONTEXT_AND_COST.md` the ceilings, and
`docs/11_SAFETY_PRIVACY_AND_HITL.md` the permissions.

Rules the schema enforces:

- a single reported experience may never be presented more strongly than "reported once"
- a stale report may never be presented as likely
- conflicting reports are shown together, never merged or averaged
- an unknown track is recorded as unknown, never inferred from the company
- a web-retrieved claim cites its exact page, fetch method, and retrieval date
- a Playwright fetch records why a plain fetch was not enough
- a duplicate or login-walled page retains no content
- an automatic pass records its queries, pages, and stop reason

## Skill scope

One session, one JD, one company, one track, one optional resume, one selected project, one Application and Interview Pack.

## Agent scope

The same initial analysis plus one update cycle after the project changes.

## Thin Web scope

The Web surface supports:

- drop or paste inputs
- progress and status
- result review
- source expansion
- correction
- update comparison

## Functional acceptance

- An Intake Result is produced from one JD alone, with no resume and no project.
- First result before any non-blocking questionnaire.
- No more than one question before first value.
- Exactly one project enters deep evidence analysis.
- Every external-facing claim has a source or unsupported status.
- Interview research and verified project evidence are never merged.
- The research pass stays inside its ceilings and always reports a stop reason.
- No research step logs in, bypasses a restriction, or crawls a domain.
- A resume bullet cannot contain an unsupported fact.
- An answer draft cannot exceed the project evidence behind it.
- One Next Build is returned.
- User corrections update affected outputs.
- The Agent update run checks only changed and dependent evidence where possible.

## Non-functional acceptance

- read-only source access
- visible error states
- versioned schemas
- token and tool-call telemetry
- reproducible eval inputs
- no hidden total candidate score
