# Decision Log

## D-001: Two products, one standard

Decision:

- build an open-source Skill
- build a stateful Agent
- share standards, schemas, and evals

Reason:

The Skill provides low-friction value and distribution. The Agent creates update and continuity value.

## D-002: One project and one role

Decision:

MVP analyzes one project against one role profile or JD.

Reason:

Multi-project selection increases input cost, tokens, explanation difficulty, and evaluation complexity.

## D-003: Application Pack output

Decision:

MVP produces grounded resume and interview assets in addition to evidence analysis.

Reason:

Users need directly usable career outputs, not an internal audit report.

## D-004: Agent value is update value

Decision:

The full Agent must detect project changes and update dependent evidence and outputs.

Reason:

A Web wrapper around the Skill would not justify a stateful Agent product.

## D-005: Role-Backwards Evidence Framework

Decision:

Use RBEF as the shared method.

Reason:

The product should connect role reality, hiring signals, project artifacts, evidence boundaries, and career outputs.

## D-006: No broad integrations in MVP

Decision:

No Gmail, job APIs, application tracking, or broad MCP set.

Reason:

They do not prove the core product promise and increase failure surface.

## D-007: Strong generic prompt as baseline

Decision:

Treat a high-quality prompt as the primary Skill competitor.

Reason:

The Skill must create value through reusable standards, scripts, references, schemas, and eval-tested behavior.

## D-008: Frameworks follow evidence

Decision:

Do not require LangGraph, multi-agent, or Deep Agent.

Reason:

Framework use must solve observed runtime problems.

## D-009: Import v6 into the existing repository

Decision:

Integrate the v6 Build System at the existing Project2Job repository root while
preserving its Git history, `origin`, `main` lineage, and MIT license.

Reason:

The repository is the public system of record. Reinitializing or nesting the
package would break provenance and make the documented paths inaccurate.

## D-010: Separate public Days from engineering dependencies

Decision:

Use `docs/build_journal/` for the Day 0–Day 7 learning narrative and retain
`work_orders/` as the technical dependency system.

Reason:

Content order and engineering order serve different purposes. Keeping both
explicit prevents the journal from becoming a duplicate roadmap or PRD.

## D-011: Exclude the generated Skill ZIP

Decision:

Do not track `dist/career-desk-project-to-application-skill_v1.zip` on Day 0.

Reason:

The package README identifies it as generated but does not provide a reproducible
rebuild command. Source files remain authoritative until a release process is
documented and verified.

## D-012: Keep the bounded Agent loop provisional

Decision:

Implement one deterministic bounded Evidence Investigator behind the same
comparison interface as the strong one-shot prompt and fixed
extract-search-validate workflow. Do not select the Agent loop as the final
architecture before comparative evidence exists.

Reason:

Adaptive control may help choose when to narrow, ask, continue, or stop as
evidence changes. The current Day 1 branches are also expressible as a fixed
workflow. Retain the loop only if labeled comparison shows better evidence
boundaries or recovery at acceptable safety, cost, latency, and trace clarity;
replace it with the fixed workflow if those benefits do not materialize.

## D-013: One vocabulary, one governance note, testable consistency

Decision:

- `Project2Job` is the canonical product and repository name. `Career Desk` is a
  legacy internal codename kept only in clearly historical records and v6-era
  code modules. The former `skill/career-desk/` path was migrated by D-018.
- Change history stays in Git, pull requests, Work Orders, and
  `docs/13_DECISION_LOG.md`. Do not add `baseline/`, `increments/`, or `review/`
  folders that duplicate them.
- Add exactly two supporting files: `GLOSSARY.md` for vocabulary and
  `docs/DOCUMENT_GOVERNANCE.md` for which document owns which question. Neither
  becomes an active product document.
- Documentation consistency is enforced by tests
  (`tests/test_document_consistency.py`), not by review habit, and the Day
  journal gate is a general prefix rule rather than a per-Day constant.
- Diagrams are added only when a process, state machine, or sequence is
  materially clearer than prose. Traces and tests remain the stronger evidence.

Reason:

The drift found before this change was two names for one product, a Day 0-only
status after Day 1 shipped, output counts that contradicted the schema, and a
validator that needed editing for every new Day. Naming and ownership rules
prevent the first three; a general rule and a test suite prevent them from
returning silently.

