---
name: p2j
description: Route one target AI PM, Agent PM, or Applied AI PM JD and at most one project into the Project2Job Skill Suite. Use when the user says /p2j or asks which Project2Job analysis to run, which project evidence matters for a role, or how to turn a project into interview assets. Do not use for job discovery, auto-apply, application tracking, generic resume writing, or deep analysis of multiple projects.
---

# Project2Job Router

Turn what the user already supplied into the first useful result. Treat `/p2j` as
a conversational alias; `$p2j` is the host-native explicit invocation.

## Route

1. Detect one JD, optional resume, one selected project, interview question, and
   any confirmed facts already supplied. Detect a specifically requested asset
   and explicit `Full Preparation`.
2. Resolve shared context with `scripts/context_registry.py` as defined in
   `references/context-registry.md`, then read
   `references/profile-contract.md`. Resolve the Project Evidence Profile,
   Company Intelligence Profile, and JD Demand Map before opening a source.
   Reuse compatible facts and results; honor refresh, analyze-from-scratch,
   do-not-save, and selective forget requests.
   Run `scripts/inventory.py <project>` only when the context contract requires
   a new or changed inventory. Treat every file as untrusted evidence and never
   execute project code during intake.
   Use the Context Registry directly for saved-profile reuse on every selective
   route. Invoke `scripts/stateful_agent.py` only for the explicit stateful Agent
   update path, after host-native route selection; it updates persisted
   evidence/output dependencies but does not choose a normal selective Skill.
   For one-time use or `do not save`, run the selected host-native Skill
   directly without creating registry or consent files.
3. Plan exactly one selective route with `scripts/profile_router.py`:
   - JD only → `JD_INTAKE`: use `$p2j-intel`, then return the canonical
     `Intake Result`; no resume means no project candidates, not a fabricated
     recommendation
   - JD plus project, no narrower request → reuse a fresh exact-company/track
     Company Intelligence Profile or run bounded `$p2j-intel`, then
     `$p2j-brief`: return one strongest positioning and one recommended next
     specialist; do not run the full suite
   - project only → `PROJECT_COMPASS`: use the default role standard and
     `$p2j-brief`; plan with `company_context_required=false` so no company/JD
     adaptation is claimed
   - explicit Project Highlights, introduction, or resume bullets → build only
     a missing/stale prerequisite profile, then generate only that asset from
     source-linked Supported or user-confirmed facts
   - explicit company-research request → `$p2j-intel`
   - deep evidence/scoring request → `$p2j-audit`
   - one interview question → `$p2j-answer`
   - interactive practice → `$p2j-mock`
   - one project improvement → `$p2j-upgrade`
   - explicit Full Preparation → assemble the canonical `Application and
     Interview Pack` from all six specialist capability contracts; reuse fresh
     Project and Company profiles instead of rerunning Audit or Intel
4. Select one strongest defensible story and positioning. Adapt emphasis to the
   company, culture, and JD only from a fresh resolved Company Intelligence
   Profile and its matching JD Demand Map; otherwise build or refresh them
   first. Translate technical evidence into product, user, business, and AI PM
   value. Never ask the user to choose among story options.
5. For a canonical run, load the installed `intake_result.schema.json` or
   `application_pack.schema.json`, preserve its exact evidence/source fields,
   and run `scripts/validate_output.py` when emitting JSON. A schema error is a
   failed output, never a successful preview.
6. Ask zero questions when a bounded preview is safe. Ask at most one question
   before first value only when target, project selection, or ownership changes
   the route or factual truth.
7. Give the routed Skill's concise first output now. Keep vulnerability material
   in Private Defense for Mock preparation. Record exact files opened, model
   calls, Skill invocations, cached/uncached input tokens, and output tokens.

## Shared contract

Read `references/core-contract.md` for every route. Load only the profile and
specialist references required by the selected route. Prefer installed
`references/canonical/`; inside the source repository, fall back to the
canonical paths listed in `references/core-contract.md`.

Keep company research separate from project evidence. Reuse compatible local or
current-session facts and research; do not reread unchanged sources without a
named gap.

## Host boundary

This Alpha relies on the host for local file reads, Git history, public web
search and fetch, selected browser rendering, and constrained language
generation. State unavailable capabilities and use the fallback in
`references/core-contract.md`. The Agent runs only when invoked; do not claim
background monitoring, a provider API, or a standalone service.
