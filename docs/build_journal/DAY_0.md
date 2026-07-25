# Day 0 — Safe Foundation

Status: IN PROGRESS

## Question

Can Project2Job begin from a public, reproducible repository without overstating
what has been built or exposing private source material?

## User value

Contributors can inspect scope, safety rules, interfaces, and planned validation
before runtime work begins.

## Core concepts

Repository truth, least privilege, read-only inputs, untrusted document content,
rollback through Git, reproducible checks, and claims bounded by evidence.

## Product and implementation scope

Import v6 at the existing repository root, preserve the MIT history and license,
add the public journal, and validate the foundation. No Skill runtime, Agent,
Web UI, RAG, evaluation harness, framework, MCP, or multi-agent feature is built.

## Required artifacts

- Existing Git repository on `day0-foundation`
- v6 root files, 14 active product documents, Work Orders, schemas, fixtures,
  tests, Skill source, and implementation interfaces
- Day 0–Day 7 journal and implementation map
- Safety-oriented `.gitignore`, truthful README/status, and decision record

## Acceptance criteria

- Required checks pass and the MIT license is unchanged
- Public fixtures contain no identifying or private data
- Unsafe/generated files are not tracked
- Day 1–Day 7 remain `PLANNED`
- Changes are committed; push and draft PR are attempted when authenticated

## Evidence

- Source: read-only `Career_Desk_Final_Build_System_v6`; manifest version `6.0`
- `git clone https://github.com/irisli0926/Project2Job.git Project2Job`: PASS
- `git fetch origin --prune`: PASS; `origin/main` at `60388e6`
- `git status --porcelain` before import: PASS, no local changes
- `sed -n '1,80p' LICENSE`: PASS, MIT License retained
- Initial `make validate`, `make test`, and `make inventory`: PASS
- Changed files: all paths in `FILE_LIST.txt` except the excluded
  `dist/career-desk-project-to-application-skill_v1.zip`; added
  `docs/build_journal/`; Day 0 reconciliation changes will be listed in Git

## Bad case or tradeoff

Committing the generated Skill ZIP would make distribution convenient, but its
rebuild process is undocumented. It is excluded until a reproducible release
process exists.

## Candidate decision checkpoint

- Decision to make: whether this repository is safe to use as the build baseline
- Considered alternatives: import v6; redesign first; retain only product docs
- Expected evidence: clean audit, passing checks, bounded scope, reproducible setup
- Final decision after evidence: pending final Day 0 validation

## What is not yet proven

Skill or Agent behavior, user value, quality, latency, tokens, cost, comparative
model performance, adoption, and hiring outcomes.

## Public content notes

- Show the difference between a designed system and an implemented product.
- Explain why read-only sources and prompt-injection fixtures matter.
- Publish commands and failures, not private inputs.
- Do not present target metrics as results.
