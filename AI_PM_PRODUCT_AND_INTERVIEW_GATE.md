# AI PM Product and Interview Gate

Use this checklist before approving a release or presenting the project in an interview.

## A. User value

- [ ] The target user and trigger are specific.
- [ ] The output changes a real application, interview, or project decision.
- [ ] The first useful result requires no more than one blocking question.
- [ ] The product creates at least one immediately usable career asset.
- [ ] The system does not expose internal complexity unless requested.
- [ ] The Skill has a reason to exist beyond hiding a prompt.
- [ ] The Agent has a reason to exist beyond putting the Skill in a Web UI.

## B. Product judgment

- [ ] MVP supports one role family, one project, and one primary application.
- [ ] Every P0 feature supports the product promise.
- [ ] Success and stop criteria are defined.
- [ ] Generic Prompt is treated as a serious baseline.
- [ ] Current claims are separated from future vision.
- [ ] A new P0 addition removes or replaces equivalent scope.

## C. AI fit and Agent fit

- [ ] Semantic work requiring a model is named.
- [ ] Deterministic work is kept out of free-form model judgment.
- [ ] Agent autonomy is limited to open-ended evidence investigation.
- [ ] The Agent has an explicit goal, tools, budget, and stop conditions.
- [ ] Agent value is tested against a fixed workflow.
- [ ] Multi-agent and Deep Agent remain experiments until failure data justifies them.

## D. Intent and routing

- [ ] Primary intents are defined at the same decision level.
- [ ] Intents are operationally MECE inside the supported scope.
- [ ] Modifiers do not create hidden duplicate flows.
- [ ] `OUT_OF_SCOPE_OR_UNCLEAR` exists.
- [ ] Low-confidence routing has a bounded default or one clarification.
- [ ] Routing has trigger, non-trigger, and mixed-intent cases.

## E. Evidence and career outputs

- [ ] Role requirements have source provenance.
- [ ] Project claims have source provenance.
- [ ] Evidence boundaries are explicit.
- [ ] Missing evidence is not treated as missing ability.
- [ ] Resume bullets use only supported facts.
- [ ] Interview answers show evidence ingredients and unsupported gaps.
- [ ] One Next Build has an acceptance test and expected evidence.

## F. Context, token, and cost

- [ ] File inventory runs before model analysis.
- [ ] The model receives a task-specific context pack.
- [ ] Repeated file reads are measured.
- [ ] File hashes support caching.
- [ ] Tool outputs have size limits.
- [ ] Turns, tool calls, tokens, latency, and stop reason are logged.
- [ ] Quality is compared at similar cost where practical.
- [ ] Token reduction never silently lowers evidence correctness.

## G. Reliability and safety

- [ ] Uploaded files are treated as untrusted data.
- [ ] Permissions are read-only by default.
- [ ] Sensitive facts require user confirmation.
- [ ] Tool errors remain visible.
- [ ] Failure does not become a fabricated success.
- [ ] Guardrails and human approval have separate responsibilities.
- [ ] User corrections invalidate affected outputs.

## H. Evaluation

- [ ] Component, outcome, process, efficiency, and recovery tests exist.
- [ ] Skill trigger behavior is evaluated.
- [ ] Skill output is compared with a strong generic prompt.
- [ ] Agent updates are compared with fresh Skill reruns.
- [ ] Gold labels include source locations and evidence boundaries.
- [ ] New failures become regression cases.
- [ ] Human reviewer disagreement is recorded.
- [ ] Mock, target, and measured metrics are clearly labeled.

## I. AI PM concept coverage

A concept is considered covered only when the project has one of:

1. a working implementation with evidence
2. an experiment and decision
3. a documented exclusion supported by reasoning and data

Coverage required:

- [ ] problem definition
- [ ] user research and alternatives
- [ ] MVP scoping
- [ ] AI fit
- [ ] Agent fit
- [ ] intent recognition
- [ ] workflow vs Agent
- [ ] tools and function calling
- [ ] Skill design
- [ ] state and session
- [ ] context design
- [ ] retrieval and provenance
- [ ] structured output
- [ ] uncertainty
- [ ] HITL
- [ ] guardrails and permissions
- [ ] stop and retry policy
- [ ] tracing and observability
- [ ] evals
- [ ] failure analysis
- [ ] cost and latency
- [ ] API and MCP decisions
- [ ] architecture tradeoffs
- [ ] user and product metrics

## J. Interview proof

- [ ] A 30-second explanation is clear without technical jargon.
- [ ] A 2-minute story explains problem, choice, system, test, and result.
- [ ] A real trace is available.
- [ ] A real failure and resulting change are available.
- [ ] A baseline comparison is available.
- [ ] The candidate can explain personal ownership.
- [ ] No claim relies only on documents that describe planned work.
