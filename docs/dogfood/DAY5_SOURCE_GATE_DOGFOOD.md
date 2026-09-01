# Day 5 Source-Gate Dogfood

Recorded: 2026-08-31

Evidence class: repository dogfood. The Day 5 citation-resolution gate was run
against real Project2Job surfaces that were not built for it — the six recorded
comparison outputs and the Skill's own shipped Brief example. No target user was
involved and nothing here establishes user value.

## Question

Did Project2Job catch a real career-evidence failure, and did a bad case change
a product rule?

## What the gate found

Against the recorded Day 5 outputs:

| Surface | Citations | Resolved | Failure |
| --- | ---: | ---: | --- |
| `lab/day5/outputs/skill/S01.json` | 8 | 2 | 6 anchored to blank absolute line 2 |
| `lab/day5/outputs/baseline/S02.json` | 19 | 0 | 19 unresolvable prose anchors |
| Other four recorded outputs | 57 | 57 | none |

Both failures survived JSON Schema validation. Both are external-facing: the
Skill case includes the top Project Highlight and the verified evidence behind
all three answer drafts.

## The bad case the dogfood produced

The first version of the gate accepted only line spans. Run against
`skill/p2j/examples/sample_brief.md` — a real committed Project2Job output — it
rejected all 7 of its citations, which use heading anchors such as
`sample_project.md#Problem and scope`.

That was the gate's failure, not the Brief's. A heading anchor names something a
reader can find and a checker can resolve. An ordinal anchor such as
`sentence 1` or `bullet 2` does not: nothing in the file marks where the count
starts.

## Product rule changed

The canonical location grammar now admits heading anchors alongside absolute
line spans, and rejects ordinal prose anchors. Recorded in
`docs/07_SHARED_EVIDENCE_AND_OUTPUT_STANDARD.md`, the Skill core contract, and
the `sourceRef` schema description. After the change all 7 Brief citations
resolve and both recorded Day 5 failures still fail.

`test_shipped_brief_citations_all_resolve` keeps the product's own output inside
the gate it enforces.

## Measurement boundary

- The gate covers structured outputs with `source_refs`. The Brief's inline
  Markdown citations were extracted by hand for this session; Markdown assets
  are not machine-checked in normal operation.
- Citation resolution says a citation points at real text. It does not say the
  text supports the claim, and it is not a groundedness measure.
- No target user, live host, or live model was involved.
- The two recorded failures remain failed cases. The recorded outputs were not
  regenerated, so no before/after model run exists — only before/after gate
  coverage.
