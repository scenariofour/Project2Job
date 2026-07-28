# Implementation Map

Days are the public learning narrative. Work Orders are the engineering
dependency system.

One Day may use several Work Orders, and one Work Order may support several
Days. Engineering dependencies must not be distorted to match content order.
The active scope, manifest context sets, and Work Order acceptance criteria
remain authoritative.

| Day | Public focus | Supporting Work Orders |
| --- | --- | --- |
| 0 | Safe repository foundation | Enables all Work Orders; no Work Order completed |
| 1 | Agent loop and observable control | WO-02 |
| 2 | Problem, MVP, intent, and routing | WO-00, WO-05, WO-01, WO-02 |
| 3 | Context, retrieval, provenance, and evidence | WO-00, WO-02, WO-04 |
| 4 | Skill/Agent boundary and human control | WO-01, WO-02, WO-03 |
| 5 | Evaluation and model decisions | WO-00, WO-01, WO-02, WO-04 |
| 6 | Tool/API contracts and safe failure | WO-02, WO-03, WO-04 |
| 7 | Product experience, pilot, and defense | WO-03, WO-04 |

Day 0 imports the Work Order system but does not claim any Work Order is
complete. Later implementation must follow dependency evidence even when the
public narrative discusses a concept earlier or later.

Day 3 is IMPLEMENTED and TESTED through the existing WO-00/WO-02 foundations,
the focused WO-04-style deterministic comparison in
`docs/build_journal/traces/day3_context_comparison.json`, and D-026. The result
does not complete WO-04's user-pilot or outcome requirements. Days 5–7 remain
PLANNED.

Day 4 is IMPLEMENTED and TESTED through the existing WO-01/WO-02 Skill,
Context Registry, and Stateful Agent paths, the focused correction/update/export
coverage, `docs/dogfood/STATEFUL_AGENT_V0_COMPARISON.json`, and D-027. It adds no
WO-03 Web implementation and does not complete target-user or live-model
validation. Days 5–7 remain PLANNED.