## D-014: JD-first flow with one deeply analyzed project

Decision:

- The run starts from one target JD, not from a project. An `Intake Result` is
  returned before any project evidence exists, so one pasted JD alone produces
  value.
- An optional resume is read to extract several project candidates **for routing
  only**. Their summaries stay `self_reported` until that project's own sources
  are read. Exactly one project may enter deep evidence analysis.
- Routing uses five bands — role relevance, likely evidence availability,
  ownership clarity, outcome strength, interview depth — so keyword overlap
  cannot decide the recommendation on its own. When nothing clearly fits, the
  product reports `no_clear_choice` and asks the user to choose.
- Company and interview material is a second, separate evidence system with its
  own source-status scale (`official`, `repeatedly_reported`, `single_report`,
  `inferred_from_jd`, `unknown`) plus source date and freshness. It never becomes
  project evidence and never reaches a resume bullet. There is no
  personality-based culture fit layer.
- The Application Pack becomes the Application and Interview Pack at schema
  2.0.0, adding the company/track brief, loop hypothesis, 5–8 prioritized
  questions, three grounded answer drafts, questions to ask the interviewer, and
  one mock-interview round specification.
- No job discovery, no platform login, no scraping, no auto-apply, no
  application tracking. Superseded in part by D-016, which makes bounded
  automatic research required.

Reason:

The previous promise assumed the user had already chosen the right project. In
the real workflow the JD arrives first and choosing the wrong project wastes the
whole analysis. Keeping research and project evidence in separate systems is what
stops company preparation from quietly becoming a fabricated resume claim.

The 2.0.0 pack bump was reviewed against gold dataset 0.1.0. Its cases assert
role-profile and evidence-status behavior and reference no pack schema ID, so no
gold case changed.

## D-015: Two schemas, not eight

Decision:

Express the eight requested contracts as three new schema files plus one revised
one: `jd_intake`, `interview_context` (shared source-status, signal, and question
definitions), `intake_result` (which embeds candidates, recommendation, and
checklist as `$defs`), and `application_pack` 2.0.0 (which embeds answer draft,
loop stage, and mock round as `$defs`).

Reason:

Resume candidate, project recommendation, and evidence checklist have exactly one
container each; separate files would add indirection with no reuse. Interview
signals and questions genuinely appear in two containers, so they get their own
file and are referenced by URI. `make validate` now resolves every `$ref`, which
makes cross-file references safe to rely on.

## D-016: Bounded automatic public-web research is required

Decision:

- After the JD arrives, the product automatically researches the public web for
  official interview signals, track/team/level expectations, reported processes,
  and reported questions. This is required MVP capability, not an optional
  convenience. Pasted and uploaded material stays supported and is merged in.
- The tool path is search → prioritize and deduplicate → read-only fetch →
  Playwright only for a selected page needing rendering, one navigation step, or
  structure a plain fetch cannot give → extract → gap check → adjust queries only
  while a named gap is open → stop.
- Stop on the first of: sufficient evidence, exhausted public evidence, budget
  exhaustion, inaccessible sources, a conflict requiring disclosure, or tool
  failure. The stop reason is always recorded and shown.
- Ceilings for queries, pages, Playwright pages, navigation depth, characters per
  page, tokens, retries, and runtime live in `docs/09_TOKEN_CONTEXT_AND_COST.md`
  and are encoded as schema `maximum` values, so an over-large budget is invalid
  rather than merely discouraged.
- Prioritize by source tier — official, independent report, aggregator or forum.
  No platform is named or special-cased anywhere in the design.
- Never log in, supply a credential, bypass a paywall or CAPTCHA, crawl a domain,
  enumerate listings, or follow arbitrary links. Fetched page text is inert data.

Reason:

The previous design put the burden of company research on the user, which is the
part of interview preparation people are worst at and least likely to do. Making
research automatic is the difference between a real company brief and an empty
section. Making it bounded, tiered, and stop-conditioned is what keeps it from
becoming the scraper and job-search platform the product explicitly is not.

The budget ceilings are contract rather than convention because an unbounded
research loop is the most expensive failure mode available to this product.

