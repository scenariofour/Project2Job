from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from inventory import inventory

SCHEMA_VERSION = "1.0.0"
REGISTRY_FILE = "context-registry.json"
CONSENT_FILE = "consent.json"
SECRET_KEYS = {
    "api_key",
    "authorization",
    "cookie",
    "credential",
    "password",
    "private_key",
    "secret",
    "session",
    "token",
}
SAFE_TELEMETRY_KEYS = {
    "cached_input_tokens",
    "input_tokens",
    "output_tokens",
    "token_usage",
    "tokens",
}
RAW_CONTENT_KEYS = {
    "body",
    "content",
    "document",
    "excerpt",
    "raw",
    "resume",
    "source_text",
    "transcript",
}
RAW_SOURCE_BODY_KEYS = {
    "document_body",
    "document_text",
    "jd_body",
    "jd_text",
    "project_body",
    "project_text",
    "resume_body",
    "resume_text",
    "transcript_body",
    "transcript_text",
}
AGENT_STATE_ID_MAPS = {
    "artifacts",
    "claims",
    "dependencies",
    "evidence",
    "outputs",
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[opsu]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{16,}", re.IGNORECASE),
)
RUN_FIELDS = {
    "agent_state",
    "agent_trace",
    "evidence",
    "scores",
    "matches",
    "reused_fact_ids",
    "unresolved_questions",
    "recommended_route",
    "output_references",
    "observed_metrics",
}
PROJECT_FIELDS = {
    "confirmed_facts",
    "ownership_boundaries",
    "unresolved_questions",
    "known_gaps",
}
SKILLS = {
    "p2j",
    "p2j-answer",
    "p2j-audit",
    "p2j-brief",
    "p2j-intel",
    "p2j-mock",
    "p2j-upgrade",
}
EVIDENCE_STATUSES = {
    "supported",
    "partially_supported",
    "inferred",
    "not_found",
    "conflicting",
    "needs_confirmation",
}


class RegistryError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def registry_home() -> Path:
    override = os.environ.get("P2J_HOME")
    return Path(override).expanduser() if override else Path.home() / ".project2job"


def empty_registry() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "projects": [],
        "jds": [],
        "analysis_runs": [],
    }


def stable_id(kind: str, identity: str) -> str:
    digest = hashlib.sha256(f"{kind}\0{identity}".encode()).hexdigest()[:24]
    return f"{kind}_{digest}"


def aggregate_fingerprint(items: list[dict]) -> str:
    digest = hashlib.sha256()
    for item in sorted(items, key=lambda value: value["path"]):
        digest.update(item["path"].encode())
        digest.update(b"\0")
        digest.update(item["fingerprint"].encode())
        digest.update(b"\0")
    return digest.hexdigest()


def run_git(project: Path, *arguments: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(project), *arguments],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value or None


def normalized_url(value: str) -> str:
    raw = value.strip()
    scp = re.match(r"^(?:[^@/]+@)?([^:/]+):(.+)$", raw)
    if scp and "://" not in raw:
        host, path = scp.groups()
        return f"{host.lower()}/{path.removesuffix('.git').strip('/')}"

    parts = urlsplit(raw)
    if parts.scheme == "file":
        return str(Path(parts.path).expanduser().resolve())
    if not parts.netloc:
        return str(Path(raw).expanduser().resolve())
    host = (parts.hostname or "").lower()
    port = f":{parts.port}" if parts.port else ""
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not any(part in key.lower() for part in SECRET_KEYS)
        and not key.lower().startswith(("utm_", "auth", "signature"))
    ]
    path = parts.path.removesuffix(".git").rstrip("/") or "/"
    return urlunsplit(
        (parts.scheme.lower() or "https", host + port, path, urlencode(query), "")
    )


def git_identity(project: Path) -> tuple[str | None, bool]:
    top = run_git(project, "rev-parse", "--show-toplevel")
    if not top:
        return None, False
    remote_names = (run_git(project, "remote") or "").splitlines()
    remotes = []
    for name in remote_names:
        value = run_git(project, "remote", "get-url", name)
        if value:
            remotes.append((name, normalized_url(value)))
    selected = next((value for name, value in remotes if name == "origin"), None)
    unique = sorted({value for _, value in remotes})
    if selected is None and len(unique) == 1:
        selected = unique[0]
    if selected is None:
        return None, len(unique) > 1
    relative = project.resolve().relative_to(Path(top).resolve())
    return f"{selected}#{relative.as_posix() or '.'}", False


