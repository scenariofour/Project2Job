# Interview Intelligence and Answer Engine

## Bounded company research

Use one automatic pass. The canonical schema ceilings remain absolute:

| Limit | Maximum |
| --- | ---: |
| search queries | 8 |
| fetched pages | 12 |
| browser/Playwright pages | 3 |
| navigation depth | 1 |
| retained characters per page | 20,000 |
| total tokens | 60,000 |
| retries per page | 1 |
| runtime seconds | 120 |

Declare a smaller Alpha operating budget to leave room for host instructions and
answer synthesis: at most 6 queries, 8 fetched pages, 2 browser pages, 45,000
total tokens, and 90 seconds. Stop before that budget rather than consuming the
schema ceiling. Record every usage field, including total tokens and runtime.

Search official sources first, then independent reports, then aggregators/forums
only for a named gap. Deduplicate canonical URLs before fetch and content after
fetch. Plain read-only fetch is the default. Use browser rendering only after a
selected page returns `render_required`, needs one same-host navigation step, or
cannot be parsed. Retain only spans that answer a named gap.

Stop at the first of: sufficient evidence, exhausted public evidence, budget,
inaccessible sources, conflict requiring disclosure, or tool failure. Record
usage, stop reason, and remaining gaps.

Each item stores exact URL and page location, source date, retrieval date,
freshness, tier, fetch method, company, track, level, location, and stage when
known. Present one report as `reported_once`; do not call stale or JD-inferred
material likely. Show conflicts together and prefer official/newer only with the
disagreement preserved.

## Question universe

Generate and prioritize from official guidance, repeated reports, single reports,
JD tasks, company product/technical surface, track/team/level, project decisions,
strongest evidence, weakest Gates, and common AI PM families.

Use labels:

`confirmed_reported`, `repeatedly_reported`, `single_report`,
`inferred_from_jd`, `company_derived`, `project_triggered`, `gap_attack`,
`general_ai_pm`.

## Answer candidates

For every question generate all seven types internally:

1. Direct Experience
2. Analogous Experience
3. Proposed Development-Stage Experiment or Decision
4. Project Counterfactual
5. Technical Concept Applied to Project
6. Company-Specific Reframing
7. True No-Direct-Experience Answer

Return 3–5 genuinely distinct top directions plus the true
no-direct-experience version. Minor rewrites are not separate candidates.

Rank on interviewer-intent match, project specificity, evidence strength, AI PM
signal density, product judgment, technical depth, result/decision quality,
follow-up defensibility, company relevance, and factual risk. Select the
strongest without making the user choose.

## Compact Answer Lab contract

Return:

1. question, family, interviewer intent, and tested capabilities
2. 3–5 candidate directions with type, evidence/source, strength, why it works,
   factual frame, and risk
3. selected direction and selection reason
4. 30-second answer
5. 60–90-second answer
6. deep-dive outline
7. second-best alternative
8. true no-direct-experience answer
9. at least three follow-up levels with suggested answers
10. minimal confirmation slots and private risks, outside the copyable answers
11. exactly one project upgrade

Answer in the first 1–2 sentences. Use one core story. Keep context shorter than
action, decision, and result. Include a rejected alternative and causal
mechanism. End the main answer on achievement, decision, containment, control,
learning, or role relevance. Select the strongest relevant subset of verified
facts for the question and company. Put unsupported claims, missing validation,
and follow-up risks in private review; disclose a limitation in the main answer
only when asked or when omission would be false or materially misleading.
Company style may not add or strengthen a historical fact.

Use short, conversational sentences. Keep framework names and report-style
factual labels out of the spoken script unless a label is necessary to
distinguish an executed event from a proposal or counterfactual. Use the JD to
choose the story and emphasis; do not append the company name or JD keywords to
the conclusion.

## Experiment boundary

For A/B-test questions distinguish:

- live randomized A/B test
- offline controlled comparison
- before/after evaluation
- proposed product experiment

Do not lead with a refusal. Select the strongest defensible direction, then make
its experiment type explicit. Cover decision, hypothesis, control, variant,
eligible segment, randomization/comparison, primary metric, diagnostics,
guardrails, sample/duration limits, decision rule, result if executed, product
decision, and next test.

## Follow-up defense

Prepare at least three levels around metric choice, alternative, confounding,
rejection rule, cost/latency, sample limits, ownership, and the current unproven
boundary. A polished answer that collapses under the first factual follow-up is
not ready.
