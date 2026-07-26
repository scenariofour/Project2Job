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
→ bounded public-web research
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
| 3 | the above, plus anything the user pasted or uploaded | company and interview context from one bounded research pass, with its query log, page log, and stop reason |
| 4–5 | optional resume | several project candidates, all `self_reported`, extracted for routing only |
| 6 | the above | **Intake Result**: Role Demand Map, company and track signals, candidates, one recommended project, reasons, risks, claims to verify, evidence checklist, One Next Input |
| 7–8 | the selected project's repo, files, PRD, evals, feedback | verified project evidence, via the existing Day 1 investigation loop |
| 9 | the above | **Application and Interview Pack** |

Several projects may be considered at step 6. Exactly one may enter step 8.

## Bounded research, not scraping

The first version of this flow made the user paste their own company research,
which is the part of interview preparation people are least likely to do. Step 3
is now automatic:

```text
search → prioritize and deduplicate → read-only fetch
→ Playwright only where a plain fetch is insufficient
→ extract → gap check → adjust queries while a gap is open → stop
```

Playwright is a required capability and the expensive one, so it is an escalation
rather than a default: a page earns it by returning `render_required`, needing one
navigation step, or resisting parsing. Every Playwright page records why.

What separates this from the scraper the product is not: fixed ceilings on
queries, pages, Playwright pages, navigation depth, characters, tokens, retries,
and runtime (`docs/09_TOKEN_CONTEXT_AND_COST.md` holds the numbers, and the
schema enforces them as maximums); official-tier-first ordering; canonical-URL
deduplication; no login ever; no domain crawling; no arbitrary link following;
and a recorded stop reason on every path. No platform is named anywhere in the design; pages are ranked by
tier, not brand.

Fetched page text is inert. It cannot cause a search, a fetch, a navigation, or a
claim.

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
| D2-AC-14 | No step logs in, bypasses a restriction, crawls a domain, or special-cases a named platform; the run degrades to user-supplied material when web access is unavailable | D2-001, D2-002, D2-015 | `jd_intake` `input_form`, `interview_context` `researchRun` `mode` |
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
| D2-AC-15 | An official source and independent reports are combined, official first, each keeping its own status | D2-011 | `interview_context` `sourceTier`, `researchRun` |
| D2-AC-16 | A web-retrieved claim cites its exact page, fetch method, and retrieval date | D2-011 | `interview_context` `researchSource` |
| D2-AC-17 | Duplicate results are deduplicated on canonical URL and retain no content | D2-014 | `interview_context` `researchPage` |
| D2-AC-18 | A login-walled or blocked page is recorded, abandoned, and never retried with a credential | D2-015 | `interview_context` `researchPage` |
| D2-AC-19 | Playwright is used only after a plain fetch is insufficient, and records why | D2-016 | `interview_context` `researchPage` |
| D2-AC-20 | Text in a fetched page cannot cause a search, fetch, navigation, or claim | D2-017 | `docs/11_SAFETY_PRIVACY_AND_HITL.md` |
| D2-AC-21 | Research stays inside every ceiling and stops with `budget_exhausted` | D2-018 | `interview_context` `researchBudget` |
| D2-AC-22 | With no useful public evidence the brief is thin, gaps are named, and nothing is inferred as reported | D2-019 | `interview_context` `researchRun` |
| D2-AC-23 | Research stops early on sufficient evidence rather than spending the budget | D2-020 | `interview_context` `researchStopReason` |
| D2-AC-24 | One report is never generalized into a common or expected question | D2-013 | `interview_context` `interviewQuestion` |

### What the schemas actually enforce

D2-AC-05, D2-AC-09, D2-AC-10, D2-AC-11, D2-AC-16, D2-AC-17, D2-AC-18, and
D2-AC-19 are enforced by conditional rules, so a violating object fails
validation rather than only failing review. So are two rules an earlier review
surfaced: an item above `inferred_from_jd` must cite a source, and any item with
known freshness must have a dated source. Official status must also carry an
official tier and official company source.

D2-AC-21's ceilings are enforced as schema `maximum` values, so a run cannot even
declare an over-large budget. Whether a run *stayed* inside its declared budget
compares two numbers in different places and is checked by the WO-05 validator
and eval case D2-018.

D2-AC-15, D2-AC-20, D2-AC-22, and D2-AC-23 are behavioral and eval-only. No
document schema can prove that a search stopped early or that injected text was
ignored.

D2-AC-12 is **not** schema-enforceable. Emphasis invariance is a property of two
runs compared against each other, which no single-document schema can express.
`emphasisProfile.fact_ids` is required so the invariant is recorded; eval case
D2-010 is what checks it.

Cross-object ID references are likewise beyond JSON Schema and belong to the
WO-05 output validator: `answer_draft.question_id`, `mock_round.question_ids`,
`claim_safety_review.checked_fact_ids`, `emphasis.fact_ids`,
non-null `recommendation.candidate_id`, `page.duplicate_of`, canonical-URL uniqueness
across extracted pages, a claim's `url` resolving to a page the run actually
extracted, and `usage` staying within a smaller declared `budget`. The one case
the schema can catch, recommending a project when no candidate exists, is
enforced.

`tests/test_jd_first_contracts.py` runs real instances through a draft-2020-12
validator when `jsonschema` is installed, so these rules are executed rather than
only read. The repository itself still has no third-party dependency; the suite
skips those tests when the library is absent.

## Evidence

Planned. Twenty synthetic cases exist in `lab/evals/day2_jd_first_cases.jsonl`;
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

The second tradeoff is the research budget. Twelve pages and three rendered pages
is enough for a well-documented company and probably not enough for a small
private one, so some runs will stop at `evidence_exhausted` with a thin brief.
Raising the ceilings would help those runs and would also be the first step
toward the scraper this product is not. Holding the line means accepting that a
thin, honest brief is the correct output for a company the public web barely
covers.

The third is that a bounded pass can be confidently wrong: two independent
write-ups of the same stale process look like corroboration. Freshness and
conflict disclosure are the guard, and neither is proven.

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
- that public evidence plus optional user-supplied material will support a useful
  company brief
- any runtime behavior for intake, routing, or pack generation

## Public content notes

- Lead with choosing the wrong project, not with the pack.
- Show the two evidence systems side by side; that separation is the product.
- Explain the excluded platform integrations as a safety and trust choice.
