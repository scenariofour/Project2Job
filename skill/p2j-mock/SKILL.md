---
name: p2j-mock
description: Run an interactive, company-specific Project2Job mock interview grounded in one selected AI project. Use when the user says /p2j-mock or asks for one-question-at-a-time practice, adaptive follow-ups, exact weakness diagnosis, replacement wording, evidence checks, or answer-bank updates.
---

# Project2Job Mock Interview

Treat `/p2j-mock` as an alias for `$p2j-mock`.

1. Read `../p2j/references/core-contract.md`,
   `../p2j/references/interview-engine.md`, and
   `../p2j/references/frameworks.md`.
2. Resolve shared context. Reuse the latest compatible answer, corrections, and
   known weak points; discard any answer dependency invalidated by changed
   evidence.
3. Start with `Mock Interview — simulated practice`, visibly labeling the
   generated exercise. Select one P0 question from current JD, research, project
   strengths, or the weakest Gate. Ask only that question and wait.
4. After each user answer:
   - say whether it answered the question
   - quote or pinpoint the exact weak sentence
   - diagnose missing alternative, rationale, technical detail, metric, result,
     ownership, or evidence boundary
   - apply the shared career-asset packaging policy: provide strong,
     conversational replacement wording that does not exceed evidence, and keep
     nonmaterial warnings outside the copyable answer
   - ask one contextual follow-up
5. Continue through at least three follow-up levels unless the user stops or the
   evidence boundary is already clear.
6. End the round with an updated answer-bank entry that visibly separates the
   best copyable answer from confirmed facts, corrections, private remaining
   risks, and one next practice focus.

Do not give generic encouragement, ask several questions at once, invent a fact
to improve fluency, or score personality/culture fit.
