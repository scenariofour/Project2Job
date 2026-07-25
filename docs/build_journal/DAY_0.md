# Day 0 — Safe Foundation

Status: IMPLEMENTED

Repository note: the canonical GitHub owner is now `scenariofour`. The original
Day 0 commands, URLs, and results below are preserved as the execution record.

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
- `git status --short --branch`: PASS, `## day0-foundation` before push
- `git remote -v`: PASS, fetch and push use
  `https://github.com/irisli0926/Project2Job.git`
- `git diff --check`: PASS, no output
- `make validate`: PASS; 14 active docs, 9 JSON files, 21 JSONL cases,
  12 public fixture files, 8 journal days, MIT license
- `make test`: PASS, 3 of 3 tests
- `make inventory`: PASS, 3 synthetic sample-project files inventoried
- `git ls-files | grep -E '(__pycache__|\.pyc$|\.env|\.DS_Store|\.log$)'`:
  PASS, no output
- Changed files: imported every path in `FILE_LIST.txt` except
  `dist/career-desk-project-to-application-skill_v1.zip`; normalized existing
  trailing whitespace in `lab/scoring_rubric.md`; added the 10 files in
  `docs/build_journal/`; reconciled `.gitignore`, `README.md`, `START_HERE.md`,
  `CODEX_FIRST_PROMPT.md`, `PROJECT_STATUS.md`, `docs/13_DECISION_LOG.md`, and
  `scripts/validate_repo.py`

## Bad case or tradeoff

Committing the generated Skill ZIP would make distribution convenient, but its
rebuild process is undocumented. It is excluded until a reproducible release
process exists.

## Candidate decision checkpoint

- Decision to make: whether this repository is safe to use as the build baseline
- Considered alternatives: import v6; redesign first; retain only product docs
- Expected evidence: clean audit, passing checks, bounded scope, reproducible setup
- Final decision after evidence: accept the repository as the Day 0 build baseline

## What is not yet proven

Skill or Agent behavior, user value, quality, latency, tokens, cost, comparative
model performance, adoption, and hiring outcomes. Days 1–7 and all Work Order
implementation remain planned.

## Public content notes

- Show the difference between a designed system and an implemented product.
- Explain why read-only sources and prompt-injection fixtures matter.
- Publish commands and failures, not private inputs.
- Do not present target metrics as results.
