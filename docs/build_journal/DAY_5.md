# Day 5 — Evaluation and Model Decisions

Status: IMPLEMENTED

Review gate: PENDING HUMAN REVIEW

The evaluation system is implemented, executable, and tested, and it has already
changed the product. Blind reviewer scores, disagreement adjudication, and a
bounded target-user pilot still do not exist, so Day 5 is not USER-VALIDATED and
no reviewer-preference or user-value claim is made.

## Question

Does Project2Job make good judgments, where does it fail, and what should change
because of that?

## Evaluation package

`lab/day5/` contains:

- the unchanged strong prompt baseline and three recorded baseline outputs;
- three comparable Project2Job `APPLICATION_PACK` outputs;
- gold expectations reusing `S01`, `S02`, `S05`, and `A17_COMPARISON`;
- eight per-case checks, six of them severe, that override any aggregate score;
- observed citation-resolution counts for both systems;
- raw JSON outputs, machine-readable results, and a bad-case log with stable IDs;
- a nine-category bad-case taxonomy, each row backed by a recorded artifact;
- a five-layer evaluation map that separates machine checks from human judgment;
- recorded product decisions with evidence pointers;
- a blind review packet, a written review protocol, blank review and
  disagreement forms, and a blank target-user pilot record;
- observed host runtime and token usage, with unavailable values left `null`.

## The baseline

`lab/baseline_prompt.md` is unchanged. It receives the same project fixture, the
same JD, the same six-status evidence scale, the same evidence rules — plan is
not result, team is not ownership, tools are not judgment — and the same
canonical Application Pack schema, and it is told never to fill an output quota.
It is a competent user with a strong general-purpose model, not a strawman. Any
claim that Project2Job wins has to beat that.

## Automated result

All six recorded outputs pass the canonical Application Pack schema. Eight
deterministic checks ran per output:

| Check | baseline | skill |
| --- | --- | --- |
| Canonical output shape | 3/3 | 3/3 |
| Expected evidence statuses present | 3/3 | 3/3 |
| Unsupported resume export blocked | 3/3 | 3/3 |
| Answer claim-safety gate closed | 3/3 | 3/3 |
| Forbidden external claim absent | 3/3 | 3/3 |
| One Next Build targets the gold gap | 3/3 | 3/3 |
| Key source location resolves | 2/3 | 2/3 |
| All source locations resolve | 2/3 | 2/3 |

Six of eight checks came out identical. **The only dimension that separates the
two systems is the one neither passed**, and each failed a different case.

## The exact-source failure, root-caused

The open Day 5 bad case was the Project2Job `S01` output citing
`S01_project.md:2` for the 20-case evaluation plan, where line 2 is blank.

It is not a hallucination and not a prompt failure. The run cited `:2` for the
plan claim and `:3` for the README claim — consistently one less than the
absolute line numbers 3 and 4, because it numbered non-empty body lines and the
file has one blank line. Every citation in the run pointed at the right content
under its own convention. Six references were affected, including the top
Project Highlight and the verified evidence behind all three answer drafts.

| Step | Finding |
| --- | --- |
| Observed failure | An exported citation resolves to a blank line |
| Expected | The cited span contains the claim |
| Actual | Body-relative line numbering, off by one |
| Earliest divergence | The first citation written, not a later export step |
| Failure layer | Output contract and provenance, not intake, routing, context, extraction, or the model |
| Root cause | The shared contract required an "exact source_location" and never defined one. Two conventions were equally compliant, and `sourceRef.location` was an unconstrained string that schema validation could not check. |
| Smallest fix | Define one location grammar; resolve every citation against real text before export |
| Regression | `tests/test_source_resolution.py`, 24 tests |
| Before / after | Before: schema-valid and unresolvable, invisible. After: the same output fails a named severe gate with the exact JSON pointer of every bad citation. |

Running the same gate over the baseline found the mirror failure: all 19
citations in `baseline/S02.json` are prose anchors such as
`Team Project, sentence 1` and `Responsibilities, bullet 2`. They are
schema-valid and unresolvable by any reader or checker.

The grader also had a bad case of its own. Its first key-source check carried a
`sentence 1` branch that let the baseline pass a gate the Skill had to clear
with a line number. That accommodation is recorded as `T-GRADER-ACCOMMODATION`
and removed; both systems now face the one grammar.

The recorded outputs were not regenerated, so both severe cases remain **failed
cases**. What changed is that the failure can no longer escape.

## Observed source precision