def project_identity(project: Path) -> dict:
    resolved = project.expanduser().resolve()
    if not resolved.is_dir():
        raise RegistryError(f"Project path is not a directory: {resolved}")
    git_value, ambiguous = git_identity(resolved)
    identity_kind = "git_remote" if git_value else "canonical_path"
    identity = git_value or str(resolved)
    return {
        "root": resolved,
        "project_id": stable_id("project", identity),
        "identity_kind": identity_kind,
        "identity_ambiguous": ambiguous,
    }


def project_snapshot(identity: dict, prior_record: dict | None = None) -> dict:
    latest = prior_record["versions"][-1] if prior_record else {}
    cached_files = {
        item["path"]: item for item in latest.get("artifacts", [])
    }
    full_inventory = inventory(
        identity["root"], git_limit=0, cached_files=cached_files
    )
    artifacts = [
        {
            "path": item["path"],
            "fingerprint": item["sha256"],
            "size_bytes": item["size_bytes"],
            "mtime_ns": item["mtime_ns"],
            "ctime_ns": item["ctime_ns"],
            "evidence_surfaces": item["evidence_surfaces"],
        }
        for item in full_inventory["files"]
        if item["is_text_candidate"]
        or item["evidence_surfaces"]
        or item["path"] in cached_files
    ]
    return {
        "project_id": identity["project_id"],
        "identity_kind": identity["identity_kind"],
        "identity_ambiguous": identity["identity_ambiguous"],
        "fingerprint": aggregate_fingerprint(artifacts),
        "artifacts": artifacts,
    }


def read_jd_content(jd_file: Path | None, use_stdin: bool) -> bytes:
    if jd_file:
        resolved = jd_file.expanduser().resolve()
        if not resolved.is_file():
            raise RegistryError(f"JD path is not a file: {resolved}")
        return resolved.read_bytes()
    if use_stdin:
        return sys.stdin.buffer.read()
    return b""


def jd_snapshot(
    jd_file: Path | None = None,
    jd_url: str | None = None,
    jd_key: str | None = None,
    use_stdin: bool = False,
) -> dict:
    content = read_jd_content(jd_file, use_stdin)
    fingerprint = hashlib.sha256(content).hexdigest()
    if jd_url:
        identity_kind = "url"
        identity = normalized_url(jd_url)
    elif jd_key:
        identity_kind = "user_key"
        identity = jd_key.strip()
    elif jd_file:
        identity_kind = "canonical_path"
        identity = str(jd_file.expanduser().resolve())
    elif content:
        identity_kind = "content"
        identity = fingerprint
    else:
        raise RegistryError("Provide JD content, a JD URL, or a JD key.")
    return {
        "jd_id": stable_id("jd", identity),
        "identity_kind": identity_kind,
        "fingerprint": fingerprint,
    }


def agent_state_id_map(context: tuple[object, ...]) -> bool:
    return (
        len(context) >= 2
        and context[-2] == "agent_state"
        and context[-1] in AGENT_STATE_ID_MAPS
    )


def bounded_output_content(
    context: tuple[object, ...], key: str
) -> bool:
    return (
        key == "content"
        and len(context) >= 3
        and context[-3] == "agent_state"
        and context[-2] == "outputs"
        and isinstance(context[-1], str)
    )


def complete_artifact_manifest(context: tuple[object, ...]) -> bool:
    return (
        len(context) >= 3
        and context[-3] == "versions"
        and isinstance(context[-2], int)
        and context[-1] == "artifacts"
    )


