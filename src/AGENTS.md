# Agent implementation rules

Read the `agent_poc` context set from `PROJECT_MANIFEST.json`.

Implement one Evidence Investigator.

Do not add specialist Agents or handoffs.

All tools must be:

- read-only in MVP
- schema-defined
- timeout-aware
- observable
- testable without a model

State updates and output invalidation must use deterministic code.
