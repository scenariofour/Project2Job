from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

TEXT_EXTENSIONS = {
    ".csv",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}
EVIDENCE_SURFACES = {
    "decisions": ("decision", "adr", "prd", "scope", "manifest"),
    "implementation": ("src", "app", "runtime", "schema", "tool"),
    "evaluation": ("test", "eval", "trace", "benchmark", "fixture"),
    "delivery": ("release", "changelog", "ci", "workflow"),
    "user_evidence": ("research", "feedback", "interview", "analytics", "metric"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_observation(root: Path, limit: int) -> dict:
    command = [
        "git",
        "-C",
        str(root),
        "log",
        f"-{limit}",
        "--date=short",
        "--format=%H%x09%ad%x09%an%x09%s",
        "--",
        ".",
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return {"available": False, "recent_commits": []}

    commits = []
    for line in result.stdout.splitlines():
        commit, date, author, subject = line.split("\t", 3)
        commits.append(
            {
                "commit": commit,
                "date": date,
                "author": author,
                "subject": subject,
            }
        )
    return {"available": True, "recent_commits": commits}


def evidence_surfaces(relative_path: str) -> list[str]:
    lowered = relative_path.lower()
    return [
        surface
        for surface, markers in EVIDENCE_SURFACES.items()
        if any(marker in lowered for marker in markers)
    ]


def inventory(
    root: Path,
    git_limit: int = 20,
    cached_files: dict[str, dict] | None = None,
) -> dict:
    resolved = root.resolve()
    files = []
    duplicates: dict[str, list[str]] = {}
    cached_files = cached_files or {}
    for path in sorted(resolved.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        relative = str(path.relative_to(resolved))
        stat = path.stat()
        cached = cached_files.get(relative, {})
        if (
            cached.get("size_bytes") == stat.st_size
            and cached.get("mtime_ns") == stat.st_mtime_ns
            and cached.get("ctime_ns") == stat.st_ctime_ns
            and cached.get("fingerprint")
        ):
            digest = cached["fingerprint"]
        else:
            digest = sha256(path)
        duplicates.setdefault(digest, []).append(relative)
        files.append(
            {
                "path": relative,
                "suffix": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
                "ctime_ns": stat.st_ctime_ns,
                "is_text_candidate": path.suffix.lower() in TEXT_EXTENSIONS,
                "sha256": digest,
                "evidence_surfaces": evidence_surfaces(relative),
            }
        )
    return {
        "root": str(resolved),
        "file_count": len(files),
        "total_bytes": sum(item["size_bytes"] for item in files),
        "duplicate_groups": [
            paths for paths in duplicates.values() if len(paths) > 1
        ],
        "files": files,
        "git": git_observation(resolved, git_limit),
        "notice": (
            "Inventory and Git metadata are discovery leads, not proof of "
            "execution, outcome, or personal ownership."
        ),
    }


def summary(full: dict, max_candidates: int) -> dict:
    candidates: dict[str, list[str]] = {
        surface: [] for surface in EVIDENCE_SURFACES
    }
    for item in full["files"]:
        for surface in item["evidence_surfaces"]:
            if len(candidates[surface]) < max_candidates:
                candidates[surface].append(item["path"])
    commits = [
        {
            "commit": item["commit"],
            "date": item["date"],
            "subject": item["subject"],
        }
        for item in full["git"]["recent_commits"]
    ]
    return {
        "root": full["root"],
        "file_count": full["file_count"],
        "total_bytes": full["total_bytes"],
        "duplicate_group_count": len(full["duplicate_groups"]),
        "evidence_candidates": candidates,
        "git": {
            "available": full["git"]["available"],
            "recent_commits": commits,
        },
        "notice": full["notice"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a read-only Project2Job evidence inventory."
    )
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--git-limit", type=int, default=20)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--max-candidates", type=int, default=5)
    args = parser.parse_args()
    target = Path(args.root)
    if not target.exists():
        raise SystemExit(f"Path does not exist: {target}")
    result = inventory(target, max(0, args.git_limit))
    if args.summary:
        result = summary(result, max(1, args.max_candidates))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