def validate_safe_value(
    value: object,
    path: str = "value",
    depth: int = 0,
    context: tuple[object, ...] = (),
) -> None:
    if depth > 10:
        raise RegistryError(f"{path} is too deeply nested to persist.")
    if isinstance(value, dict):
        keys_are_ids = agent_state_id_map(context)
        for key, item in value.items():
            normalized_key = str(key)
            lowered = normalized_key.lower()
            if not keys_are_ids:
                if lowered not in SAFE_TELEMETRY_KEYS and (
                    lowered in SECRET_KEYS
                    or any(part in lowered for part in SECRET_KEYS)
                ):
                    raise RegistryError(
                        f"{path}.{key} may contain a secret and was not saved."
                    )
                if (
                    lowered in RAW_CONTENT_KEYS
                    or lowered in RAW_SOURCE_BODY_KEYS
                ) and not bounded_output_content(context, normalized_key):
                    raise RegistryError(
                        f"{path}.{key} contains source body content and was not saved."
                    )
            validate_safe_value(
                item,
                f"{path}.{key}",
                depth + 1,
                (*context, normalized_key),
            )
    elif isinstance(value, list):
        if len(value) > 200 and not complete_artifact_manifest(context):
            raise RegistryError(f"{path} contains too many items to persist.")
        for index, item in enumerate(value):
            validate_safe_value(
                item,
                f"{path}[{index}]",
                depth + 1,
                (*context, index),
            )
    elif isinstance(value, str):
        if len(value) > 4000:
            raise RegistryError(f"{path} is too large to persist.")
        if any(pattern.search(value) for pattern in SECRET_PATTERNS):
            raise RegistryError(f"{path} appears to contain a secret and was not saved.")
    elif value is not None and not isinstance(value, (bool, int, float)):
        raise RegistryError(f"{path} contains an unsupported value.")


def validate_registry(data: object) -> dict:
    if not isinstance(data, dict):
        raise RegistryError("Context Registry root must be an object.")
    required = {"schema_version", "projects", "jds", "analysis_runs"}
    if set(data) != required or data.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError("Context Registry has an unsupported structure or version.")
    for key in ("projects", "jds", "analysis_runs"):
        if not isinstance(data[key], list):
            raise RegistryError(f"Context Registry field '{key}' must be a list.")
    required_fields = {
        "projects": {
            "record_type",
            "project_id",
            "identity_kind",
            "versions",
            *PROJECT_FIELDS,
        },
        "jds": {"record_type", "jd_id", "identity_kind", "versions"},
        "analysis_runs": {
            "record_type",
            "run_id",
            "created_at",
            "project_id",
            "project_version",
            "jd_id",
            "jd_version",
            "skill",
        },
    }
    record_types = {
        "projects": "project",
        "jds": "jd",
        "analysis_runs": "analysis_run",
    }
    for collection, required_record_fields in required_fields.items():
        for record in data[collection]:
            if not isinstance(record, dict) or not required_record_fields.issubset(
                record
            ):
                raise RegistryError(
                    f"Context Registry contains an invalid {collection} record."
                )
            if record.get("record_type") != record_types[collection]:
                raise RegistryError(
                    f"Context Registry contains a mistyped {collection} record."
                )
            if collection != "analysis_runs" and (
                not isinstance(record["versions"], list) or not record["versions"]
            ):
                raise RegistryError(
                    f"Context Registry contains an unversioned {collection} record."
                )
            for version in record.get("versions", []):
                if not isinstance(version, dict) or not {
                    "version",
                    "fingerprint",
                    "observed_at",
                }.issubset(version):
                    raise RegistryError(
                        f"Context Registry contains an invalid {collection} version."
                    )
                if collection == "projects" and not isinstance(
                    version.get("artifacts"), list
                ):
                    raise RegistryError("Context Registry project artifacts must be a list.")
            if collection == "projects" and any(
                not isinstance(record[field], list) for field in PROJECT_FIELDS
            ):
                raise RegistryError("Context Registry project fields must be lists.")
            if collection == "analysis_runs" and record["skill"] not in SKILLS:
                raise RegistryError("Context Registry contains an unknown Skill run.")
    validate_safe_value(data, "registry")
    return data


def load_registry(home: Path | None = None) -> dict:
    path = (home or registry_home()) / REGISTRY_FILE
    if not path.exists():
        return empty_registry()
    try:
        return validate_registry(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError, RegistryError) as error:
        raise RegistryError(
            f"Context Registry is corrupted or unreadable at {path}: {error}"
        ) from error


