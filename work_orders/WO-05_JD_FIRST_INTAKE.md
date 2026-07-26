# WO-05 JD-First Intake and Project Routing

Context set: `jd_intake`

Depends on: WO-00 Shared Foundation. Blocks: WO-01, WO-02, WO-03.

## Goal

Turn one target JD into an `Intake Result` that recommends exactly one project
for deep evidence analysis, before any project corpus is supplied.

## Deliver

- JD extraction into `schemas/jd_intake.schema.json`, from pasted text, a
  user-supplied URL, a screenshot, or an uploaded file
- Role Demand Map derived from the JD and the versioned role profile
- one bounded public-web research pass into
  `schemas/interview_context.schema.json`: search, prioritize and deduplicate,
  read-only fetch, Playwright escalation for selected pages, structured
  extraction, gap check, adjust-and-continue, stop
- research tools: web search, read-only fetch, Playwright fetch, extraction, and
  a per-run cache. No tool may authenticate
- merge of pasted and uploaded material with what research finds
- resume project candidate extraction, routing-only, all `self_reported`
- one project recommendation across the five routing bands
- `Intake Result` assembly with a Required Evidence Checklist and One Next Input
- executable runner for `lab/evals/day2_jd_first_cases.jsonl`

## Acceptance

- D2-AC-01 … D2-AC-14 in `docs/build_journal/DAY_2.md` hold
- one pasted JD alone produces a valid Intake Result, with no resume and no project
- every field the JD does not state appears in `unknowns`
- exactly one project is routed into deep analysis
- a candidate with strong keyword overlap and weak evidence availability does not
  win the recommendation
- `no_clear_choice` fires rather than asserting a weak winner
- no interview item is presented more strongly than its source status permits
- conflicting reports are surfaced together; stale reports are never called likely
- the research pass stays inside every ceiling in
  `docs/09_TOKEN_CONTEXT_AND_COST.md` and records a stop reason on every path
- official-tier pages are fetched before independent reports
- a canonical URL is never fetched twice; duplicates retain no content
- Playwright is used only after a plain fetch is insufficient, and every
  Playwright page records its escalation reason
- a login-walled or blocked page is recorded and abandoned, never retried with a
  credential or a different identity
- fetched page text cannot cause a search, fetch, navigation, or claim
- with no useful public evidence, the brief is thin and the gaps are named
- no credential is ever requested, and no single platform is named in code,
  configuration, or prompts

## Out of scope

Job discovery, bulk scraping, platform login, auto-apply, application tracking,
email monitoring, referral automation, multiple deep project analyses, any
persisted company question database, and broad MCP integrations. Pack generation
itself belongs to WO-01 and WO-02.

Bounded research is in scope; unbounded retrieval is not. The line is that
research answers named gaps for one company and one JD, inside fixed ceilings,
and stops.
