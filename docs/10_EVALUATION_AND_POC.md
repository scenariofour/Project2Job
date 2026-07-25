# Evaluation and Proof-of-Concept Plan

## What can be evaluated before a broad user launch

- role standard quality
- intent routing
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
- requirement extraction
- claim extraction
- retrieval
- source mapping
- output validation

### Outcome

- Role Fit Map correctness
- Project Highlight grounding
- resume bullet grounding
- interview question relevance
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
- prompt injection
- source conflict
- user correction
- interrupted update

## PoC gates

### Skill PoC passes when

- valid installable package exists
- trigger and non-trigger tests pass
- output schema passes
- no severe unsupported career claim in gold cases
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
- users mainly want generic resume rewriting
- source error rate remains unsafe
- project upload cost exceeds perceived value
- Agent update provides no measurable advantage
- outputs are impressive but rarely adopted
