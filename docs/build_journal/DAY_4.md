# Day 4 — Skill, Agent, and Human Control

Status: PLANNED

## Question

Which responsibilities belong to a reusable Skill, a stateful Agent, or the user?

## User value

Users get low-friction first value while retaining control over claims,
corrections, and updates.

## Core concepts

Skill versus Agent, fixed workflow versus autonomy, HITL, corrections, versioned
updates, and dependency invalidation.

## Product and implementation scope

Test the shared contract across one initial analysis and one later update cycle.
No long-term general memory or external action.

## Required artifacts

- Responsibility boundary and approval points
- Correction and invalidation tests
- Update comparison with affected outputs

## Acceptance criteria

- User corrections propagate to dependent claims
- Only affected outputs are regenerated
- External-facing claims require evidence and approval

## Evidence

Planned: correction traces, dependency tests, and fresh-run comparison.

## Bad case or tradeoff

Persistent state reduces repeated work but can preserve stale or incorrect claims.

## Candidate decision checkpoint

- Decision to make: which update responsibilities justify the Agent
- Considered alternatives: Skill only; fixed stateful workflow; bounded Agent
- Expected evidence: repeated reads, correction accuracy, update clarity, friction
- Final decision after evidence: pending

## What is not yet proven

That users need persistent state or that update value exceeds its complexity.

## Public content notes

- Show where human approval changes state.
- Include a stale-claim bad case.
- Explain the Skill and Agent as separate products.
