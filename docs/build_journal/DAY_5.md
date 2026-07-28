# Day 5 — Evaluation and Model Decisions

Status: PLANNED

Review gate: PENDING HUMAN REVIEW

The reproducible offline package is prepared and automated checks have run.
Day 5 is not implemented or validated because blind reviewer scores,
disagreement adjudication, a complete bounded pilot record, and a resulting
model/product decision do not exist. One later product-owner target-user
dogfood session is recorded, but it is not independent validation.

## Question

Does Project2Job outperform a strong prompt, and what model approach is
justified?

## Evaluation package

`lab/day5/` contains:

- the unchanged strong prompt baseline and three recorded baseline outputs;
- three comparable Project2Job `APPLICATION_PACK` outputs;
- gold expectations reusing `S01`, `S02`, `S05`, and `A17_COMPARISON`;
- per-case severe checks that override any future aggregate score;
- raw JSON outputs, machine-readable results, and a bad-case log;
- a blind review packet, blank review form, and disagreement template;
- a blank target-user pilot record;
- observed host runtime and token usage, with unavailable values left `null`.

The representative cases cover plan versus result, team versus personal
ownership, and implementation versus user value. The Agent comparison remains
the existing deterministic update-versus-fresh-replay dogfood; it is not
relabeled as a live-model or user-value result.

## Automated result

All six recorded outputs passed the canonical Application Pack schema at
capture. The deterministic evaluator found one severe exact-source failure:
the Project2Job `S01` output cites `S01_project.md:2` for the 20-case plan, but
line 2 is blank and the claim appears on line 3. The claim exists in the
permitted source, but its external-facing citation does not resolve. The
automated gate therefore fails regardless of any future average score.

The ownership case also remains explicitly pending human adjudication because
both systems use first-person team framing while individual contribution is
unconfirmed.

## Product-owner target-user dogfood

A real product-owner target-user dogfood session reviewed a Project2Job Day 5
interview answer. The participant rated the asset 8/10 and said they would use
it after minor-to-moderate editing. Actual external use was not observed.

The bad case was career-asset packaging: accurate safety and evidence warnings
leaked into the spoken answer, making pending validation, failed gates, and
missing outcomes more memorable than the supported achievement, product
judgment, and role relevance. An ad hoc correction successfully separated the
strong external script from private warnings.

The session is recorded in
`docs/dogfood/PROJECT2JOB_DAY5_CAREER_ASSET_DOGFOOD.md` and now backs a shared
policy plus behavioral regressions. It is product-owner target-user dogfood,
not independent user validation or proof of hiring impact.

## Observable efficiency only

The host exposed token counts for all six runs:

| System | Input tokens | Cached input tokens | Output tokens | Reasoning output tokens |
| --- | ---: | ---: | ---: | ---: |
| Strong prompt | 493,062 | 383,232 | 19,772 | 1,929 |
| Project2Job Skill | 1,396,120 | 1,203,968 | 41,802 | 3,237 |

Observed wall time totals are incomplete for the baseline: 269.59 seconds over
2/3 runs. The Skill total is 844.88 seconds over 3/3 runs. These totals are
reported as observed execution data, not as a complete latency comparison. The
first baseline runtime, model identifier, and provider cost were unavailable
and remain `null`.

The baseline host still loaded the global Skill catalog despite
`--ignore-user-config`. No Project2Job Skill file was opened in the baseline
traces, but perfect catalog isolation was not observable. This limitation is in
the bad-case log and prevents a clean token-overhead attribution.

## Reproduce

```bash
python3 scripts/run_day5_evaluation.py --check
python3 -m unittest tests.test_day5_evaluation -v
```

The committed evaluator rebuilds the machine results, bad-case log, and blind
packet from the recorded raw outputs and fails if they drift.

Focused verification on 2026-07-27:

- 7 Day 5 tests passed;
- all 6 committed outputs passed full Application Pack schema validation with
  `jsonschema>=4`;
- `make validate` passed with 14 active documents, 42 JSON files, 112 JSONL
  cases, 20 public fixture files, 84 schema references, and highest completed
  Day 4;
- `make test` ran 250 tests: 233 passed and 17 optional `jsonschema` tests
  skipped in the default environment;
- `make inventory` found 3 files and no duplicate groups;
- `git diff --check` passed with no output;
- `make skill-package` built `dist/project2job-skill-suite-alpha.zip`.

Career-asset packaging verification on 2026-07-28:

- the Skill Creator validator passed `p2j`, `p2j-answer`, and `p2j-mock`;
- 90 focused Skill and Application Pack tests passed with
  `jsonschema>=4`;
- `make validate` passed with 14 active documents, 42 JSON files, 119 JSONL
  cases, 20 public fixture files, 84 schema references, and highest completed
  Day 4;
- `make test` ran 256 tests: 239 passed and 17 optional `jsonschema` tests
  skipped in the default environment;
- `make inventory` found 3 files and no duplicate groups;
- `git diff --check` passed with no output;
- `make skill-package` built `dist/project2job-skill-suite-alpha.zip`.

## Human review still required

Before Day 5 can change status:

1. two independent reviewers must score A and B for all three cases using the
   0–3 rubric;
2. any category delta over one point and every severe-error disagreement must
   be adjudicated;
3. the exact-source failure must remain a failed case or be corrected through
   a new recorded Skill run and regression;
4. a bounded target-user pilot record must include first useful output,
   corrections, selected asset, edit level, and any action actually taken; the
   product-owner dogfood captured the correction, rating, and stated use but
   not first-use timing or actual external use;
5. only then may the project record reviewer preference, product usability, or
   a continue/change/stop decision.

## Candidate decision checkpoint

- Decision to make: prompt, retrieval/RAG, fine-tuning, and model/runtime choice.
- Current decision: pending.
- Current constraint: no retrieval, fine-tuning, framework, or product feature
  is justified by this package.
- Evidence still needed: blind scores, adjudicated disagreements, target-user
  actions, and a corrected or accepted severe case.

## What is not yet proven

- that Project2Job beats the strong prompt;
- independent usability or actual use beyond the product owner's stated intent;
- that a target user takes an external action;
- complete latency or provider-cost differences;
- model-specific quality;
- Agent advantage beyond the existing deterministic mechanics comparison.

## Public content notes

- Publish the unchanged baseline prompt.
- Lead with the exact-source failure and unresolved ownership wording.
- Keep blind-review fields blank until observed and leave any uncaptured pilot
  fields null.
- Never rename this offline comparison as an A/B test.
