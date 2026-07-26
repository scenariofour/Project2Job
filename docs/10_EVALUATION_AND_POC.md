# Evaluation and Proof-of-Concept Plan

## What can be evaluated before a broad user launch

- role standard quality
- intent routing
- JD extraction correctness and unknown handling
- project routing: does the recommended project match a reviewer's pick
- interview source-status labeling, freshness, and conflict handling
- answer-draft claim safety and emphasis invariance
- source correctness
- claim boundaries
- resume grounding
- interview relevance
- tool choice
- stop behavior
- failure handling
- token and context behavior
- consistency across Skill hosts
- Agent update correctness

## What requires user behavior

- onboarding friction
- which output matters most
- asset adoption
- project changes
- repeated use
- willingness to maintain a Career Evidence OS
- recommendation or payment

## Comparison A: Generic Prompt vs Skill

Strong baseline prompt:

> Read this project and target JD. Identify the role capabilities the project supports, produce grounded resume bullets, prepare role-relevant interview questions, and recommend the highest-priority project improvement. Do not invent facts.

Compare:

- source precision
- unsupported claim rate
- role relevance
- output usability
- action specificity
- first-result time
- questions before value
- user and reviewer preference

## Comparison B: Fresh Skill vs Stateful Agent Update

Scenario:

- initial project analyzed
- user adds a new eval file or completes One Next Build
- compare fresh Skill rerun with Agent update

Measure:

- repeated reads
- repeated questions
- cost
- latency
- changed-claim detection
- dependent-output updates
- stale output rate
- change explanation quality

## Evaluation layers

### Component

- artifact inventory
- intent routing
- JD intake extraction
- resume project candidate extraction
- project recommendation
- interview signal labeling
- requirement extraction
- claim extraction
- retrieval
- source mapping
- output validation

### Outcome

- Intake Result usefulness from a JD alone
- project recommendation agreement with reviewers
- Role Fit Map correctness
- Project Highlight grounding
- resume bullet grounding
- interview question relevance and correct source status
- answer-draft grounding and boundary discipline
- Next Build quality

### Process

- tool selection
- source reread before verification
- unnecessary search
- ask timing
- stop timing

### Efficiency

- token usage
- tool calls
- repeated reads
- cost
- latency

### Recovery

- unreadable file
- empty retrieval
- schema error
- prompt injection, including in a JD or a pasted interview report
- source conflict
- conflicting or stale interview reports
- no resume supplied
- no project clearly matching the role
- user correction
- interrupted update

## PoC gates

### Intake PoC passes when

- one pasted JD alone produces a usable Intake Result
- extracted company, role family, level, and track match the JD, with everything
  unstated recorded as unknown
- the recommended project matches a reviewer's pick on labeled routing cases
- no interview item is presented more strongly than its source status allows
- `lab/evals/day2_jd_first_cases.jsonl` passes

### Skill PoC passes when

- valid installable package exists
- trigger and non-trigger tests pass
- output schema passes
- no severe unsupported career claim in gold cases
- no answer draft exceeds its verified evidence
- company emphasis changes wording without changing fact sets
- blind reviewer preference over generic prompt is positive
- output is usable with minor editing

### Agent PoC passes when

- state survives sessions
- project version changes are detected
- affected claims update correctly
- dependent outputs update
- update run reduces repeated work
- traces and budgets are visible

### User-value PoC passes when

- target users receive a useful asset
- at least one user changes a project or career output
- friction is acceptable relative to value
- users can understand and correct the result

## Kill or pivot criteria

- Skill does not beat the strong prompt on meaningful quality or usability
- the project recommendation is no better than the user's own first instinct
- users mainly want generic resume rewriting
- users will not paste interview material, leaving company context permanently thin
- source error rate remains unsafe
- project upload cost exceeds perceived value
- Agent update provides no measurable advantage
- outputs are impressive but rarely adopted
