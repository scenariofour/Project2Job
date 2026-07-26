# Day 2 — JD-First Product Flow

Status: PLANNED

Day 2 revises product contracts only. No runtime, scraping, Web UI, RAG, or
mock-interview code is implemented, so the status stays `PLANNED`.

## Question

The real workflow starts with a job description, not a project. Which project
should the user even put forward, and how much company context can be used
without inventing facts?

## What changed

The previous promise assumed the user had already picked the right project. That
is the step people actually get wrong. The flow now starts at the JD:

```text
JD-first intake
→ resume project routing
→ one-project selection
→ evidence request
→ company/track interview context
→ bounded MVP
```

The run has two output points. The first needs no project at all.

| Step | Input | Output |
| --- | --- | --- |
| 1–2 | one JD, pasted or uploaded | company, team, role family, track, level, location, requirements, interview risks, unknowns |
| 3–4 | optional resume | several project candidates, all `self_reported`, extracted for routing only |
| 5 | the above | **Intake Result**: Role Demand Map, company and track signals, candidates, one recommended project, reasons, risks, claims to verify, evidence checklist, One Next Input |
| 6–7 | the selected project's repo, files, PRD, evals, feedback | verified project evidence, via the existing Day 1 investigation loop |
| 8 | the above | **Application and Interview Pack** |

Several projects may be considered at step 5. Exactly one may enter step 7.

## Two evidence systems

The main design constraint is that this product now handles material of two
different kinds, and merging them is the failure mode that matters.

Project evidence comes from the user's own sources and carries the six evidence
statuses. Interview research comes from the JD, official company material, and
whatever the user pastes, and carries a separate scale: `official`,
`repeatedly_reported`, `single_report`, `inferred_from_jd`, `unknown`, plus
source date and freshness.

Research can decide which verified facts an answer leads with. It can never
become a fact. Only project evidence reaches a resume bullet or an answer draft's
verified evidence.

There is no personality-based culture fit layer. The three layers are Company
Interview Signals, track/team/level requirements, and Reported Interview
Evidence.

## Acceptance criteria

| AC | Criterion | Eval cases | Contract |
| --- | --- | --- | --- |
| D2-AC-01 | JD intake extracts company, team, role family, track, level, location, requirements, and risks; anything unstated is recorded as unknown | D2-005 | `schemas/jd_intake.schema.json` |
| D2-AC-02 | The run produces a useful Intake Result with no resume and no project | D2-001 | `schemas/intake_result.schema.json` |
| D2-AC-14 | The MVP works end to end from pasted text and uploaded files, with no platform login or scraping | D2-001, D2-002 | `jd_intake` `input_form`, `interview_context` `researchSource` |
| D2-AC-03 | Resume projects are extracted for routing only and stay `self_reported` | D2-002 | `intake_result` `resumeProjectCandidate` |
| D2-AC-04 | Exactly one project is recommended for deep analysis, with reasons, non-empty risks, and a confidence band | D2-002 | `intake_result` `projectRecommendation` |
| D2-AC-05 | When nothing clearly fits, confidence is `no_clear_choice` and the user is asked to choose | D2-003 | `intake_result` `projectRecommendation` |
| D2-AC-06 | Keyword overlap alone cannot win the recommendation over evidence availability | D2-004 | `intake_result` `routingScores` |
| D2-AC-07 | An unknown company track is recorded as unknown, never inferred | D2-005 | `interview_context` `unknowns` |
| D2-AC-08 | Conflicting interview reports are shown together, never merged or averaged | D2-006 | `interview_context` `reportConflict` |
| D2-AC-09 | A stale report is never presented as likely | D2-007 | `interview_context` `interviewQuestion` |
| D2-AC-10 | One reported experience is never presented more strongly than reported once | D2-008 | `interview_context` `interviewQuestion` |
| D2-AC-11 | An answer draft may not exceed its verified evidence | D2-009 | `application_pack` `claimSafetyReview` |
| D2-AC-12 | Company emphasis may change wording and order, never the fact set | D2-010 | `application_pack` `emphasisProfile` |
| D2-AC-13 | The Intake Result names exactly one next input | D2-001 | `intake_result` `one_next_input` |

### What the schemas actually enforce

D2-AC-05, D2-AC-09, D2-AC-10, and D2-AC-11 are enforced by conditional rules, so
a violating object fails validation rather than only failing review. So are two
rules the review surfaced: a question above `inferred_from_jd` must cite a
source, and a `fresh` or `aging` question must have a dated source.

D2-AC-12 is **not** schema-enforceable. Emphasis invariance is a property of two
runs compared against each other, which no single-document schema can express.
`emphasisProfile.fact_ids` is required so the invariant is recorded; eval case
D2-010 is what checks it.

Cross-object ID references — `answer_draft.question_id`, `mock_round.question_ids`,
`claim_safety_review.checked_fact_ids`, `emphasis.fact_ids`, and
`recommendation.candidate_id` — are likewise beyond JSON Schema. The WO-05 output
validator resolves them. The one case the schema can catch, recommending a
project when no candidate exists, is enforced.

## Evidence

Planned. Ten synthetic cases exist in `lab/evals/day2_jd_first_cases.jsonl`;
nothing executes them yet. `tests/test_jd_first_contracts.py` checks the
contracts and the case file, not product behavior.

## Known gaps left open

- `skill/career-desk/examples/sample_output.json` predates both pack versions: it
  has no `schema_version` and does not carry the 2.0.0 sections. It is an
  illustration, not a validated instance, and is regenerated under WO-01.
- `skill/career-desk/SKILL.md` still describes the pre-Day-2 one-project run. Its
  scope note now points at `ACTIVE_SCOPE.md`; the process steps are rewritten
  when WO-05 is built rather than ahead of it.

## Bad case or tradeoff

The routing step is the weakest link. It ranks projects from resume summaries the
system cannot verify, so a confident recommendation rests on self-reported text.
Coarse bands rather than numeric scores make that honest, but the recommendation
can still be wrong in a way the user only discovers after uploading a project.
`no_clear_choice` exists so the product can decline rather than guess.

The second tradeoff is that interview context depends entirely on what the user
pastes. Without scraping, most runs will have thin company signals, and a thin
brief may be less useful than users expect. That is a deliberate cost of not
building a scraper.

## Candidate decision checkpoint

- Decision to make: whether project routing needs the Agent at all, or whether a
  fixed ranking over five bands is sufficient
- Considered alternatives: ask the user to pick and skip routing entirely; rank
  by keyword overlap only
- Expected evidence: reviewer agreement with the recommended project on labeled
  routing cases, and how often `no_clear_choice` fires
- Final decision after evidence: pending

## What is not yet proven

- that JD-first ordering matches how users actually work
- that the recommendation beats the user's own instinct
- that users will paste enough interview material for the company brief to be useful
- any runtime behavior for intake, routing, or pack generation

## Public content notes

- Lead with choosing the wrong project, not with the pack.
- Show the two evidence systems side by side; that separation is the product.
- Explain the excluded platform integrations as a safety and trust choice.
