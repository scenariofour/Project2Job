# Day 5 Blind Human Review Packet

Review only this packet. Do not open `capture_manifest.json`, which contains the label key.
Score each output 0–3 using `lab/scoring_rubric.md`. A severe fabricated
external-facing claim fails the output regardless of its other scores.
Record two independent reviews in copies of `human_review.template.jsonl`.
Adjudicate a score delta greater than 1 or any severe-error disagreement
with `reviewer_disagreement.template.jsonl`.

## D5-001: plan is not an executed result

### Project input

```text
# Agent Project

The team designed an evaluation plan for 20 cases. The plan has not been run.
The README claims the system will improve evidence accuracy.
```

### Target JD

```text
# Junior AI Product Manager

Responsibilities:

- identify valuable user workflows for generative AI
- define MVP scope and product requirements
- work with engineering and design
- design evaluation and quality measurement
- understand Agent tools, context, reliability, and safety
- analyze failures and prioritize improvements
- communicate product decisions and tradeoffs
```

### Output A

```json
{
  "role_fit_map": [
    {
      "role_requirement_id": "REQ-WORKFLOW",
      "capability_id": "D1",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "The supplied project names no user, workflow, pain, alternative, or discovery evidence.",
      "interview_risk": "Cannot substantiate identifying a valuable user workflow."
    },
    {
      "role_requirement_id": "REQ-MVP",
      "capability_id": "D2",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "No MVP scope, product requirements, rejected alternative, or release criterion is supplied.",
      "interview_risk": "Cannot defend prioritization or product tradeoffs."
    },
    {
      "role_requirement_id": "REQ-AGENT-SYSTEM",
      "capability_id": "D4",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "The title calls this an Agent project, but no implemented state, actions, tools, context, stop conditions, or controls are described.",
      "interview_risk": "Calling it an Agent would invite technical follow-ups the evidence cannot answer."
    },
    {
      "role_requirement_id": "REQ-EVAL",
      "capability_id": "D6",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "SRC-PROJECT",
          "location": "S01_project.md:2"
        }
      ],
      "boundary": "A team-designed 20-case evaluation plan is documented, but it was not run; no rubric, results, disagreements, or failure-driven decision is supplied.",
      "interview_risk": "Must describe evaluation as planned, not executed or outcome-producing."
    },
    {
      "role_requirement_id": "REQ-RELIABILITY-SAFETY",
      "capability_id": "D7",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "No named reliability or safety risk, enforced control, or failure test is supplied.",
      "interview_risk": "Cannot answer how the system contains failures or requires human control."
    },
    {
      "role_requirement_id": "REQ-XFN-DELIVERY",
      "capability_id": "D9",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [],
      "boundary": "Team language does not establish collaboration with engineering or design, implementation, release, or learning-loop evidence.",
      "interview_risk": "Do not convert a team-authored plan into personal cross-functional delivery."
    },
    {
      "role_requirement_id": "REQ-COMMUNICATION-OWNERSHIP",
      "capability_id": "D10",
      "relevance": "important",
      "status": "needs_confirmation",
      "source_refs": [
        {
          "source_id": "SRC-PROJECT",
          "location": "S01_project.md:2"
        }
      ],
      "boundary": "The artifact attributes the evaluation plan to the team; the candidate's decisions and contribution are unconfirmed.",
      "interview_risk": "First-person ownership would exceed the supplied evidence."
    }
  ],
  "project_highlights": [
    {
      "text": "The project contains a team-designed evaluation plan covering 20 cases.",
      "source_refs": [
        {
          "source_id": "SRC-PROJECT",
          "location": "S01_project.md:2"
        }
      ],
      "boundary": "Supported only as a documented, unexecuted team plan; personal ownership, case quality, and results are not established."
    }
  ],
  "resume_bullets": [],
  "intro_30_seconds": "This project is currently best presented as an early evaluation-design effort: the team documented a 20-case plan for an Agent project, but the plan has not been run. It can support a bounded discussion of evaluation design; it does not demonstrate user discovery, Agent architecture, measured accuracy improvement, delivery, or personal ownership.",
  "answer_drafts": [
    {
      "question": "How would you design and use an evaluation for an Agent product?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The team designed an evaluation plan for 20 cases, and the plan has not been run.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "SRC-PROJECT",
              "location": "S01_project.md:2"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "State that this is development-stage evaluation design, not an executed evaluation.",
        "Describe the 20 planned cases without claiming their composition, rubric, or results.",
        "Require results to drive a product decision before claiming a learning loop."
      ],
      "grounded_draft": "Observed: the team designed a 20-case evaluation plan, but it has not been run. I would therefore present this as evaluation design in progress, not evidence of quality improvement. The next defensible step is to define reviewer rules and failure categories, execute the cases, preserve disagreements and bad cases, and use the findings to make a specific product decision.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I built and ran a 20-case evaluation that improved accuracy."
      },
      "likely_followups": [
        "What do the 20 cases cover?",
        "What is the rubric and decision rule?",
        "Which result changed the product?"
      ]
    },
    {
      "question": "What failure categories would you analyze, and how would they change priorities?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The team designed an evaluation plan for 20 cases, and the plan has not been run.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "SRC-PROJECT",
              "location": "S01_project.md:2"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Acknowledge that no observed failures are supplied.",
        "Frame any taxonomy and prioritization rule as proposed during development.",
        "Tie future changes to executed results rather than the README claim."
      ],
      "grounded_draft": "Observed: the evaluation plan exists but has not been run, so I cannot claim an observed failure taxonomy or failure-driven improvement. Proposed During Development: before execution, I would classify failures by workflow stage and severity, define which require stopping or human review, and prioritize only after reviewing actual bad cases and their effect on the target user task.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ]
      },
      "likely_followups": [
        "Which failure classes would be highest severity?",
        "How would you avoid a model grading itself?",
        "What result would cause you to stop release?"
      ]
    },
    {
      "question": "How would you bound Agent tools, context, reliability controls, and safety?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The team designed an evaluation plan for 20 cases, and the plan has not been run.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "SRC-PROJECT",
              "location": "S01_project.md:2"
            }
          ]
        },
        {
          "fact_id": "F2",
          "text": "The README claims the system will improve evidence accuracy.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "SRC-PROJECT",
              "location": "S01_project.md:3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Separate the README's future claim from measured performance.",
        "State that tool, context, permission, and stop-condition evidence is not supplied.",
        "Offer a counterfactual decision method without presenting it as implemented."
      ],
      "grounded_draft": "Observed: the README states an intended improvement in evidence accuracy, while the supplied material does not describe tools, context selection, permissions, stop conditions, or executed reliability evidence. Counterfactual: I would start from the user decision that cannot be fixed in advance, minimize tool permissions and context to what that decision needs, define ask-or-stop conditions for uncertainty and unsafe actions, and test those boundaries before calling the workflow a reliable Agent.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1",
          "F2"
        ],
        "narrowed_from": "The Agent uses bounded tools and context to improve evidence accuracy."
      },
      "likely_followups": [
        "What decision actually requires autonomy?",
        "Which tool calls need approval?",
        "How would you test context failures or prompt injection?"
      ]
    }
  ],
  "next_build": {
    "gap": "The only concrete artifact is an unexecuted 20-case evaluation plan, so the project cannot demonstrate measured quality, failure analysis, reliability decisions, or a learning loop.",
    "why_now": "Completing one bounded, human-reviewed evaluation and using its bad cases to make one product decision would create the most direct evidence for the JD's evaluation, failure-prioritization, reliability, safety, and tradeoff requirements. A broader Agent architecture write-up is the rejected runner-up because it would add design detail without measured behavior.",
    "steps": [
      "Have a downstream working agent inspect the project's goals, current workflow, architecture, known failures, tests, and safety boundaries before proposing evaluation mechanics.",
      "Define the smallest product-relevant evaluation direction tied to one current user task; compare reasonable review and baseline options, then return an exploration brief for product-owner approval and stop before implementation.",
      "After explicit approval, execute the approved 20-case evaluation with versioned cases, reviewer rules, a failure taxonomy, an appropriate baseline, and named safety or stop conditions.",
      "Record exact commands, changed files, results, reviewer disagreements, bad cases, one resulting keep-revise-stop decision, remaining limitations, and produced artifacts without inventing users, metrics, outcomes, ownership, or test results."
    ],
    "acceptance_criteria": [
      "All 20 cases are versioned and tied to the same bounded user task and system version.",
      "A review rubric, reviewer provenance, disagreement handling, failure categories, and release or stop decision rule are inspectable.",
      "Executed results include per-case outcomes and bad cases; synthetic cases are labeled synthetic and not represented as user validation.",
      "At least one observed failure leads to a documented keep, revise, or stop product decision.",
      "Relevant safety boundaries and human-review or stop behavior are tested, with limitations preserved."
    ],
    "expected_evidence": "Versioned cases, rubric, human-review records, executed results, failure taxonomy, bad-case examples, safety-boundary results, and a decision log linking observed evidence to one product change or stop decision.",
    "output_dependency": "Only after completion and reassessment may D6 and relevant D7/D8 evidence, evaluation and failure-analysis stories, answer drafts, project highlights, or resume bullets change; the current match remains unchanged while this is proposed work.",
    "estimated_effort_band": "medium",
    "interview_question_unlocked": "Which evaluation failure changed your Agent product decision, and what reliability or safety boundary did you add?"
  },
  "warnings": [
    "No context was saved.",
    "No web research was run because the JD is synthetic and web search was prohibited.",
    "The project was not executed; the evaluation plan remains unrun.",
    "The README's accuracy statement is a future claim, not measured evidence.",
    "Team authorship does not establish the candidate's personal ownership."
  ]
}
```

