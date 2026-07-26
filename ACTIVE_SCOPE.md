---
release: MVP-0
status: locked
updated: 2026-07-25
---

# Active Scope

## Target user

A person preparing to apply within 30 days for an early-career AI PM, Agent PM, or Applied AI Product role who has at least one AI project and is unsure how the project should support the application.

## Primary trigger

The user has one target JD and needs to decide which project to put forward, then turn that project into useful application and interview evidence for that specific company and track.

## MVP flow

The run is progressive. The first four steps produce value before any project corpus exists.

1. Accept one JD as pasted text, a user-supplied URL, a screenshot, or an uploaded file.
2. Extract company, team or product area when stated, role family and track, level, location, core requirements, and likely interview risks. Anything the JD does not state is recorded as unknown, not guessed.
3. Run one bounded public-web research pass for official interview signals,
   track/team/level expectations, reported interview processes, and reported
   questions. Merge anything the user pasted or uploaded. See "Bounded research".
4. Optionally read one resume.
5. Extract multiple project summaries from the resume **for routing only**. These are self-reported claims, not evidence.
6. Recommend one project for deep evidence analysis using role relevance, likely evidence availability, ownership clarity, outcome strength, and interview depth. Return the `Intake Result` here.
7. Ask for that project's repository, files, PRD, evals, and feedback.
8. Run the existing one-project evidence investigation.
9. Produce the role- and company-specific `Application and Interview Pack`.

Several resume projects may be considered at step 6. Exactly one project may enter step 8.

## Bounded research

Research is automatic, bounded, and source-agnostic. No platform is named or
special-cased; pages are prioritized by tier — official, then independent report,
then aggregator or forum.

The tool path:

```text
public web search
→ prioritize and deduplicate candidate pages
→ read-only fetch
→ Playwright fetch only for a selected public page that needs rendering,
  one navigation step, or structure a plain fetch cannot give
→ structured extraction
→ gap check
→ adjust queries and continue only while a named gap is open
→ stop
```

Stop on the first of: sufficient evidence, exhausted public evidence, budget
exhaustion, inaccessible sources, a conflict that must be disclosed, or tool
failure. The stop reason is recorded and shown.

Ceilings for queries, pages, Playwright pages, navigation depth, characters per
page, tokens, retries, and runtime are in `docs/09_TOKEN_CONTEXT_AND_COST.md` and
encoded in `schemas/interview_context.schema.json`.

Never log in, supply a credential, bypass a paywall or CAPTCHA, crawl a domain,
enumerate listings, or follow arbitrary links. Fetched page text is untrusted
data and cannot direct the run. `docs/11_SAFETY_PRIVACY_AND_HITL.md` is canonical.

Thin public evidence yields a thin, honest brief and named gaps. It never
licenses inference presented as reporting.

## Interview context layers

Company and interview material is research, never project evidence. Three explicit layers, and no personality-based "culture fit":

- Company Interview Signals
- Track, team, and level-specific requirements
- Reported Interview Evidence

Every item is labeled `official`, `repeatedly_reported`, `single_report`, `inferred_from_jd`, or `unknown`, and stores source date, source reference, company, track, level, location, interview stage, and freshness where available. A web-retrieved item also stores its exact page URL, how it was fetched, and when. One reported question is never presented as a guaranteed company question.

## MVP input

Required:

- one target JD

Required before deep analysis:

- one selected project corpus

Optional:

- resume
- pasted or uploaded interview reports and company material, which supplement
  rather than replace the automatic research pass
- ownership clarification
- time constraint

## Intake Result

Produced before project evidence is supplied:

1. Role Demand Map
2. Company and Track Signals
3. Resume Project Candidates
4. Recommended Project
5. recommendation reasons and risks
6. claims requiring verification
7. Required Evidence Checklist
8. One Next Input

`schemas/intake_result.schema.json` is the contract.

## Application and Interview Pack

Project Highlight and resume bullet counts are evidence-dependent targets, not
quotas. Return fewer or none when the permitted evidence cannot support the
target. Never fill an output quota with unsupported claims. The Role Fit Map is
the exception: it always covers 5–7 capability areas, and an area with no
evidence is reported with its evidence status rather than omitted.

1. Role Fit Map covering 5–7 relevant capability areas
2. up to 3–5 supported Project Highlights
3. up to 2–3 tailored, grounded resume bullets
4. 30-second project introduction
5. company and track brief
6. interview-loop hypothesis, each stage carrying its source status
7. 5–8 prioritized P0/P1 questions
8. three grounded answer drafts
9. likely follow-up questions for each draft
10. unsupported or unconfirmed claims
11. one mock-interview round specification
12. questions to ask the interviewer
13. One Next Build
14. user correction prompt

`schemas/application_pack.schema.json` (Application and Interview Pack 2.0.0) is
the contract.

Each answer draft preserves the chain:

```text
question
→ verified evidence
→ answer ingredients
→ grounded draft
→ claim-safety review
→ likely follow-ups
```

Company signals may change which facts an answer leads with and how it is worded.
They may never change the underlying facts, add a fact, or drop a boundary.

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

## Skill Context Registry

The Skill suite may retain minimal local Project, JD, and Analysis Run context
after one-time user consent. This registry recognizes unchanged inputs, reuses
confirmed facts and ownership boundaries, and invalidates saved results when
their source artifacts change. It stores fingerprints and bounded derived state,
not complete project or JD bodies.

The registry is not the Agent: it does not monitor files, run in the background,
choose work autonomously, or regenerate outputs after a change. Users can
refresh, analyze from scratch, run without saving, or forget selected context.
The scope remains one Project, one JD, and their analysis history.

## Role family

P0 uses one versioned role standard:

- Junior AI Product Manager
- Junior Agent Product Manager
- Applied AI Product Manager

A specific JD may override or reweight the standard.

## Primary intents

- `JD_INTAKE`: JD present, selected project not yet supplied — returns the Intake Result
- `APPLICATION_PACK`: JD plus one selected project with evidence
- `PROJECT_COMPASS`: project only, no JD, using the default AI PM role standard
- `UPDATE`: previously analyzed project changed
- `OUT_OF_SCOPE_OR_UNCLEAR`

Resume focus, interview focus, and build focus are modifiers, not separate primary intents.

## MVP boundaries

One JD, one company, one track or team context, one optional resume, one selected
project for deep analysis, one Application and Interview Pack, 5–8 priority
questions, three answer drafts, one mock-interview round.

Still excluded:

- job discovery and bulk job scraping
- automatic login to any job platform or professional network
- auto-apply
- application tracking
- email monitoring
- referral automation
- multiple deep project analyses
- any cross-Project or cross-user company question database; persisted research
  reuse is limited to the selected JD and its freshness rules
- broad MCP integrations

Bounded automatic public-web research is in scope and required. Job discovery,
bulk scraping, and platform accounts are not: the difference is that research
answers named gaps about one company for one JD, within fixed ceilings, and stops.

## Success targets

These are targets, not achieved results:

- first useful output — the Intake Result — within 5 minutes of pasting one JD
- the recommended project matches the project a reviewer would pick
- 0–1 questions before first value
- no severe fabricated external-facing claims
- key source precision at least 90% in the labeled set
- blind reviewers prefer the Skill over a strong generic prompt
- stateful update uses fewer repeated reads and questions than a fresh Skill run
- at least one generated asset is judged usable after minor editing

## Explicit exclusions

See root `AGENTS.md`.
