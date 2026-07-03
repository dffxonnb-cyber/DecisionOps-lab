"""Run the full local verification workflow for DecisionOps Lab.

This script is a convenience runner for reviewers and for local development.
It rebuilds the default reports, runs the full scenario matrix, restores the
primary demonstration reports, and executes the test suite.

Usage:
    python scripts/run_full_verification.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def run_step(title: str, args: list[str]) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)
    print("$ " + " ".join(args))
    subprocess.run(args, cwd=ROOT_DIR, check=True)


def main() -> None:
    python = sys.executable

    steps = [
        ("Generate default strong_positive dataset", [python, "scripts/generate_dataset.py", "--scenario", "strong_positive"]),
        ("Run SQL pipeline", [python, "scripts/run_pipeline.py"]),
        ("Run data quality checks", [python, "scripts/run_quality_checks.py"]),
        ("Run experiment analysis", [python, "scripts/run_experiment_analysis.py"]),
        ("Generate decision memo", [python, "scripts/generate_decision_memo.py"]),
        ("Generate reviewer report", [python, "scripts/generate_review_report.py"]),
        ("Run scenario matrix", [python, "scripts/run_scenario_matrix.py"]),
        ("Run pytest", [python, "-m", "pytest"]),
    ]

    for title, args in steps:
        run_step(title, args)

    print("\n" + "=" * 72)
    print("Full verification complete")
    print("=" * 72)
    print("Artifacts:")
    print("- reports/quality_report.json")
    print("- reports/experiment_result.json")
    print("- reports/decision_memo.md")
    print("- reports/review_report.html")
    print("- reports/scenario_matrix.json")
    print("- reports/scenario_matrix.md")


if __name__ == "__main__":
    main()
