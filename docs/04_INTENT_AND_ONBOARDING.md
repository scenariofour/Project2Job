# Intent and Onboarding

## Design goal

The user should be able to drop what they have and receive a useful bounded result without learning product modes.

## Primary intents

Primary intents represent the next supported run, so they are mutually exclusive inside MVP scope.

### JD_INTAKE

Detected when:

- a target JD is present
- no selected project corpus is present yet

Outcome:

- `Intake Result`: Role Demand Map, company and track signals, resume project candidates when a resume was supplied, one recommended project with reasons and risks, claims requiring verification, Required Evidence Checklist, One Next Input

This is the normal entry point. It must produce value with a JD alone.

### APPLICATION_PACK

Detected when:

- a target JD is present
- one selected project corpus is present

Outcome:

- full `Application and Interview Pack`

### PROJECT_COMPASS

Detected when:

- a project is present
- no target JD is present

Outcome:

- preview against the default AI PM Role Standard
- request a JD only as a capability unlock

### UPDATE

Detected when:

- an existing project profile is present
- new or changed project evidence is supplied

Outcome:

- delta analysis
- affected output update

### OUT_OF_SCOPE_OR_UNCLEAR

Examples:

- no usable JD and no usable project material
- request is only for job discovery, bulk scraping, or auto-apply
- a request to analyze several projects in depth in one run
- unsupported role family
- intent remains ambiguous after bounded inference

## Modifiers

Modifiers change emphasis without creating new flows:

- company_emphasis
- resume_focus
- interview_focus
- build_focus
- ownership_unclear
- urgent_application
- incomplete_artifacts

## Routing order

1. deterministic artifact and permission checks
2. explicit user goal
3. supported intent model
4. policy validation
5. bounded default or one clarification

## Question economy

Before first useful result:

- ask zero questions when safe
- ask one blocking question when ownership or target is essential
- show non-blocking missing information as optional unlocks

## Low-confidence behavior

- safe default exists: run a bounded preview
- material conflict affects a major claim: ask one clarification
- request is unsupported: explain the boundary and stop

## Onboarding response

Immediately show:

- what artifacts were detected
- what the system can do now
- which mode will run
- what optional input would unlock
- whether a user confirmation is required

In `JD_INTAKE` the onboarding response is the Intake Result itself. The single
next input is named explicitly: which project to investigate, or that project's
evidence.

## Routing evaluation

Test:

- trigger cases
- non-trigger cases
- multilingual and mixed-language requests
- indirect phrasing
- incomplete inputs
- multiple intents
- unsupported requests
- prompt injection in documents, resumes, JDs, and pasted interview reports
- a JD with no stated team, level, or track
- a resume with several projects, and a resume with none
