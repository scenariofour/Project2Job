# Day 6 — Tools, API, and Safe Failure

Status: PLANNED

## Question

How should tools fail without hiding uncertainty or expanding permissions?

## User value

Users receive clear errors, bounded retries, and safe fallback behavior.

## Core concepts

Read-only tools, schemas, OpenAPI, parameters, error codes, authentication,
authorization, timeout, retry, fallback, and failure injection.

## Product and implementation scope

Define only the interfaces required by observed workflows. Revisit MCP and
framework choices after failure and interoperability evidence.

## Required artifacts

- Typed tool/API contracts and permission table
- Timeout, retry, fallback, and error semantics
- Failure-injection tests and decision records

## Acceptance criteria

- Tools are read-only by default and least-privileged
- Failures remain visible in state and user-facing output
- Retries are bounded and non-destructive

## Evidence

Planned: contract tests, injected failures, latency, and recovery traces.

## Bad case or tradeoff

Automatic retries can improve completion while multiplying cost or repeating an
unsafe action.

## Candidate decision checkpoint

- Decision to make: API shape, MCP need, and framework need
- Considered alternatives: local functions; REST/OpenAPI; MCP; framework runtime
- Expected evidence: interoperability, failure handling, complexity, maintenance
- Final decision after evidence: pending

## What is not yet proven

That MCP or any Agent framework is needed.

## Public content notes

- Demo one timeout and one authorization failure.
- Show parameters and error codes.
- Explain least privilege in product terms.