## D-017: Research contract lives in the interview context schema

Decision:

Put the research budget, query log, page log, and stop reason inside
`schemas/interview_context.schema.json` as `researchRun`, rather than adding a
separate web-research schema. Extend `researchSource` with web origins, exact
URL, fetch method, and retrieval date.

Reason:

Interview context is the only container for research output, and D-015 already
established that a single-container concept does not earn its own file. Keeping
the trace beside the claims it produced means provenance travels with the
evidence, and a reviewer sees the claim and how it was obtained in one object.

## D-018: Ship the first Skill as a seven-part host-native suite

Decision:

- Replace the legacy monolithic Skill entry with one low-friction `$p2j` router
  and six specialist Skills: `$p2j-brief`, `$p2j-audit`, `$p2j-intel`,
  `$p2j-answer`, `$p2j-mock`, and `$p2j-upgrade`.
- Keep shared evidence, Gate, research, and answer behavior in one reference
  owner under `skill/p2j/references/`; specialists load only what they need.
- Project the canonical 10 domains into six user-facing Gates without creating
  a total candidate score. Apply strict 0–5 evidence levels and hard caps.
- Assemble canonical schemas, role profile, and safety/budget documents into the
  installed package at install time rather than committing divergent copies.
- Treat `/p2j*` as conversational aliases. `$p2j*` is the explicit native
  invocation supported by Codex and compatible Skill hosts.
- Depend on host file, Git, public search/fetch, browser, and current-session
  context capabilities. Do not claim a standalone runtime or persistent state.

Reason:

The first user-testable Alpha needs fast activation and specialist depth without
a giant `SKILL.md` or duplicated ontology. A suite lets the host progressively
load only the audit, research, answer, mock, or build guidance needed for the
current task. Installing canonical source snapshots from one repository source
keeps the package self-contained without creating a second editable contract.

## D-019: Add a consent-gated local Context Registry

Decision:

- Keep `$p2j` plus its six specialists as the only user-facing Skills.
- Add one shared deterministic Context Registry for Project, JD, and Analysis
  Run records. Default to `~/.project2job`, respect `P2J_HOME`, and require
  one-time consent before the first persistent write.
- Store identities, versions, fingerprints, bounded confirmed facts and
  ownership boundaries, source/output references, unresolved questions, and
  known gaps. Do not store credentials, secrets, source bodies, complete
  generated answers, or unrelated personal data.
- Resolve source changes before every Skill run. Preserve unaffected facts,
  invalidate only dependent outputs, and keep current source evidence
  authoritative.
- Support refresh, analyze from scratch, do not save, and selective forget.
- Keep the Agent boundary: the registry is passive storage and resolution; the
  future Agent actively orchestrates change-driven regeneration and explains
  updates.

Reason:

Repeated Brief, Audit, Answer, Mock, Intel, and Upgrade runs should not discard
confirmed work or repeat ownership questions. One shared local envelope avoids
duplicating state across seven Skills while preserving the product boundary:
one Project, one JD, no background process, and no general candidate database.

## D-020: Add one bounded orchestration layer and one data-driven report

Decision:

- Keep the existing Evidence Investigator and seven user-facing Skills.
- Add one explicit runtime that accepts scripted or host-mediated action
  selection while deterministic policy enforces the allowed actions,
  permissions, budgets, validation, one repair, and stop.
- Store dependency edges from artifacts through evidence and claims to outputs,
  then regenerate only dependency descendants.
- Render Initial Analysis, Evidence Inspection, Project Updated, and No Relevant
  Changes from structured state and traces through one local HTML shell.
- Do not add an Agent SDK, LangGraph, frontend framework, background monitor, or
  another Skill.

Reason:

The requested initial, correction, Project-update, JD-update, and unchanged
paths require durable state and selective dependency work, but not durable graph
checkpointing or a production Web service. One small policy loop and one
renderer make the Agent behavior inspectable without creating framework-shaped
architecture.

## D-021: Persist one canonical Agent state and integrate one real update path

Decision:

- Persist the orchestrator's evidence, claims, outputs, dependencies, trace, and
  observed metrics inside the existing Context Registry Analysis Run rather
  than introducing a second state store.
- Restore that state in a separate process and save the next valid state with
  the registry's existing atomic write.
