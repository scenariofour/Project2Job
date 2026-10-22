from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from source_resolution import (  # noqa: E402
    parse_source_arguments,
    resolve_refs,
    summarize,
)

SCHEMAS = {
    "application_pack": "application_pack.schema.json",
    "company_intelligence_profile": "company_intelligence_profile.schema.json",
    "intake_result": "intake_result.schema.json",
    "jd_demand_map": "jd_demand_map.schema.json",
    "project_evidence_profile": "project_evidence_profile.schema.json",
}


def schema_root() -> Path:
    installed = Path(__file__).resolve().parents[1] / "references" / "canonical" / "schemas"
    if installed.is_dir():
        return installed
    repository = Path(__file__).resolve().parents[3] / "schemas"
    if repository.is_dir():
        return repository
    raise RuntimeError("Canonical schemas are unavailable; reinstall the Skill suite.")


def validate(instance: object, schema_name: str) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError as exc:
        raise RuntimeError(
            "Full output validation requires jsonschema>=4; "
            "install the repository's dev extra or jsonschema directly."
        ) from exc

    root = schema_root()
    resources = []
    for path in sorted(root.glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        if "$id" in schema:
            resources.append(Resource.from_contents(schema))
    registry = Registry().with_resources(
        [(resource.id(), resource) for resource in resources]
    )
    schema = json.loads((root / SCHEMAS[schema_name]).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, registry=registry)
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in sorted(validator.iter_errors(instance), key=str)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a Project2Job canonical JSON output instance."
    )
    parser.add_argument("output", type=Path)
    parser.add_argument("--schema", choices=sorted(SCHEMAS), required=True)
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="[SOURCE_ID=]PATH",
        help=(
            "A permitted source file. Repeat once per source to also resolve "
            "every citation against real text before export."
        ),
    )
    args = parser.parse_args()
    try:
        instance = json.loads(args.output.read_text(encoding="utf-8"))
        errors = validate(instance, args.schema)
        resolution = (
            summarize(resolve_refs(instance, parse_source_arguments(args.source)))
            if args.source
            else None
        )
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        raise SystemExit(2) from exc

    report = {"valid": not errors, "errors": errors}
    if resolution is not None:
        # Schema validity and citation resolution are separate gates: an output
        # can be perfectly shaped and still cite a blank line.
        report["source_resolution"] = resolution
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if errors or (resolution is not None and not resolution["all_resolve"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