def has_consent(home: Path) -> bool:
    path = home / CONSENT_FILE
    if not path.exists():
        return False
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise RegistryError(f"Consent record is corrupted at {path}: {error}") from error
    return value.get("persistent_context") is True


def atomic_write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    validate_safe_value(value)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.chmod(temporary, 0o600)
    temporary.replace(path)


def ensure_consent(home: Path, consent: bool) -> None:
    if has_consent(home):
        return
    if not consent:
        raise RegistryError(
            "Persistent Project2Job context needs one-time consent. "
            "Review what is stored, then rerun with --consent."
        )
    atomic_write(
        home / CONSENT_FILE,
        {"persistent_context": True, "granted_at": utc_now()},
    )


def find_record(records: list[dict], key: str, value: str) -> dict | None:
    return next((record for record in records if record.get(key) == value), None)


def artifact_changes(previous: dict | None, current: dict) -> dict[str, list[str]]:
    if not previous:
        return {
            "added": [item["path"] for item in current["artifacts"]],
            "changed": [],
            "removed": [],
        }
    old = {item["path"]: item["fingerprint"] for item in previous["artifacts"]}
    new = {item["path"]: item["fingerprint"] for item in current["artifacts"]}
    return {
        "added": sorted(new.keys() - old.keys()),
        "changed": sorted(
            path for path in new.keys() & old.keys() if new[path] != old[path]
        ),
        "removed": sorted(old.keys() - new.keys()),
    }


def current_or_next_version(record: dict | None, fingerprint: str) -> tuple[int, bool]:
    if record and record["versions"]:
        latest = record["versions"][-1]
        if latest["fingerprint"] == fingerprint:
            return latest["version"], False
        return latest["version"] + 1, True
    return 1, True


def source_paths(item: dict) -> set[str]:
    values = item.get("source_paths", [])
    return {str(value) for value in values if value}


def reusable_project_items(record: dict | None, affected: set[str]) -> dict:
    if not record:
        return {
            "confirmed_facts": [],
            "ownership_boundaries": [],
            "unresolved_questions": [],
            "known_gaps": [],
        }
    result = {}
    for field in PROJECT_FIELDS:
        result[field] = [
            item
            for item in record.get(field, [])
            if not (source_paths(item) & affected)
        ]
    return result


def run_dependency_paths(run: dict) -> set[str]:
    paths = set()
    for item in run.get("evidence", []):
        if isinstance(item, str):
            paths.add(item)
        elif isinstance(item, dict) and item.get("path"):
            paths.add(str(item["path"]))
    state = run.get("agent_state", {})
    paths.update(str(path) for path in state.get("artifacts", {}))
    return paths


