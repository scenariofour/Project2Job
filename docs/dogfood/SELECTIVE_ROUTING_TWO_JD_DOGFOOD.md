# Selective Routing: One Project, Two Same-Company JDs

Date: 2026-07-28

Status: executed selective repository dogfood, not target-user or
hiring-outcome validation

## Setup

- Project: the bounded Project2Job Skill Suite source set named in the JSON
  Project Evidence Profile
- Exact normalized company/track cache key:
  `openai::api product management`
- JD 1: [Product Manager, API Agents](https://openai.com/careers/product-manager-api-agents-san-francisco/)
- JD 2: [Product Manager, API Infrastructure](https://openai.com/careers/product-manager-api-infrastructure-san-francisco/)
- Shared official interview source: [OpenAI interview guide](https://openai.com/interview-guide/)
- Request for each JD: one 60-second project introduction

The run called the actual `context_registry.resolve_context`, `save_run`, and
`profile_router.plan_request` implementation in an isolated registry. It built
and saved one source-linked Project Evidence Profile, one fresh Company
Intelligence Profile, and the first JD Demand Map. The second run reused both
profiles and saved only its new JD Demand Map. Exact route plans, registry
states, sources, files opened, boundaries, and measurements are in
`SELECTIVE_ROUTING_TWO_JD_DOGFOOD.json`.

## Execution paths

Old default path for each JD:

```text
Brief → Intel → Audit → Answer → Mock → Upgrade → full pack
```

New path:

```text
JD 1:
Audit → Project Evidence Profile
Intel → Company Intelligence Profile
lightweight JD Demand Map
requested introduction

JD 2:
reuse Project Evidence Profile
reuse fresh Company Intelligence Profile
lightweight JD Demand Map
requested introduction
```

The recorded plans show two prerequisite specialists on JD 1 and none on JD 2;
the complete six-Skill path would have planned twelve specialist invocations
across the same two requests. Eleven Project files were opened during the first
profile build and zero unchanged Project files were reopened for JD 2. The
bounded `$p2j-intel` pass opened the two official JDs and official interview
guide once; JD 2 reused that exact-track Company profile.

The executed output artifacts are:

- `selective-routing-two-jd/api-agents-introduction.json` — 140 words
- `selective-routing-two-jd/api-infrastructure-introduction.json` — 147 words

Both pass the external-asset validator and preserve unresolved ownership and
outcome claims only in Private Defense.

## Different framing from the same evidence

The API Agents introduction selects the selective-agent-workflow story:

> A product-architecture story about turning a broad agentic analysis workflow
> into a low-friction developer experience through reusable context, selective
> execution, and explicit quality boundaries.

The API Infrastructure introduction selects the evidence-controls story:

> A high-trust platform story about deterministic permissions, provenance,
> schema validation, cache freshness, and dependency-aware invalidation around
> model-driven work.

Both resolve to the same Project Evidence Profile and exact Company profile key.
Neither adds a Project fact. The artifacts use neutral project language because
personal ownership is not established by repository evidence.

## Observed execution telemetry

Observed in the executed dogfood:

- three saved analysis records across two Project2Job requests;
- the Project and Company profiles moved from `miss` to `hit` on JD 1;
- both were `hit` before JD 2 and its JD map alone was `miss`;
- 11 Project files opened for JD 1 and zero for JD 2;
- three official company/JD pages fetched once;
- two complete output artifacts produced.

The Codex host did not expose isolated provider input, cached-input,
uncached-input, output-token, call-count, billing, or latency telemetry for this
dogfood. Those live fields remain `null`.

## Token replay

This is a separate deterministic planned-path comparison retained from PR #16.
It replays instruction, reference, raw-evidence/profile, company-source, and
JD-map context assigned to each planned call using `tiktoken==0.11.0` with
`o200k_base`. It is not the live execution telemetry above.

| Run | Old input tokens | New input tokens | Savings |
| --- | ---: | ---: | ---: |
| JD 1, including profile creation | 65,024 | 46,593 | 18,431 (28.3%) |
| JD 2, with reusable profiles | 35,447 | 7,043 | 28,404 (80.1%) |
| Total | 100,471 | 53,636 | 46,835 (46.6%) |

The two complete introductions contain 349 `o200k_base` tokens. Provider-reported
cached input tokens, uncached input tokens, old-path output tokens, billing
cost, and live model latency were unavailable and remain `null`. These are
deterministic context-replay measurements, not billed production usage.

## Result boundary

This dogfood establishes actual registry save/reuse, deterministic route
selection, distinct JD strategy inputs, two completed artifacts, no-reread
behavior, and a lower modeled context path. It does not establish that the
positioning is preferred by hiring managers, that the user owns the repository
work, or that live provider billing will fall by the replay percentage.
