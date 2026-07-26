---
name: p2j-audit
description: Run a deep Project2Job evidence audit for one selected AI project and target AI PM, Agent PM, or Applied AI PM JD. Use when the user says /p2j-audit or asks for strict six-Gate 0–5 scoring, canonical 10-domain mapping, technical concept coverage, source-backed claims, hard caps, interview risks, or one highest-leverage Next Build.
---

# Project2Job Audit

Treat `/p2j-audit` as an alias for `$p2j-audit`.

1. Read `../p2j/references/core-contract.md` and
   `../p2j/references/gates.md`.
2. Inventory before analysis. Inspect project facts across files, Git history,
   decisions, committed tests, evals, traces, failures, release evidence,
   feedback, and ownership records. Use no more than six evidence searches and
   four rereads for any high-value claim and no more than twenty line-targeted
   source sections overall. Do not concatenate whole files or the repository
   into context. Search a named claim, reread the original source, update its
   evidence state, then Continue / Adjust / Ask / Stop. Inspect existing
   results; do not execute project tests or code.
3. Map each claim to one primary canonical domain and optional secondary
   retrieval tags. Map domains to six Gates only for the user-facing summary.
4. Apply score caps mechanically. Exclude genuinely irrelevant technical
   concepts as `N/A`; do not reward term density or component count.
5. Return:
   - six Gate scores with mapped domains, sub-capabilities, caps, exact sources,
     status, and boundary
   - technical concepts as `implemented`, `experiment-plus-decision`,
     `reasoned-exclusion`, `planned`, `mentioned`, `not-found`, or `N/A`
   - strongest evidence and safest interview claims
   - dangerous claims and likely follow-up attacks
   - exactly one Next Build using the required contract

Ask no more than one pre-value question. Ownership uncertainty caps the affected
claim; it does not block the rest of the audit.
