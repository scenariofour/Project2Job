# Agent Architecture

## Architecture principle

Use the smallest amount of autonomy that improves evidence quality.

## System layers

```text
Input and Inventory
→ Role and Claim Extraction
→ Evidence Investigator
→ Evidence Validation
→ Career Output Generation
→ User Correction
→ State and Update
```

## Deterministic services

- file inventory
- source IDs
- hashes and change detection
- permission checks
- schema validation
- caches
- budgets
- state transitions
- dependency invalidation
- export validation

## Constrained LLM workflows

- requirement extraction
- claim extraction
- capability mapping
- resume language generation
- interview question generation
- concise explanations

## Core Agent

### Name

Evidence Investigator

### Goal

For a high-value role requirement or project claim, find support, contradiction, or a defensible evidence boundary inside permitted project sources.

### Inputs

- requirement
- claim
- allowed sources
- existing evidence
- state summary
- remaining budget

### Tools

- inventory_sources
- search_sources
- read_source
- compare_evidence
- request_confirmation
- submit_evidence_result

### Decisions

- which claim to inspect next
- which source or query to use
- whether evidence is sufficient
- whether to narrow a claim
- whether to ask the user
- whether to stop

### Stop conditions

- evidence sufficient for bounded claim
- permitted sources searched and no evidence found
- conflict requires user confirmation
- budget reached
- unrecoverable tool failure
- policy boundary reached

## Agent loop

```text
observe current claim and state
→ choose one action
→ call one tool
→ inspect result
→ update evidence state
→ continue, ask, or stop
```

## Baselines

Every Agent experiment compares with:

1. strong one-shot prompt
2. fixed extract-search-validate workflow

## Framework decisions

### OpenAI Agents SDK

Candidate for the first controlled Agent runtime because it supports tools, guardrails, sessions, and tracing.

### LangGraph

Evaluate after a real need for durable pause, checkpoint recovery, or complex conditional execution appears.

### Multi-agent

Excluded from MVP.

### Deep Agent

Excluded from MVP.

### MCP

Use later to expose Career Desk tools to external Agent clients or add a measured source connector. It is not the domain architecture.
