# Token, Context, and Cost Policy

## Objective

Minimize irrelevant reading and repeated work while maintaining evidence correctness.

## Context policy

The model receives only:

- current role requirement
- current project claim
- applicable Skill reference
- current state summary
- small set of retrieved source excerpts
- last tool observation
- remaining budget

Do not place the full repository or all project files into one model call.

## Pre-model inventory

Before model analysis:

- enumerate files
- identify types
- calculate hashes
- detect duplicates
- estimate size
- identify likely project roots
- flag unreadable or unsafe content

## Progressive loading

Skill host:

- discover Skill via name and description
- load `SKILL.md` when selected
- load references only when required
- resolve compatible local context before source retrieval
- reuse cached fingerprints and source-linked facts for unchanged artifacts
- run scripts only when required
- resolve the Project Evidence Profile, Company Intelligence Profile, and JD
  Demand Map before opening sources
- invoke only the specialist Skill required by the requested asset
- reserve the six-Skill path for explicit Full Preparation

Agent runtime:

- load a task-specific context set
- retrieve only source sections needed for the current claim
- cache stable extraction results

## Initial budgets

Targets to calibrate:

### Skill trial

- one project
- 5–7 role capabilities
- 3–5 verified highlights
- no more than 6 evidence searches
- no more than 4 source rereads per high-value claim
- stop once the output contract is supportable

### Public-web interview research

One bounded research pass per JD. These are hard ceilings, encoded as `maximum`
values in `schemas/interview_context.schema.json` `researchBudget`; a run may
declare less, never more.

| Limit | Ceiling |
| --- | --- |
| max_search_queries | 8 |
| max_pages_fetched | 12 |
| max_playwright_pages | 3 |
| max_navigation_depth | 1 |
| max_chars_per_page | 20000 |
| max_total_tokens | 60000 |
| max_retries_per_page | 1 |
| max_runtime_seconds | 120 |

Cost discipline for the pass:

- official sources first; independent reports only to confirm, conflict, or fill
  a named gap
- deduplicate on canonical URL before fetching, and on content after
- cache page extractions for the run; never fetch the same canonical URL twice
- plain read-only fetch is the default. Escalate to Playwright only for a page
  that returned `render_required`, needs one navigation step, or cannot be parsed
  otherwise. Playwright is a required capability and an expensive one
- retain only the extracted spans that answer a named gap, never whole pages
- issue a follow-up query only when a gap is still open after the current results
- stop at the first sufficient answer rather than spending the remaining budget

### Agent update

- compare hashes first
- read changed files and dependent evidence first
- do not re-open unchanged sources without reason
- regenerate only dependent assets

### Skill context reuse

- compare Project and JD fingerprints before evidence retrieval
- do not reopen unchanged sources without a named evidence need
- reparse a changed JD without repeating the Project audit
- on a changed Project, read changed artifacts and dependent evidence first
- `refresh` recomputes while retaining compatible confirmed facts
- `fresh` bypasses reuse without deleting history
- reuse one current Project Evidence Profile across JDs
- reuse a fresh Company Intelligence Profile only for an exact normalized
  company/track-key match
- reuse a JD Demand Map only when its Company profile key matches
- open every added Project source and inspect its evidence surfaces before
  narrowing which Project profile sections need updates
- extract a lightweight JD Demand Map for each changed JD

## Telemetry

Record:

- files discovered
- files opened
- search queries issued
- pages fetched, deduplicated, and skipped
- Playwright pages and why each was escalated
- maximum retries used on any one page
- research stop reason
- source sections read
- repeated reads
- retrieval chunks
- model calls
- tool calls
- agent turns
- input tokens
- cached input tokens
- output tokens
- uncached input tokens
- specialist Skills invoked
- latency
- estimated cost
- supported claims
- accepted outputs
- stop reason

## Efficiency metrics

- tokens per supported claim
- evidence yield per tool call
- redundant read rate
- cost per usable career asset
- cost per accepted Next Build
- update cost relative to fresh run

## Release rule

A cheaper version does not win when it creates materially worse evidence boundaries or unsupported outputs.

A more expensive Agent does not win unless it improves user or quality outcomes.