def resolve_context(
    registry: dict,
    project: dict | None,
    jd: dict | None,
    mode: str = "normal",
) -> dict:
    project_record = (
        find_record(registry["projects"], "project_id", project["project_id"])
        if project
        else None
    )
    jd_record = (
        find_record(registry["jds"], "jd_id", jd["jd_id"]) if jd else None
    )
    project_version, project_is_new_version = (
        current_or_next_version(project_record, project["fingerprint"])
        if project
        else (None, False)
    )
    jd_version, jd_is_new_version = (
        current_or_next_version(jd_record, jd["fingerprint"])
        if jd
        else (None, False)
    )
    if project and project.get("identity_ambiguous"):
        state = "identity_ambiguous"
    elif project_is_new_version and jd_is_new_version:
        state = "new" if not project_record and not jd_record else "both_changed"
    elif project_is_new_version:
        state = "project_changed" if project_record else "new"
    elif jd_is_new_version:
        state = "jd_changed" if jd_record else "new"
    else:
        state = "unchanged"

    previous_project_version = (
        project_record["versions"][-1] if project_record else None
    )
    changes = (
        artifact_changes(previous_project_version, project)
        if project
        else {"added": [], "changed": [], "removed": []}
    )
    affected = set(changes["changed"]) | set(changes["removed"])
    reusable = reusable_project_items(project_record, affected)
    compatible_runs = []
    invalidated_outputs = []
    previous_agent_state = None
    for run in registry["analysis_runs"]:
        same_identity = (
            (project is None or run.get("project_id") == project["project_id"])
            and (jd is None or run.get("jd_id") == jd["jd_id"])
        )
        if same_identity and run.get("agent_state"):
            previous_agent_state = run["agent_state"]
        same_project = run.get("project_id") is None or (
            project is not None
            and run.get("project_id") == project["project_id"]
            and run.get("project_version") == project_version
        )
        same_jd = run.get("jd_id") is None or (
            jd is not None
            and run.get("jd_id") == jd["jd_id"]
            and run.get("jd_version") == jd_version
        )
        if same_project and same_jd:
            compatible_runs.append(
                {
                    "skill": run["skill"],
                    "created_at": run["created_at"],
                    "evidence": run.get("evidence", []),
                    "scores": run.get("scores"),
                    "matches": run.get("matches"),
                    "unresolved_questions": run.get("unresolved_questions", []),
                    "recommended_route": run.get("recommended_route"),
                    "output_references": run.get("output_references", []),
                    "agent_state": run.get("agent_state"),
                    "agent_trace": run.get("agent_trace"),
                    "observed_metrics": run.get("observed_metrics"),
                }
            )
        elif project and run.get("project_id") == project["project_id"]:
            if run_dependency_paths(run) & affected:
                invalidated_outputs.extend(run.get("output_references", []))

    if mode == "fresh" or state == "identity_ambiguous":
        reusable = reusable_project_items(None, set())
        compatible_runs = []
    elif mode == "refresh":
        compatible_runs = []

    recompute = []
    if mode in {"refresh", "fresh"}:
        if project:
            recompute.extend(["project_scores", "claims", "interview_value"])
        if jd:
            recompute.extend(["jd_match", "recommended_route"])
    if state in {"jd_changed", "both_changed"}:
        recompute.extend(["jd_match", "recommended_route"])
    if state in {"project_changed", "both_changed"}:
        recompute.extend(["dependent_scores", "dependent_claims", "interview_value"])
    return {
        "context_state": state,
        "mode": mode,
        "project_version": project_version,
        "jd_version": jd_version,
        "changes": changes,
        "reusable": reusable,
        "compatible_runs": compatible_runs,
        "previous_agent_state": (
            None if mode == "fresh" or state == "identity_ambiguous"
            else previous_agent_state
        ),
        "invalidated_output_references": sorted(set(invalidated_outputs)),
        "recompute": list(dict.fromkeys(recompute)),
        "reuse_notice": bool(
            mode != "fresh"
            and (
                compatible_runs
                or reusable["confirmed_facts"]
                or reusable["ownership_boundaries"]
            )
        ),
    }


def append_version(record: dict, snapshot: dict, kind: str) -> int:
    fingerprint = snapshot["fingerprint"]
    version, changed = current_or_next_version(record, fingerprint)
    if changed:
        value = {
            "version": version,
            "fingerprint": fingerprint,
            "observed_at": utc_now(),
        }
        if kind == "project":
            value["artifacts"] = snapshot["artifacts"]
        record["versions"].append(value)
    return version


