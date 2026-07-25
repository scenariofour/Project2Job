from __future__ import annotations

import hashlib
from pathlib import Path


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def changed_paths(previous: dict[str, str], current: dict[str, str]) -> dict[str, list[str]]:
    previous_keys = set(previous)
    current_keys = set(current)
    return {
        "added": sorted(current_keys - previous_keys),
        "removed": sorted(previous_keys - current_keys),
        "changed": sorted(
            key for key in previous_keys & current_keys
            if previous[key] != current[key]
        ),
        "unchanged": sorted(
            key for key in previous_keys & current_keys
            if previous[key] == current[key]
        ),
    }
