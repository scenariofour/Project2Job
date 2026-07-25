# WO-00 Shared Foundation

Context set: `shared_foundation`

Status: IMPLEMENTED

This status means the shared contracts and gold cases pass repository validation.
It does not mean hiring relevance, product quality, or user value is validated.

## Goal

Finalize the shared Role Standard, evidence model, and output contracts before parallel development.

## Deliver

- validated role profile
- 10 labeled role/project cases
- final output schema
- source registry
- reviewer instructions
- baseline prompt

## Acceptance

- schemas parse
- every role capability has evidence tests
- every gold label has source and boundary
- Skill and Agent can consume the same contracts
- no implementation framework is required

## Stop

Do not build the Skill or Agent runtime in this Work Order.

## Implemented artifacts

- Role profile:
  `references/role_profiles/ai_pm_early_career.v0.1.0.json`
- Shared consumer contract: `references/shared_contract.v1.json`
- Schemas: `schemas/role_profile.schema.json`,
  `schemas/project_evidence.schema.json`,
  `schemas/application_pack.schema.json`, and `schemas/gold_case.schema.json`
- Gold cases: `lab/evals/shared_foundation_cases.v0.1.0.jsonl`
- Reviewer guide: `lab/REVIEWER_AND_ANNOTATION_GUIDE.md`
- Baseline: `lab/baseline_prompt.md`
- Reviewed source registry: `references/source_registry.json`

## Validation

- 10 capability domains each have an explicit evidence test
- 10 gold cases cover every domain and all six evidence statuses
- every gold label has a resolvable source location and evidence boundary
- Skill and Agent declarations resolve the same role and schema versions
- repository validation and contract tests pass without a runtime framework
