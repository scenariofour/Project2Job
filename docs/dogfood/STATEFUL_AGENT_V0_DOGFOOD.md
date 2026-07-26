# Stateful Agent V0 Dogfood

Date: 2026-07-26

Status: host-mediated repository dogfood, not deterministic model validation and
not target-user validation.

## Repository gap audit

Before this slice, `main` contained a deterministically tested per-claim
Evidence Investigator and a host-native Skill suite. The stateful run paths
existed only as product documents, a stub state schema, and four eval records.
There was no persistent context on `main`, Project/JD version resolution,
correction application, dependency traversal, selective regeneration,
orchestration runtime, four-state report, or measured fresh-run comparison.

## Live host-mediated decision

The runtime observed one added Project artifact, `eval_results.csv`, with an
unchanged JD and no pending correction. After seeing that observation, the
Codex host supplied the allowed `investigate_evidence` action. The action
rechecked the new evaluation evidence and updated only `score_evaluation` and
`match_eval`.

This proves the host adapter can accept a decision made from an observation. It
does not prove live model decision quality.

## Scripted comparison

`STATEFUL_AGENT_V0_COMPARISON.json` records the exact run.

| Metric | Stateful update | Fresh Skill rerun |
| --- | ---: | ---: |
| Files read | 1 | 5 |
| Repeated questions | 0 | 1 |
| Capability calls | 1 | 2 |
| Expected outputs correctly updated | 2 | 2 |
| Unaffected outputs incorrectly changed | 0 | 0 |
| Outputs regenerated | 2 | 11 |
| Token usage | unavailable | unavailable |

The stateful update shows an advantage for this scripted case on reads,
repeated questions, calls, and selective regeneration without losing output
correctness. The sub-millisecond local latency values are not representative,
and the fresh run happened to be faster at this scale, so no latency advantage
is claimed.

## Report review

The four local reports were rendered in headless Chrome at 1440×1400 and
reviewed against the Stitch reference. They share one shell, show Project and JD
context, use an ordered Agent activity rail, derive changed/preserved lists from
the trace, and require approval before correction.

## Still unproven

- live model planning quality and token use
- target-user comprehension, usability, and asset adoption
- production latency, concurrency, and recovery
- company-research refresh against live public sources
- Agent advantage outside the scripted update case
- cross-host live invocation after package installation