def safe_analysis(analysis: dict) -> dict:
    if not isinstance(analysis, dict):
        raise RegistryError("Analysis input must be a JSON object.")
    selected = {
        key: analysis[key]
        for key in RUN_FIELDS | PROJECT_FIELDS | {"resolved_question_ids"}
        if key in analysis
    }
    validate_safe_value(selected, "analysis")
    item_ids = {
        "confirmed_facts": "fact_id",
        "ownership_boundaries": "claim_id",
        "unresolved_questions": "question_id",
        "known_gaps": "gap_id",
    }
    item_fields = {
        "confirmed_facts": {"fact_id", "text", "status", "source_paths"},
        "ownership_boundaries": {
            "claim_id",
            "boundary",
            "status",
            "source_paths",
        },
        "unresolved_questions": {
            "question_id",
            "text",
            "status",
            "source_paths",
        },
        "known_gaps": {"gap_id", "text", "status", "source_paths"},
    }
    for field, id_key in item_ids.items():
        items = selected.get(field, [])
        if not isinstance(items, list):
            raise RegistryError(f"Analysis field '{field}' must be a list.")
        for item in items:
            if not isinstance(item, dict) or not item.get(id_key):
                raise RegistryError(f"Each {field} item needs '{id_key}'.")
            if not isinstance(item.get("source_paths"), list):
                raise RegistryError(f"Each {field} item needs source_paths.")
        selected[field] = [
            {key: value for key, value in item.items() if key in item_fields[field]}
            for item in items
        ]
    for fact in selected.get("confirmed_facts", []):
        if not fact.get("text") or fact.get("status") not in EVIDENCE_STATUSES:
            raise RegistryError(
                "Each confirmed fact needs text and a canonical evidence status."
            )
    for field in ("evidence", "reused_fact_ids", "output_references"):
        if field in selected and not isinstance(selected[field], list):
            raise RegistryError(f"Analysis field '{field}' must be a list.")
    for field in ("agent_state", "agent_trace", "observed_metrics"):
        if field in selected and not isinstance(selected[field], dict):
            raise RegistryError(f"Analysis field '{field}' must be an object.")
    for field in ("reused_fact_ids", "output_references"):
        if not all(isinstance(value, str) for value in selected.get(field, [])):
            raise RegistryError(f"Analysis field '{field}' must contain strings.")
    route = selected.get("recommended_route")
    if route is not None and not isinstance(route, str):
        raise RegistryError("recommended_route must be a string.")
    resolved = selected.get("resolved_question_ids", [])
    if not isinstance(resolved, list) or not all(
        isinstance(value, str) for value in resolved
    ):
        raise RegistryError("resolved_question_ids must be a list of strings.")
    return selected


def merge_by_id(existing: list[dict], incoming: list[dict], id_keys: tuple[str, ...]) -> list[dict]:
    merged = list(existing)
    for item in incoming:
        key = next((item.get(name) for name in id_keys if item.get(name)), None)
        if key is None:
            raise RegistryError(f"Persisted item needs one of: {', '.join(id_keys)}")
        merged = [
            current
            for current in merged
            if not any(current.get(name) == key for name in id_keys)
        ]
        merged.append(item)
    return merged


def save_run(
    registry: dict,
    project: dict | None,
    jd: dict | None,
    skill: str,
    analysis: dict,
) -> tuple[dict, dict]:
    if skill not in SKILLS:
        raise RegistryError(f"Unknown Project2Job Skill: {skill}")
    selected = safe_analysis(analysis)
    project_record = None
    project_version = None
    if project:
        project_record = find_record(
            registry["projects"], "project_id", project["project_id"]
        )
        if project_record is None:
            project_record = {
                "record_type": "project",
                "project_id": project["project_id"],
                "identity_kind": project["identity_kind"],
                "versions": [],
                "confirmed_facts": [],
                "ownership_boundaries": [],
                "unresolved_questions": [],
                "known_gaps": [],
            }
            registry["projects"].append(project_record)
        previous = project_record["versions"][-1] if project_record["versions"] else None
        changes = artifact_changes(previous, project)
        affected = set(changes["changed"]) | set(changes["removed"])
        reusable = reusable_project_items(project_record, affected)
        for field in PROJECT_FIELDS:
            project_record[field] = reusable[field]
        resolved = set(selected.get("resolved_question_ids", []))
        project_record["unresolved_questions"] = [
            item
            for item in project_record["unresolved_questions"]
            if item.get("question_id") not in resolved
        ]
        for field, id_keys in (
            ("confirmed_facts", ("fact_id",)),
            ("ownership_boundaries", ("claim_id",)),
            ("unresolved_questions", ("question_id",)),
            ("known_gaps", ("gap_id",)),
        ):
            project_record[field] = merge_by_id(
                project_record[field],
                selected.get(field, []),
                id_keys,
            )
        project_version = append_version(project_record, project, "project")

    jd_record = None
    jd_version = None
    if jd:
        jd_record = find_record(registry["jds"], "jd_id", jd["jd_id"])
        if jd_record is None:
            jd_record = {
                "record_type": "jd",
                "jd_id": jd["jd_id"],
                "identity_kind": jd["identity_kind"],
                "versions": [],
            }
            registry["jds"].append(jd_record)
        jd_version = append_version(jd_record, jd, "jd")

    run = {
        "record_type": "analysis_run",
        "run_id": f"run_{uuid.uuid4().hex}",
        "created_at": utc_now(),
        "project_id": project["project_id"] if project else None,
        "project_version": project_version,
        "jd_id": jd["jd_id"] if jd else None,
        "jd_version": jd_version,
        "skill": skill,
    }
    for field in RUN_FIELDS:
        if field in selected:
            run[field] = selected[field]
    registry["analysis_runs"].append(run)
    validate_registry(registry)
    return registry, run