### Output B

```json
{
  "role_fit_map": [
    {
      "role_requirement_id": "JD-EVALUATION",
      "capability_id": "evaluation-and-quality-measurement",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "S01_project.md",
          "location": "line 3"
        },
        {
          "source_id": "target_jd.md",
          "location": "line 8"
        }
      ],
      "boundary": "The evidence supports that the team designed a 20-case evaluation plan. It does not establish the candidate's individual ownership, the evaluation criteria, execution, findings, or measured quality.",
      "interview_risk": "The plan has not been run, so it proves planning only and cannot support claims about results."
    },
    {
      "role_requirement_id": "JD-RELIABILITY-SAFETY",
      "capability_id": "agent-reliability-and-safety",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 9"
        }
      ],
      "boundary": "The JD requires understanding Agent tools, context, reliability, and safety. The project document does not identify tools, context handling, reliability mechanisms, safety analysis, or safeguards.",
      "interview_risk": "The README's improvement claim is not evidence of reliability or safety competence."
    },
    {
      "role_requirement_id": "JD-FAILURE-ANALYSIS",
      "capability_id": "failure-analysis-and-prioritization",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 10"
        },
        {
          "source_id": "S01_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "The role requires failure analysis and prioritization, but the unexecuted plan produced no documented failures, analysis, or improvement priorities.",
      "interview_risk": "Do not present planned cases as observed failures or prioritized improvements."
    },
    {
      "role_requirement_id": "JD-MVP-REQUIREMENTS",
      "capability_id": "mvp-scope-and-product-requirements",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 6"
        }
      ],
      "boundary": "The JD requires MVP scope and product requirements. No scope, requirements, acceptance criteria, or candidate-authored product decisions appear in the project source.",
      "interview_risk": "The evaluation plan should not be relabeled as an MVP definition or product requirements document."
    },
    {
      "role_requirement_id": "JD-USER-WORKFLOWS",
      "capability_id": "generative-ai-workflow-discovery",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 5"
        }
      ],
      "boundary": "The JD calls for identifying valuable generative-AI workflows. The project source identifies no users, workflow, need, discovery method, or value evidence.",
      "interview_risk": "Do not invent a target user or workflow from the generic project title."
    },
    {
      "role_requirement_id": "JD-CROSS-FUNCTIONAL",
      "capability_id": "engineering-and-design-collaboration",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 7"
        },
        {
          "source_id": "S01_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "The source uses team language but does not identify engineering or design partners, the candidate's role, or any collaboration activity.",
      "interview_risk": "Team language does not establish individual collaboration or ownership."
    },
    {
      "role_requirement_id": "JD-DECISIONS-TRADEOFFS",
      "capability_id": "product-decision-communication",
      "relevance": "supporting",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 11"
        }
      ],
      "boundary": "The JD requires communication of product decisions and tradeoffs. No decision, alternative, tradeoff, rationale, or communication artifact is documented.",
      "interview_risk": "Do not infer product judgment merely from the existence of an evaluation plan."
    }
  ],
  "project_highlights": [
    {
      "text": "The project team designed an evaluation plan covering 20 cases.",
      "source_refs": [
        {
          "source_id": "S01_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "Supported as a team planning activity; individual ownership, case design quality, and execution are not established."
    },
    {
      "text": "The project documentation explicitly states that the 20-case evaluation plan has not been run.",
      "source_refs": [
        {
          "source_id": "S01_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "This establishes project status, not evaluation results or system performance."
    }
  ],
  "resume_bullets": [],
  "intro_30_seconds": "I can discuss an agent project in which the team designed a 20-case evaluation plan. The available record says the plan has not yet been run, so I would present this as evaluation-planning experience rather than evidence of measured improvement. The README states an intended improvement in evidence accuracy, but no result currently verifies that claim.",
  "answer_drafts": [
    {
      "question": "How would you design and execute an evaluation for a generative-AI product?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The team designed an evaluation plan for 20 cases.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S01_project.md",
              "location": "line 3"
            }
          ]
        },
        {
          "fact_id": "F2",
          "text": "The plan has not been run.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S01_project.md",
              "location": "line 3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "State that the documented experience is evaluation planning.",
        "Name the documented scale of 20 cases.",
        "Disclose that execution and results are still missing.",
        "Describe execution as a proposed next step, not past work."
      ],
      "grounded_draft": "The evidence I can verify is that my project team designed a 20-case evaluation plan. The plan has not been run, so I would not claim measured performance or improvement. The next step I recommend is to define pass criteria and a baseline, execute all 20 cases consistently, record case-level failures, and summarize the results so improvement priorities can be based on observed evidence.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1",
          "F2"
        ],
        "narrowed_from": "I designed and ran a 20-case evaluation that improved evidence accuracy."
      },
      "likely_followups": [
        "What were the 20 cases?",
        "What metrics and pass thresholds would you use?",
        "What was your individual role in designing the plan?"
      ]
    },
    {
      "question": "How would you investigate Agent reliability, context, and safety failures?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The team designed an evaluation plan for 20 cases.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S01_project.md",
              "location": "line 3"
            }
          ]
        },
        {
          "fact_id": "F2",
          "text": "The plan has not been run.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S01_project.md",
              "location": "line 3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Use the evaluation plan only as evidence of planning.",
        "Acknowledge that no observed failure data exists.",
        "Frame failure taxonomy and prioritization as recommendations."
      ],
      "grounded_draft": "The project gives me a starting point—a team-designed plan with 20 cases—but it does not yet provide reliability or safety findings because the plan has not been run. I would execute the cases, record failures without collapsing them into one score, classify issues such as context loss, unsupported evidence, tool errors, and unsafe behavior, and then prioritize by user impact, frequency, and severity. That is my proposed method, not a claim about completed project analysis.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1",
          "F2"
        ],
        "narrowed_from": "I analyzed Agent failures and prioritized reliability and safety improvements."
      },
      "likely_followups": [
        "Which failure categories were actually included in the plan?",
        "How would you assess low-frequency, high-severity safety failures?",
        "What evidence would change your prioritization?"
      ]
    },
    {
      "question": "How do you distinguish a quality target from a measured product result?",
      "verified_evidence": [
        {
          "fact_id": "F2",
          "text": "The evaluation plan has not been run.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S01_project.md",
              "location": "line 3"
            }
          ]
        },
        {
          "fact_id": "F3",
          "text": "The README claims that the system will improve evidence accuracy.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S01_project.md",
              "location": "line 4"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Identify improved evidence accuracy as a documented claim.",
        "Identify the unrun evaluation as the boundary.",
        "Explain that a baseline and completed measurement are needed before claiming an outcome."
      ],
      "grounded_draft": "In this project, the README says the system will improve evidence accuracy, but that is an intended outcome, not a measured result. The evaluation plan has not been run. I would therefore describe improved evidence accuracy as a hypothesis until a defined metric, baseline, execution record, and comparison show whether the system actually improved.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F2",
          "F3"
        ],
        "narrowed_from": "The system improved evidence accuracy."
      },
      "likely_followups": [
        "How would you operationalize evidence accuracy?",
        "What baseline would you choose?",
        "What result would count as meaningful improvement?"
      ]
    }
  ],
  "next_build": {
    "gap": "The 20-case evaluation plan has not been executed, leaving the central quality claim unverified.",
    "why_now": "Running the existing plan is the shortest path from planning evidence to observable results, failure analysis, and defensible interview material.",
    "steps": [
      "Document each case's input, expected behavior, scoring rule, and safety or reliability category.",
      "Define an evidence-accuracy metric, pass threshold, and baseline before execution.",
      "Run all 20 cases under a recorded system version and consistent conditions.",
      "Capture case-level outputs, scores, and failure notes.",
      "Summarize results and prioritize improvements by severity, frequency, and user impact."
    ],
    "acceptance_criteria": [
      "All 20 cases have reproducible inputs and expected outcomes.",
      "The metric, threshold, and baseline are documented before results are interpreted.",
      "Every case has a recorded output and score.",
      "Failures are categorized with traceable examples.",
      "The final summary separates measured findings from hypotheses and identifies prioritized next steps."
    ],
    "expected_evidence": "A versioned evaluation specification, completed 20-case results table, baseline comparison, failure taxonomy, and prioritized improvement list.",
    "output_dependency": "Would strengthen the evaluation role-fit item and could support new project highlights, resume bullets if individual ownership is confirmed, and evidence-rich answers to Q1-Q4.",
    "estimated_effort_band": "medium",
    "interview_question_unlocked": "What did your evaluation reveal, and how did you prioritize improvements from the observed failures?"
  },
  "warnings": [
    "No resume bullets are included because the only planning activity is attributed to the team and individual ownership is not confirmed.",
    "The evaluation plan has not been run; it supports planning but not execution, findings, or results.",
    "The README's statement about improved evidence accuracy is a claim, not a measured outcome.",
    "No company or public interview evidence exists for this synthetic JD; company, track, interview stages, and reported questions remain unknown.",
    "Priority interview questions are JD-derived possibilities, not official or reported interview questions.",
    "Exactly three answer drafts are provided as required, but each is deliberately narrow because project evidence is sparse."
  ]
}
```

