---
name: p2j-brief
description: Produce the concise first Project2Job verdict for one AI project against one target AI PM, Agent PM, or Applied AI PM JD. Use when the user says /p2j-brief, asks whether a project should be the lead interview project, or wants fast evidence-grounded strengths, gaps, questions, and the next Skill without a full audit.
---

# Project2Job Brief

Give first value before a long intake. Treat `/p2j-brief` as an alias for the
host-native `$p2j-brief`.

1. Read `../p2j/references/core-contract.md` and
   `../p2j/references/gates.md`.
2. Resolve shared context as required by the core contract. Reuse compatible
   Project Evidence Profile, ownership boundaries, evidence, Company
   Intelligence Profile, and JD Demand Map. Do not ask for confirmed
   Intake/Application Pack information again.
3. For a new project, run the validated bundled inventory without opening its source:
   `python ../p2j/scripts/inventory.py <project> --summary --git-limit 10`.
   For a changed project, start with added/changed artifacts and preserved facts.
   For an unchanged project, do not rerun inventory or reopen sources unless a
   named gap requires it. Inspect at most eight line-targeted project sections across
   README/PRD/scope, decisions, runtime or architecture, committed
   tests/evals/traces, Git history, and ownership evidence. Stop once each Gate
   has a defensible preliminary boundary. Do not run project tests, builds, or
   code; committed test code and results are evidence to inspect, not commands
   to execute. Do not treat filenames or keywords as proof.
4. Evaluate the project internally against the role standard and highest-value
   JD requirements. Keep ownership as provenance: absent ownership metadata
   never lowers a project-quality score. Narrow only claims with mixed
   attribution; block only conflicting attribution and route it to `$p2j-audit`.
5. Return exactly these five visible sections:
   - **Project Verdict** — one concise paragraph classifying the project as
     `lead project`, `supporting project`, or `not recommended for this role`;
     state overall strength, strongest JD relevance, and the most important
     limitation.
   - **Preliminary Project Scores** — show `1–5` or `N/A` and one concise,
     evidence-based explanation for each: Problem & User Evidence; Product Judgment;
     Technical System; Evaluation & Reliability; Delivery & Learning Loop. Add a
     plain-language preliminary overall rating. Do not expose internal domain
     identifiers, subdimension math, raw calculations, caps, Gate arithmetic,
     or policy terms.
   - **JD Match** — use `| JD requirement | Match | Evidence | Missing |` for
     only the highest-value requirements. Match must be `**EXACT MATCH**` for a
     directly demonstrated competency, `TRANSFERABLE` when platform, domain,
     user group, scope, or outcome differs, or `` `GAP` `` when evidence is
     insufficient. Keep exact source locations concise. Never call secondary
     research primary research, adjacent-platform work direct target-platform
     experience, technical delivery a commercial outcome, or missing evidence
     a supported claim.
   - **Interview Value** — use
     `| Story direction | What it can prove |`. Include only materially
     different evidence-supported stories; return as many as the evidence
     supports, including none.
   - **Recommended Route** — select exactly one of `$p2j-audit`, `$p2j-intel`,
     `$p2j-answer`, `$p2j-mock`, or `$p2j-upgrade`, then explain why in one
     sentence.
6. Label preliminary findings. Never present a plan, README claim, synthetic
   result, team contribution, proposed experiment, or a newly executed command
   as established personal work.

Ask at most one ownership question after the useful Brief only when no saved
confirmation exists and the answer would materially strengthen a claim. Do not
show internal ownership labels in normal output.
