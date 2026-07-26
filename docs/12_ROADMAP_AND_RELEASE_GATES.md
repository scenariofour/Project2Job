# Roadmap and Release Gates

## Phase 0: Shared Foundation

Build:

- RBEF
- role standard
- schemas
- gold-label format
- baseline prompt
- source registry

Exit:

- contracts validate
- 10 representative gold cases labeled
- reviewer agreement process defined

## Phase 1: JD-First Intake

Build:

- JD intake extraction into `schemas/jd_intake.schema.json`
- Role Demand Map
- interview context capture from pasted and uploaded material only
- resume project candidate extraction for routing
- one-project recommendation across the five routing dimensions
- `Intake Result` assembly

Exit:

- one pasted JD alone produces a valid Intake Result
- `lab/evals/day2_jd_first_cases.jsonl` passes
- unknown company, track, and level are recorded rather than inferred
- exactly one project is routed into deep analysis
- no interview item outruns its source status

## Track A: Skill PoC

Build:

- short SKILL.md
- progressive references
- inventory script
- output validator
- examples
- trigger and behavior evals

Exit:

- installable zip
- works in at least two Agent hosts
- produces a valid Intake Result and a valid Application and Interview Pack
- answer drafts pass claim-safety review
- comparison with generic prompt completed

## Track B: Agent PoC

Build:

- Evidence Investigator
- six read-only tools
- session state
- file hashing
- correction
- update run
- traces and budgets

Exit:

- stateful update works
- dependency updates work
- failure tests pass
- update advantage measured

## Phase 3: Thin Web

Build:

- drop/paste input
- result review
- evidence drawer
- correction
- update comparison

Exit:

- first-value path works
- no more than one pre-value question
- error states visible
- product analytics events defined

## Phase 4: Pilot and Case Study

Build:

- reviewer set
- user pilot
- bad-case log
- before-and-after results
- interview case study

Exit:

- measured evidence for user value
- honest decision on continuation or pivot

## Future candidates

Only after MVP evidence:

- multiple projects
- role library expansion
- GitHub or Drive connector
- Career Desk MCP server
- interview answer practice
- recruiter outreach
- application workspace
- LangGraph experiment
- multi-agent or Deep Agent experiment

## Feature admission test

A feature enters P0 only when:

1. it directly improves the current product promise
2. it does not add a new primary user
3. it has an acceptance test
4. it has an eval case
5. it does not create an unapproved external action
6. equivalent scope is removed or timeline explicitly changes