- Limit the first real capability adapter to explicitly named changed evidence
  artifacts. Run the existing bounded Evidence Investigator on that surface,
  then recompute only dependency descendants.
- Keep initial Brief, company research, Answer, and Mock generation
  host-provided and label them as such.
- Keep one-time Skill use independent: without save consent, a host-native Skill
  may return its normal result without loading the update runtime or creating
  registry/consent files.
- Classify controlled dogfood additions as an existing-fact summary, a
  simulated proposal, or an actually executed result. Only the last may add
  executed capability evidence.
- Generate a Codex/Claude Code execution handoff from `$p2j-upgrade`; never
  execute the inspected Project modification from Project2Job.

Reason:

Cross-process restoration and a real selective update require one source of
state truth, but they do not require a service, provider API, graph framework,
or another user-facing Skill. Restricting the real adapter to a labeled changed
surface makes the evidence boundary inspectable and deterministically testable
while host-native generation remains available in Codex or Claude Code.

## D-022: Validate persisted state by schema role and split Upgrade diagnosis from execution exploration

Decision:

- Validate dynamic artifact, evidence, claim, output, and dependency identifiers
  as data in their defined Agent-state maps, while continuing to scan every
  persisted string for secret patterns.
- Allow the complete compact Project artifact manifest and bounded derived
  output `content` in their schema-defined locations. Continue to reject
  credential fields and raw Project, JD, resume, transcript, and document
  bodies.
- Make `$p2j-upgrade` own the evidence gap, JD mismatch, capability category,
  one evidence direction, boundaries, and reassessment evidence.
- Make the downstream working Agent inspect the Project, compare options,
  propose concrete implementation and evaluation details, stop for
  product-owner approval, and only then implement and produce evidence.
- Keep the current Match for proposed work. Reassess only completed evidence,
  using `EXACT MATCH`, `TRANSFERABLE`, and `GAP`.

Reason:

The first consented real-project run exposed false positives from a
field-name-only persistence check and an undersized generic list limit. The same
test showed that a useful Upgrade diagnosis should constrain the career evidence
goal without pre-choosing repository-specific solution details.

## D-023: Route on evidence availability, and let the intake decline

Decision:

- Gate project routing on likely evidence availability. A candidate whose
  evidence availability is `weak` or `unknown` cannot be recommended, whatever
  its role relevance, and the ranking orders evidence availability above role
  relevance, ownership, outcome, and interview depth.
- Return `no_clear_choice` with every candidate listed as an alternative when no
  candidate passes the gate or when the top two rank identically.
- Cap confidence by the winner's own evidence band: a `clear_choice` needs both a
  margin over the field and `strong` evidence availability. Winning a weak field
  is a `narrow_choice`.
- Keep the five bands coarse and derived from the JD's own mapped capabilities,
  so a short JD does not make every candidate look weak.

Reason:

The failure this product exists to prevent is putting forward the project whose
wording matches the JD rather than the project that can be defended. Keyword
overlap is the cheapest signal and the most misleading one, so it may inform the
ranking but never decide it. The confidence cap came from the Day 2 dogfood,
which reported a `clear_choice` over a field where the winner's own evidence was
only adequate.

## D-024: Bound research with a host capability, a fixture host, and a modeled cost

Decision:

- Keep the intake runtime socket-free. It drives a `ResearchHost` protocol —
  search, read-only fetch, Playwright render — that the host implements, and
  records queries, pages, tiers, escalations, duplicates, walls, usage, and one
  stop reason.
- Treat only search results as the fetch frontier. Page text is counted, never
  interpreted, so text inside a page cannot cause a search, a fetch, a
  navigation, or a claim.
- Deduplicate on canonical URL before fetching and on page body after, so a
  mirror is one report while two independent write-ups stay two.
- Read one page for a gap an official source closes, and up to two for a
  reported one, so corroboration is possible without spending the budget.
- Model `runtime_seconds` and `total_tokens` from a fixed per-call cost rather
  than measuring them, and say so wherever they appear.

Reason:

Every acceptance criterion about research is about restraint, and restraint is
only testable if the run is reproducible. A fixture host makes each case
executable; a measured clock would make every trace and eval non-deterministic.
The cost of this choice is stated rather than hidden: no case has run against a
live host, and the modeled numbers are not measurements.

