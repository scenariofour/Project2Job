from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def compare(stateful_path: Path, project: Path, jd_file: Path) -> dict:
    """Compare an observed selective run with an observed fresh host replay."""
    stateful = json.loads(stateful_path.read_text(encoding="utf-8"))
    expected = set(stateful["trace"]["affected_outputs"])
    seed = {
        "report": {
            "project_name": stateful["project"]["name"],
            "jd_label": stateful["jd"]["label"],
        },
        "state": stateful["state"],
    }

    with tempfile.TemporaryDirectory(prefix="p2j-fresh-comparison-") as directory:
        temporary = Path(directory)
        seed_path = temporary / "seed.json"
        seed_path.write_text(json.dumps(seed), encoding="utf-8")
        environment = os.environ.copy()
        environment["P2J_HOME"] = str(temporary / "p2j-home")
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "skill" / "p2j" / "scripts" / "stateful_agent.py"),
                "--project",
                str(project),
                "--jd-file",
                str(jd_file),
                "--seed",
                str(seed_path),
                "--mode",
                "fresh",
                "--do-not-save",
            ],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        fresh = json.loads(completed.stdout)

    expected_values = {
        output_id: stateful["state"]["outputs"][output_id]
        for output_id in expected
    }
    preserved = set(stateful["trace"]["preserved_outputs"])
    fresh_outputs = fresh["state"]["outputs"]
    fresh_metrics = deepcopy(fresh["metrics"])
    fresh_metrics["expected_outputs_correctly_updated"] = sum(
        fresh_outputs.get(output_id) == output
        for output_id, output in expected_values.items()
    )
    fresh_metrics["unrelated_outputs_incorrectly_changed"] = sum(
        fresh_outputs.get(output_id)
        != stateful["state"]["outputs"].get(output_id)
        for output_id in preserved
    )
    classifications = sorted(
        {
            item["artifact_type"]
            for item in stateful["state"]["evidence"].values()
            if item.get("artifact_type")
        }
    )

    return {
        "comparison_type": "observed_integrated_host_replay",
        "changed_artifact_classification": classifications,
        "expected_changed_outputs": sorted(expected),
        "expected_preserved_outputs": sorted(preserved),
        "stateful_agent_update": stateful["metrics"],
        "fresh_skill_rerun": fresh_metrics,
        "correctness": {
            "stateful_expected_values_present": len(expected_values),
            "fresh_expected_values_present": sum(
                fresh_outputs.get(output_id) == output
                for output_id, output in expected_values.items()
            ),
            "stateful_before_values_recorded": sum(
                "before" in stateful["state"]["outputs"][output_id]
                for output_id in expected
            ),
        },
        "trace_clarity": {
            "stateful_detected_change": stateful["trace"]["detected_change"],
            "stateful_stop_reason": stateful["trace"]["stop_reason"],
            "fresh_detected_change": fresh["trace"]["detected_change"],
            "fresh_stop_reason": fresh["trace"]["stop_reason"],
        },
        "limitations": [
            "Both runs used deterministic orchestration and host-supplied analysis; no live model planner was called.",
            "The fresh run replayed the final source-grounded host analysis to measure full-read and regeneration cost.",
            "The controlled summary surfaces an existing fact and is not counted as a new Project capability or executed result.",
            "Token usage is unavailable because no model call was made.",
            "This is repository dogfood, not target-user validation.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stateful-run", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--jd-file", type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / "docs" / "dogfood" / "STATEFUL_AGENT_V0_COMPARISON.json"
    output.write_text(
        json.dumps(
            compare(args.stateful_run, args.project, args.jd_file),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
