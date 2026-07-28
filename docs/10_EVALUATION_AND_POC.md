# Evaluation and Proof-of-Concept Plan

## What can be evaluated before a broad user launch

- role standard quality
- intent routing
- JD extraction correctness and unknown handling
- project routing: does the recommended project match a reviewer's pick
- research: official-first ordering, deduplication, Playwright escalation
  discipline, budget adherence, and stop-reason correctness
- resilience to inaccessible pages and to injection in fetched pages
- interview source-status labeling, freshness, and conflict handling
- answer-draft claim safety and bounded company/question emphasis
- source correctness
- claim boundaries
- resume grounding
- interview relevance
- tool choice
- stop behavior
- failure handling
- token and context behavior
- selective Skill invocation and explicit Full Preparation
- Project Evidence Profile reuse across JDs
- Company Intelligence Profile reuse, freshness, and material-change handling
- JD-specific framing from the same verified Project fact pool
- external-asset versus Private Defense separation
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
- unnecessary specialist invocation
- unchanged-file reopening

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
- the research pass finds official signals when they exist publicly, stays inside
  its ceilings, and reports the right stop reason on each failure path
- Playwright is used only where a plain fetch was insufficient
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
- normal asset requests do not run the full specialist suite
- the same Project and fresh company profile are reused across compatible JDs
- external career assets contain no weakness or Private Defense leakage
- every run reports file opens, model calls, Skill invocations, and
  cached/uncached/output token counts when the host exposes them

### Agent PoC passes when

- state survives sessions
- project version changes are detected
- affected claims update correctly
- dependent outputs update
- update run reduces repeated work
- traces and budgets are visible

The integrated V0 case in
`docs/dogfood/STATEFUL_AGENT_V0_COMPARISON.json` passes these mechanical
conditions for one controlled summary of existing evaluation facts: 2/2
presentation outputs changed,
0 unrelated outputs changed, one file was opened instead of six, and no
Project score or JD Match was inflated. The fresh path replays the final
source-grounded host analysis, so this is observed repository dogfood rather
than target-user or live-model validation.

### User-value PoC passes when

- target users receive a useful asset
- at least one user changes a project or career output
- friction is acceptable relative to value
- users can understand and correct the result

## Kill or pivot criteria

- Skill does not beat the strong prompt on meaningful quality or usability
- the project recommendation is no better than the user's own first instinct
- users mainly want generic resume rewriting
- public interview evidence is too thin or too stale to beat the user's own search
- research cost or latency exceeds the value of the company brief
- source error rate remains unsafe
- project upload cost exceeds perceived value
- Agent update provides no measurable advantage
- outputs are impressive but rarely adopted
