"""One bounded public-web research pass (WO-05, Day 2).

The runtime never opens a socket. It drives a `ResearchHost` the host provides
and records what happened: queries, pages, tiers, duplicates, escalations,
blocked pages, budget usage, and one stop reason.

Two rules hold on every path.

1. Fetched page text is inert. It is counted, never interpreted. Only the
   host's structured extraction becomes an item, and only a search result can
   enter the fetch frontier, so text inside a page cannot cause a search, a
   fetch, a navigation, or a claim.
2. Nothing here is project evidence. Interview research carries its own
   source-status scale and can never reach a resume bullet.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

#: Ceilings from docs/09_TOKEN_CONTEXT_AND_COST.md, also encoded as schema maximums.
DEFAULT_BUDGET = {
    "max_search_queries": 8,
    "max_pages_fetched": 12,
    "max_playwright_pages": 3,
    "max_navigation_depth": 1,
    "max_chars_per_page": 20000,
    "max_total_tokens": 60000,
    "max_retries_per_page": 1,
    "max_runtime_seconds": 120,
}

ZERO_USAGE = {
    "search_queries": 0,
    "pages_fetched": 0,
    "playwright_pages": 0,
    "navigation_depth_used": 0,
    "total_tokens": 0,
    "max_retries_used_per_page": 0,
    "runtime_seconds": 0,
}

COMPANY_GAPS = (
    "official_interview_signals",
    "reported_interview_process",
    "reported_interview_questions",
)
TRACK_GAP = "track_team_level_expectations"

GAP_QUERY = {
    "official_interview_signals": "{company} official interview process",
    "track_team_level_expectations": "{company} {track} expectations",
    "reported_interview_process": "{company} reported interview loop",
    "reported_interview_questions": "{company} reported interview questions",
}

TIER_RANK = {"official": 0, "independent_report": 1, "aggregator_or_forum": 2, "unknown": 3}

#: Deterministic cost model. These are modeled seconds, not wall-clock: a
#: measured runtime would make every trace and eval non-reproducible.
SECONDS_PER_QUERY = 2
SECONDS_PER_FETCH = 3
SECONDS_PER_RENDER = 6
TOKENS_PER_QUERY = 40

TRACKING_PARAMS = ("utm_", "ref", "source", "fbclid", "gclid", "mc_cid")

FRESH_DAYS = 548  # about 18 months
AGING_DAYS = 1096  # about 36 months


@dataclass(frozen=True)
class SearchResult:
    """One candidate page. Only a search result may enter the fetch frontier."""

    url: str
    tier: str = "unknown"


@dataclass(frozen=True)
class ExtractedItem:
    """One structured item the host extracted from a page it read."""

    kind: str  # "signal" or "question"
    topic: str
    statement: str
    purpose: str
    source_date: str | None = None
    interview_stage: str | None = None
    priority: str = "P1"


@dataclass(frozen=True)
class FetchResult:
    outcome: str
    text: str = ""
    items: tuple[ExtractedItem, ...] = ()


class ResearchHost(Protocol):
    def search(self, query: str, purpose: str) -> list[SearchResult]: ...
    def fetch(self, url: str) -> FetchResult: ...
    def render(self, url: str) -> FetchResult: ...


@dataclass(frozen=True)
class PastedReport:
    """Material the user supplied. Never retrieved, never web-sourced."""

    kind: str
    topic: str
    statement: str
    reference: str
    source_date: str | None = None
    interview_stage: str | None = None
    priority: str = "P1"


def canonical_url(url: str) -> str:
    """Normalize a URL for deduplication: no fragment, no tracking parameters."""
    parts = urlsplit(url)
    query = "&".join(
        pair
        for pair in parts.query.split("&")
        if pair and not pair.split("=")[0].lower().startswith(TRACKING_PARAMS)
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))


def freshness_for(source_date: str | None, today: date) -> str:
    if not source_date:
        return "unknown"
    try:
        parsed = date.fromisoformat(source_date)
    except ValueError:
        return "unknown"
    age = (today - parsed).days
    if age <= FRESH_DAYS:
        return "fresh"
    if age <= AGING_DAYS:
        return "aging"
    return "stale"


def presented_as_for(source_status: str, freshness: str) -> str:
    """A claim is never presented more strongly than its source permits."""
    if source_status == "single_report":
        return "reported_once"
    if source_status in ("inferred_from_jd", "unknown"):
        return "speculative"
    return "possible" if freshness == "stale" else "likely"


def _fingerprint(items: tuple[ExtractedItem, ...], text: str) -> str:
    """Identify a mirror of a page already kept.

    The page body is the fingerprint: a mirror serves the same text, while two
    independent write-ups that happen to agree do not. Grouping on the extracted
    statement instead would collapse real corroboration into one report.
    """
    payload = " ".join(text.split()) or "|".join(
        sorted(f"{item.kind}:{item.topic}:{item.statement}" for item in items)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class _Held:
    """One item as extracted, with where it came from."""

    item: ExtractedItem
    origin: str
    tier: str
    reference: str
    url: str | None = None
    fetch_method: str | None = None
    retrieved_on: str | None = None


@dataclass
class ResearchRun:
    research: dict
    signals: list[dict] = field(default_factory=list)
    questions: list[dict] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)


def _source_record(held: _Held) -> dict:
    source = {"origin": held.origin, "reference": held.reference}
    if held.url:
        source["url"] = held.url
        source["fetch_method"] = held.fetch_method
        source["retrieved_on"] = held.retrieved_on
    if held.item.source_date:
        source["source_date"] = held.item.source_date
    if held.item.interview_stage:
        source["interview_stage"] = held.item.interview_stage
    return source


def _assemble(held_items: list[_Held], company: str, today: date) -> ResearchRun:
    """Group items into signals and questions, then disclose any conflict.

    An official statement keeps its own record: it is never merged with, or
    downgraded to match, an independent report about the same topic.
    """
    groups: dict[tuple, list[_Held]] = {}
    for held in held_items:
        official = held.tier == "official" and held.origin in (
            "official_company_page",
            "official_company_material",
        )
        key = (held.item.kind, held.item.topic, held.item.statement, official)
        groups.setdefault(key, []).append(held)

    signals: list[dict] = []
    questions: list[dict] = []
    by_topic: dict[str, list[tuple[str, dict, list[_Held]]]] = {}

    for (kind, topic, statement, official), members in groups.items():
        distinct = {member.reference for member in members}
        if official:
            source_status = "official"
        elif len(distinct) >= 2:
            source_status = "repeatedly_reported"
        else:
            source_status = "single_report"

        dates = [member.item.source_date for member in members if member.item.source_date]
        freshness = freshness_for(max(dates) if dates else None, today)
        tier = min((member.tier for member in members), key=lambda t: TIER_RANK[t])
        sources = []
        for member in members:
            record = _source_record(member)
            if record not in sources:
                sources.append(record)

        item_id = (
            f"s{len(signals) + 1}" if kind == "signal" else f"q{len(questions) + 1}"
        )
        common = {
            "layer": "company_interview_signal"
            if official
            else "reported_interview_evidence",
            "source_status": source_status,
            "presented_as": presented_as_for(source_status, freshness),
            "tier": tier,
            "sources": sources,
            "freshness": freshness,
            "company": company,
        }
        if kind == "question":
            record = {
                "question_id": item_id,
                "text": statement,
                "priority": members[0].item.priority,
                **common,
            }
            questions.append(record)
        else:
            record = {"signal_id": item_id, "statement": statement, **common}
            signals.append(record)
        by_topic.setdefault(topic, []).append((item_id, record, members))

    conflicts = []
    for topic, entries in by_topic.items():
        statements = {
            entry[1].get("statement") or entry[1].get("text") for entry in entries
        }
        if len(entries) < 2 or len(statements) < 2:
            continue
        if any(entry[1]["source_status"] == "official" for entry in entries):
            resolution = "official_preferred_both_shown"
        elif len({entry[1]["freshness"] for entry in entries}) > 1:
            resolution = "newer_preferred_both_shown"
        else:
            resolution = "unresolved_both_shown"
        conflicts.append(
            {
                "item_ids": [entry[0] for entry in entries],
                "disagreement": f"Sources disagree about {topic}; both are shown.",
                "resolution": resolution,
            }
        )

    return ResearchRun(research={}, signals=signals, questions=questions, conflicts=conflicts)


class BoundedResearch:
    """Search, prioritize, fetch, extract, check gaps, adjust, stop."""

    def __init__(
        self,
        company: str,
        host: ResearchHost,
        *,
        today: date,
        budget: dict | None = None,
        track: str | None = None,
    ) -> None:
        self.company = company
        self.host = host
        self.today = today
        self.budget = {**DEFAULT_BUDGET, **(budget or {})}
        self.track = track
        self.usage = dict(ZERO_USAGE)
        self.queries: list[dict] = []
        self.pages: list[dict] = []
        self.held: list[_Held] = []
        self.seen_canonical: dict[str, str] = {}
        self.fingerprints: dict[str, str] = {}
        self.closed: set[str] = set()
        self.tool_failed = False

    # -- budget ---------------------------------------------------------
    def _query_budget_left(self) -> bool:
        return self.usage["search_queries"] < self.budget["max_search_queries"]

    def _page_budget_left(self) -> bool:
        return self.usage["pages_fetched"] < self.budget["max_pages_fetched"]

    def _render_budget_left(self) -> bool:
        return self.usage["playwright_pages"] < self.budget["max_playwright_pages"]

    # -- run ------------------------------------------------------------
    def run(self) -> ResearchRun:
        target_gaps = list(COMPANY_GAPS)
        if self.track:
            target_gaps.insert(1, TRACK_GAP)
        pending = list(target_gaps)
        budget_hit = False

        while pending:
            if not self._query_budget_left():
                budget_hit = True
                break
            gap = pending[0]
            if self._search_and_read(gap) == "budget":
                budget_hit = True
                break
            if self.tool_failed:
                break
            # Drop every gap this pass closed; an unclosed one is abandoned
            # after its own query rather than searched forever.
            pending = [item for item in pending if item not in self.closed]
            if gap in pending:
                pending.remove(gap)

        unclosed = [gap for gap in target_gaps if gap not in self.closed]
        assembled = _assemble(self.held, self.company, self.today)
        assembled.research = {
            "mode": "automatic_bounded",
            "budget": dict(self.budget),
            "usage": dict(self.usage),
            "queries": self.queries,
            "pages": self.pages,
            "stop_reason": self._stop_reason(unclosed, budget_hit, assembled.conflicts),
            "gaps": [
                f"No public source established: {gap.replace('_', ' ')}."
                for gap in unclosed
            ],
        }
        return assembled

    def _stop_reason(self, unclosed: list[str], budget_hit: bool, conflicts: list) -> str:
        if self.tool_failed:
            return "tool_failure"
        if conflicts:
            return "conflict_requires_disclosure"
        if not unclosed:
            return "evidence_sufficient"
        if budget_hit:
            return "budget_exhausted"
        blocked = {"inaccessible_login_required", "inaccessible_blocked"}
        if self.pages and all(page["outcome"] in blocked for page in self.pages):
            return "sources_inaccessible"
        return "evidence_exhausted"

    def _search_and_read(self, gap: str) -> str:
        template = GAP_QUERY[gap]
        query = template.format(company=self.company, track=self.track or "")
        query = " ".join(query.split())
        try:
            results = list(self.host.search(query, gap))
        except Exception:
            self.tool_failed = True
            return "failed"
        self.usage["search_queries"] += 1
        self.usage["runtime_seconds"] += SECONDS_PER_QUERY
        self.usage["total_tokens"] += TOKENS_PER_QUERY

        # Record the query before reading anything, so a run that stops mid-pass
        # still shows the query it spent.
        record = {
            "query": query,
            "purpose": gap,
            "results_considered": len(results),
            "results_kept": 0,
        }
        self.queries.append(record)

        ordered = sorted(results, key=lambda result: TIER_RANK.get(result.tier, 3))
        for result in ordered:
            canonical = canonical_url(result.url)
            if canonical in self.seen_canonical:
                self.pages.append(
                    {
                        "url": result.url,
                        "canonical_url": canonical,
                        "tier": result.tier,
                        "outcome": "duplicate_of_kept_page",
                        "chars_retained": 0,
                        "duplicate_of": self.seen_canonical[canonical],
                    }
                )
                continue
            if not self._page_budget_left():
                self.pages.append(
                    {
                        "url": result.url,
                        "canonical_url": canonical,
                        "tier": result.tier,
                        "outcome": "skipped_budget",
                        "chars_retained": 0,
                    }
                )
                return "budget"
            record["results_kept"] += 1
            self._read(result, canonical)
            if self.tool_failed:
                return "failed"
            if gap not in self.closed:
                continue
            # One official page settles a gap. A reported one is worth a second
            # read, because one report is not corroboration — but never a third.
            if result.tier == "official" or record["results_kept"] >= 2:
                break

        return "ok"

    def _read(self, result: SearchResult, canonical: str) -> None:
        try:
            outcome = self.host.fetch(result.url)
        except Exception:
            self.tool_failed = True
            return
        self.usage["pages_fetched"] += 1
        self.usage["runtime_seconds"] += SECONDS_PER_FETCH
        retrieved_on = self.today.isoformat()

        if outcome.outcome == "render_required":
            self.pages.append(
                {
                    "url": result.url,
                    "canonical_url": canonical,
                    "tier": result.tier,
                    "fetch_method": "read_only_fetch",
                    "outcome": "render_required",
                    "retrieved_on": retrieved_on,
                    "chars_retained": 0,
                }
            )
            if not (self._render_budget_left() and self._page_budget_left()):
                return
            try:
                outcome = self.host.render(result.url)
            except Exception:
                self.tool_failed = True
                return
            self.usage["pages_fetched"] += 1
            self.usage["playwright_pages"] += 1
            self.usage["runtime_seconds"] += SECONDS_PER_RENDER
            self._record(result, canonical, outcome, "playwright", retrieved_on)
            return

        self._record(result, canonical, outcome, "read_only_fetch", retrieved_on)

    def _record(
        self,
        result: SearchResult,
        canonical: str,
        outcome: FetchResult,
        fetch_method: str,
        retrieved_on: str,
    ) -> None:
        page = {
            "url": result.url,
            "canonical_url": canonical,
            "tier": result.tier,
            "outcome": outcome.outcome,
            "chars_retained": 0,
        }
        if outcome.outcome in ("inaccessible_login_required", "inaccessible_blocked"):
            # A wall is recorded and abandoned. No credential, no browser, no
            # inference about what sits behind it.
            self.pages.append(page)
            return
        if outcome.outcome != "extracted":
            page["fetch_method"] = fetch_method
            page["retrieved_on"] = retrieved_on
            self.pages.append(page)
            return

        fingerprint = _fingerprint(outcome.items, outcome.text)
        if fingerprint in self.fingerprints:
            page["outcome"] = "duplicate_of_kept_page"
            page["duplicate_of"] = self.fingerprints[fingerprint]
            self.pages.append(page)
            self.seen_canonical[canonical] = self.fingerprints[fingerprint]
            return

        page["fetch_method"] = fetch_method
        page["retrieved_on"] = retrieved_on
        if fetch_method == "playwright":
            page["escalation_reason"] = "javascript_rendered"
            page["plain_fetch_outcome"] = "render_required"
        # Only the retained character count survives. The page body itself is
        # never stored, quoted, or read for instructions.
        page["chars_retained"] = min(len(outcome.text), self.budget["max_chars_per_page"])
        self.pages.append(page)
        self.usage["total_tokens"] += page["chars_retained"] // 4
        self.fingerprints[fingerprint] = canonical
        self.seen_canonical[canonical] = canonical

        origin = (
            "official_company_page" if result.tier == "official" else "public_report_page"
        )
        for item in outcome.items:
            self.held.append(
                _Held(
                    item=item,
                    origin=origin,
                    tier=result.tier,
                    reference=f"{canonical}#{item.topic}",
                    url=result.url,
                    fetch_method=fetch_method,
                    retrieved_on=retrieved_on,
                )
            )
            self.closed.add(item.purpose)


def user_supplied_context(
    company: str, reports: list[PastedReport], today: date
) -> ResearchRun:
    """Assemble a context from user-supplied material only. No research ran."""
    held = [
        _Held(
            item=ExtractedItem(
                kind=report.kind,
                topic=report.topic,
                statement=report.statement,
                purpose="reported_interview_process",
                source_date=report.source_date,
                interview_stage=report.interview_stage,
                priority=report.priority,
            ),
            origin="user_pasted_report",
            tier="unknown",
            reference=report.reference,
        )
        for report in reports
    ]
    assembled = _assemble(held, company, today)
    assembled.research = {
        "mode": "user_supplied_only",
        "usage": dict(ZERO_USAGE),
        "queries": [],
        "pages": [],
        "stop_reason": "research_not_run",
        "gaps": ["No public-web research ran; only user-supplied material was used."],
    }
    return assembled


def unavailable_context() -> ResearchRun:
    return ResearchRun(
        research={
            "mode": "unavailable",
            "usage": dict(ZERO_USAGE),
            "queries": [],
            "pages": [],
            "stop_reason": "research_not_run",
            "gaps": ["Public-web research was unavailable in this host."],
        }
    )


def usage_exceeding_budget(research: dict) -> list[str]:
    """Every spend that went past its own declared ceiling."""
    budget = research.get("budget")
    if not budget:
        return []
    pairs = {
        "search_queries": "max_search_queries",
        "pages_fetched": "max_pages_fetched",
        "playwright_pages": "max_playwright_pages",
        "navigation_depth_used": "max_navigation_depth",
        "total_tokens": "max_total_tokens",
        "max_retries_used_per_page": "max_retries_per_page",
        "runtime_seconds": "max_runtime_seconds",
    }
    return [
        f"{spent} {research['usage'][spent]} exceeds {ceiling} {budget[ceiling]}"
        for spent, ceiling in pairs.items()
        if research["usage"][spent] > budget[ceiling]
    ]