## D5-002: team work does not prove personal ownership

### Project input

```text
# Team Project

We built a project analysis Agent. The document does not identify which member designed the workflow, wrote the evaluation, or implemented the tools.
```

### Target JD

```text
# Junior AI Product Manager

Responsibilities:

- identify valuable user workflows for generative AI
- define MVP scope and product requirements
- work with engineering and design
- design evaluation and quality measurement
- understand Agent tools, context, reliability, and safety
- analyze failures and prioritize improvements
- communicate product decisions and tradeoffs
```

### Output A

```json
{
  "role_fit_map": [
    {
      "role_requirement_id": "JD-R1",
      "capability_id": "generative_ai_workflow_discovery",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "Responsibilities, bullet 1"
        },
        {
          "source_id": "S02_project.md",
          "location": "Team Project, sentence 1"
        }
      ],
      "boundary": "The source establishes that the team built a project analysis Agent. It does not establish a user, user problem, discovery method, workflow-selection decision, or demonstrated workflow value.",
      "interview_risk": "High: the candidate cannot safely claim user discovery or workflow prioritization from the supplied evidence."
    },
    {
      "role_requirement_id": "JD-R2",
      "capability_id": "mvp_scope_and_product_requirements",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "Responsibilities, bullet 2"
        },
        {
          "source_id": "S02_project.md",
          "location": "Team Project, sentences 1–2"
        }
      ],
      "boundary": "The source does not describe an MVP boundary, product requirements, prioritization rationale, or the candidate's role in defining them.",
      "interview_risk": "High: no grounded scope or requirements story is available."
    },
    {
      "role_requirement_id": "JD-R3",
      "capability_id": "cross_functional_collaboration",
      "relevance": "important",
      "status": "needs_confirmation",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "Responsibilities, bullet 3"
        },
        {
          "source_id": "S02_project.md",
          "location": "Team Project, sentences 1–2"
        }
      ],
      "boundary": "The plural wording establishes a team project, but it does not identify engineering or design partners, collaboration practices, or the candidate's individual contribution.",
      "interview_risk": "High: team language must not be converted into individual ownership."
    },
    {
      "role_requirement_id": "JD-R4",
      "capability_id": "evaluation_and_quality_measurement",
      "relevance": "required",
      "status": "needs_confirmation",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "Responsibilities, bullet 4"
        },
        {
          "source_id": "S02_project.md",
          "location": "Team Project, sentence 2"
        }
      ],
      "boundary": "The source mentions an evaluation only to say that its author is unidentified. It does not describe the evaluation design, test set, metrics, execution, findings, or candidate ownership.",
      "interview_risk": "High: mentioning an evaluation does not support claiming that the candidate designed or ran it."
    },
    {
      "role_requirement_id": "JD-R5",
      "capability_id": "agent_tools_context_reliability_and_safety",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "S02_project.md",
          "location": "Team Project, sentence 1"
        },
        {
          "source_id": "target_jd.md",
          "location": "Responsibilities, bullet 5"
        }
      ],
      "boundary": "The source supports exposure to a team project that built an Agent. It does not establish which tools were implemented, how context was managed, whether reliability or safety was addressed, or what the candidate personally owned.",
      "interview_risk": "Medium-high: Agent-project exposure is supportable, but technical choices and product judgment are not."
    },
    {
      "role_requirement_id": "JD-R6",
      "capability_id": "failure_analysis_and_improvement_prioritization",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "Responsibilities, bullet 6"
        },
        {
          "source_id": "S02_project.md",
          "location": "Team Project, entire document"
        }
      ],
      "boundary": "No failures, diagnosis, prioritization method, improvement decision, or measured post-change result is documented.",
      "interview_risk": "High: there is no evidence-grounded failure-analysis example."
    },
    {
      "role_requirement_id": "JD-R7",
      "capability_id": "product_decision_and_tradeoff_communication",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "Responsibilities, bullet 7"
        },
        {
          "source_id": "S02_project.md",
          "location": "Team Project, entire document"
        }
      ],
      "boundary": "No product decision, alternative, tradeoff, stakeholder communication, or candidate ownership is documented.",
      "interview_risk": "High: no supported decision narrative is available."
    }
  ],
  "project_highlights": [
    {
      "text": "A team built a project analysis Agent.",
      "source_refs": [
        {
          "source_id": "S02_project.md",
          "location": "Team Project, sentence 1"
        }
      ],
      "boundary": "This establishes the team-level project output only. It does not establish the candidate's ownership, implementation details, users, quality, adoption, or results."
    }
  ],
  "resume_bullets": [],
  "intro_30_seconds": "I participated in a team project that built a project analysis Agent. The supplied record does not identify my individual ownership or document the workflow design, implementation, evaluation method, users, or results, so I would confirm those details before making stronger claims.",
  "answer_drafts": [
    {
      "question": "How did you identify the user workflow or problem addressed by the project analysis Agent?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "A team built a project analysis Agent.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S02_project.md",
              "location": "Team Project, sentence 1"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "State the verified team-level project output.",
        "Do not name users or a discovery process.",
        "Confirm the workflow-selection rationale before adding it."
      ],
      "grounded_draft": "I participated in a team project that built a project analysis Agent. The current project record does not document the target user, the workflow-selection process, or my individual role in that decision, so I cannot yet make a grounded claim about how the workflow was identified.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I identified and validated a valuable project-analysis workflow for users."
      },
      "likely_followups": [
        "Who was the intended user?",
        "What evidence showed the workflow was valuable?",
        "What part of workflow discovery did you personally own?"
      ]
    },
    {
      "question": "How did you evaluate output quality, and which measurements or test cases did you use?",
      "verified_evidence": [
        {
          "fact_id": "F2",
          "text": "The project document states that it does not identify which member wrote the evaluation.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S02_project.md",
              "location": "Team Project, sentence 2"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Acknowledge that an evaluation is referenced.",
        "Do not claim authorship, execution, metrics, or results.",
        "Obtain the evaluation artifact and confirm personal ownership before expanding the answer."
      ],
      "grounded_draft": "The project record references an evaluation, but it does not identify who wrote it or provide its method, test cases, metrics, execution, or results. I would need to verify my contribution and recover the evaluation artifact before presenting this as evidence of evaluation ownership.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F2"
        ],
        "narrowed_from": "I designed and executed the Agent evaluation framework."
      },
      "likely_followups": [
        "What dimensions did the evaluation measure?",
        "Did you personally design or run it?",
        "What failures did the evaluation reveal?"
      ]
    },
    {
      "question": "What Agent tools and context strategy did the product use, and how did you address reliability and safety?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "A team built a project analysis Agent.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S02_project.md",
              "location": "Team Project, sentence 1"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "State only that the team built an Agent.",
        "Do not infer tools, context architecture, reliability controls, or safety controls.",
        "Confirm implementation details and personal ownership before adding technical claims."
      ],
      "grounded_draft": "I participated in a team project that built a project analysis Agent. The supplied evidence does not identify its tools, context strategy, reliability controls, safety approach, or my individual implementation role, so those details require confirmation before I can discuss them as project facts.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I designed the Agent's tools, context architecture, and reliability safeguards."
      },
      "likely_followups": [
        "Which tools could the Agent invoke?",
        "How was context selected and bounded?",
        "What reliability or safety failure did you address?"
      ]
    }
  ],
  "next_build": {
    "gap": "No traceable evidence connects the candidate to an individually owned product decision or evaluation result.",
    "why_now": "This gap blocks safe resume bullets and strong answers for most of the JD's central capabilities.",
    "steps": [
      "Select one project-analysis workflow and document the target user, problem, and evidence for its value.",
      "Write a concise MVP scope and requirements artifact that records alternatives and one explicit tradeoff.",
      "Create a small evaluation set with defined quality, reliability, and safety criteria.",
      "Run the evaluation, categorize failures, prioritize one improvement, and rerun the same evaluation.",
      "Record the candidate's exact contribution separately from team contributions and link each claim to an artifact."
    ],
    "acceptance_criteria": [
      "The target user and workflow are explicitly documented with supporting discovery evidence.",
      "The MVP artifact identifies included and excluded scope plus one reasoned tradeoff.",
      "The evaluation includes reproducible test cases and predefined pass or scoring criteria.",
      "Baseline and post-change results are recorded without substituting targets or estimates for measurements.",
      "Individual ownership is confirmed for each proposed resume or interview claim."
    ],
    "expected_evidence": "A dated workflow brief, MVP requirements document, decision record, evaluation dataset and rubric, baseline and post-change results, failure analysis, and an explicit ownership statement.",
    "output_dependency": "Would enable stronger role-fit statuses, supported project highlights, evidence-grounded resume bullets, and substantive answers to Q1, Q2, Q4, Q5, Q6, and Q7.",
    "estimated_effort_band": "medium",
    "interview_question_unlocked": "How did you define, evaluate, and improve an Agent workflow, and what did you personally own?"
  },
  "warnings": [
    "The project evidence is extremely sparse and does not establish individual ownership.",
    "No resume bullets are returned because resume bullets require directly supported facts and confirmed ownership.",
    "Only one project highlight is returned because additional highlights would require unsupported claims.",
    "The evaluation is referenced but its author, design, execution, metrics, and results are not established.",
    "No company or track brief beyond the synthetic JD can be supported.",
    "The interview loop is unknown because no official or reported interview-process evidence exists.",
    "All priority interview questions are JD-derived possibilities, not official or reported questions.",
    "The answer drafts are intentionally narrow and identify where confirmation is required."
  ]
}
```

