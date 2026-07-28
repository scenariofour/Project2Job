# Day 2 — JD-First Product Flow

Status: IMPLEMENTED

Not validated. Day 2 implements the intake half of the flow: one JD becomes one
Intake Result. Pack generation, scraping, Web UI, RAG, and mock-interview code
remain unimplemented, and no target user has run it.

## Actual implementation scope

`src/career_desk/jd_intake.py` and `src/career_desk/research.py` run the first
six steps of the MVP flow deterministically:

```text
JD intake
→ explicit requirements, everything unstated recorded as unknown
→ Role Demand Map from the versioned role profile
→ one bounded research pass through a host-provided capability
→ optional resume candidates, routing-only and self_reported
→ one recommended project or no_clear_choice
→ Required Evidence Checklist and exactly one next input
```

The runtime opens no socket. It drives a `ResearchHost` the host provides —
search, read-only fetch, Playwright render — and records what happened. Under
deterministic tests that host is a fixture, so every trace and eval is
reproducible. Two of its numbers are modeled rather than measured:
`runtime_seconds` is a fixed per-call cost model, and `total_tokens` is derived
from retained characters. Real latency and token cost are unmeasured.

`cross_reference_errors()` is the WO-05 output validator: it checks what one
JSON Schema document cannot, and `scripts/run_day2_intake_evals.py` executes the
intake-stage eval cases.

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

## Acceptance traceability

Every criterion, its labeled eval cases, the test that executes it, and the
result. Unit tests live in `tests/test_jd_first_intake.py` unless the row says
otherwise. Passing these validates intake behavior, not output quality, user
value, or any advantage over a strong prompt.

| AC | Criterion | Eval cases | Test | Result |
| --- | --- | --- | --- | --- |
| D2-AC-01 | JD intake extracts company, team, role family, track, level, location, requirements, and risks; anything unstated is recorded as unknown | D2-005 | `test_unstated_jd_fields_stay_unknown`, `test_a_stated_field_is_not_reported_as_unknown` | Pass |
| D2-AC-02 | The run produces a useful Intake Result with no resume and no project | D2-001 | `test_a_pasted_jd_alone_produces_a_valid_intake_result`, `test_the_result_needs_no_resume_and_no_project` | Pass |
| D2-AC-03 | Resume projects are extracted for routing only and stay `self_reported` | D2-002 | `test_every_candidate_stays_self_reported` | Pass |
| D2-AC-04 | Exactly one project is recommended for deep analysis, with reasons, non-empty risks, and a confidence band | D2-002 | `test_exactly_one_project_is_routed_into_deep_analysis` | Pass |
| D2-AC-05 | When nothing clearly fits, confidence is `no_clear_choice` and the user is asked to choose | D2-003 | `test_weak_candidates_produce_no_clear_choice`, `test_no_clear_choice_asks_the_user_to_choose_one_project` | Pass |
| D2-AC-06 | Keyword overlap alone cannot win the recommendation over evidence availability | D2-004 | `test_keyword_overlap_alone_cannot_win_the_recommendation` | Pass |
| D2-AC-07 | An unknown company track is recorded as unknown, never inferred | D2-005, D2-019 | `test_an_unknown_track_never_becomes_a_track_requirement` | Pass |
| D2-AC-08 | Conflicting interview reports are shown together, never merged or averaged | D2-006, D2-012 | `test_conflicting_reports_are_shown_together` | Pass |
| D2-AC-09 | A stale report is never presented as likely | D2-007, D2-012 | `test_a_stale_report_is_never_presented_as_likely` | Pass |
| D2-AC-10 | One reported experience is never presented more strongly than reported once | D2-008, D2-013 | `test_one_report_stays_reported_once`; the D2-008 pack wording is not executed | Partial |
| D2-AC-11 | An answer draft may not exceed its verified evidence | D2-009 | `test_a_draft_exceeding_its_evidence_cannot_validate` in `tests/test_jd_first_contracts.py` | Contract only |
| D2-AC-12 | Company emphasis may select, reorder, and reword a relevant subset of the verified project-fact pool without adding or strengthening a historical fact | D2-010 | `test_company_emphasis_case_allows_bounded_subset_selection` in `tests/test_jd_first_contracts.py` | Contract only |
| D2-AC-13 | The Intake Result names exactly one next input | D2-001 | `test_exactly_one_next_input_is_returned` | Pass |
| D2-AC-14 | No step logs in, bypasses a restriction, crawls a domain, or special-cases a named platform; the run degrades to user-supplied material when web access is unavailable | D2-001, D2-002, D2-015 | `test_a_walled_or_blocked_page_is_recorded_and_abandoned`, `test_every_intake_stage_case_is_executed` | Pass |
| D2-AC-15 | An official source and independent reports are combined, official first, each keeping its own status | D2-011 | `test_official_pages_are_fetched_before_independent_reports`, `test_official_and_reported_statuses_are_not_merged` | Pass |
| D2-AC-16 | A web-retrieved claim cites its exact page, fetch method, and retrieval date | D2-011 | `test_every_web_source_cites_an_exact_dated_page` | Pass |
| D2-AC-17 | Duplicate results are deduplicated on canonical URL and retain no content | D2-014 | `test_a_duplicate_is_recorded_once_and_never_refetched` | Pass |
| D2-AC-18 | A login-walled or blocked page is recorded, abandoned, and never retried with a credential | D2-015 | `test_a_walled_or_blocked_page_is_recorded_and_abandoned` | Pass |
| D2-AC-19 | Playwright is used only after a plain fetch is insufficient, and records why | D2-016 | `test_playwright_is_used_only_after_a_plain_fetch_is_insufficient` | Pass |
| D2-AC-20 | Text in a fetched page cannot cause a search, fetch, navigation, or claim | D2-017 | `test_fetched_page_text_cannot_cause_a_fetch_or_a_claim` | Pass |
| D2-AC-21 | Research stays inside every ceiling and stops with `budget_exhausted` | D2-018 | `test_research_stays_inside_a_declared_budget_and_says_why_it_stopped` | Pass |
| D2-AC-22 | With no useful public evidence the brief is thin, gaps are named, and nothing is inferred as reported | D2-019 | `test_no_useful_public_evidence_yields_a_thin_honest_brief` | Pass |
| D2-AC-23 | Research stops early on sufficient evidence rather than spending the budget | D2-020 | `test_research_stops_early_once_every_gap_closes` | Pass |
| D2-AC-24 | One report is never generalized into a common or expected question | D2-013 | `test_one_report_stays_reported_once` | Pass |

