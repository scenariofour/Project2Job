# Day 5 — Evaluation and Model Decisions

Status: PLANNED

## Question

Does Project2Job outperform a strong prompt, and what model approach is justified?

## User value

Architecture choices are tied to reliable, usable outputs rather than novelty.

## Core concepts

Prompt baseline, Skill and Agent comparisons, annotation, grader disagreement,
bad cases, regression, model benchmarking, and decision thresholds.

## Product and implementation scope

Run offline comparisons for prompting, Skill, Agent, and candidate models. Decide
among prompting, RAG, and fine-tuning; do not claim production A/B testing.

## Required artifacts

- Versioned cases, gold labels, and annotation guide
- Blind review and grader disagreement log
- Quality, latency, token, and cost comparison

## Acceptance criteria

- Severe fabricated claims are reported regardless of averages
- Targets and measurements are visibly separate
- Behavior changes add regression cases

## Evidence

Planned: reproducible runs, human scores, disagreements, and bad-case taxonomy.

## Bad case or tradeoff

Aggregate scores can hide a career-damaging unsupported claim.

## Candidate decision checkpoint

- Decision to make: prompt, RAG, fine-tuning, and model/runtime choice
- Considered alternatives: strong prompt; Skill; bounded Agent; model variants
- Expected evidence: quality, severe errors, latency, tokens, cost, usability
- Final decision after evidence: pending

## What is not yet proven

Any comparative advantage, model-performance target, or production impact.

## Public content notes

- Publish the baseline prompt.
- Lead with bad cases and disagreement.
- Never rename an offline comparison as an A/B test.
