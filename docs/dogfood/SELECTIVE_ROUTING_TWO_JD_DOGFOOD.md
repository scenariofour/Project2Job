# Selective Routing: One Project, Two Same-Company JDs

Date: 2026-07-28

Status: repository dogfood, not target-user or hiring-outcome validation

## Setup

- Project: the bounded Project2Job Skill Suite source set named in the JSON
  Project Evidence Profile
- Company/track cache key: `OpenAI::API Product Management`
- JD 1: [Product Manager, API Agents](https://openai.com/careers/product-manager-api-agents-san-francisco/)
- JD 2: [Product Manager, API Infrastructure](https://openai.com/careers/product-manager-api-infrastructure-san-francisco/)
- Shared official interview source: [OpenAI interview guide](https://openai.com/interview-guide/)
- Request for each JD: one 60-second project introduction

The run built one source-linked Project Evidence Profile, one fresh Company
Intelligence Profile, and two lightweight JD Demand Maps. Exact derived state,
sources, boundaries, and measurements are in
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

Across the two JDs, planned specialist invocations fell from 12 to 2 and planned
model calls fell from 12 to 6. Both paths preserve the existing no-unchanged-file
reread rule: 11 Project files were opened during the first profile build and
zero unchanged Project files were reopened for JD 2. The new path also reduced
official company-page fetches from 6 to 3 by reusing the fresh company/track
profile.

## Different framing from the same evidence

The API Agents map selected the selective-agent-workflow story:

> A product-architecture story about turning a broad agentic analysis workflow
> into a low-friction developer experience through reusable context, selective
> execution, and explicit quality boundaries.

The API Infrastructure map selected the evidence-controls story:

> A high-trust platform story about deterministic permissions, provenance,
> schema validation, cache freshness, and dependency-aware invalidation around
> model-driven work.

Both resolve to the same Project Evidence Profile. Neither adds a Project fact.
The outputs are visibly treated as mock positioning because personal ownership
is not established by repository evidence.

## Token replay

The comparison replays the exact instruction, reference, raw-evidence/profile,
company-source, and JD-map context assigned to each planned call. It uses
`tiktoken==0.11.0` with `o200k_base`.

| Run | Old input tokens | New input tokens | Savings |
| --- | ---: | ---: | ---: |
| JD 1, including profile creation | 65,024 | 46,593 | 18,431 (28.3%) |
| JD 2, with reusable profiles | 35,447 | 7,043 | 28,404 (80.1%) |
| Total | 100,471 | 53,636 | 46,835 (46.6%) |

The two recorded new positioning outputs contain 60 `o200k_base` tokens.
Provider-reported cached input tokens, uncached input tokens, old-path output
tokens, billing cost, and live model latency were unavailable and remain
`null`. These are deterministic context-replay measurements, not billed
production usage.

## Result boundary

This dogfood establishes the deterministic routing, cache reuse, distinct JD
strategy inputs, no-reread behavior, and a lower modeled context path. It does
not establish that the positioning is preferred by hiring managers, that the
user owns the repository work, or that live provider billing will fall by the
same percentage.
