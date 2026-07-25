from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx",
    ".json", ".yaml", ".yml", ".csv", ".toml"
}
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build"}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def inventory(root: Path) -> dict:
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        stat = path.stat()
        files.append({
            "path": str(path.relative_to(root)),
            "suffix": path.suffix.lower(),
            "size_bytes": stat.st_size,
            "is_text_candidate": path.suffix.lower() in TEXT_EXTENSIONS,
            "sha256": sha256(path),
        })
    return {
        "root": str(root.resolve()),
        "file_count": len(files),
        "files": files,
    }

if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    if not target.exists():
        raise SystemExit(f"Path does not exist: {target}")
    print(json.dumps(inventory(target), indent=2))