The two evidence systems have their own executable boundary:
`test_research_never_reaches_a_candidate_or_a_verification_claim` and
`test_research_cannot_change_a_routing_score` assert that interview research
changes nothing about a candidate project.

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

D2-AC-12 is **not** fully schema-enforceable. Verified-pool membership is a
property of the project evidence and multiple emphasized runs, which no single
document schema can express. `emphasisProfile.fact_ids` is required so each
selected subset is recorded; eval case D2-010 checks that every selection stays
inside the same verified project-fact pool.

Cross-object ID references are likewise beyond JSON Schema and belong to the
WO-05 output validator, now implemented as
`src/career_desk/jd_intake.py::cross_reference_errors`. It checks non-null
`recommendation.candidate_id`, `page.duplicate_of`, canonical-URL uniqueness
across extracted pages, a claim's `url` resolving to a page the run actually
extracted, conflict item IDs resolving, and `usage` staying within a smaller
declared `budget`. The pack-side references — `answer_draft.question_id`,
`mock_round.question_ids`, `claim_safety_review.checked_fact_ids`, and
`emphasis.fact_ids` — remain unimplemented with pack generation itself. The one
case the schema can catch, recommending a project when no candidate exists, is
enforced.

`tests/test_jd_first_contracts.py` runs real instances through a draft-2020-12
validator when `jsonschema` is installed, so these rules are executed rather than
only read. The repository itself still has no third-party dependency; the suite
skips those tests when the library is absent.

## Evidence

Seventeen of the twenty cases in `lab/evals/day2_jd_first_cases.jsonl` — every
`intake`-stage case — are executed by `lab/day2_intake_eval.py` through
`scripts/run_day2_intake_evals.py`. Each case builds its own world, runs the
real intake, and checks the expectations the case states.

```text
executed: 17    checks: 85    failed_cases: []
not executed: D2-008, D2-009, D2-010
```

Every produced Intake Result is also validated against
`schemas/intake_result.schema.json` and passes `cross_reference_errors`.

The three unexecuted cases are `pack`-stage. Pack generation belongs to WO-01 and
WO-02, so D2-AC-11 and D2-AC-12 stay contract-and-eval definitions. Claiming them
as behavior would be the exact overstatement this journal exists to prevent.

`tests/test_jd_first_intake.py` holds 43 behavior tests;
`tests/test_jd_first_contracts.py` still holds the contract tests.

## Dogfood

One JD-first run over the repository's own committed fixtures, recorded in
`docs/dogfood/DAY2_JD_FIRST_DOGFOOD.md` with the full artifact in
`docs/build_journal/traces/day2_jd_first_dogfood.json` and regenerated by
`scripts/build_day2_dogfood.py`.

What it produced: seven role demands, five self-reported candidates, one narrow
recommendation, a five-item evidence checklist, and one next input, from a JD
that states no company and no title.

What it exposed: the parser reads labeled headers, so an unlabeled JD leaves
`company` unstated and `role_family` unsupported rather than guessing — honest,
and thin. It also caught a real bad case: a winner with only `adequate` evidence
was reported as `clear_choice`. Confidence is now capped by the winner's own
evidence band, with a regression test.

Evidence maturity: deterministic and fixture-level. No live web research, no
real resume, no target user, no model in the loop.

## Known gaps left open

- The intake runtime and the host-native Skill suite reach the same contract by
  different routes: the runtime is deterministic Python, the Skills are
  instructions a host executes. Nothing yet checks that a Skill run and a runtime
  run agree on the same JD.
- Pack generation (WO-01, WO-02) does not consume the Intake Result yet. The
  handoff is the schema, not a call.
- The JD parser reads labeled headers and bulleted sections. A prose JD with no
  labels yields `unstated` and `other_or_unsupported` rather than a guess, which
  is honest but thin. Screenshot and URL input forms are declared in the schema
  and not implemented.
- The two earlier gaps in this section named `skill/career-desk/`, which no
  longer exists; the suite is the seven `skill/p2j*` packages.

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

The fourth arrived with the implementation. Telling a mirror from genuine
corroboration decides whether one article becomes `single_report` or
`repeatedly_reported`, and the runtime decides it on the page body: an identical
body is a mirror, a different one is a second report. A syndicated article that
is lightly reworded therefore still counts twice. Canonical-URL deduplication
catches the easy half of this problem and nothing more.

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
- any pack-generation behavior; WO-05 stops at the Intake Result
- any behavior against a live host: every executed case uses a fixture host, so
  real search results, real page structure, real latency, and real token cost
  are untested
- that the five routing bands, derived from keyword and phrase tables, agree with
  a human reviewer on real resumes
- that modeled `runtime_seconds` and `total_tokens` resemble measured ones

Day 2 is `IMPLEMENTED`, not `VALIDATED`.

## Public content notes

- Lead with choosing the wrong project, not with the pack.
- Show the two evidence systems side by side; that separation is the product.
- Explain the excluded platform integrations as a safety and trust choice.