## D-025: Implement the intake half of WO-05 and leave the pack half unclaimed

Decision:

- Implement JD intake, the Role Demand Map, bounded research, routing, the
  Required Evidence Checklist, and One Next Input; stop at the Intake Result.
- Execute the 17 `intake`-stage Day 2 eval cases, and declare the three
  `pack`-stage cases unexecuted rather than reporting them as covered.
- Implement the WO-05 output validator for the intake-side cross-object
  references only, and record which pack-side references remain.

Reason:

Pack generation belongs to WO-01 and WO-02. Marking Day 2 `IMPLEMENTED` requires
executable acceptance evidence for what it claims, and claiming the pack-stage
criteria would be exactly the overstatement the journal exists to prevent.

## D-026: Retain manifest-scoped context and defer retrieval

Decision:

- Keep broad/full Project context as a comparison baseline, not the default.
- Retain the existing manifest-scoped context policy.
- Do not add an index, vector store, embedding model, or RAG layer for Day 3.
- Require external exports to traverse a direct Evidence → Claim dependency
  path and to have resolved attribution; a citation alone is insufficient.

Reason:

The deterministic three-case comparison opened 21 files and 2,841 characters
for broad context, 12 files and 1,815 characters for manifest scope, and 3 files
and 435 characters for targeted filename selection. Manifest scope matched the
broad baseline on 3/3 claim-to-source judgments and missed no critical source.
The targeted selector scored 2/3 because it missed the separate team-ownership
boundary. Runtime, tokens, cost, model quality, and user value were not measured.
The observed context saving does not justify accepting a known boundary failure
or adding retrieval complexity.

## D-027: Retain the bounded Agent only for explicit update cycles

Decision:

- Keep the Skill as the default one-off analysis product and fresh replay as the
  comparison baseline.
- Retain the bounded Agent for user-invoked updates that require saved-context
  resolution, change detection, dependency invalidation, selective
  regeneration, and a Before / After / Why explanation.
- Keep deterministic policy responsible for permissions, approval gates,
  budgets, allowed actions, export validation, preservation, and stop
  conditions. The user remains responsible for persistence consent, factual and
  ownership confirmation, correction approval, and actual external use.
- Do not add background monitoring, external actions, another Agent, an Agent
  framework, or a second state store.
- Reconsider the Agent if target-user or live-model evidence does not show an
  advantage over a fixed stateful workflow or fresh Skill replay.

Reason:

In the one controlled repository comparison, the stateful update opened 1 file
and regenerated 2 outputs, while fresh replay opened 6 files and regenerated 23.
Both matched the same 2 expected final values, and the stateful path changed 0
unrelated outputs. Correction and removal tests also show that dependency
descendants update while unrelated outputs survive.

This evidence supports the mechanics of bounded continuity, not broad product
value. No live model planner ran, token use was unavailable, the fresh path
replayed source-grounded host analysis, and no target user evaluated the result.
The comparison did not show a latency advantage or independent quality
superiority.

## D-028: Keep Day 5 pending and defer the model/architecture decision

Decision:

- Preserve the unchanged strong generic prompt as the comparison baseline.
- Use the three existing `S01`, `S02`, and `S05` boundary cases for the smallest
  representative live-output set, plus the existing `A17_COMPARISON` Agent
  mechanics record.
- Treat every severe per-case failure as an aggregate override. The current
  Project2Job `S01` exact-source failure therefore blocks an automated pass.
- Record only host-observed tokens and wall time. Leave the missing first
  baseline runtime, model identifier, provider cost, human scores,
  disagreement, target-user feedback, and product value `null`.
- Make no prompt-versus-Skill winner, RAG, fine-tuning, framework, or runtime
  decision until blind review, disagreement adjudication, and a bounded
  target-user pilot exist.

Reason:

All six outputs validate structurally, but structural validity is not product
quality. The exact-source failure shows why averages cannot approve a career
output, and the ownership case still requires human judgment. The host also
loaded the global Skill catalog during baseline sessions, so observed token
differences cannot be cleanly attributed to Project2Job instructions. The
package is reproducible evidence for review, not evidence of product advantage.