def remove_selected(
    registry: dict, project: dict | None, jd: dict | None
) -> tuple[dict, dict]:
    project_id = project["project_id"] if project else None
    jd_id = jd["jd_id"] if jd else None
    before = {
        "projects": len(registry["projects"]),
        "jds": len(registry["jds"]),
        "analysis_runs": len(registry["analysis_runs"]),
    }
    if project_id:
        registry["projects"] = [
            item for item in registry["projects"] if item["project_id"] != project_id
        ]
    if jd_id:
        registry["jds"] = [item for item in registry["jds"] if item["jd_id"] != jd_id]
    registry["analysis_runs"] = [
        item
        for item in registry["analysis_runs"]
        if not (
            (project_id and item.get("project_id") == project_id)
            or (jd_id and item.get("jd_id") == jd_id)
        )
    ]
    removed = {
        key: before[key] - len(registry[key])
        for key in ("projects", "jds", "analysis_runs")
    }
    return registry, removed


def add_context_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", type=Path)
    parser.add_argument("--jd-file", type=Path)
    parser.add_argument("--jd-url")
    parser.add_argument("--jd-key")
    parser.add_argument("--jd-stdin", action="store_true")


def snapshots(
    args: argparse.Namespace, registry: dict
) -> tuple[dict | None, dict | None]:
    project = None
    if args.project:
        identity = project_identity(args.project)
        prior = find_record(
            registry["projects"], "project_id", identity["project_id"]
        )
        project = project_snapshot(identity, prior)
    has_jd = args.jd_file or args.jd_url or args.jd_key or args.jd_stdin
    jd = (
        jd_snapshot(args.jd_file, args.jd_url, args.jd_key, args.jd_stdin)
        if has_jd
        else None
    )
    if project is None and jd is None:
        raise RegistryError("Provide a Project, a JD, or both.")
    return project, jd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve and store consent-gated local Project2Job context."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    resolve = commands.add_parser("resolve")
    add_context_arguments(resolve)
    resolve.add_argument(
        "--mode", choices=("normal", "refresh", "fresh"), default="normal"
    )

    save = commands.add_parser("save-run")
    add_context_arguments(save)
    save.add_argument("--skill", required=True)
    save.add_argument("--analysis", type=Path, required=True)
    save.add_argument("--consent", action="store_true")
    save.add_argument("--do-not-save", action="store_true")

    forget = commands.add_parser("forget")
    add_context_arguments(forget)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        home = registry_home()
        registry = load_registry(home)
        project, jd = snapshots(args, registry)
        if args.command == "resolve":
            print(json.dumps(resolve_context(registry, project, jd, args.mode), indent=2))
            return
        if args.command == "forget":
            updated, removed = remove_selected(registry, project, jd)
            if any(removed.values()):
                atomic_write(home / REGISTRY_FILE, updated)
            print(json.dumps({"forgotten": removed}, indent=2))
            return
        analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
        if args.do_not_save:
            print(json.dumps({"saved": False, "reason": "do_not_save"}, indent=2))
            return
        updated, run = save_run(registry, project, jd, args.skill, analysis)
        ensure_consent(home, args.consent)
        atomic_write(home / REGISTRY_FILE, updated)
        print(
            json.dumps(
                {
                    "saved": True,
                    "project_version": run["project_version"],
                    "jd_version": run["jd_version"],
                },
                indent=2,
            )
        )
    except (RegistryError, json.JSONDecodeError, OSError) as error:
        raise SystemExit(f"Project2Job Context Registry error: {error}") from error


if __name__ == "__main__":
    main()
