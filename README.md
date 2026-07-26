# Project2Job

Project2Job is a role-backwards product for people preparing for early-career AI
Product Manager, Agent Product Manager, or Applied AI Product roles. Project2Job
is the canonical product and repository name; `Career Desk` is a legacy internal
codename that survives only in historical records and existing paths such as
`skill/career-desk/`. Vocabulary is defined in `GLOSSARY.md`.

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

The product has been designed and a bounded evidence loop is implemented. Its
user value has not been validated.

## Skill and Agent responsibilities

The planned open-source Project2Job Skill is the low-friction, session-scoped
entry point. Given one project and one role or JD, it is responsible for a Role
Fit Map, Project Highlights, evidence-grounded resume bullets, an Interview Prep
Pack, One Next Build, and a correction prompt. It runs in the user's Agent host
and does not maintain product state.

The planned Project2Job Evidence Agent is the stateful product. It is responsible for
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

`PROJECT_STATUS.md` is the canonical implementation truth. In summary:

- WO-00 Shared Foundation is complete: role profile, source registry, shared
  contract, schemas, and ten labeled gold cases.
- The Day 1 bounded Agent Loop is implemented and tested: a deterministic
  Evidence Investigator with explicit state, action, observation, and
  state-update records, Continue / Adjust / Ask / Stop decisions, enforced
  budgets, a permitted-source boundary, and committed deterministic traces.
- Day 1 uses deterministic scripted read-only tools. It is not a production
  model-powered Agent runtime.
- The full WO-02 stateful project-update cycle is not complete.

Unproven: the Skill runtime in a real Agent host, the Web UI, production RAG,
production model behavior, user value, product quality, latency, cost, and any
Agent advantage over a strong one-shot prompt or a fixed workflow.

Other files under `src/` are interfaces or stubs imported from v6; their
presence does not mean those runtime features are implemented.

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

Python 3.11 or later is required. No third-party dependency is needed.

```bash
make validate
make test
make inventory
git diff --check
```

These checks validate repository structure, JSON/JSONL parsing, Day journal
status ordering, documentation consistency, the Day 1 Agent loop, and
deterministic sample-project inventory. They do not validate product quality or
user value.

`docs/DOCUMENT_GOVERNANCE.md` records which file owns which question and what a
contract change must update.
