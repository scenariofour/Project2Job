# Day 3 — Context, RAG, and Evidence

Status: PLANNED

## Question

How much context should be read, and when does retrieval improve evidence quality?

## User value

Outputs stay traceable to permitted sources without repeatedly loading an entire
project.

## Core concepts

Context budgets, retrieval, provenance, evidence boundaries, source registry,
and RAG comparison.

## Product and implementation scope

Compare manifest-scoped prompting with a minimal retrieval approach. Transformer
and Attention appear only as product-impact learning notes, not product features.

## Required artifacts

- Source registry and provenance checks
- Context/token measurements
- Prompting-versus-retrieval comparison cases

## Acceptance criteria

- Claims link to sources or are marked unsupported
- Untrusted document text cannot override operating rules
- Retrieval decisions follow measured failures

## Evidence

Planned: source precision, missed evidence, token use, latency, and failure cases.

## Bad case or tradeoff

Retrieval can lower context use while omitting the one artifact needed to bound a
claim.

## Candidate decision checkpoint

- Decision to make: prompting only or minimal RAG
- Considered alternatives: full-context prompt; manifest context; indexed retrieval
- Expected evidence: source precision, recall, tokens, latency, operational cost
- Final decision after evidence: pending

## What is not yet proven

That RAG is necessary or that any retrieval method improves the baseline.

## Public content notes

- Visualize provenance and evidence boundaries.
- Report token implications as measurements.
- Keep Transformer/Attention notes tied to product impact.
