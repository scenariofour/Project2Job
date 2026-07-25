# WO-02 Agent PoC

Context set: `agent_poc`

## Goal

Implement one stateful Evidence Investigator and one project-update cycle.

## Deliver

- six read-only tools
- Agent loop
- project state
- file hashing
- user correction
- dependency invalidation
- update comparison
- traces
- token and tool telemetry

## Acceptance

- Agent respects budgets and stop conditions
- tool failures remain visible
- user correction updates dependent outputs
- changed files are prioritized
- fresh Skill rerun comparison completed
- no multi-agent or Deep Agent
