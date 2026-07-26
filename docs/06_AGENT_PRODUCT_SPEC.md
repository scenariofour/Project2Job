# Agent Product Specification

## Product role

The Project2Job Evidence Agent turns the one-time Skill analysis into a maintained project evidence system.

## Independent user value

The Agent is justified only when it creates value that a fresh Skill run cannot reliably provide.

Required Agent advantages:

- remembers user-confirmed facts
- preserves ownership corrections
- tracks project versions
- detects changed artifacts
- rechecks affected claims
- updates only affected outputs
- explains changes
- reduces repeated reading and questions

## MVP runs

### Run 0: JD Intake

Input:

- one target JD
- optional resume

Output:

- `Intake Result`
- saved JD intake, role demand map, and interview context
- saved project recommendation and its reasons and risks

### Run 1: Initial Application and Interview Pack

Input:

- the one selected project's evidence
- the saved JD intake from Run 0

Output:

- same contract as the Skill
- saved project evidence profile
- saved user confirmations
- saved One Next Build

### Run 2: Project Update

Input:

- changed project files
- new evidence
- user marks an action complete

Output:

- changed artifacts
- changed claims
- updated evidence status
- updated resume and interview assets
- remaining risk
- next action
- comparison with Run 1

## State retained

- project ID and version
- source file hashes
- target JD intake, company, and track
- interview context items with their source status and freshness
- the project recommendation and which project the user chose
- target role or JD version
- user-confirmed ownership
- claims and evidence links
- evidence statuses
- generated assets and their dependencies
- One Next Build and completion status
- run metadata and stop reason

## State excluded

- all chat history
- unrelated personal preferences
- a reusable company interview question database
- resume projects that were not selected, beyond their routing summary
- multiple role tracks
- general long-term career profile
- unapproved inferred facts
- sensitive source content in traces

## Thin UI

The product UI needs five surfaces:

1. Paste the JD
2. Intake Result, including the project recommendation
3. Application and Interview Pack
4. Evidence and correction drawer, showing project evidence and interview
   research in separate, differently labeled regions
5. What changed after update

## Agent success condition

The second run must be measurably better than starting over:

- fewer repeated reads
- fewer repeated questions
- lower cost or latency at similar quality
- correct dependency updates
- clear change explanation