| System | Citations | Resolved | Blank span | Unresolvable format |
| --- | ---: | ---: | ---: | ---: |
| Strong prompt | 60 | 41 | 0 | 19 |
| Project2Job Skill | 24 | 18 | 6 | 0 |

Three cases per system. This is a count, not a rate, and it says a citation
points at real text — not that the text supports the claim.

## Dogfood

The gate was run against the Skill's own shipped Brief example, which was not
built for it. Its first version rejected all 7 of that Brief's heading-anchor
citations. A heading names something a reader can find; an ordinal such as
`sentence 1` does not. The grammar now admits heading anchors and rejects
ordinal prose anchors, all 7 Brief citations resolve, and both recorded Day 5
failures still fail. Recorded in `docs/dogfood/DAY5_SOURCE_GATE_DOGFOOD.md`.

The earlier product-owner career-asset session is recorded separately in
`docs/dogfood/PROJECT2JOB_DAY5_CAREER_ASSET_DOGFOOD.md`. It rated an interview
asset 8/10, exposed risk leakage into a copyable script, and produced D-029. It
is product-owner target-user dogfood, not independent validation.

## Bad-case taxonomy

Nine categories in `lab/day5/bad_case_taxonomy.json`, each backed by a recorded
artifact and each naming the layer that has to change. A test fails if a
category cites a file that does not exist.

| ID | Layer | Status |
| --- | --- | --- |
| T-SOURCE-GRAMMAR | Output contract and provenance | Fixed at gate |
| T-UNVERIFIABLE-LOCATION | Output contract and provenance | Fixed at gate |
| T-GRADER-ACCOMMODATION | Rubric and grader | Fixed |
| T-OWNERSHIP-AMBIGUITY | Ownership and claim classification | Needs adjudication |
| T-ASSET-RISK-LEAKAGE | Career-asset packaging | Fixed (D-029) |
| T-CONTEXT-SELECTION-MISS | Context selection | Accepted tradeoff (D-026) |
| T-STALE-PERSISTENT-CLAIM | Orchestration and state | Fixed |
| T-HARNESS-ISOLATION | Eval harness | Open |
| T-HARNESS-INSTRUMENTATION | Eval harness | Open |

## Evaluation layers

`lab/day5/evaluation_layers.json` records what each layer measures and what it
does not. Layers 1–3 are executable and tested. Layer 4 is protocol only: every
human score is `null`. Layer 5 has not started. No automated grader stands in
for a reviewer.

## Product decisions

`lab/day5/product_decisions.json`, recorded as D-032.

| Mechanism | Verdict |
| --- | --- |
| Source location contract and citation gate | REVISE |
| Evidence gate on external export | KEEP |
| Six-status evidence scale | KEEP |
| Useful abstention over quota filling | KEEP |
| One Next Build recommendation | KEEP |
| Manifest-scoped context without retrieval | KEEP |
| Ownership handling on team artifacts | UNPROVEN |
| Structured flow versus the strong prompt | UNPROVEN |
| Retrieval, fine-tuning, or an agent framework | STOP |
| Blind two-reviewer human evaluation | KEEP |

## Observable efficiency only

| System | Input tokens | Cached input | Output tokens | Reasoning output |
| --- | ---: | ---: | ---: | ---: |
| Strong prompt | 493,062 | 383,232 | 19,772 | 1,929 |
| Project2Job Skill | 1,396,120 | 1,203,968 | 41,802 | 3,237 |

Observed wall time is incomplete for the baseline: 269.59 seconds over 2/3 runs
against 844.88 seconds over 3/3 Skill runs. The first baseline runtime, the
model identifier, and provider cost were unavailable and remain `null`. The
baseline host still loaded the global Skill catalog despite
`--ignore-user-config`, so the token difference cannot be attributed cleanly to
Project2Job instructions.

## Reproduce

```bash
python3 scripts/run_day5_evaluation.py --check
python3 -m unittest tests.test_day5_evaluation -v
python3 -m unittest tests.test_source_resolution -v
```

Inspect one recorded failure directly:

```bash
python3 skill/p2j/scripts/validate_output.py lab/day5/outputs/skill/S01.json --schema application_pack --source S01_project.md=lab/fixtures/fixture_project_plan_only.md
```

Print the generated records:

```bash
python3 scripts/run_day5_evaluation.py --print taxonomy
```

Fresh model generation stays separate from deterministic replay. Use the prompt,
route, isolation statement, and fixture paths in `capture_manifest.json`, then
validate every output with the command above.

## Acceptance traceability

