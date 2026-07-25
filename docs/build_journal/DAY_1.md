# Day 1 — Agent Loop

Status: PLANNED

## Question

What is the smallest observable loop that can investigate evidence safely?

## User value

The user can see why the system continued, adjusted, asked, or stopped.

## Core concepts

Action, observation, state, stop conditions, budgets, traces, and bad cases.

## Product and implementation scope

Define and test one bounded loop contract. Do not add multiple agents,
frameworks, or autonomous external actions.

## Required artifacts

- State transition and stop-condition tests
- Trace format with visible tool failures
- Bad cases for contradiction, missing evidence, and exhausted budgets

## Acceptance criteria

- Every step maps action and observation into explicit state
- Continue/adjust/ask/stop paths are testable
- Loop terminates within configured budgets

## Evidence

Planned: deterministic tests and inspected traces from labeled cases.

## Bad case or tradeoff

More autonomy may find evidence faster while making control and failure diagnosis
harder.

## Candidate decision checkpoint

- Decision to make: fixed workflow or bounded Agent loop
- Considered alternatives: one-shot prompt; fixed steps; adaptive single Agent
- Expected evidence: trace quality, completion, error rate, token/tool counts
- Final decision after evidence: pending

## What is not yet proven

That an Agent loop adds value over a strong prompt or fixed workflow.

## Public content notes

- Animate state changes, not hidden reasoning.
- Include one stop-condition failure.
- Separate loop mechanics from user-value claims.
