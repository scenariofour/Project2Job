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
3. Compare only material evidence gaps. Rank candidate actions by:
   - number and importance of Gates improved
   - target-JD relevance
   - new direct evidence produced
   - interview questions and story branches unlocked
   - risk reduced
   - effort and dependency cost
4. Choose exactly one action. Reject the runner-up explicitly.
5. Return: gap, why now, bounded steps, acceptance criteria, expected new
   evidence and exact artifact, affected outputs/questions/Gates, effort band,
   and the interview question unlocked.

Do not return a roadmap or a bundle of loosely related actions. A proposed build
earns no executed-evidence score until its acceptance evidence exists.
