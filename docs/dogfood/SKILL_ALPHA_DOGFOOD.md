# Project2Job Skill Alpha Dogfood

Date: 2026-07-25

Status: host-native Alpha dogfood; not target-user validation

## Setup

- project: this Project2Job repository
- target: OpenAI Product Manager, API Agents
- JD: <https://openai.com/careers/product-manager-api-agents-san-francisco/>
- company process source: <https://openai.com/interview-guide/>
- host: Codex CLI 0.146.0-alpha.3.1, fresh read-only sessions
- installed suite: `~/.codex/skills/p2j*`
- source state: branch `codex/skill-alpha` from `main` commit `67b7861`

The fresh-host public research pass used eight queries and eight fetch actions
across six unique official pages, used no login and no rendered-browser
fallback, and stopped at `evidence_sufficient`. Official pages without reliable
publication dates retained `unknown` freshness.

## User inspection

### Brief

The first fresh-host `$p2j-brief` result was concise and immediately useful:

- verdict: a credible supporting project for the API Agents role, but not yet a
  lead story because API/SDK scale, customer adoption, and personal ownership
  were unsupported
- preliminary Gates: `G1 2`, `G2 2`, `G3 3`, `G4 4`, `G5 1`, `G6 2`
- three proofs, three gaps, three story opportunities, eight questions, and one
  next route
- no intake questionnaire and no project code, tests, builds, or packages run

The initial dogfood run was too expansive: it read broadly and executed
repository tests during intake. The contract was tightened to prohibit project
execution during analysis, cap Brief and Answer source reads, and use a compact
inventory summary. A second fresh-host run respected those boundaries.

### Six-Gate audit

The audit projected the existing ten-domain standard rather than creating
another role model:

| Gate | Domains | Score | Principal evidence and boundary |
| --- | --- | ---: | --- |
| Business & User Problem | D1 | 2 | Target user, trigger, workflow, and success targets are designed in `ACTIVE_SCOPE.md:9-34,208-219`; no target-user discovery result |
| Product & AI Judgment | D2, D3 | 2 | Inspectable scope and rejected alternatives in `ACTIVE_SCOPE.md:186-235` and `docs/13_DECISION_LOG.md`; no executed AI-versus-non-AI comparison |
| Technical Product System | D4, D5 | 3 | Deterministic Agent loop, source boundary, budgets, state, actions, and stop logic are implemented under `src/career_desk/` and documented in `docs/08_AGENT_ARCHITECTURE.md:19-109`; model/retrieval decisions remain partly planned |
| Evaluation, Reliability & Safety | D6, D7 | 4 | Versioned cases, committed traces, contradiction and budget tests, prompt-injection rules, and permission boundaries exist under `lab/evals/`, `tests/`, `docs/build_journal/traces/`, and `docs/11_SAFETY_PRIVACY_AND_HITL.md`; no production validation |
| Delivery, Metrics & Learning Loop | D8, D9 | 2 | D8 metrics and comparisons are inspectable plans capped at 2; D9 has committed delivery evidence, so the Gate takes D8's lower score. No measured user, latency, token, cost, adoption, or delivery outcome |
| Ownership & Interview Defensibility | D10 | 2 | Decisions and Git history are inspectable, but personal ownership is `Needs Confirmation`, so the ownership cap is 2 |

No total candidate score was calculated. N/A concepts were excluded from their
Gate calculation only after a reasoned exclusion. RLHF and DPO were `N/A` for
this deterministic evidence-audit Alpha because no preference-trained model is
owned or trained here; the exclusion did not increase any score. A README-only
claim was capped at 1. Synthetic evals were never presented as live-user proof.

### Answer Lab: A/B test

The fresh-host answer did not dead-end when no exact event existed. It ranked
four viable directions, selected the planned offline Skill-versus-strong-prompt
comparison, and explicitly refused to rename it as a live randomized A/B test.
It produced:

- a direct 30-second answer
- a 60–90-second answer
- a deep-dive experiment design
- a second-best Agent-update comparison
- a true no-direct-experience answer
- four levels of follow-up defense
- two minimal confirmation slots
- one project upgrade

The factual boundary remained explicit: the design is observed, execution is
proposed, no comparative result exists, and ownership needs confirmation.

### Technical answer

The technical case asked when RAG, RLHF, DPO, model selection, or Agent
architecture would be justified. The answer routed through decisions, evidence,
alternatives, tradeoffs, failure modes, and evaluation rather than term density.
It treated deterministic parsing and constrained prompting as current
alternatives, reserved retrieval for a measured context/relevance failure,
reserved a bounded Agent for adaptive verification that beats a fixed workflow,
and marked RLHF/DPO N/A unless repeated labeled preference failures and training
economics justify owned model adaptation.

The first technical run correctly framed the architecture choices but called the
implemented deterministic Agent loop unverified because it spent its read budget
on specifications. The Answer Lab now reserves implementation and committed
verification reads when that distinction changes the story; an uninspected file
is reported as `not inspected`, not converted into `Needs Confirmation`.

