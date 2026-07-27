---
name: p2j-upgrade
description: Choose exactly one highest-leverage project action that strengthens several AI PM interview assets while producing inspectable evidence. Use when the user says /p2j-upgrade or asks what to build next, how to improve weak Gates, or which experiment, eval, trace, decision, or user test will most improve a selected project's interview defensibility.
---

# Project2Job One Next Build

Treat `/p2j-upgrade` as an alias for `$p2j-upgrade`.

1. Read `../p2j/references/core-contract.md` and
   `../p2j/references/gates.md`.
2. Resolve shared context. Reuse current gaps and acceptance evidence; remove a
   completed build from consideration and recompute only gaps affected by
   changed evidence.
3. Compare only material evidence gaps. Rank candidate evidence directions by:
   - number and importance of Gates improved
   - target-JD relevance
   - new direct evidence produced
   - interview questions and story branches unlocked
   - risk reduced
   - effort and dependency cost
4. Diagnose the current career and evidence problem:
   - current evidence gap
   - why the Project does not fully satisfy the target JD
   - relevant hiring capability category, inferred when justified from the JD,
     company, and Project evidence
   - current Match using only `EXACT MATCH`, `TRANSFERABLE`, or `GAP`
5. Choose exactly one broad evidence direction and reject the runner-up
   explicitly. Do not choose repository-specific implementation subclasses
   before the downstream working Agent inspects the Project.
6. Define the direction's product and safety boundaries, the evidence artifacts
   needed for later reassessment, and which Project2Job outputs should change
   only after completed evidence exists.
7. Return:
   - Gap
   - JD mismatch and why it matters
   - Hiring capability category
   - Current Match
   - One recommended evidence direction
   - Product and safety boundaries
   - Reassessment evidence artifacts
   - Outputs expected to change
   - Interview questions unlocked
   - Execution Handoff Prompt
8. Make the handoff prompt directly copyable into Codex or Claude Code. It must
   name the existing Project, diagnosis, one direction, boundaries, later
   reassessment evidence, and affected Project2Job outputs.

## Execution handoff

Project2Job owns the career diagnosis and evidence direction. The downstream
working Agent owns the repository-grounded solution exploration.

Require the downstream Agent to:

1. inspect current product goals, architecture, workflows, known failures,
   tests, and safety boundaries before choosing implementation details;
2. confirm a plausible connection to the Project's current user task and name
   one relevant limitation, failure mode, or unmet need;
3. identify the smallest product-relevant problem worth addressing;
4. compare reasonable implementation options;
5. define the smallest justified implementation and state model;
6. define an evaluation approach appropriate to the feature and risk;
7. derive concrete subclasses such as state names, turn limits, prompt
   structure, UI behavior, corpus size, metrics, and file organization from
   Project inspection;
8. return one exploration brief for product-owner approval and stop before
   implementation;
9. after explicit approval, implement the approved direction, run real
   verification, and produce inspectable evidence.

Keep the product-fit check lightweight. Preserve the Project's core identity
and safety boundaries. When relevance is uncertain, ask for a bounded
prototype, experiment, or evaluation that can resolve the uncertainty. When the
direction does not fit, require the downstream Agent to return a better evidence
direction rather than force the recommendation into the Project.

When subjective product quality matters, require genuine human-reviewed
evidence. The downstream Agent proposes the review sample, rubric, and workflow
from the inspected implementation and risk. Completed evidence preserves real
human judgments, meaningful disagreements, and the resulting keep, revise, or
stop decision. Synthetic review is not human evidence.

The copyable handoff must prohibit invented metrics, users, outcomes, ownership,
and test results; require changed files, commands, exact results, remaining
limitations, and produced artifacts in the report; and preserve
repository-grounded exploration before editing.

Do not execute the Project modification. Do not return a roadmap or a bundle of
loosely related actions. A proposed build keeps the current Match and earns no
executed-evidence score. Completed and sufficient evidence may move the relevant
requirement from `GAP` to `TRANSFERABLE`; Project2Job reassesses that only after
the evidence exists.