| Acceptance criterion | Eval cases | Executable evidence | Result |
| --- | --- | --- | --- |
| D5-AC-01 Representative cases cover the product's boundary failure modes | D5-001, D5-002, D5-003, D5-004 | `test_gold_cases_are_complete_and_reuse_existing_cases` | Pass |
| D5-AC-02 The baseline is strong, unhandicapped, and comparable | D5-001, D5-002, D5-003 | `test_three_pairs_are_schema_valid_at_capture` | Pass |
| D5-AC-03 Deterministic checks stay separate from subjective quality | D5-001, D5-002, D5-003 | `test_human_judgement_layers_claim_no_measurement` | Pass |
| D5-AC-04 One severe per-case failure overrides any aggregate score | D5-001, D5-002 | `test_severe_error_is_not_hidden_by_aggregate_scores` | Pass |
| D5-AC-05 Both systems face the same grader | D5-001, D5-002, D5-003 | `test_both_systems_face_the_same_citation_grammar` | Pass |
| D5-AC-06 An exported citation must resolve to real text | D5-001, D5-002 | `test_blank_line_citation_does_not_resolve`, `test_schema_valid_output_still_fails_on_an_unresolved_citation` | Pass |
| D5-AC-07 Source precision is observed for both systems | D5-001, D5-002, D5-003 | `test_source_precision_is_observed_for_both_systems` | Pass |
| D5-AC-08 Every bad case maps to a taxonomy category backed by a real artifact | D5-001, D5-002 | `test_every_taxonomy_category_is_backed_by_a_real_artifact`, `test_every_emitted_bad_case_maps_to_a_taxonomy_category` | Pass |
| D5-AC-09 Bad-case IDs stay stable when a new failure is found | D5-001, D5-002 | `test_bad_case_ids_are_stable_under_new_findings` | Pass |
| D5-AC-10 Unobservable measurements and human results stay null | D5-001, D5-002, D5-003 | `test_unobservable_measurements_and_human_results_stay_null` | Pass |
| D5-AC-11 Human review has a protocol and no fabricated record | D5-001, D5-002, D5-003 | `test_human_templates_contain_no_fabricated_review`, `test_review_protocol_names_who_reviewed_and_what_that_does_not_prove` | Pass |
| D5-AC-12 Product decisions cite evidence that exists | D5-001, D5-002, D5-003 | `test_product_decisions_cite_evidence_and_use_allowed_verdicts` | Pass |
| D5-AC-13 The product's own shipped output passes its own gate | D5-003 | `test_shipped_brief_citations_all_resolve` | Pass |
| D5-AC-14 The Agent comparison stays a bounded mechanics result | D5-004 | `test_agent_comparison_remains_bounded` | Pass |

## Maturity

| Label | Day 5 state |
| --- | --- |
| IMPLEMENTED | Cases, baseline, recorded runs, layered evaluation, citation gate, taxonomy, layer map, review protocol, and product decisions exist and run. |
| TESTED | 15 Day 5 tests and 24 source-resolution tests pass; the full suite is 309 tests. |
| DOGFOODED | Two sessions: the source gate against real Project2Job surfaces, and the earlier product-owner career-asset session. |
| HUMAN-REVIEWED | No. Every blind reviewer score is null. |
| USER-VALIDATED | No. No target user has completed the bounded pilot. |
| OUTCOME-PROVEN | No application, interview, or hiring outcome is established. |

## What is not yet proven

- that Project2Job beats the strong prompt; six of eight checks tied and no
  human has scored either output;
- reviewer preference, usability, or actual external use;
- whether first-person team framing stays inside the evidence boundary;
- complete latency or provider cost, and clean token attribution;
- model-specific quality and live-host behavior;
- anything about a population: three cases support direction, not a rate;
- Agent advantage beyond the existing deterministic mechanics comparison.

## Bad case or tradeoff

The most useful Day 5 finding is uncomfortable for the product. On these three
boundary cases a strong prompt carrying the same evidence rules refused to
overclaim exactly as often as the structured system did. The structured system's
defensible advantage is not that its judgments were better here; it is that it
can carry an enforcing gate a one-shot prompt cannot. That is an argument about
architecture, and it stays UNPROVEN as a product claim until a reviewer says the
output is worth using.

## Public content notes

- Lead with the root cause: an undefined contract, not a hallucinating model.
- Show that the evaluation found a failure in its own grader.
- Report six of eight checks tied; do not hide it behind the one difference.
- Never rename this offline comparison as an A/B test.
