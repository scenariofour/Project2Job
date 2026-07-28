# Day 5 Evaluation Package

Status: prepared; pending blind human review and target-user pilot.

A later product-owner target-user dogfood session is recorded separately in
`docs/dogfood/PROJECT2JOB_DAY5_CAREER_ASSET_DOGFOOD.md`. It found a career-asset
packaging failure and produced the regression policy in this change. It is not
part of the captured six-output comparison, does not replace blind review, and
is not independent user validation.

This package compares the unchanged strong generic prompt in
`lab/baseline_prompt.md` with the Project2Job `APPLICATION_PACK` path on three
existing synthetic cases:

- `S01`: plan versus executed result
- `S02`: team work versus personal ownership
- `S05`: implementation versus user value

The same host, project fixture, JD, and canonical output schema were used for
each pair. The six raw JSON outputs are under `outputs/`. `capture_manifest.json`
records only observed host metadata, token usage, wall time, and explicit
measurement gaps. Provider cost, one baseline runtime, the model identifier,
human scores, reviewer disagreement, target-user feedback, and product value
remain `null`.

The existing `skill/p2j/examples/sample_brief.md` is retained as a structural
calibration output. It is not preference-scored because a Brief is not directly
comparable with the canonical Application Packs used in the blind packet.

## Reproduce the deterministic checks

```bash
python3 scripts/run_day5_evaluation.py --check
python3 -m unittest tests.test_day5_evaluation -v
```

Fresh model generation is intentionally separate from deterministic replay.
Use the exact prompt, route, isolation statement, and fixture paths recorded in
`capture_manifest.json`; capture the host JSONL event stream and wall time, then
validate every output with:

```bash
python3 skill/p2j/scripts/validate_output.py \
  --schema application_pack <output.json>
```

Full schema validation requires `jsonschema>=4`.

## Human review

Give reviewers only `blind_review_packet.md`,
`human_review.template.jsonl`, and `lab/scoring_rubric.md`. Use two independent
reviewers. Do not reveal `capture_manifest.json`, which contains the A/B key.

Record a disagreement when category scores differ by more than one point or
when reviewers disagree about a severe external-facing claim. Resolve it with
`reviewer_disagreement.template.jsonl`; do not average away the disagreement.

The comparison remains pending until:

1. two independent blind reviews exist for all three cases;
2. every severe-error disagreement is adjudicated;
3. the open exact-source failure is resolved or accepted as a failed Skill case;
4. at least one eligible target user completes the bounded pilot record in
   `target_user_pilot.template.jsonl`;
5. the evidence supports a continue, change, or stop decision.

No current artifact supports a Skill-preference, user-value, cost, or product
impact claim.
