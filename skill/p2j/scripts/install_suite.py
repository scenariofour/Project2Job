from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

from validate_suite import SKILLS, validate

CANONICAL_FILES = (
    "ACTIVE_SCOPE.md",
    "GLOSSARY.md",
    "docs/03_AI_PM_ROLE_STANDARD.md",
    "docs/07_SHARED_EVIDENCE_AND_OUTPUT_STANDARD.md",
    "docs/09_TOKEN_CONTEXT_AND_COST.md",
    "docs/11_SAFETY_PRIVACY_AND_HITL.md",
    "references/role_profiles/ai_pm_early_career.v0.1.0.json",
    "references/shared_contract.v1.json",
    "schemas/application_pack.schema.json",
    "schemas/context_registry.schema.json",
    "schemas/gold_case.schema.json",
    "schemas/interview_context.schema.json",
    "schemas/intake_result.schema.json",
    "schemas/jd_intake.schema.json",
    "schemas/project_evidence.schema.json",
    "schemas/role_profile.schema.json",
    "lab/evals/shared_foundation_cases.v0.1.0.jsonl",
)


def repository_root() -> Path:
    candidate = Path(__file__).resolve().parents[3]
    if not (candidate / "PROJECT_MANIFEST.json").is_file():
        raise RuntimeError("Run the installer from a Project2Job source checkout.")
    return candidate


def install_suite(destination: Path, replace: bool = False) -> list[Path]:
    repo = repository_root()
    source_root = repo / "skill"
    destination.mkdir(parents=True, exist_ok=True)
    installed: list[Path] = []
    for name in SKILLS:
        source = source_root / name
        target = destination / name
        if target.exists():
            if not replace:
                raise FileExistsError(
                    f"{target} exists; rerun with --replace after reviewing the target."
                )
            shutil.rmtree(target)
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.py[co]"),
        )
        installed.append(target)

    canonical_root = destination / "p2j" / "references" / "canonical"
    for relative in CANONICAL_FILES:
        source = repo / relative
        target = canonical_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    errors = validate(destination, require_canonical=True)
    if errors:
        raise RuntimeError("Installed suite failed validation: " + "; ".join(errors))
    return installed


def build_archive(archive: Path) -> Path:
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary) / "skills"
        install_suite(staging)
        with zipfile.ZipFile(
            archive, "w", compression=zipfile.ZIP_DEFLATED
        ) as bundle:
            for path in sorted(staging.rglob("*")):
                if path.is_file():
                    bundle.write(
                        path,
                        Path("project2job-skill-suite") / path.relative_to(staging),
                    )
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install or package the Project2Job host-native Skill Suite."
    )
    parser.add_argument("--dest", type=Path)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    if not args.dest and not args.archive:
        parser.error("provide --dest and/or --archive")
    if args.dest:
        installed = install_suite(args.dest.expanduser().resolve(), args.replace)
        print(f"Installed {len(installed)} Skills in {args.dest.expanduser().resolve()}")
    if args.archive:
        archive = build_archive(args.archive.expanduser().resolve())
        print(f"Built {archive}")


if __name__ == "__main__":
    main()
