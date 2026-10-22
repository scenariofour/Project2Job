"""Resolve Application Pack source citations against their permitted sources.

JSON Schema validation proves an output has a `location` string. It cannot prove
the string points at real text. Day 5 recorded a Project2Job run whose top
Project Highlight cited `S01_project.md:2` while the claim it exported sits on
absolute line 3, because the run numbered non-empty body lines instead of file
lines. Every citation in that run was internally consistent and pointed at the
right content, so nothing downstream could notice.

This module is the deterministic gate for that failure. It reads no model output
into a judgement: it parses a location, opens the cited file, and reports whether
the cited span exists and carries text.

Canonical grammar
-----------------

    <source-file>:<line>
    <source-file>:<start>-<end>
    line <line>
    lines <start>-<end>
    <source-file>#<Heading>

Line numbers are absolute and 1-based, and count every line in the file
including blank ones. A heading anchor names a real heading and resolves to that
section. Both forms are things a reader can check. An ordinal prose anchor such
as `sentence 1` or `bullet 2` is not: nothing in the file marks where the count
starts. A location that names no resolvable anchor, points outside the file, or
resolves to a blank span does not resolve and may not support an external claim.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator

RESOLVED = "resolved"
BLANK_SPAN = "blank_span"
OUT_OF_RANGE = "out_of_range"
UNPARSED_LOCATION = "unparsed_location"
UNMAPPED_SOURCE = "unmapped_source"

FAILURE_STATUSES = (BLANK_SPAN, OUT_OF_RANGE, UNPARSED_LOCATION, UNMAPPED_SOURCE)

# The canonical forms, matched whole so prose anchors such as
# "Responsibilities, bullet 2" or "Team Project, sentence 1" are rejected rather
# than mistaken for line 2 and line 1. An en dash is accepted because hosts
# routinely rewrite a hyphenated range.
_RANGE = r"(?P<start>\d+)(?:\s*[-\u2013]\s*(?P<end>\d+))?"
_HEADING = re.compile(r"^\s*(?P<file>[^\s#][^#]*?)?\s*#\s*(?P<heading>[^#].*?)\s*$")
_MARKDOWN_HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+?)\s*$")
_LOCATION_FORMS = (
    # path.md:3, path.md:3-4, path.md:line 3
    re.compile(rf"^\s*(?P<file>[^\s:][^:]*?)\s*:\s*(?:lines?\s+)?{_RANGE}\s*$"),
    # line 3, lines 3-5
    re.compile(rf"^\s*lines?\s+{_RANGE}\s*$"),
    # 3, 3-5
    re.compile(rf"^\s*{_RANGE}\s*$"),
)


def _walk(node: Any, pointer: str = "") -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield every `{source_id, location}` object with its JSON pointer."""
    if isinstance(node, dict):
        if isinstance(node.get("source_id"), str) and isinstance(
            node.get("location"), str
        ):
            yield pointer, node
        for key, value in node.items():
            yield from _walk(value, f"{pointer}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk(value, f"{pointer}/{index}")


def parse_location(location: str) -> dict[str, Any] | None:
    """Describe a location, or None when nothing in it can be resolved.

    Returns `{"file": key or None, "kind": "lines"|"heading", ...}`. `file` is
    None when the location carries only an anchor and the source ID has to name
    the file.
    """
    for form in _LOCATION_FORMS:
        match = form.match(location)
        if not match:
            continue
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        if end < start:
            start, end = end, start
        return {
            "file": match.groupdict().get("file"),
            "kind": "lines",
            "start": start,
            "end": end,
        }
    heading = _HEADING.match(location)
    if heading:
        return {
            "file": heading.group("file"),
            "kind": "heading",
            "heading": heading.group("heading"),
        }
    return None


def _heading_span(lines: list[str], heading: str) -> tuple[int, int] | None:
    """The 1-based line span of `heading` through the end of its section."""
    target = heading.casefold()
    for index, line in enumerate(lines):
        match = _MARKDOWN_HEADING.match(line)
        if not match or match.group("text").casefold() != target:
            continue
        level = len(match.group("hashes"))
        for offset in range(index + 1, len(lines)):
            next_heading = _MARKDOWN_HEADING.match(lines[offset])
            if next_heading and len(next_heading.group("hashes")) <= level:
                return index + 1, offset
        return index + 1, len(lines)
    return None


def resolve_refs(
    instance: dict[str, Any], sources: dict[str, Path]
) -> list[dict[str, Any]]:
    """Resolve every source ref in `instance` against `sources`.

    `sources` maps a source ID or a cited file name to a readable path. Results
    keep the JSON pointer so a failure names the exact exported field.
    """
    cache: dict[Path, list[str]] = {}
    results: list[dict[str, Any]] = []
    for pointer, ref in _walk(instance):
        source_id = ref["source_id"]
        location = ref["location"]
        record: dict[str, Any] = {
            "pointer": pointer,
            "source_id": source_id,
            "location": location,
        }
        parsed = parse_location(location)
        if parsed is None:
            record["status"] = UNPARSED_LOCATION
            record["detail"] = (
                "The location names no absolute line or line range, so no reader "
                "or checker can confirm the cited text."
            )
            results.append(record)
            continue

        # When the location names a file, that file is the citation. Falling
        # back to the source ID here would silently resolve a citation against
        # a document it does not name.
        file_key = parsed["file"]
        path = sources.get(file_key) if file_key else sources.get(source_id)
        if path is None:
            record["status"] = UNMAPPED_SOURCE
            record["detail"] = f"No permitted source is mapped for {file_key or source_id!r}."
            results.append(record)
            continue

        if path not in cache:
            cache[path] = path.read_text(encoding="utf-8").splitlines()
        lines = cache[path]
        record["resolved_path"] = str(path)

        if parsed["kind"] == "heading":
            span = _heading_span(lines, parsed["heading"])
            if span is None:
                record["status"] = OUT_OF_RANGE
                record["detail"] = (
                    f"{path.name} has no heading {parsed['heading']!r}."
                )
                results.append(record)
                continue
            start, end = span
        else:
            start, end = parsed["start"], parsed["end"]
            if start < 1 or end > len(lines):
                record["status"] = OUT_OF_RANGE
                record["detail"] = (
                    f"{path.name} has {len(lines)} lines; the citation asks for "
                    f"{start}-{end}."
                )
                results.append(record)
                continue

        record["cited_lines"] = [start, end]
        excerpt = "\n".join(lines[start - 1 : end])
        if not excerpt.strip():
            record["status"] = BLANK_SPAN
            record["detail"] = (
                f"{path.name} lines {start}-{end} are blank, so the citation "
                "supports nothing."
            )
            results.append(record)
            continue

        record["status"] = RESOLVED
        record["excerpt"] = excerpt
        results.append(record)
    return results


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts plus the unresolved records, ordered as produced."""
    counts = {
        status: sum(1 for item in results if item["status"] == status)
        for status in (RESOLVED, *FAILURE_STATUSES)
    }
    unresolved = [item for item in results if item["status"] != RESOLVED]
    return {
        "total_refs": len(results),
        "counts": counts,
        "all_resolve": not unresolved,
        "unresolved": unresolved,
    }


def parse_source_arguments(values: list[str]) -> dict[str, Path]:
    """Turn repeated `--source` values into a source map.

    Accepts `KEY=path` and bare `path`; a bare path is keyed by its file name.
    """
    sources: dict[str, Path] = {}
    for value in values:
        key, separator, raw = value.partition("=")
        path = Path(raw if separator else key).expanduser()
        if not path.is_file():
            raise ValueError(f"Permitted source is not a readable file: {path}")
        sources[key if separator else path.name] = path
    return sources


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Resolve every source citation in a Project2Job output against its "
            "permitted sources."
        )
    )
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="[SOURCE_ID=]PATH",
        help="A permitted source. Repeat once per file.",
    )
    args = parser.parse_args()
    try:
        instance = json.loads(args.output.read_text(encoding="utf-8"))
        sources = parse_source_arguments(args.source)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"all_resolve": False, "errors": [str(exc)]}, indent=2))
        raise SystemExit(2) from exc

    summary = summarize(resolve_refs(instance, sources))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if not summary["all_resolve"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
