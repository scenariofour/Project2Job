# Day 5 Human Review Protocol

The deterministic gate decides whether an output is contractually safe. It
cannot decide whether the output is worth using. Those are different questions,
and this protocol keeps them apart.

Nothing here has been executed. Every score field in
`human_review.template.jsonl` is still `null`, and no reviewer has been
recruited. A reviewer record exists only once a person fills one in.

## Who counts as what

| Reviewer | What their record proves |
| --- | --- |
| Product owner | The author's own judgement. Useful for finding failures. Never independent validation. |
| Independent reviewer | One outside opinion on output quality. Not target-user validation unless the reviewer is job-seeking for this role. |
| Target user | An early-career candidate preparing for an AI PM role, reviewing against their own project and a real JD. |

Label the record with what actually happened. A product-owner session is
product-owner review, not **target-user validation**, no matter how favourable
the score.

## Materials

Give a reviewer exactly three files:

- `lab/day5/blind_review_packet.md`
- a copy of `lab/day5/human_review.template.jsonl`
- `lab/scoring_rubric.md`

Do not share `capture_manifest.json`. It holds the A/B key. The review is
**blind** to which output came from which system; it is not blind to the source
material, because a reviewer cannot judge grounding without the sources.

## What one reviewer does

For each of D5-001, D5-002, and D5-003, and for each output A and B:

1. Score the seven rubric categories 0–3.
2. Set `severe_external_claim` true when the output makes an external-facing
   claim its sources do not support. One severe claim fails the output no
   matter what the other scores say.
3. Answer four questions in `notes`:
   - Is the recommended next build genuinely useful for this JD?
   - Did the output identify the most important risk in this project?
   - Did it surface a gap that does not matter?
   - Would you send this to a recruiter after editing?
4. Record `Accept / Revise / Reject` for the output as a whole:
   - **Accept** — usable after minor editing.
   - **Revise** — usable only after rewriting a specific named part.
   - **Reject** — unsafe, or not worth the editing it needs.
5. Record `preference` (A, B, or neither) and one sentence of
   `preference_reason`.

Seven categories, three cases, two outputs. A reviewer who cannot finish in one
sitting is being asked too much; cut cases before cutting categories.

## Two reviewers and disagreement

Two reviewers work independently. Record a disagreement in
`reviewer_disagreement.template.jsonl` when category scores differ by more than
one point, or when the reviewers disagree about a severe external-facing claim.
Adjudicate it. Do not average it away — the disagreement is the finding.

## What the record feeds

A completed review is a Day 7 pilot input, not a replacement for one. It cannot
establish adoption, external use, or hiring outcome. Those need the bounded
pilot record in `target_user_pilot.template.jsonl`.