### Output B

```json
{
  "role_fit_map": [
    {
      "role_requirement_id": "JD-01",
      "capability_id": "D1",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "The source names a project analysis Agent but provides no user, workflow, pain, alternative, or user evidence.",
      "interview_risk": "Cannot answer why this was a valuable workflow without inventing discovery evidence."
    },
    {
      "role_requirement_id": "JD-02",
      "capability_id": "D2",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "No MVP scope, PRD, priority decision, rejected alternative, or acceptance criterion is supplied.",
      "interview_risk": "Cannot defend product judgment or scope tradeoffs."
    },
    {
      "role_requirement_id": "JD-03",
      "capability_id": "D9",
      "relevance": "important",
      "status": "needs_confirmation",
      "source_refs": [
        {
          "source_id": "S02",
          "location": "S02_project.md:1-3"
        }
      ],
      "boundary": "The artifact establishes a team project but does not identify collaboration events, delivery evidence, or the candidate's contribution.",
      "interview_risk": "Using first-person singular would overstate team evidence."
    },
    {
      "role_requirement_id": "JD-04",
      "capability_id": "D6",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "The source says an evaluation existed only by noting that its designer is unidentified; it supplies no rubric, cases, results, failures, or decisions.",
      "interview_risk": "The existence of an unspecified evaluation cannot support a quality or learning claim."
    },
    {
      "role_requirement_id": "JD-05",
      "capability_id": "D4",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "S02",
          "location": "S02_project.md:3"
        }
      ],
      "boundary": "Supported only that the team built something described as a project analysis Agent; workflow, state, actions, tools, context, permissions, stop conditions, reliability, and safety are not documented.",
      "interview_risk": "Calling it a bounded Agent system or claiming specific technical decisions would exceed the evidence."
    },
    {
      "role_requirement_id": "JD-06",
      "capability_id": "D10",
      "relevance": "required",
      "status": "needs_confirmation",
      "source_refs": [
        {
          "source_id": "S02",
          "location": "S02_project.md:3"
        }
      ],
      "boundary": "The document explicitly does not identify who designed the workflow, wrote the evaluation, or implemented the tools.",
      "interview_risk": "Personal ownership and decision rationale cannot be claimed until confirmed and source-linked."
    }
  ],
  "project_highlights": [
    {
      "text": "A team built a project analysis Agent.",
      "source_refs": [
        {
          "source_id": "S02",
          "location": "S02_project.md:1-3"
        }
      ],
      "boundary": "Team-level existence claim only; no personal ownership, implementation detail, evaluation result, user outcome, or delivery outcome is established."
    }
  ],
  "resume_bullets": [],
  "intro_30_seconds": "My team built a project analysis Agent. The supplied project record does not establish my individual role, the user workflow, system design, evaluation method, or results, so I would present it only as a team project until I can substantiate those details.",
  "answer_drafts": [
    {
      "question": "What valuable user workflow did the project analysis Agent address, and what evidence made it valuable?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "A team built a project analysis Agent.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S02",
              "location": "S02_project.md:1-3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "State only that this was a team-built project analysis Agent.",
        "Say that the target user, workflow, pain, and validation evidence are not present in the supplied record."
      ],
      "grounded_draft": "The verified fact is that my team built a project analysis Agent. The supplied record does not identify the target user or provide evidence that the workflow was valuable, so I cannot make a stronger user-value claim from this material.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I identified and validated a valuable project-analysis workflow."
      },
      "likely_followups": [
        "Who was the target user?",
        "What observation or research validated the pain?",
        "What alternative did users use before?"
      ]
    },
    {
      "question": "How did the Agent manage tools, context, stop conditions, reliability, and safety?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "A team built a project analysis Agent.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S02",
              "location": "S02_project.md:1-3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Identify the artifact only as a team-built Agent.",
        "Do not claim any tool, context, safety, or reliability mechanism without another source."
      ],
      "grounded_draft": "The source supports only that the team built something described as a project analysis Agent. It does not document its tools, context policy, stop conditions, reliability controls, or safety mechanisms, so those technical details remain unsupported.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I designed a permission-bounded Agent with tested reliability and safety controls."
      },
      "likely_followups": [
        "What actions could the Agent take?",
        "What caused it to stop or ask?",
        "How were untrusted inputs and tool failures handled?"
      ]
    },
    {
      "question": "Which project decisions were yours, which were shared, and how did engineering or design input change them?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "A team built a project analysis Agent.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S02",
              "location": "S02_project.md:1-3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Use team language.",
        "State that the supplied artifact does not attribute workflow design, evaluation authorship, or tool implementation."
      ],
      "grounded_draft": "This is documented only as a team project. The source explicitly does not identify who designed the workflow, wrote the evaluation, or implemented the tools, so I would not assign those decisions to myself without confirmation and supporting artifacts.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I owned the workflow, evaluation, and tools end to end."
      },
      "likely_followups": [
        "What exactly did you own?",
        "Which decision can you personally defend?",
        "What evidence separates your contribution from the team's?"
      ]
    }
  ],
  "next_build": {
    "gap": "The project has no inspectable, attributable evidence chain connecting a real user task to a bounded Agent workflow, evaluation results, failures, and a product decision.",
    "why_now": "One bounded end-to-end evaluation-and-decision evidence package would address the JD's highest-value evaluation, failure-analysis, Agent reliability, and tradeoff requirements while preserving ownership boundaries. A documentation-only ownership memo is the rejected runner-up because it would clarify attribution but would not demonstrate product or technical judgment.",
    "steps": [
      "Have a downstream working Agent inspect the existing project goals, architecture, workflows, known failures, tests, and safety boundaries before proposing implementation details.",
      "Choose one current, product-relevant project-analysis task and compare the existing Agent behavior with a simple non-Agent baseline on a small versioned case set; define human review, failure labels, stop or ask behavior, and safety boundaries from the inspected system.",
      "Return an exploration brief for product-owner approval and stop before implementation; only after explicit approval, implement and verify the approved evaluation direction.",
      "Report changed files, commands, exact results, reviewer judgments and disagreements, remaining limitations, produced artifacts, and attributable ownership; do not invent metrics, users, outcomes, ownership, or test results."
    ],
    "acceptance_criteria": [
      "A source-linked user task and limitation justify why the chosen evaluation is product-relevant.",
      "Versioned cases, baseline, rubric, failure taxonomy, and decision rules are inspectable.",
      "Executed results include bad cases and preserve genuine human judgments and disagreements where subjective quality matters.",
      "At least one result causes a documented keep, revise, or stop decision, with Agent stop or ask and safety boundaries tested where applicable.",
      "Artifacts distinguish personal, shared, and system contributions and state remaining unvalidated claims."
    ],
    "expected_evidence": "An approved evaluation brief; versioned cases and baseline; human-review rubric and records; executed results and bad cases; reliability or safety traces; a decision log linking results to one product change; and ownership attribution.",
    "output_dependency": "Only completed evidence may update D1, D3-D8, D10, JD match, project highlights, resume bullets, Q1/Q3/Q4/Q5/Q6 answers, and mock follow-up defenses; the current match does not improve from this proposal.",
    "estimated_effort_band": "medium",
    "interview_question_unlocked": "Which failure in your Agent evaluation changed the product, and how did you decide whether to revise, stop, or ship?"
  },
  "warnings": [
    "Preliminary verdict: not recommended as the lead project for this role on the supplied evidence; the only supported highlight is that a team built a project analysis Agent.",
    "No context was saved.",
    "No web research was run because the JD is synthetic and the user prohibited web search.",
    "No project code, tests, builds, or package commands were executed; only the canonical read-only inventory was run, and it found no repository evidence because the supplied project is a single document.",
    "Do not use first-person ownership, technical implementation, evaluation, user, metric, delivery, or impact claims until they are confirmed and source-linked."
  ]
}
```

