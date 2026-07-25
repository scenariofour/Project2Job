# Project2Job

Project2Job is the repository for Career Desk, a role-backwards product concept
for people preparing for early-career AI Product Manager, Agent Product Manager,
or Applied AI Product roles.

The intended workflow turns one real AI project into grounded career assets:

```text
Target role or JD
→ role requirements
→ project evidence
→ defensible claims
→ resume bullets
→ interview preparation
→ one next project action
```

The product has been designed but its user value and runtime behavior have not
yet been validated.

## Skill and Agent responsibilities

The planned open-source Career Desk Skill is the low-friction, session-scoped
entry point. Given one project and one role or JD, it is responsible for a Role
Fit Map, Project Highlights, evidence-grounded resume bullets, an Interview Prep
Pack, One Next Build, and a correction prompt. It runs in the user's Agent host
and does not maintain product state.

The planned Career Evidence Agent is the stateful product. It is responsible for
maintaining user-confirmed evidence, applying corrections, detecting one project
update, invalidating dependent claims, and regenerating affected assets. It does
not have permission to fabricate claims or take external action.

Both products share evidence rules, schemas, source boundaries, evaluation
cases, and safety requirements. They do not require the same runtime.

## Current MVP

The MVP is limited to:

- one AI project
- one target role profile or JD
- one initial Project-to-Application analysis
- one later project-update cycle

It excludes job discovery, auto-apply, application tracking, Gmail or Calendar,
multiple projects or JDs, full resume generation, networking automation, broad
MCP integrations, multi-agent, and Deep Agents.

## Current implementation status

Day 0 establishes the repository foundation only.

What exists:

- the v6 product definition and 14 active product documents
- Work Orders and manifest-scoped context sets
- schemas, public fixtures, starter eval cases, and a baseline prompt
- Skill source materials and deterministic implementation interfaces
- repository validation, contract tests, and inventory scripts
- the public Day 0–Day 7 build journal

What remains planned:

- live Skill behavior and host validation
- Evidence Investigator and stateful update behavior
- thin Web UI and RAG comparison
- evaluation harness execution, model decisions, and target-user pilot
- measured quality, latency, token, cost, model, adoption, and user-value results

Files under `src/` are interfaces or stubs imported from v6; their presence does
not mean the runtime features are implemented.

## Safety and source handling

- Original user inputs are read-only.
- Uploaded and project documents are untrusted data, not instructions.
- Ownership, users, metrics, outcomes, decisions, and career claims cannot be
  invented.
- External-facing claims require source evidence or an unsupported label.
- No external action occurs without explicit user approval.
- Private resumes, JDs, personal data, secrets, logs, caches, and run outputs
  must not be committed.

Public examples are synthetic and contain no identifying data.

## Build and learning path

The concise public narrative is in `docs/build_journal/`. Days do not replace
engineering dependencies:

| Day | Focus |
| --- | --- |
| 0 | Safe Foundation |
| 1 | Agent Loop |
| 2 | Problem, MVP, and Intent |
| 3 | Context, RAG, and Evidence |
| 4 | Skill, Agent, and Human Control |
| 5 | Evaluation and Model Decisions |
| 6 | Tools, API, and Safe Failure |
| 7 | Product Experience and Defense |

Work Orders in `work_orders/` remain the technical dependency and acceptance
system. `PROJECT_MANIFEST.json` defines the smallest context set for each task;
do not read the whole repository by default.

## Start building

Read:

1. `START_HERE.md`
2. `AGENTS.md`
3. `ACTIVE_SCOPE.md`
4. `PROJECT_MANIFEST.json`
5. the assigned Work Order and its manifest context set

## Validation

Python 3.11 or later is required. No third-party dependency is needed for the
Day 0 checks.

```bash
make validate
make test
make inventory
git diff --check
```

These checks validate repository structure, JSON/JSONL parsing, starter contract
tests, and deterministic sample-project inventory. They do not validate product
quality or user value.
