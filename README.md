# Project2Job

Project2Job is a role-backwards product for people preparing for early-career AI
Product Manager, Agent Product Manager, or Applied AI Product roles. Project2Job
is the canonical product and repository name; `Career Desk` is a legacy internal
codename that survives only in historical records and some v6-era code modules.
Vocabulary is defined in `GLOSSARY.md`.

The intended workflow starts at the job description and ends at a pack for that
specific company:

```text
One target JD
→ company, track, level, and role requirements
→ optional resume, read to route between projects
→ one recommended project to investigate
→ that project's evidence, verified
→ defensible claims
→ tailored resume bullets
→ company-specific interview preparation
→ one next project action
```

The first four steps run without a project and produce an `Intake Result`. The
rest produce an `Application and Interview Pack`.

The product has been designed and a bounded evidence loop is implemented. Its
user value has not been validated.

## Skill, Context Registry, and Agent responsibilities

The host-native Project2Job Skill Alpha is the low-friction method. Its `$p2j`
router and six specialists produce a concise Brief, evidence audit, company
intelligence, grounded answer lab, interactive mock, and One Next Build.

After one-time consent, the shared local Context Registry stores minimal
Project/JD/run identity, fingerprints, confirmed facts, ownership boundaries,
gaps, and output references. It lets Skills reuse compatible work across
sessions. It is passive infrastructure: it does not monitor files, decide what
to run, or regenerate outputs in the background.

The planned Project2Job Evidence Agent is the stateful product. It is responsible for
actively handling one project update, resolving dependencies, regenerating
affected assets, and explaining what changed. It does not have permission to
fabricate claims or take external action.

Both products share evidence rules, schemas, source boundaries, evaluation
cases, and safety requirements. They do not require the same runtime.

## Install and invoke the Skill Alpha

Python 3.11 or later is required. Install the seven Skills from a source
checkout:

```bash
python3 skill/p2j/scripts/install_suite.py --dest ~/.codex/skills
python3 skill/p2j/scripts/install_suite.py --dest ~/.claude/skills
```

Add `--replace` only when intentionally updating an existing Project2Job
installation. Build the portable archive with `make skill-package`.
Canonical JSON outputs can be checked with
`python3 ~/.codex/skills/p2j/scripts/validate_output.py --schema
application_pack <output.json>`; full instance validation uses the repository's
optional `jsonschema>=4` dev dependency.

In Codex, invoke `$p2j` or a specialist such as `$p2j-brief`; `/p2j` is a
conversational alias, not a custom Codex slash-command runtime. In Claude Code,
invoke `/p2j` or `/p2j-brief` after the host has reloaded its Skills. Start with
one JD and, for project analysis, one local project folder.

The suite depends on the host for local file reads, Git history, public search
and fetch, optional browser rendering, and local storage. The Context Registry
defaults to `~/.project2job`; set `P2J_HOME` to override it. The first write
requires consent, and users may refresh, analyze from scratch, run without
saving, or forget selected context. The suite has no standalone service,
background refresh, or Web UI.

## Current MVP

The MVP is limited to:

- one target JD, one company, one track or team context
- one optional resume, read only to route between candidate projects
- one selected AI project for deep evidence analysis
- one Intake Result and one Application and Interview Pack
- 5–8 priority questions, three answer drafts, one mock-interview round
- one later project-update cycle

It excludes job discovery and bulk scraping, automatic login to any job platform
or professional network, auto-apply, application tracking, email monitoring,
referral automation, Gmail or Calendar, multiple deep project analyses, any
cross-Project company question database, full resume generation, networking
automation, broad MCP integrations, multi-agent, and Deep Agents.

After the JD arrives the MVP runs one bounded public-web research pass for
company and interview context, inside explicit query, page, Playwright, token,
and runtime ceilings. It never logs in, bypasses a restriction, crawls a domain,
or names a specific job platform. Pasted and uploaded material is equally
supported and merged with what research finds.

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
- Day 2 revised the product contracts around the JD-first flow. Those contracts
  and their eval cases exist. The host-native Skill Alpha implements the
  JD/project routing and interview-prep workflows through host tools; no
  standalone intake or pack runtime exists.

Unproven: user value beyond dogfood, cross-host consistency, the Web UI,
production RAG, production model behavior, latency, cost, and any Agent
advantage over a strong one-shot prompt or a fixed workflow.

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
| 2 | JD-First Product Flow |
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