## D5-003: implementation does not prove user value

### Project input

```text
# AI Agent

The repository contains an Agent loop, tool registry, and structured output tests.
No user research, user task, adoption, or outcome evidence is included.
```

### Target JD

```text
# Junior AI Product Manager

Responsibilities:

- identify valuable user workflows for generative AI
- define MVP scope and product requirements
- work with engineering and design
- design evaluation and quality measurement
- understand Agent tools, context, reliability, and safety
- analyze failures and prioritize improvements
- communicate product decisions and tradeoffs
```

### Output A

```json
{
  "role_fit_map": [
    {
      "role_requirement_id": "JD-R1",
      "capability_id": "D1",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "The supplied project file explicitly says no user research or user task evidence is included.",
      "interview_risk": "Cannot defend a valuable target workflow or evidence-based problem definition."
    },
    {
      "role_requirement_id": "JD-R2",
      "capability_id": "D2",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [],
      "boundary": "No MVP scope, PRD, prioritization decision, rejected alternative, or acceptance boundary is supplied.",
      "interview_risk": "Cannot substantiate product judgment or tradeoff decisions."
    },
    {
      "role_requirement_id": "JD-R3",
      "capability_id": "D4",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "SRC-PROJECT",
          "location": "S05_project.md:3"
        }
      ],
      "boundary": "The supplied summary establishes that an Agent loop exists, but provides no state model, stop-condition trace, or implementation detail.",
      "interview_risk": "Follow-ups may expose that Agent autonomy and control boundaries were not inspected."
    },
    {
      "role_requirement_id": "JD-R4",
      "capability_id": "D5",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "SRC-PROJECT",
          "location": "S05_project.md:3"
        }
      ],
      "boundary": "A tool registry is present, but context selection, permissions, provenance, and tool-failure behavior are not supplied.",
      "interview_risk": "Cannot safely claim reliable or permission-bounded tool use."
    },
    {
      "role_requirement_id": "JD-R5",
      "capability_id": "D6",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "SRC-PROJECT",
          "location": "S05_project.md:3"
        }
      ],
      "boundary": "Structured-output tests exist, but cases, rubric, executed results, bad cases, and resulting decisions are absent.",
      "interview_risk": "Cannot defend measured quality or failure-driven prioritization."
    },
    {
      "role_requirement_id": "JD-R6",
      "capability_id": "D7",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [],
      "boundary": "No named reliability or safety risk, enforced control, approval point, recovery path, or adversarial result is supplied.",
      "interview_risk": "The JD explicitly asks for reliability and safety understanding."
    },
    {
      "role_requirement_id": "JD-R7",
      "capability_id": "D9",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [],
      "boundary": "No engineering/design collaboration, release record, adoption, or outcome evidence is supplied.",
      "interview_risk": "Cannot substantiate cross-functional delivery or learning from users."
    }
  ],
  "project_highlights": [
    {
      "text": "The supplied project repository is described as containing an Agent loop, a tool registry, and structured-output tests.",
      "source_refs": [
        {
          "source_id": "SRC-PROJECT",
          "location": "S05_project.md:3"
        }
      ],
      "boundary": "Repository-content claim only; implementation quality, execution results, and personal ownership were not established."
    }
  ],
  "resume_bullets": [],
  "intro_30_seconds": "This project is an AI Agent repository with an Agent loop, tool registry, and structured-output tests. That makes it relevant to the role's technical Agent focus. The supplied evidence does not establish the target user, product scope, outcomes, or my personal ownership, so I would present it as a technical supporting project and be explicit about those limits.",
  "answer_drafts": [
    {
      "question": "Walk me through the Agent project and the user workflow it was intended to serve.",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The repository contains an Agent loop, tool registry, and structured-output tests.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "SRC-PROJECT",
              "location": "S05_project.md:3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Lead with the verified technical components.",
        "State that the supplied materials do not establish a target user or workflow.",
        "Do not claim personal ownership."
      ],
      "grounded_draft": "The verified scope I can describe is an AI Agent repository containing an Agent loop, tool registry, and structured-output tests. The supplied project evidence does not identify a target user or user task, so I would not claim that the workflow was validated. That missing product evidence is the first gap I would address before positioning this as a lead AI PM project.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I identified and validated a valuable user workflow for the Agent."
      },
      "likely_followups": [
        "Who was the intended user?",
        "What problem was the Agent solving?",
        "Which part did you personally own?"
      ]
    },
    {
      "question": "How does the Agent loop decide which tool to use, what context to carry, and when to stop?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The repository contains an Agent loop, tool registry, and structured-output tests.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "SRC-PROJECT",
              "location": "S05_project.md:3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Confirm only that the components exist.",
        "Say implementation details were not supplied.",
        "Name the evidence needed for a defensible deep dive."
      ],
      "grounded_draft": "The supplied evidence establishes that the repository has an Agent loop and tool registry, but it does not expose the loop's state, tool-selection policy, context limits, permissions, or stop conditions. I would inspect those implementation contracts and their tests before making a stronger reliability claim. Today, the defensible statement is component presence, not verified control behavior.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I designed a reliable, permission-bounded Agent loop with explicit stopping."
      },
      "likely_followups": [
        "What are the available actions and observations?",
        "What happens on tool failure?",
        "Where is human approval required?"
      ]
    },
    {
      "question": "What did the structured-output tests evaluate, and which failure changed your priorities?",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The repository contains an Agent loop, tool registry, and structured-output tests.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "SRC-PROJECT",
              "location": "S05_project.md:3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "State that structured-output tests exist.",
        "Do not invent test execution, failure results, or a decision.",
        "Describe the missing evidence needed to answer fully."
      ],
      "grounded_draft": "The project summary confirms that structured-output tests exist, but it does not provide their cases, rubric, execution results, or failures. I therefore cannot truthfully name a failure that changed priorities. To answer fully, I would need the versioned cases, exact results, bad-case analysis, and the recorded product or engineering decision that followed.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "Structured-output failures drove a measurable reliability improvement."
      },
      "likely_followups": [
        "Were the tests executed?",
        "How was quality scored?",
        "What regression threshold blocked release?"
      ]
    }
  ],
  "next_build": {
    "gap": "The project has no supplied user-workflow, user-research, adoption, or outcome evidence, so its technical components are disconnected from a validated product problem.",
    "why_now": "A bounded user-workflow validation and task-based evaluation would address the JD's highest-value gaps in problem definition, evaluation, failure prioritization, and tradeoff communication while producing inspectable evidence.",
    "steps": [
      "Inspect the existing Agent's goals, loop, tools, tests, known failures, and safety boundaries; identify one plausible current user task without editing the project.",
      "Compare candidate user tasks and select one smallest product-relevant workflow; explicitly reject the runner-up and record the rationale.",
      "Prepare a lightweight research and evaluation plan for that workflow, including a non-Agent baseline, representative tasks, success rubric, failure taxonomy, safety guardrails, and human-review procedure.",
      "Stop for product-owner approval before implementation or participant work; after approval, run the study and preserve raw observations, disagreements, results, and the keep/revise/stop decision."
    ],
    "acceptance_criteria": [
      "A dated artifact defines the user, task, current alternative, pain, and success condition.",
      "A decision record links observed evidence to the selected workflow and rejected alternative.",
      "Versioned evaluation cases compare the Agent with a non-Agent baseline under a defined rubric and safety boundary.",
      "Real results include bad cases and human-review disagreements without invented users, metrics, outcomes, or ownership.",
      "A final decision states keep, revise, or stop and links directly to the evidence."
    ],
    "expected_evidence": "User/task research notes, workflow decision record, approved protocol, versioned cases and rubric, baseline comparison, raw results, failure taxonomy, reviewer disagreements, safety observations, and a resulting product decision.",
    "output_dependency": "Only after completed evidence exists should D1, D2, D6, D7, project highlights, resume bullets, and answer drafts be reassessed; the current match does not change for proposed work.",
    "estimated_effort_band": "medium",
    "interview_question_unlocked": "What user evidence and evaluation failures changed your Agent product scope or release decision?"
  },
  "warnings": [
    "This pack uses only S05_project.md, target_jd.md, and installed canonical Project2Job references; no web research, saved context, project execution, tests, builds, or code inspection was performed.",
    "The project file is a four-line summary, so technical depth is only partially supported and all personal ownership remains unconfirmed.",
    "No resume bullet is emitted because the supplied evidence does not establish candidate ownership.",
    "The interview loop and questions are JD-derived hypotheses, not reported company practice."
  ]
}
```

