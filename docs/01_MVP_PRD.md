# MVP PRD

## Target user

A person applying within 30 days for a Junior AI PM, Agent PM, or Applied AI Product role who has at least one AI project and lacks confidence about how the project should support the application.

## Trigger

The user has:

- a target role profile or JD
- one project that may be relevant

## Core user task

Transform the project into a role-aligned Application Pack without overstating what the project proves.

## Inputs

Required:

- one project corpus
- one target role profile or one JD

Optional:

- resume
- ownership clarification
- project time constraint

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

### 4. Interview Prep Pack

- 30-second project introduction
- three likely follow-up questions
- evidence ingredients for each answer
- unsupported or weak areas

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

## Skill scope

One session, one project, one role or JD, one Application Pack.

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

- First result before any non-blocking questionnaire.
- No more than one question before first value.
- Every external-facing claim has a source or unsupported status.
- A resume bullet cannot contain an unsupported fact.
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
