# Career Evidence Agent

## Problem

Early-career AI PM candidates build projects quickly but struggle to determine which project decisions and artifacts are credible evidence for a target role.

## Product decision

The product links role requirements to project claims and original project sources. It separates Supported, Partially Supported, Inferred, Missing, and Conflicting claims.

## Agent design

A single Evidence Investigator chooses which claim to inspect, searches permitted project material, reads the original source, updates the evidence state, and stops when the evidence boundary is clear.

## Evaluation plan

The project will compare a strong one-shot prompt, a fixed workflow, and the Agent on source precision, unsupported claims, repeated reads, latency, and cost.

## Current status

The product and schemas are defined. Live Agent results and user outcomes have not been measured yet.
