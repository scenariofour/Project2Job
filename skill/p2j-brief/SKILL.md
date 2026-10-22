---
name: p2j-brief
description: Produce the concise first Project2Job positioning for one AI project against one target AI PM, Agent PM, or Applied AI PM JD. Use when the user says /p2j-brief, asks whether a project should be the lead interview project, or wants the strongest evidence-grounded positioning and one recommended route without a full audit.
---

# Project2Job Brief

Give first value before a long intake. Treat `/p2j-brief` as an alias for the
host-native `$p2j-brief`.

1. Read `../p2j/references/core-contract.md` and
   `../p2j/references/gates.md`.
2. Resolve shared context as required by the core contract. Reuse the Project
   Evidence Profile, ownership boundaries, evidence, a fresh Company
   Intelligence Profile for the exact normalized company and track, and the JD
   Demand Map bound to that Company profile. If the Company profile is missing,
   stale, or materially changed, invoke one bounded `$p2j-intel` pass before
   writing the Brief. Do not claim company or culture adaptation without that
   context. Do not ask for confirmed Intake/Application Pack information again.
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
   JD requirements. Keep the full five-dimension `1–5` or `N/A` scoring and
   `EXACT MATCH` / `TRANSFERABLE` / `GAP` assessment internal. Keep ownership as
   provenance: absent ownership metadata never lowers a project-quality score.
   Narrow only claims with mixed attribution; block only conflicting
   attribution and route it to `$p2j-audit`.
5. Return exactly these five visible sections:
   - **Project Verdict** — one concise paragraph classifying the project as
     `lead project`, `supporting project`, or `not recommended for this role`;
     state one strongest positioning and its company- and JD-specific hiring
     value.
   - **Strongest Demonstrated Signals** — show only the strongest
     evidence-supported signals from Problem & User Evidence; Product Judgment;
     Technical System; Evaluation & Reliability; and Delivery & Learning Loop.
     Do not show numeric scores, low-confidence dimensions, internal domain
     identifiers, calculations, caps, policy terms, a weakness list, or a gap
     inventory.
   - **JD Match** — use `| JD requirement | Match | Evidence |` for only the
     strongest supported requirements. Match must be `**EXACT MATCH**` for a
     directly demonstrated competency or `TRANSFERABLE` when platform, domain,
     user group, scope, or outcome differs. Do not display `GAP` rows. Keep
     insufficient-match assessment internal for Private Defense or route the
     single highest-value improvement to `$p2j-upgrade`. Never call secondary
     research primary research, adjacent-platform work direct target-platform
     experience, technical delivery a commercial outcome, or missing evidence
     a supported claim.
   - **Interview Value** — use
     `| Strongest story | What it can prove |`. Return exactly one strongest
     evidence-supported story and positioning. If no story is defensible, say
     so in one sentence and route to `$p2j-audit` or `$p2j-upgrade`; do not
     substitute a weakness list.
   - **Recommended Route** — select exactly one of `$p2j-audit`, `$p2j-intel`,
     `$p2j-answer`, `$p2j-mock`, or `$p2j-upgrade`, then explain why in one
     sentence.
6. Keep factual risks, unsupported claims, hard follow-ups, and evidence gaps
   out of the visible Brief. Preserve them in Private Defense for `$p2j-mock`
   or hand the single highest-leverage evidence gap to `$p2j-upgrade`.
7. Label preliminary findings. Never present a plan, README claim, synthetic
   result, team contribution, proposed experiment, or a newly executed command
   as established personal work.

Ask at most one ownership question after the useful Brief only when no saved
confirmation exists and the answer would materially strengthen a claim. Do not
show internal ownership labels in normal output.
