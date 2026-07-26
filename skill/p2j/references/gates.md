# Six-Gate Scoring and Technical Coverage

The Gates are a user-facing projection of the canonical 10 domains, not a second
role model and not a total candidate score.

## Mapping

| Gate | Canonical domains |
| --- | --- |
| 1. Business & User Problem | D1 User and Problem Definition |
| 2. Product & AI Judgment | D2 Product Scope and Prioritization; D3 AI Fit and Model Boundaries |
| 3. Technical Product System | D4 Agent and Workflow Design; D5 Data, Tools, Retrieval, and Context |
| 4. Evaluation, Reliability & Safety | D6 Evaluation and Error Analysis; D7 Reliability, Safety, and Human Control |
| 5. Delivery, Metrics & Learning Loop | D8 Metrics, Cost, and Performance; D9 Delivery and Cross-functional Execution |
| 6. Ownership & Interview Defensibility | D10 Communication and Ownership |

Keep one primary domain per evaluated claim. Use secondary tags only for
retrieval and explanation.

## Brief presentation

The Brief runs the same internal coverage checks but presents five
project-focused dimensions:

| Visible dimension | Internal coverage |
| --- | --- |
| Problem & User Evidence | Business & User Problem |
| Product Judgment | Product & AI Judgment |
| Technical System | Technical Product System |
| Evaluation & Reliability | Evaluation, Reliability & Safety |
| Delivery & Learning Loop | Delivery, Metrics & Learning Loop |

Show `1–5` or `N/A` plus one concise evidence-based explanation for each. Give
an understandable preliminary overall rating without exposing domain IDs,
subdimension arithmetic, raw levels, caps, Gate calculations, or policy
terminology. Ownership is provenance, not a sixth visible score: missing
ownership metadata does not lower project quality, while mixed or conflicting
attribution narrows only the affected external-facing claim.

## Strict 0–5 score

Score every applicable canonical domain first:

- `0` — relevant capability absent from searched permitted evidence
- `1` — mentioned or claimed
- `2` — designed or planned with an inspectable decision artifact
- `3` — implemented with inspectable artifacts
- `4` — executed tests, comparisons, bad cases, or failure validation
- `5` — representative or real-world validation changed a product decision

For a multi-domain Gate, show each domain score and set the Gate score to the
lowest applicable domain score. Exclude `N/A` domains/concepts from this
calculation. If every mapped item is genuinely irrelevant, show Gate `N/A`.
Never add the Gates into a total score.

## Hard caps

Apply all matching caps; the lowest wins:

- no exact source location → maximum `1`
- README-only or self-reported claim → maximum `1`
- design/plan only → maximum `2`
- implementation without executed testing or observed use → maximum `3`
- unconfirmed ownership → ownership-dependent claim and Gate 6 maximum `2`
- unvalidated adoption or business impact → corresponding value claim maximum `3`
- technical term without a decision, exclusion, implementation, or experiment → maximum `1`
- proposed experiment → never score as executed
- synthetic test → never present as production or user validation

State the raw level, applied cap, final score, evidence status, exact source, and
boundary. A cap narrows a claim; it does not convert the evidence status.

## Gate tests

1. Business & User Problem: user, trigger, job, pain, workflow, alternative,
   observation versus assumption, segment, success condition, and discovery-led
   scope change.
2. Product & AI Judgment: AI fit, non-AI baseline, deterministic boundary, MVP,
   rejected scope, build/buy, fallback, abstention, release and kill criteria.
3. Technical Product System: structured output, model choice, context,
   retrieval, provenance, cache, state/action/observation, tools, permissions,
   retry, budget, stop, API/MCP/browser decisions.
4. Evaluation, Reliability & Safety: versioned cases, labels, rubric, human
   review, disagreement, baseline, bad cases, regression, injection, guardrails,
   HITL, recovery, traces.
5. Delivery, Metrics & Learning Loop: release and acceptance, user testing,
   activation/adoption/retention/task success, quality/cost/latency,
   instrumentation, feedback, and changed decisions.
6. Ownership & Interview Defensibility: personal/shared/system ownership,
   stakeholders, ambiguity, conflict, rationale, failure, learning, and
   defensibility at 30 seconds, 60–90 seconds, and deep-dive depth.

## Technical concepts

A concept is covered only by:

1. working implementation with evidence;
2. experiment plus a decision; or
3. reasoned documented exclusion.

Otherwise label `planned`, `mentioned`, or `not-found`. Use `N/A` when the
concept is genuinely unnecessary for this project's user need and architecture.
`N/A` is a decision, not a penalty. Evaluate technical concepts by the decision,
alternative, evidence, failure mode, and evaluation—not keyword density or
component count.

Cover only relevant concepts from model interaction; RAG/retrieval/context;
Agents/tools; evaluation; safety/governance; metrics/economics; and delivery.

## One Next Build

Return exactly one action with:

- gap
- why now
- bounded steps
- acceptance criteria
- expected new evidence and artifact
- output dependency across Gates/questions/stories/bullets
- estimated effort band
- interview question unlocked

Prefer the action that creates the most direct evidence across several important
surfaces. Explicitly reject the runner-up.
