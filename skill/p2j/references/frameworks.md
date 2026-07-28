# Interview Framework Registry

Choose by question family → intent → evidence/candidates → base framework →
company adapter → time limit. Use frameworks internally; write natural answers.

## Behavioral

### PARADE+

Use for decisions, ambiguity, failure, conflict, leadership, and changed beliefs:

Problem → Anticipated consequence → personal Role → Alternatives and Action →
Decision rationale → Evidence and Result → Learning and Next Decision.

### STAR-L

Use when official guidance expects STAR or time is tight. Keep Situation and Task
short; include alternatives and decision rationale inside Action; end with
Learning.

### FLAIR

Use for failure: Product/user problem → relevant Failure signal → Loss/risk →
containment and root cause → product change or decision → result/control →
repeat-prevention and role-relevant judgment. Require a mechanism that reduces
recurrence. End on that mechanism, decision, result, or capability—not on the
failure signal, an unrelated disclaimer, or pending work.

### ALIGN

Use for conflict: Actors/goals → Latent tradeoff → Information/evidence →
Governance mechanism → Next commitment. Allow evidence to change the
candidate's view.

### Ambiguity and ownership

For ambiguity: name unknowns, separate assumptions, classify reversibility,
choose the smallest test, make a bounded decision, and define change evidence.

For every behavioral answer separate `MINE`, `SHARED`, and `SYSTEM`, and mark
what still needs confirmation.

## Project introduction

- 30 seconds: target user/workflow → product/AI approach → ownership → strongest
  current achievement, decision, or control → role relevance.
- 90 seconds: user/problem → inadequate alternative → MVP/system choice →
  defining tradeoff → bad case/change → containment or product decision →
  result/control → role relevance.
- Deep dive: prepare branches for discovery, scope, AI fit, architecture,
  context/retrieval, evals, reliability, economics, delivery, ownership, and
  learning rather than one monologue.

Apply the material-disclosure rule before adding a limitation to an
introduction. If disclosure is necessary, state it briefly without letting it
become the final emphasis.

## Technical

### DATER

Use for RAG, embeddings, fine-tuning, RLHF/DPO, structured output, tool calling,
model routing, memory, MCP, or guardrails:

Definition → Application/non-application → Tradeoffs/alternatives → Evaluation →
Risks/boundary. Answer directly in the first sentence.

### BOUND

Use for system design:

Business/user requirement → Operational constraints → User/data flow →
Necessary components/boundaries → Alternatives/tradeoffs →
Reliability/safety/human control → Evaluation/observability →
Cost/latency/scale → Rollout/recovery.

Every component needs a user or operational reason.

### Why Agent

Identify the decision that cannot be fixed in advance; define state,
observation, actions, tools, permissions, and Continue/Adjust/Ask/Stop; compare
with a deterministic workflow; cite tests/traces; state what remains unvalidated.

### Model selection

Define task/quality threshold and constraints; establish a baseline; compare
models on the same cases; add routing/fallback only if useful; choose on the
quality-cost-performance frontier; monitor drift/regression.

### Prompting, RAG, fine-tuning, RLHF, and DPO

- Prompting: instructions/examples suffice; no changing external knowledge or
  durable learned behavior is required.
- RAG: attributable or changing external knowledge must be retrieved.
- Fine-tuning: repeated behavior remains unstable after prompt/workflow
  improvement and enough quality training data exists.
- RLHF/DPO: preference alignment is the product problem, preference data exists,
  and benefit justifies training and regression risk.

Apply the conditions to the project. `N/A` or a simpler design can be the
strongest answer.

## Experiments and metrics

For experiments use: decision → hypothesis → control/variant → segment and
randomization/comparison → primary/diagnostic/guardrail metrics → duration/sample
limits → decision rule → result if executed → product decision → next test.

For metrics use GIMME: Goal → user Intent/behavior → Main metric →
Mechanism/input metrics → Monitor/guardrails → Evaluation cadence and decision.

For model underperformance use SLICE: Signal → Locate by segment/stage →
Immediate containment → Cause hypotheses → Experiment and regression.

## Product and strategy

For AI product design use WORKBACK-AI: goal/why now → segment → workflow and
alternative → pain → non-AI baseline → AI advantage/uncertainty → prioritized
solution → system boundary → failure UX/control → metrics → rollout/learning.

For prioritization, choose and explicitly reject one alternative. For strategy,
cover objective, user/buyer, alternatives, AI advantage, distribution,
defensibility, risks, sequencing, metrics, and decision points.

## Company adapters

Research adapters; never infer them from reputation.

Use an adapter to select the strongest relevant story, terminology, and
emphasis. Keep the facts project-grounded. Do not force a company name,
principle, or copied JD phrase into the final sentence.

### Amazon

When current official guidance supports it, use STAR-L outside and decision
rationale, data, personal ownership, and repeatable mechanisms inside. Lead with
customer need where relevant. Map reusable stories to primary/secondary
Leadership Principles and tensions; never force every principle into one story.

### OpenAI

When current official guidance supports it, lead with a thesis, expose reasoning
and alternatives, show technical/product depth, state safety/reliability limits,
name what changed the candidate's mind, and prepare for stretch questions.

### Generic adapter record

Store company, role/track, official principles/guidance, preferred answer shape,
detail and metric expectations, technical depth, writing/case components,
follow-up style, disallowed overclaims, exact sources, freshness, and confidence.
The adapter changes emphasis, never project facts.
