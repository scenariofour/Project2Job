# Start Here

The product direction is sufficiently defined to begin building. The design is still a hypothesis until the Skill, Agent, and comparison tests run successfully.

## Recommended operating sequence

### Step 1: Initialize the repository

```bash
git init
git add .
git commit -m "chore: initialize Career Desk final build system v6"
```

### Step 2: Give the coding agent one task

Paste `CODEX_FIRST_PROMPT.md` into Codex or Claude Code.

The agent must read only:

- root operating files
- one Work Order
- the Work Order's context set from `PROJECT_MANIFEST.json`

### Step 3: Build the shared standard first

Complete `work_orders/WO-00_SHARED_FOUNDATION.md`.

This locks:

- Role-Backwards Evidence Framework
- AI PM Role Standard
- evidence schemas
- output contract
- initial eval labels

### Step 4: Run Skill and Agent tracks in parallel

Track A:

- `WO-01_SKILL_POC.md`

Track B:

- `WO-02_AGENT_POC.md`

Both use the same schemas and eval cases.

### Step 5: Build the thin Web interface

Only after the Agent contract works:

- `WO-03_THIN_WEB.md`

### Step 6: Compare and validate

Run:

- Generic Prompt vs Skill
- From-scratch Skill rerun vs stateful Agent update
- human reviewer scoring
- failure cases
- token and context measurements

Use `WO-04_EVAL_AND_PILOT.md`.

## Commands

```bash
make validate
make test
make inventory
```

## Current truth

The repository defines the product and implementation contract.

It does not yet prove:

- that the Skill beats a strong generic prompt
- that the Agent creates meaningful stateful value
- that users adopt the generated assets
- that the role standard predicts hiring outcomes

All claims about results must remain labeled as targets until measured.
