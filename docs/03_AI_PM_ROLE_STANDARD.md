# AI PM Role Standard v0.1

## Scope

This standard covers early-career roles near:

- AI Product Manager
- Agent Product Manager
- Applied AI Product Manager

It is a versioned reference profile, not a claim that every employer uses the same rubric.

A specific JD can reweight or replace individual requirements.

## Source model

The standard is triangulated from:

1. current official AI and Agent product job descriptions
2. skills-based hiring guidance
3. current Agent product and evaluation practices
4. project and interview evidence patterns

See `references/source_registry.json`.

## Capability domains

The domains are operationally MECE for scoring: every evaluated claim receives one primary domain. Secondary tags are allowed for search and explanation.

### D1. User and Problem Definition

Can the candidate identify a real user, task, pain, alternative, and success condition?

Strong project evidence:

- user interviews or task observation
- clear problem statement
- alternative analysis
- narrowed target user
- changed scope after discovery

### D2. Product Scope and Prioritization

Can the candidate choose an MVP, reject attractive features, and define release criteria?

Evidence:

- MVP contract
- decision log
- excluded features
- hypothesis and kill criteria
- staged release

### D3. AI Fit and Model Boundaries

Can the candidate explain why AI is appropriate and where it should not decide?

Evidence:

- baseline without AI
- model task definition
- known failure boundaries
- rules vs model split
- fallback behavior

### D4. Agent and Workflow Design

Can the candidate distinguish deterministic flow, LLM workflow, and Agent autonomy?

Evidence:

- Agent contract
- state and stop conditions
- tool decisions
- approval points
- comparison with fixed workflow

### D5. Data, Tools, Retrieval, and Context

Can the candidate design reliable access to information and actions?

Evidence:

- tool schemas
- retrieval tests
- source metadata
- context selection
- caching
- permission design
- API and MCP decisions

### D6. Evaluation and Error Analysis

Can the candidate define quality, build evals, classify failures, and use results?

Evidence:

- labeled cases
- metrics
- graders and human review
- bad cases
- before-and-after comparison
- regression tests

### D7. Reliability, Safety, and Human Control

Can the candidate handle errors, uncertainty, sensitive actions, and recovery?

Evidence:

- guardrails
- HITL
- retries and budgets
- fail-closed behavior
- prompt-injection handling
- privacy design

### D8. Metrics, Cost, and Performance

Can the candidate measure user value and system efficiency?

Evidence:

- product metrics
- task success
- token usage
- cost and latency
- quality-cost tradeoff
- activation or retention behavior

### D9. Delivery and Cross-functional Execution

Can the candidate move from idea to shipped system and coordinate disciplines?

Evidence:

- implementation plan
- interface contracts
- feedback to engineering/design
- release decisions
- tradeoff communication
- working product

### D10. Communication and Ownership

Can the candidate clearly explain personal decisions, limitations, and impact?

Evidence:

- ownership map
- concise project story
- defended decisions
- honest limitations
- artifacts tied to personal work

## Project scoring rule

Career Desk does not create a single candidate score.

For each role requirement, it reports:

- relevance
- evidence status
- evidence quality
- source
- boundary
- recommended use

## Operational evidence tests

The reviewed profile instance is
`references/role_profiles/ai_pm_early_career.v0.1.0.json`. Each capability has
one claim-level evidence test and one matching gold case.

| Domain | Evidence test | Minimum direct evidence |
| --- | --- | --- |
| D1 | `ET-D1-01` | User/task observation connected to a bounded decision |
| D2 | `ET-D2-01` | Scope choice, rejected alternative, reason, and release boundary |
| D3 | `ET-D3-01` | Executed AI/non-AI comparison plus boundary or fallback |
| D4 | `ET-D4-01` | State, action/observation, stop, and approval contract with test or trace |
| D5 | `ET-D5-01` | Provenance, context, permission, and failure contracts with tests |
| D6 | `ET-D6-01` | Versioned labels, executed results, disagreement, and failure analysis |
| D7 | `ET-D7-01` | Named control with an enforced failure or adversarial test |
| D8 | `ET-D8-01` | Versioned measurements connected to a decision |
| D9 | `ET-D9-01` | Released scope, acceptance results, owners, and decision follow-through |
| D10 | `ET-D10-01` | Contribution artifacts plus confirmed personal ownership and limits |

Design or planning artifacts can support a narrower design/planning claim but
cannot establish execution or results. JD overrides affect relevance and which
5–7 domains appear in the Role Fit Map; they do not change evidence labels or
create a total candidate score.

## Role profile lifecycle

- version the source set
- preserve source links and dates
- record changes
- re-run gold labels when the profile changes
- allow the target JD to override weights
- retire rather than overwrite a released profile instance
- distinguish structural/gold-case validation from hiring-outcome validation
