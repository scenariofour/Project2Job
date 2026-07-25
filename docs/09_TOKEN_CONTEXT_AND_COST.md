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
- run scripts only when required

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

### Agent update

- compare hashes first
- read changed files and dependent evidence first
- do not re-open unchanged sources without reason
- regenerate only dependent assets

## Telemetry

Record:

- files discovered
- files opened
- source sections read
- repeated reads
- retrieval chunks
- model calls
- tool calls
- agent turns
- input tokens
- cached input tokens
- output tokens
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
