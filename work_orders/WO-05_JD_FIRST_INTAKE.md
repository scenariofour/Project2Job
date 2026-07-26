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
- interview context capture into `schemas/interview_context.schema.json` from
  pasted and uploaded material only
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
- no network call to a job platform, and no credential is ever requested

## Out of scope

Job discovery, bulk scraping, platform login, auto-apply, application tracking,
email monitoring, referral automation, multiple deep project analyses, a reusable
company question database, and broad MCP integrations. Pack generation itself
belongs to WO-01 and WO-02.