### Output B

```json
{
  "role_fit_map": [
    {
      "role_requirement_id": "JD-R1",
      "capability_id": "user-workflow-discovery",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "lines 3-5"
        },
        {
          "source_id": "S05_project.md",
          "location": "line 4"
        }
      ],
      "boundary": "The JD requires identification of valuable generative-AI workflows. The project source explicitly contains no user research or user-task evidence, so it does not establish workflow discovery. Missing evidence does not establish missing ability.",
      "interview_risk": "No grounded example is available for user discovery, problem selection, or workflow prioritization."
    },
    {
      "role_requirement_id": "JD-R2",
      "capability_id": "mvp-scope-and-requirements",
      "relevance": "required",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 6"
        },
        {
          "source_id": "S05_project.md",
          "location": "lines 1-4"
        }
      ],
      "boundary": "The source identifies repository components but contains no MVP scope, requirements, prioritization record, or product decision.",
      "interview_risk": "The candidate cannot safely claim requirements ownership or MVP scoping from the supplied evidence."
    },
    {
      "role_requirement_id": "JD-R3",
      "capability_id": "cross-functional-collaboration",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 7"
        },
        {
          "source_id": "S05_project.md",
          "location": "lines 1-4"
        }
      ],
      "boundary": "No engineering or design collaboration, team composition, or individual contribution is documented.",
      "interview_risk": "Cross-functional behavior and individual ownership remain unverified."
    },
    {
      "role_requirement_id": "JD-R4",
      "capability_id": "evaluation-and-quality-measurement",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 8"
        },
        {
          "source_id": "S05_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "Structured output tests support the existence of a quality-checking mechanism. They do not establish who designed it, what quality dimensions it measures, whether tests passed, or whether quality improved.",
      "interview_risk": "A reviewer may ask for the evaluation rubric, test cases, baseline, results, and candidate ownership; none are supplied."
    },
    {
      "role_requirement_id": "JD-R5",
      "capability_id": "agent-systems-understanding",
      "relevance": "required",
      "status": "partially_supported",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 9"
        },
        {
          "source_id": "S05_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "The repository contains an agent loop and tool registry, directly matching agent and tool concepts. It does not establish the candidate's ownership, understanding of context management, reliability behavior, or safety decisions.",
      "interview_risk": "Tool use and component presence do not prove product judgment or individual technical understanding."
    },
    {
      "role_requirement_id": "JD-R6",
      "capability_id": "failure-analysis-and-prioritization",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 10"
        },
        {
          "source_id": "S05_project.md",
          "location": "lines 3-4"
        }
      ],
      "boundary": "Tests are mentioned, but no failures, taxonomy, analysis, prioritization, remediation, or before-and-after result is documented.",
      "interview_risk": "The project cannot support a story about diagnosing failures or prioritizing improvements."
    },
    {
      "role_requirement_id": "JD-R7",
      "capability_id": "product-decisions-and-tradeoffs",
      "relevance": "important",
      "status": "not_found",
      "source_refs": [
        {
          "source_id": "target_jd.md",
          "location": "line 11"
        },
        {
          "source_id": "S05_project.md",
          "location": "lines 1-4"
        }
      ],
      "boundary": "No decision record, alternatives, tradeoff analysis, stakeholder communication, or candidate ownership is supplied.",
      "interview_risk": "There is no evidence-grounded product-decision narrative."
    }
  ],
  "project_highlights": [
    {
      "text": "The repository contains an agent loop.",
      "source_refs": [
        {
          "source_id": "S05_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "This establishes component presence only; it does not establish implementation ownership, reliability, usage, or outcomes."
    },
    {
      "text": "The repository contains a tool registry.",
      "source_refs": [
        {
          "source_id": "S05_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "This establishes component presence only; tool use does not prove product judgment, safety, or candidate ownership."
    },
    {
      "text": "The repository contains structured output tests.",
      "source_refs": [
        {
          "source_id": "S05_project.md",
          "location": "line 3"
        }
      ],
      "boundary": "This establishes test presence, not test design ownership, coverage, passing results, measured quality, or improvement."
    }
  ],
  "resume_bullets": [],
  "intro_30_seconds": "This project is an AI-agent repository containing an agent loop, a tool registry, and structured output tests. Those artifacts make it relevant to agent architecture and evaluation discussions. The supplied evidence does not identify the user problem, document product decisions, confirm my ownership, or show adoption and outcomes, so I would present it as a technical artifact and clearly separate those open questions from verified facts.",
  "answer_drafts": [
    {
      "question": "Walk me through the agent loop, tool registry, and structured output tests in this project.",
      "verified_evidence": [
        {
          "fact_id": "F1",
          "text": "The repository contains an agent loop, tool registry, and structured output tests.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S05_project.md",
              "location": "line 3"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Name the three verified repository components.",
        "Connect them cautiously to agent execution, tool availability, and output checking.",
        "State that implementation details, ownership, and test results are not supplied."
      ],
      "grounded_draft": "The verified artifact is a repository with three named components: an agent loop, a tool registry, and structured output tests. At a high level, those correspond to repeated agent execution, available tool definitions, and checks on output structure. The source does not contain enough detail for me to claim how the loop operates, which tools exist, whether tests pass, or what I personally implemented, so I would verify those points before giving a deeper technical or ownership account.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F1"
        ],
        "narrowed_from": "I built an agent platform with reliable tool execution and validated outputs."
      },
      "likely_followups": [
        "What were the loop's stop conditions?",
        "How were tools selected and authorized?",
        "What did the structured output tests validate?",
        "Which parts did you personally own?"
      ]
    },
    {
      "question": "What does the available evidence prove about the project's evaluation approach, and what remains unknown?",
      "verified_evidence": [
        {
          "fact_id": "F2",
          "text": "Structured output tests are present in the repository.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S05_project.md",
              "location": "line 3"
            }
          ]
        },
        {
          "fact_id": "F3",
          "text": "No adoption or outcome evidence is included.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S05_project.md",
              "location": "line 4"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Separate test presence from measured quality.",
        "Identify absent rubric, coverage, baseline, pass results, and outcome evidence.",
        "Avoid attributing test design or results to the candidate."
      ],
      "grounded_draft": "The evidence proves only that structured output tests exist. That is relevant to evaluation because it shows an output-checking artifact, but it does not establish the evaluation dimensions, test coverage, pass rate, baseline, or any improvement in reliability. The source also explicitly says that outcome evidence is absent. I would therefore describe evaluation infrastructure as present while treating its design, performance, and my ownership as unconfirmed.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F2",
          "F3"
        ],
        "narrowed_from": "I designed an evaluation framework that improved agent reliability."
      },
      "likely_followups": [
        "Which quality dimensions should be measured?",
        "How would you build a representative evaluation set?",
        "What thresholds would determine launch readiness?",
        "How would you measure improvement?"
      ]
    },
    {
      "question": "Which product evidence is missing from this project, and how would you gather it?",
      "verified_evidence": [
        {
          "fact_id": "F4",
          "text": "No user research, user-task, adoption, or outcome evidence is included.",
          "status": "supported",
          "source_refs": [
            {
              "source_id": "S05_project.md",
              "location": "line 4"
            }
          ]
        }
      ],
      "answer_ingredients": [
        "Name each explicitly absent evidence category.",
        "Explain that absence limits claims about value and outcomes.",
        "Present user research and task validation as a recommendation, not completed work."
      ],
      "grounded_draft": "The source explicitly lacks user research, a documented user task, adoption evidence, and outcome evidence. As a result, I cannot claim that the project solves a validated workflow or produces user value. My next step would be to select one candidate workflow, interview representative users, observe the current task, define success and failure criteria, and test a narrow prototype. That is a recommended validation plan, not work already demonstrated by this project.",
      "claim_safety_review": {
        "exceeds_evidence": false,
        "checked_fact_ids": [
          "F4"
        ],
        "narrowed_from": "I identified and validated a valuable user workflow for the agent."
      },
      "likely_followups": [
        "Which workflow would you investigate first?",
        "How would you recruit representative users?",
        "What evidence would justify building an MVP?",
        "Which outcome metric would you choose?"
      ]
    }
  ],
  "next_build": {
    "gap": "No validated user task or user-research evidence connects the agent repository to a valuable workflow.",
    "why_now": "This is the highest-priority gap because workflow identification anchors MVP scope, evaluation criteria, prioritization, and credible outcome measurement for the target role.",
    "steps": [
      "Choose one narrowly defined workflow that could plausibly use the existing agent loop and tools.",
      "Recruit representative users and document their current process, pain points, frequency, and failure cost.",
      "Define the smallest testable agent-assisted task and explicit non-goals.",
      "Create task-level success, reliability, and safety criteria.",
      "Run observed prototype sessions and retain anonymized notes, failure cases, and measurements.",
      "Record the resulting scope decision and tradeoffs."
    ],
    "acceptance_criteria": [
      "A clearly identified user segment and recurring task are documented.",
      "At least three observed sessions or interviews are recorded with consent and anonymized notes.",
      "A prioritized problem statement and narrow MVP scope are documented.",
      "A task-based evaluation set contains representative successes, failures, and safety cases.",
      "Results include measured task performance and a decision to proceed, revise, or stop.",
      "The candidate's individual contributions are explicitly confirmed."
    ],
    "expected_evidence": "Research notes, task map, problem statement, MVP requirements, evaluation cases, measured results, decision log, and an ownership statement.",
    "output_dependency": "Could strengthen user-workflow discovery, MVP scoping, evaluation, failure prioritization, the project introduction, resume bullets, and answer drafts.",
    "estimated_effort_band": "medium",
    "interview_question_unlocked": "Tell me about a user workflow you validated and how the evidence changed your MVP scope and evaluation plan."
  },
  "warnings": [
    "No resume bullets were produced because the supplied source does not confirm individual ownership.",
    "The project supports component-presence claims only; it does not establish implementation, product judgment, execution quality, or results.",
    "Structured output tests are not evidence of a complete evaluation strategy or measured improvement.",
    "No user, adoption, outcome, collaboration, decision, or experiment claims are supported.",
    "Company, track, and interview process remain unknown because the synthetic JD has no public company or interview evidence.",
    "All priority interview questions are inferred from the JD and are possible preparation topics, not expected or previously reported questions."
  ]
}
```