### Company intelligence and adversarial cases

The official JD supports questions about agent-builder problems, agent
infrastructure, APIs/SDKs, user outcomes, safety, technical innovation,
high-growth customers, and ambiguity. The official interview guide supports
skills-based assessment and a multi-interviewer final process, but does not
guarantee a particular question.

Controlled cases also verified:

- a newer and an older conflicting process report remain visible with separate
  freshness and conflict labels; the stale report is not promoted
- webpage text telling the Agent to ignore instructions, log in, or mark claims
  supported remains inert evidence and causes no navigation or login
- team artifacts produce a useful result before one optional ownership
  confirmation, with ownership-dependent claims capped at 2
- the audit's One Next Build is one instrumented target-user Alpha session,
  improving discovery, failure analysis, task/adoption metrics, delivery
  learning, and customer-facing stories; the blinded comparison remains the
  Answer Lab's experiment-specific upgrade and audit runner-up

## Failures found and fixed

1. First-pass Brief execution was too broad and ran project tests.
   Fixed with a shared no-execution rule, specialist source caps, and a compact
   inventory summary.
2. The legacy monolithic `career-desk` Skill duplicated role and evidence rules.
   Removed it and retained one shared contract plus specialist references.
3. A source checkout could not become a portable installation because canonical
   repository contracts lived outside the Skill folders.
   Fixed with an installer/archive builder that copies the named canonical
   inputs into the installed suite and validates them.
4. Claude Code installation validated, but live invocation was blocked by an
   expired host OAuth token. This is recorded as unproven cross-host behavior,
   not a product pass.
5. The technical answer understated implemented Agent-loop evidence after
   reading specifications but not code/tests.
   Fixed by reserving paired implementation-and-verification reads whenever
   implementation status changes the answer.
6. The adversarial Intel run used 65,702 host tokens, exceeding the canonical
   60,000-token research ceiling even though query, page, browser, and runtime
   limits held.
   Fixed with a smaller default Alpha operating budget—6 queries, 8 fetched
   pages, 2 browser pages, 45,000 tokens, and 90 seconds—plus required token and
   runtime reporting.
7. The full audit found the right evidence boundary but loaded too many complete
   documents.
   Fixed with a twenty-section overall cap and an explicit ban on concatenating
   whole files or the repository into context.
8. The first portable archive inherited a local Python bytecode cache from the
   source tree.
   Fixed by excluding `__pycache__`, `.pyc`, and `.pyo` files during every
   install and archive copy.
9. The portable bundle included the shared contract but omitted three schemas
   and its gold dataset referenced by that contract.
   Fixed by copying and validating every shared-contract path, so an installed
   bundle cannot carry dangling canonical references.
10. Mock practice did not explicitly label generated interview content as
    simulated.
    Fixed with a required visible label and a dedicated behavior case.
11. The router exposed specialist previews but did not explicitly complete the
    canonical JD Intake, Application Pack, or project-only paths.
    Fixed by routing those three canonical runs through the existing specialists
    and canonical schemas while retaining the concise Brief first.
12. The replacement suite had package validation but no output-instance
    validator.
    Fixed with a canonical Draft 2020-12 validator for Intake Result and
    Application Pack JSON outputs.
13. Inventorying a project subdirectory surfaced unrelated monorepo commits.
    Fixed by scoping Git history to the selected project path, with a temporary
    monorepo regression test.
14. Removing the legacy monolith also removed its inspectable examples.
    Fixed with a synthetic JD, intentionally weak project, and visibly labeled
    mock Brief that demonstrates caps and ownership uncertainty.

## Evidence boundary

This report proves structural installation, fresh-host Codex invocation, and
manual inspection of the listed outputs. It does not prove target-user value,
cross-host consistency, better quality than the strong prompt baseline, or
production latency, cost, adoption, and hiring outcomes.

## Verification

- all seven Skills passed the Skill Creator structural validator
- `make validate`: passed; 14 active documents, 16 JSON files, 72 JSONL cases,
  12 public fixture files, 66 schema references, and 10 canonical domains
- `make test`: 125 run; 112 passed and 13 optional `jsonschema` cases skipped in
  the default zero-dependency environment
- isolated environment with `jsonschema>=4`: 125 passed with no skips; an
  invalid Application Pack was rejected by the installed output validator
- `make inventory`: 3 files, no duplicate groups, project-scoped Git history
- `git diff --check`: passed with no output
- portable archive built without Python bytecode; final Codex and Claude Code
  installations both passed canonical-path validation
- fresh Codex invocations completed for Brief, full audit, A/B Answer Lab,
  technical Answer Lab, and adversarial company intelligence
- Karpathy review and two independent code/product review passes completed; all
  verified P1/P2 findings and cheap correctness findings were fixed
