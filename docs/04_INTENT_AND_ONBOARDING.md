# Intent and Onboarding

## Design goal

The user should be able to drop what they have and receive a useful bounded result without learning product modes.

## Primary intents

Primary intents represent the next supported run, so they are mutually exclusive inside MVP scope.

### APPLICATION_PACK

Detected when:

- a project is present
- a target role or JD is present

Outcome:

- full MVP Application Pack

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

- no usable project material
- request is only for job discovery or auto-apply
- multiple projects without a selected target
- unsupported role family
- intent remains ambiguous after bounded inference

## Modifiers

Modifiers change emphasis without creating new flows:

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

## Routing evaluation

Test:

- trigger cases
- non-trigger cases
- multilingual and mixed-language requests
- indirect phrasing
- incomplete inputs
- multiple intents
- unsupported requests
- prompt injection in documents
