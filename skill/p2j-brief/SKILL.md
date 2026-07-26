---
name: p2j-brief
description: Produce the concise first Project2Job verdict for one AI project against one target AI PM, Agent PM, or Applied AI PM JD. Use when the user says /p2j-brief, asks whether a project should be the lead interview project, or wants fast evidence-grounded strengths, gaps, questions, and the next Skill without a full audit.
---

# Project2Job Brief

Give first value before a long intake. Treat `/p2j-brief` as an alias for the
host-native `$p2j-brief`.

1. Read `../p2j/references/core-contract.md` and
   `../p2j/references/gates.md`.
2. Run the validated bundled inventory without opening its source:
   `python ../p2j/scripts/inventory.py <project> --summary --git-limit 10`.
   Then inspect at most eight line-targeted project source sections across
   README/PRD/scope, decisions, runtime or architecture, committed
   tests/evals/traces, Git history, and ownership evidence. Stop once each Gate
   has a defensible preliminary boundary. Do not run project tests, builds, or
   code; committed test code and results are evidence to inspect, not commands
   to execute. Do not treat filenames or keywords as proof.
3. Map the JD to the canonical 10 domains, then summarize them through the six
   user-facing Gates. Apply every cap before showing a preliminary score.
4. Return only:
   - Project Verdict — 2–3 sentences
   - Preliminary Gate Scores — six lines with score or `N/A`, boundary, and one
     exact source location
   - Strongest Proofs — 3
   - Highest-Risk Gaps — 3
   - Best Story Opportunities — 3
   - Highest-Priority Questions — 8
   - Recommended Next Step — exactly 1 Skill or action
5. Label preliminary findings. Never present a plan, README claim, synthetic
   result, team contribution, proposed experiment, or a newly executed command
   as established personal work.

Ask at most one ownership confirmation after the useful brief when it would
materially strengthen an external-facing claim.
