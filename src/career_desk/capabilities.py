from __future__ import annotations

import asyncio
import re
from copy import deepcopy
from pathlib import Path

from .contracts import EvidenceStatus, InvestigationRequest, RunBudget
from .runtime import EvidenceInvestigator


EVIDENCE_FILE = re.compile(r"^p2j-evidence--([a-zA-Z0-9_.-]+)\.md$")
CORRECTABLE_CLAIM_FIELDS = {"statement", "status", "attribution_scope"}
ATTRIBUTION_SCOPES = {
    "directly_owned",
    "ai_assisted",
    "collaborator_owned",
    "unresolved",
}


class LocalEvidenceTools:
    """Read-only tools for one explicitly permitted changed evidence surface."""

    def __init__(self, project_root: Path, source_paths: list[str]) -> None:
        self.project_root = project_root.resolve()
        self.sources = {
            path: (self.project_root / path).resolve() for path in source_paths
        }
        self.content: dict[str, str] = {}
        self.events: list[dict] = []

    def inventory_sources(self, project_root: str) -> dict:
        return {"source_ids": sorted(self.sources)}

    def search_sources(
        self, query: str, source_ids: list[str], limit: int
    ) -> dict:
        self.events.append({"kind": "tool_call", "tool": "search_sources"})
        matches = []
        for source_id in source_ids:
            text = self._read(source_id)
            fields = self._fields(text)
            if (
                fields.get("claim", "").casefold() == query.casefold()
                or query.casefold() in text.casefold()
                or (
                    fields.get("claim id")
                    and EVIDENCE_FILE.match(Path(source_id).name)
                )
            ):
                matches.append({"source_id": source_id, "location": "evidence record"})
            if len(matches) >= limit:
                break
        return {"matches": matches, "exhausted": True}

    def read_source(
        self, source_id: str, location: str, max_chars: int
    ) -> dict:
        self.events.append({"kind": "tool_call", "tool": "read_source"})
        fields = self._fields(self._read(source_id)[:max_chars])
        assessment = fields.get("assessment", "irrelevant").casefold()
        if assessment not in {"direct", "partial", "contradictory", "irrelevant"}:
            assessment = "irrelevant"
        result = {
            "source_id": source_id,
            "location": location,
            "assessment": assessment,
        }
        if assessment == "partial" and fields.get("narrowed claim"):
            result["narrowed_claim"] = fields["narrowed claim"]
        return result

    def compare_evidence(self, claim: str, evidence: list[dict]) -> dict:
        return {"claim": claim, "evidence_count": len(evidence)}

    def request_confirmation(self, question: str, context: dict) -> dict:
        self.events.append({"kind": "question_asked"})
        return {"pending": True}

    def submit_evidence_result(self, result: dict) -> dict:
        return {"accepted": True}

    def fields_for(self, source_id: str) -> dict[str, str]:
        return self._fields(self._read(source_id))

    def _read(self, source_id: str) -> str:
        path = self.sources.get(source_id)
        if path is None or self.project_root not in path.parents:
            raise RuntimeError("source is outside the permitted project surface")
        if source_id in self.content:
            return self.content[source_id]
        self.events.append(
            {"kind": "file_opened", "path": source_id, "chars": path.stat().st_size}
        )
        self.content[source_id] = path.read_text(encoding="utf-8", errors="replace")
        return self.content[source_id]

    @staticmethod
    def _fields(text: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for line in text.splitlines()[:20]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            normalized = key.lstrip("# ").strip().casefold()
            if normalized in {
                "claim id",
                "claim",
                "assessment",
                "artifact type",
                "narrowed claim",
                "evidence summary",
                "source location",
            }:
                fields.setdefault(normalized, value.strip())
        return fields


class Project2JobCapabilities:
    """Stable capability adapters used by the stateful vertical slice."""

    def __init__(self, project_root: Path, seed: dict | None = None) -> None:
        self.project_root = project_root
        self.seed = deepcopy(seed or {})

    def execute(self, action: str, context: dict) -> dict:
        if action == "refresh_jd_context":
            return self._refresh_jd(context)
        if action == "produce_brief":
            return self._produce_brief(context)
        if action == "investigate_evidence":
            return self._investigate(context)
        if action == "request_confirmation":
            return {
                "capability": "host_confirmation",
                "observation_summary": "One factual confirmation is required.",
                "events": [{"kind": "question_asked"}],
                "stop": True,
                "stop_reason": "complete",
            }
        return {
            "capability": f"host_provided:{action}",
            "observation_summary": "The selected specialist remains host-provided.",
            "events": [],
            "stop": True,
        }

    def _refresh_jd(self, context: dict) -> dict:
        state = context["state"]
        seeded = self.seed.get("state", {})
        research = deepcopy(self.seed.get("research", {}))
        outputs = {
            key: deepcopy(value)
            for key, value in seeded.get("outputs", {}).items()
            if value.get("kind") in {"company_intelligence", "question"}
        }
        dependencies = {
            "jd": list(
                dict.fromkeys(
                    [
                        *state.get("dependencies", {}).get("jd", []),
                        *outputs,
                    ]
                )
            )
        }
        return {
            "capability": "p2j-intel:host_research",
            "outputs": outputs,
            "dependencies": dependencies,
            "affected_outputs": sorted(outputs),
            "observation_summary": (
                "Bounded company and interview intelligence was supplied by the "
                "host research capability and kept separate from Project evidence."
            ),
            "events": [
                {"kind": "capability_event", "name": "p2j-intel"},
                {
                    "kind": "host_research_summary",
                    "search_queries": research.get("search_queries", 0),
                    "pages_opened": research.get("pages_opened", 0),
                    "browser_pages": research.get("browser_pages", 0),
                    "stop_reason": research.get("stop_reason", "host_provided"),
                    "remaining_gaps": research.get("remaining_gaps", []),
                },
            ],
            "stop": context["change"]["kind"] != "new",
        }

    def _produce_brief(self, context: dict) -> dict:
        seeded = self.seed.get("state", {})
        current_outputs = context["state"].get("outputs", {})
        events = [{"kind": "capability_event", "name": "p2j-brief"}]
        opened: set[str] = set()
        for item in seeded.get("evidence", {}).values():
            source = item.get("source")
            if not source or source in opened:
                continue
            path = (self.project_root / source).resolve()
            if self.project_root.resolve() not in path.parents or not path.is_file():
                raise RuntimeError(f"seeded evidence source is unavailable: {source}")
            path.read_bytes()[:4000]
            events.append({"kind": "file_opened", "path": source})
            opened.add(source)
        outputs = {
            key: deepcopy(value)
            for key, value in seeded.get("outputs", {}).items()
            if key not in current_outputs
        }
        return {
            "capability": "p2j-brief:host_analysis",
            "evidence": deepcopy(seeded.get("evidence", {})),
            "claims": deepcopy(seeded.get("claims", {})),
            "outputs": outputs,
            "dependencies": deepcopy(seeded.get("dependencies", {})),
            "confirmed_facts": deepcopy(seeded.get("confirmed_facts", {})),
            "affected_outputs": sorted(outputs),
            "observation_summary": (
                "The host supplied a bounded, source-linked Project2Job Brief; "
                "the deterministic runtime validated and recorded it."
            ),
            "events": events,
            "stop": True,
        }

    def _investigate(self, context: dict) -> dict:
        state = deepcopy(context["state"])
        change = context["change"]
        correction = context["request"].get("correction")
        changed_paths = [
            *change.get("added", []),
            *change.get("changed", []),
        ]
        removed_paths = change.get("removed", [])
        removed_evidence = {
            evidence_id
            for evidence_id, item in state.get("evidence", {}).items()
            if item.get("source") in removed_paths
        }
        affected_claims = self._claims_for_paths(
            state, changed_paths + removed_paths + sorted(removed_evidence)
        )

        for path in changed_paths:
            match = EVIDENCE_FILE.match(Path(path).name)
            if match and match.group(1) in state.get("claims", {}):
                affected_claims.add(match.group(1))

        evidence: dict[str, dict] = {}
        claims: dict[str, dict] = {}
        outputs: dict[str, dict] = {}
        dependencies: dict[str, list[str]] = {}
        events: list[dict] = []

        if correction:
            corrected_claim, corrected_outputs, correction_event = (
                self._apply_correction(state, correction)
            )
            claim_id = correction["claim_id"]
            claims[claim_id] = corrected_claim
            outputs.update(corrected_outputs)
            state["claims"][claim_id] = corrected_claim
            state["outputs"].update(corrected_outputs)
            events.append(correction_event)
            affected_claims.discard(claim_id)

        for claim_id in sorted(affected_claims):
            prior_claim = deepcopy(state["claims"][claim_id])
            candidate_paths = [
                path
                for path in changed_paths
                if EVIDENCE_FILE.match(Path(path).name)
                and EVIDENCE_FILE.match(Path(path).name).group(1) == claim_id
            ]
            if not candidate_paths:
                candidate_paths = [
                    path
                    for path in changed_paths
                    if claim_id in self._descendants(state, path)
                ]

            if candidate_paths:
                tools = LocalEvidenceTools(self.project_root, candidate_paths)
                run = asyncio.run(
                    EvidenceInvestigator(
                        tools,
                        RunBudget(
                            max_turns=3,
                            max_tool_calls=3,
                            max_source_chars_per_call=4000,
                        ),
                    ).investigate(
                        InvestigationRequest(
                            claim_id=claim_id,
                            text=prior_claim.get("statement", claim_id),
                            allowed_source_ids=candidate_paths,
                        )
                    )
                )
                status = run.state.status.value
                source_path = candidate_paths[0]
                fields = tools.fields_for(source_path)
                evidence_id = f"evidence:{claim_id}:{source_path}"
                evidence[evidence_id] = {
                    "source": source_path,
                    "location": fields.get("source location", "evidence record"),
                    "summary": fields.get(
                        "evidence summary", "The changed artifact was inspected."
                    ),
                    "artifact_type": fields.get(
                        "artifact type", "unclassified_changed_evidence"
                    ),
                }
                dependencies[source_path] = [evidence_id]
                dependencies[evidence_id] = [claim_id]
                events.extend(tools.events)
            else:
                remaining_evidence = any(
                    evidence_id not in removed_evidence
                    and claim_id in self._descendants(state, evidence_id)
                    for evidence_id in state.get("evidence", {})
                )
                status = "partially_supported" if remaining_evidence else "not_found"
                source_path = next(
                    (
                        state["evidence"][evidence_id]["source"]
                        for evidence_id in removed_evidence
                        if claim_id in self._descendants(state, evidence_id)
                    ),
                    removed_paths[0] if removed_paths else "",
                )

            updated_claim = deepcopy(prior_claim)
            updated_claim["status"] = status
            claims[claim_id] = updated_claim
            for output_id in sorted(self._descendants(state, claim_id)):
                if output_id not in state.get("outputs", {}):
                    continue
                before = state["outputs"][output_id]
                after = self._recompute(
                    before,
                    updated_claim,
                    source_path,
                    evidence.get(
                        f"evidence:{claim_id}:{source_path}", {}
                    ).get("artifact_type", "unclassified_changed_evidence"),
                )
                if after != before:
                    outputs[output_id] = after

            events.append(
                {
                    "kind": "dependent_outputs_evaluated",
                    "claim_id": claim_id,
                    "evaluated_outputs": sorted(
                        output_id
                        for output_id in self._descendants(state, claim_id)
                        if output_id in state.get("outputs", {})
                    ),
                    "changed_outputs": sorted(outputs),
                }
            )

        artifact_types = {
            item.get("artifact_type") for item in evidence.values()
        }
        if artifact_types == {"controlled_summary_existing_fact"}:
            summary = (
                "The Evidence Investigator inspected a controlled summary of "
                "existing Project evidence. It added no new capability and only "
                "updated affected presentation outputs."
            )
        elif "simulated_proposed_artifact" in artifact_types:
            summary = (
                "The Evidence Investigator inspected a simulated proposed "
                "artifact. It updated planning-related outputs only and did not "
                "establish executed target-platform experience."
            )
        else:
            summary = (
                "The Evidence Investigator inspected only the changed evidence "
                "surface and updated only the results affected by that source."
            )
        return {
            "capability": "p2j-audit:evidence_investigator",
            "evidence": evidence,
            "claims": claims,
            "outputs": outputs,
            "dependencies": dependencies,
            "removed_evidence": sorted(removed_evidence),
            "removed_dependency_nodes": sorted(
                set(removed_paths) | removed_evidence
            ),
            "affected_outputs": sorted(outputs),
            "observation_summary": summary,
            "events": events,
            "stop": not change.get("jd_changed", False),
        }

    def _apply_correction(
        self, state: dict, correction: dict
    ) -> tuple[dict, dict[str, dict], dict]:
        if not correction.get("approved"):
            raise ValueError("correction must be approved before application")
        claim_id = correction.get("claim_id")
        if claim_id not in state.get("claims", {}):
            raise ValueError("correction names an unknown claim")
        fields = correction.get("fields")
        if fields is None:
            fields = {
                key: value
                for key, value in correction.items()
                if key in CORRECTABLE_CLAIM_FIELDS
            }
        if not isinstance(fields, dict) or not fields:
            raise ValueError("correction must name at least one claim field")
        unknown = set(fields) - CORRECTABLE_CLAIM_FIELDS
        if unknown:
            raise ValueError(
                "correction cannot update claim fields: "
                + ", ".join(sorted(unknown))
            )
        if (
            "status" in fields
            and fields["status"] not in {status.value for status in EvidenceStatus}
        ):
            raise ValueError("correction has an invalid evidence status")
        if (
            "attribution_scope" in fields
            and fields["attribution_scope"] not in ATTRIBUTION_SCOPES
        ):
            raise ValueError("correction has an invalid attribution scope")

        prior = state["claims"][claim_id]
        updated = deepcopy(prior)
        changes = []
        for field, value in fields.items():
            before = prior.get(field)
            if before == value:
                continue
            updated[field] = value
            changes.append(
                {
                    "field": field,
                    "before": before,
                    "after": value,
                    "why": "The user approved this claim correction.",
                }
            )
        if not changes:
            return updated, {}, {
                "kind": "approved_correction",
                "claim_id": claim_id,
                "changes": [],
            }

        outputs = {}
        for output_id in sorted(self._descendants(state, claim_id)):
            if output_id not in state.get("outputs", {}):
                continue
            before = state["outputs"][output_id]
            after = self._recompute(
                before,
                updated,
                "",
                "approved_correction",
            )
            if after != before:
                outputs[output_id] = after
        return updated, outputs, {
            "kind": "approved_correction",
            "claim_id": claim_id,
            "changes": changes,
        }

    @staticmethod
    def _claims_for_paths(state: dict, paths: list[str]) -> set[str]:
        claims = set(state.get("claims", {}))
        found: set[str] = set()
        for path in paths:
            found.update(
                item
                for item in Project2JobCapabilities._descendants(state, path)
                if item in claims
            )
        return found

    @staticmethod
    def _descendants(state: dict, root: str) -> set[str]:
        edges = state.get("dependencies", {})
        found: set[str] = set()
        frontier = [root]
        while frontier:
            current = frontier.pop()
            for child in edges.get(current, []):
                if child not in found:
                    found.add(child)
                    frontier.append(child)
        return found

    @staticmethod
    def _recompute(
        output: dict,
        claim: dict,
        source_path: str,
        artifact_type: str,
    ) -> dict:
        updated = deepcopy(output)
        status = claim["status"]
        if output.get("kind") == "score":
            value = (
                claim.get("score_if_supported", output.get("value", 1))
                if status == "supported"
                else 1
            )
            if value == output.get("value"):
                return output
            updated["before"] = output.get("value")
            updated["value"] = value
        elif output.get("kind") == "jd_match":
            if artifact_type == "simulated_proposed_artifact":
                return output
            if status == "supported":
                direct = bool(claim.get("direct_competency"))
                match = (
                    claim.get("match_if_supported", "TRANSFERABLE")
                    if direct
                    else "TRANSFERABLE"
                )
            else:
                match = "GAP"
            if match == output.get("match"):
                return output
            updated["before"] = output.get("match")
            updated["match"] = match
            if claim.get("match_evidence_if_supported"):
                updated["evidence"] = claim["match_evidence_if_supported"]
            if claim.get("match_missing_if_supported"):
                updated["missing"] = claim["match_missing_if_supported"]
        elif output.get("kind") == "story":
            summary = claim.get("story_if_supported")
            if status != "supported":
                summary = "Current Project evidence does not support this story."
            if not summary or summary == output.get("summary"):
                return output
            updated["before"] = output.get("summary")
            updated["summary"] = summary
        elif output.get("kind") == "question":
            summary = claim.get("question_if_supported")
            if status != "supported":
                summary = "Current Project evidence does not support this question."
            if not summary or summary == output.get("summary"):
                return output
            updated["before"] = output.get("summary")
            updated["summary"] = summary
        elif output.get("kind") == "route":
            route = claim.get("route_if_supported")
            if status != "supported" or not route or route == output.get("route"):
                return output
            updated["before"] = output.get("route")
            updated["route"] = route
            if claim.get("route_summary_if_supported"):
                updated["summary"] = claim["route_summary_if_supported"]
        else:
            return output
        if artifact_type == "approved_correction":
            updated["why"] = (
                "An approved correction changed the supporting claim; no Project "
                "source evidence was added."
            )
        elif artifact_type == "controlled_summary_existing_fact":
            updated["why"] = (
                "This controlled summary made an existing source link easier to "
                "inspect; it did not add a new Project capability."
            )
        elif artifact_type == "simulated_proposed_artifact":
            updated["why"] = (
                "This simulated proposal added planning evidence only; it does "
                "not establish execution or target-platform experience."
            )
        else:
            updated["why"] = (
                f"The changed evidence at {source_path} resolved this supporting claim."
                if status == "supported"
                else f"The prior supporting evidence at {source_path} is unavailable."
            )
        return updated


def execution_handoff(project: str, build: dict) -> dict:
    """Return the bounded p2j-upgrade contract without modifying the Project."""
    required = {
        "capability_category",
        "current_match",
        "evidence_artifacts_needed",
        "gap",
        "jd_mismatch",
        "product_and_safety_boundaries",
        "recommended_evidence_direction",
        "requires_human_review",
        "why_it_matters",
        "outputs_expected_to_change",
        "interview_questions_unlocked",
    }
    missing = required - set(build)
    if missing:
        raise ValueError(f"upgrade handoff is missing: {', '.join(sorted(missing))}")
    match_states = {"EXACT MATCH", "TRANSFERABLE", "GAP"}
    if build["current_match"] not in match_states:
        raise ValueError(
            "current_match must be EXACT MATCH, TRANSFERABLE, or GAP"
        )
    direction = build["recommended_evidence_direction"]
    if not isinstance(direction, str) or not direction.strip():
        raise ValueError(
            "recommended_evidence_direction must contain exactly one direction"
        )
    list_fields = (
        "evidence_artifacts_needed",
        "product_and_safety_boundaries",
        "outputs_expected_to_change",
        "interview_questions_unlocked",
    )
    for field in list_fields:
        if not isinstance(build[field], list) or not build[field]:
            raise ValueError(f"{field} must be a non-empty list")
    if not isinstance(build["requires_human_review"], bool):
        raise ValueError("requires_human_review must be a boolean")

    human_review = (
        """
Because subjective product quality matters here, the evidence must include
genuine human review. In the exploration brief, propose the review sample,
rubric, and workflow based on the implementation and risk. In the completed
evidence, preserve the real human judgments, meaningful disagreements, and the
resulting keep, revise, or stop decision. Do not substitute synthetic review
for human judgment."""
        if build["requires_human_review"]
        else """
If repository inspection shows that subjective product quality materially
affects acceptance, add genuine human review. Propose the review sample, rubric,
and workflow from the implementation and risk, and preserve real judgments,
meaningful disagreements, and the resulting keep, revise, or stop decision."""
    )
    prompt = f"""Inspect the existing Project at {project} before editing.

Project2Job diagnosis
- Current Match: {build['current_match']}
- Evidence gap: {build['gap']}
- Why the current Project does not fully satisfy the target JD: {build['jd_mismatch']}
- Why this matters now: {build['why_it_matters']}
- Hiring capability category: {build['capability_category']}
- Exactly one evidence direction: {direction}

Preserve these product and safety boundaries:
{chr(10).join(f"- {item}" for item in build['product_and_safety_boundaries'])}

Produce inspectable evidence sufficient for later Project2Job reassessment:
{chr(10).join(f"- {item}" for item in build['evidence_artifacts_needed'])}

After completed evidence exists, Project2Job expects to reconsider only:
{chr(10).join(f"- {item}" for item in build['outputs_expected_to_change'])}

The proposal itself must not change the current Match. Completed and sufficient
evidence may support a later move from GAP to TRANSFERABLE. Use only EXACT
MATCH, TRANSFERABLE, and GAP when discussing Match.

Phase 1 — repository-grounded exploration
- Inspect the current product goals, architecture, workflows, known failures,
  tests, and safety boundaries.
- Confirm that the recommended direction plausibly serves the Project's
  existing user task, and identify one relevant limitation, failure mode, or
  unmet need.
- Identify the smallest product-relevant problem worth addressing.
- Compare reasonable implementation options before choosing one.
- Define the smallest justified implementation and state model.
- Define an evaluation approach appropriate to the feature and risk.
- Derive concrete subclasses such as state names, turn limits, prompt
  structure, UI behavior, corpus size, metrics, and file organization only
  after inspecting the repository.
- Keep the product-fit check lightweight: preserve the Project's core identity
  and safety boundaries while establishing a plausible user-task connection.
- When relevance is uncertain, propose a bounded prototype, experiment, or
  evaluation that can resolve the uncertainty.
- When the direction does not fit the Project, return a better evidence
  direction instead of forcing it into the repository.
{human_review}

Return one exploration brief with the diagnosis, product-fit finding, options
and tradeoffs, recommended smallest implementation, proposed state model,
evaluation plan, evidence plan, affected files, risks, and open questions.
Then stop for product-owner approval before implementation.

Phase 2 — only after explicit approval
Implement the approved direction and produce the inspectable evidence above.
Do not invent metrics, users, outcomes, ownership, or test results. Run real
verification appropriate to the repository. Report changed files, commands,
exact results, remaining limitations, and every produced evidence artifact."""
    return {
        **deepcopy(build),
        "execution_handoff_prompt": prompt,
    }
