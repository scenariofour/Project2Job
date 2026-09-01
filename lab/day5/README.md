# Day 5 Evaluation Package

Status: implemented and tested. Blind human review and the target-user pilot are
still outstanding; every human score in this directory is `null`.

## What this compares

The unchanged strong generic prompt in `lab/baseline_prompt.md` against the
Project2Job `APPLICATION_PACK` path, over three existing synthetic boundary
cases:

- `S01` / `D5-001`: a plan is not an executed result
- `S02` / `D5-002`: team work is not personal ownership
- `S05` / `D5-003`: implementation is not user value

Same host, project fixture, JD, evidence rules, and canonical output schema for
each pair. The six raw JSON outputs are under `outputs/`. `D5-004` reuses the
existing bounded Agent update-versus-fresh-replay mechanics comparison.

`capture_manifest.json` records observed host metadata, token usage, wall time,
the working file names the capture presented, and explicit measurement gaps.
Provider cost, one baseline runtime, the model identifier, human scores,
reviewer disagreement, target-user feedback, and product value remain `null`.

`skill/p2j/examples/sample_brief.md` is retained as a structural calibration
output. It is not preference-scored: a Brief is not comparable with an
Application Pack.

## Generated records

Everything below is rebuilt from the recorded outputs and fails the check
command if it drifts:

| File | What it holds |
| --- | --- |
| `results.json` | Per-case checks, citation resolution, severe errors, measurements |
| `bad_cases.jsonl` | Bad cases with stable content-derived IDs and taxonomy links |
| `bad_case_taxonomy.json` | Nine categories, each backed by a real artifact |
| `evaluation_layers.json` | What each of the five layers measures and does not |
| `blind_review_packet.md` | Blinded outputs for reviewers |

`product_decisions.json` is authored, not generated: a verdict is a judgment.
Each decision cites evidence that a test confirms exists.

## Reproduce

```bash
python3 scripts/run_day5_evaluation.py --check
python3 -m unittest tests.test_day5_evaluation -v
python3 -m unittest tests.test_source_resolution -v
```

Inspect the recorded exact-source failure:

```bash
python3 skill/p2j/scripts/validate_output.py lab/day5/outputs/skill/S01.json --schema application_pack --source S01_project.md=lab/fixtures/fixture_project_plan_only.md
```

Print any generated record:

```bash
python3 scripts/run_day5_evaluation.py --print taxonomy
```

Rewrite them after a deliberate change:

```bash
python3 scripts/run_day5_evaluation.py --write
```

Full schema validation requires `jsonschema>=4`. Fresh model generation stays
separate from deterministic replay: use the prompt, route, isolation statement,
and fixture paths in `capture_manifest.json`, capture the host JSONL event
stream and wall time, then validate each output with the command above.

## Human review

Follow `REVIEW_PROTOCOL.md`. Give reviewers only `blind_review_packet.md`, a
copy of `human_review.template.jsonl`, and `lab/scoring_rubric.md`. Use two
independent reviewers. Do not reveal `capture_manifest.json`; it holds the A/B
key.

Record a disagreement when category scores differ by more than one point or when
reviewers disagree about a severe external-facing claim. Resolve it with
`reviewer_disagreement.template.jsonl`. Do not average it away.

No artifact here supports a Skill-preference, user-value, cost, or product
impact claim.
