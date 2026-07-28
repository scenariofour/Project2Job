# Day 2 JD-First Dogfood

Run date: 2026-07-27. Artifact: `docs/build_journal/traces/day2_jd_first_dogfood.json`.
Regenerate or verify with:

```bash
python3 scripts/build_day2_dogfood.py --check
```

## What was run

One JD-first intake over the repository's own committed fixtures, so the run is
reproducible and nothing was written for the occasion:

- JD: `lab/fixtures/fixture_ai_pm_jd.md` — a Junior AI PM description that
  states seven responsibilities and no company, team, track, level, or location
- Resume: five candidates built from `lab/fixtures/fixture_project_plan_only.md`,
  `fixture_project_with_code_no_users.md`, `fixture_team_project.md`,
  `fixture_project_without_jd.md`, and `fixture_prompt_injection.md`, each using
  that fixture's own words
- Host: no web capability, so research mode is `unavailable`

## What it produced

| Output | Result |
| --- | --- |
| JD extraction | 7 requirements; `company` unstated; `role_family` `other_or_unsupported`; 6 unknowns |
| Role Demand Map | 7 demands, each with what evidence would satisfy it |
| Candidates | 5, all `self_reported`, each with five routing bands |
| Recommendation | `AI Agent` (the repository fixture), confidence `narrow_choice` |
| Risks | 3, including unestablished ownership and no measured outcome |
| Evidence checklist | 5 artifacts, ending in `ownership_clarification` |
| One Next Input | "Send the repository or files for one project: AI Agent." |
| Research | mode `unavailable`, stop reason `research_not_run`, usage all zero |
| Cross-reference errors | none |

The recommendation is defensible from the material: the only candidate naming
artifacts a reviewer could open — a repository, a tool registry, structured
output tests — won, and the plan-only, team-attributed, and injection fixtures
did not. The injection fixture's text was echoed back as a candidate summary and
routed nothing; it never became an instruction.

## Evidence maturity

Deterministic and fixture-level. This run proves the intake produces a valid,
internally consistent Intake Result from real committed inputs. It proves
nothing about live search results, real resumes, model behavior, latency, or
token cost.

## What it changed

The first run reported the winner as `clear_choice` while its own evidence
availability was only `adequate` — a confident-sounding verdict over a weak
field. Confidence is now capped by the winner's own evidence band, covered by
`test_winning_a_weak_field_is_a_narrow_choice_not_a_clear_one`.

## What remains unvalidated

- whether a reviewer would pick the same project from the same five summaries
- whether the routing bands survive contact with real resume prose
- whether a real bounded research pass behaves as the fixture host does
- whether a JD with no labeled headers is common enough that the thin
  `unstated` result is a product problem rather than an honest one
