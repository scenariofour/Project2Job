# Day 2 — Problem, MVP, and Intent

Status: PLANNED

## Question

Which user trigger merits AI assistance, and what belongs outside the MVP?

## User value

One project and one role become a focused analysis instead of a broad career
automation workflow.

## Core concepts

Target user, trigger, workaround, AI fit, Agent fit, capability boundaries,
prioritization, and MECE intent routing.

## Product and implementation scope

Test `APPLICATION_PACK`, `PROJECT_COMPASS`, `UPDATE`, and
`OUT_OF_SCOPE_OR_UNCLEAR` against the locked one-project/one-role boundary.

## Required artifacts

- Intent labels and ambiguous/out-of-scope cases
- Prioritized capability map
- Explicit MVP and non-goal review

## Acceptance criteria

- Routes are mutually distinguishable and collectively cover supported inputs
- Unsupported requests do not expand scope
- At most one safe blocking question precedes first value

## Evidence

Planned: reviewer agreement and routing test results on labeled inputs.

## Bad case or tradeoff

Fine-grained intent labels can feel precise while increasing ambiguity and
maintenance cost.

## Candidate decision checkpoint

- Decision to make: retain or revise the four primary intents
- Considered alternatives: one universal flow; more task-specific intents
- Expected evidence: routing errors, reviewer disagreement, user friction
- Final decision after evidence: pending

## What is not yet proven

That the defined trigger is urgent or that users prefer this workflow.

## Public content notes

- Show the current workaround before the feature map.
- Explain exclusions as prioritization.
- Label AI fit and Agent fit separately.
