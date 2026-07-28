---
name: p2j-answer
description: Generate and rank evidence-grounded answer directions for one AI PM, Agent PM, or Applied AI PM interview question using one selected project and company context. Use when the user says /p2j-answer or asks for 30-second, 60–90-second, deep-dive, alternative, true no-direct-experience, technical, experiment, behavioral, or follow-up-defense answers.
---

# Project2Job Answer Lab

Treat `/p2j-answer` as an alias for `$p2j-answer`.

1. Read `../p2j/references/core-contract.md`,
   `../p2j/references/interview-engine.md`, and
   `../p2j/references/frameworks.md`.
2. Resolve shared context, then identify the question family and interviewer
   intent. Use the latest compatible supported claims and confirmed ownership
   from Brief/Audit first; never use a claim invalidated by changed evidence.
   Otherwise reconstruct relevant events
   from at most twelve line-targeted sections across original files, Git,
   committed tests, evals, traces, and decisions. Do not execute project code or
   tests. When an implemented-versus-specified distinction changes the answer,
   reserve at least one section for the implementation and one for its committed
   test, trace, or result. If those sources are not inspected, say `not
   inspected`; do not turn that search omission into `Needs Confirmation`.
3. Generate all seven candidate types internally: direct, analogous, proposed
   development-stage, counterfactual, technical-applied, company-reframed, and
   true no-direct-experience. A missing exact event triggers `Adjust`, never a
   dead end.
4. Rank distinct directions on intent match, specificity, evidence, AI PM
   signal, judgment, technical depth, result, defensibility, company relevance,
   and factual risk. Select the strongest; do not ask the user to choose.
5. Apply the career-asset packaging policy in the shared contract, then route
   through the question-family framework and company adapter. Company and
   question context may select and reorder a relevant subset of verified facts;
   it may never add or strengthen a historical fact.
6. Return the compact Answer Lab contract from
   `../p2j/references/interview-engine.md`, including 30-second, 60–90-second,
   deep-dive, second-best, true no-direct-experience, at least three follow-up
   levels, minimal confirmation slots, private risks, and one project upgrade.

Use `Observed`, `Derived`, `Strongly Inferred`, `Proposed During Development`,
`Counterfactual`, or `Needs Confirmation` explicitly whenever the distinction
protects factual truth. Never write a proposed event as history.
