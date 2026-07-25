# Career Desk

Career Desk is a **role-backwards project career system** for people applying to early-career AI Product Manager, Agent Product Manager, and Applied AI Product roles.

It helps a user turn one real AI project into grounded career assets:

```text
Target role or JD
→ role requirements
→ project evidence
→ defensible claims
→ resume bullets
→ interview preparation
→ one next project action
```

## Two user products

### 1. Career Desk Skill

A low-friction, open-source Skill for Codex, Claude Code, OpenCode, and other agent hosts.

The user provides one project and a target role or JD. The Skill returns:

- Role Fit Map
- Project Highlights
- 2–3 evidence-grounded resume bullets
- Interview Prep Pack
- One Next Build

The Skill uses the user's host model and current session. It does not require a Career Desk account.

### 2. Career Evidence Agent

A stateful product that maintains a user's confirmed project evidence over time.

The Agent supports:

- Initial Project-to-Application analysis
- User corrections
- Project update detection
- Evidence status updates
- Regeneration of affected resume and interview assets
- A persistent record of what the project can and cannot support

The Agent exists because a one-time Skill cannot reliably maintain evidence, corrections, project versions, and update history across sessions.

## Shared foundation

The Skill and Agent share:

- Role-Backwards Evidence Framework
- AI PM Role Standard
- Evidence status definitions
- Source and claim rules
- Output schemas
- Evaluation cases
- Safety rules
- Product quality gates

They do not share the same model runtime. The Skill runs inside a host agent; the full Agent runs in a controlled Career Desk runtime.

## Current MVP

The initial release supports:

- One role family: early-career AI PM / Agent PM / Applied AI PM
- One target role profile or one JD
- One project corpus
- Optional resume and ownership clarification
- One initial analysis
- One post-update re-analysis in the Agent product

Excluded from MVP:

- Job discovery
- Auto-apply
- Application tracking
- Gmail and calendar
- Multiple projects
- Multiple JDs
- Full resume builder
- Cold-email sending
- Long-term general career memory
- Multi-agent
- Deep Agent
- Large MCP connector set

## Two entry points

### I want to build the product

Read:

1. `START_HERE.md`
2. `AGENTS.md`
3. `ACTIVE_SCOPE.md`
4. `PROJECT_MANIFEST.json`
5. the assigned Work Order

### I want to use the open-source Skill

Open:

- `skill/career-desk/README.md`
- `skill/career-desk/SKILL.md`

A standalone Skill package is generated as:

- `career-desk-project-to-application-skill_v1.zip`

## Repository design

Only 14 product documents are active. Other files are schemas, tests, examples, Skill resources, or implementation stubs.

A coding agent must never read the whole repository by default. `PROJECT_MANIFEST.json` defines the smallest context set for each task.
