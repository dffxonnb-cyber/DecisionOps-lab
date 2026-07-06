"""Run multiple synthetic experiment scenarios and summarize decision outcomes.

Outputs:
- reports/scenario_matrix.json
- reports/scenario_matrix.md

After creating the matrix, this script restores the default strong_positive reports.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"
SCENARIOS = ["strong_positive", "guardrail_risk", "weak_evidence", "neutral", "quality_failure"]


def run_command(args: list[str]) -> None:
    print("$ " + " ".join(args))
    subprocess.run(args, cwd=ROOT_DIR, check=True)


def choose_decision(quality_status: str, experiment: dict[str, Any]) -> str:
    if quality_status == "FAIL":
        return "Investigate"
    return str(experiment.get("suggested_decision", "Unknown"))


def run_pipeline_for_scenario(scenario: str) -> dict[str, Any]:
    run_command([sys.executable, "scripts/generate_dataset.py", "--scenario", scenario])
    run_command([sys.executable, "scripts/run_pipeline.py"])
    run_command([sys.executable, "scripts/run_quality_checks.py"])
    run_command([sys.executable, "scripts/run_experiment_analysis.py"])
    run_command([sys.executable, "scripts/generate_decision_memo.py"])

    experiment = json.loads((REPORTS_DIR / "experiment_result.json").read_text(encoding="utf-8"))
    quality = json.loads((REPORTS_DIR / "quality_report.json").read_text(encoding="utf-8"))
    quality_status = str(quality.get("status"))
    guardrails = experiment.get("guardrails", {})

    return {
        "scenario": scenario,
        "quality_status": quality_status,
        "decision": choose_decision(quality_status, experiment),
        "experiment_suggested_decision": experiment.get("suggested_decision"),
        "variant_a_activation": experiment.get("variant_a", {}).get("activation_rate"),
        "variant_b_activation": experiment.get("variant_b", {}).get("activation_rate"),
        "absolute_lift": experiment.get("absolute_lift"),
        "relative_lift": experiment.get("relative_lift"),
        "p_value": experiment.get("p_value"),
        "d7_revisit_delta": experiment.get("d7_revisit_delta"),
        "refund_rate_delta": experiment.get("refund_rate_delta"),
        "session_duration_status": guardrails.get("session_duration", {}).get("status"),
        "guardrail_status": experiment.get("guardrail_status"),
    }


def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def build_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Scenario Matrix",
        "",
        "DecisionOps Lab runs the same pipeline across multiple synthetic experiment scenarios.",
        "",
        "| Scenario | Quality | A Activation | B Activation | Lift | D7 Delta | Refund Delta | Session Guardrail | Overall Guardrail | Decision |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]

    for row in rows:
        lines.append(
            "| {scenario} | {quality} | {a} | {b} | {lift} | {d7} | {refund} | {session} | {guardrail} | {decision} |".format(
                scenario=row["scenario"],
                quality=row["quality_status"],
                a=fmt_pct(row["variant_a_activation"]),
                b=fmt_pct(row["variant_b_activation"]),
                lift=fmt_pct(row["absolute_lift"]),
                d7=fmt_pct(row["d7_revisit_delta"]),
                refund=fmt_pct(row["refund_rate_delta"]),
                session=row["session_duration_status"],
                guardrail=row["guardrail_status"],
                decision=row["decision"],
            )
        )

    lines.extend(
        [
            "",
            "## Scenario Purpose",
            "",
            "- `strong_positive`: primary metric improves and guardrails remain stable.",
            "- `guardrail_risk`: primary metric improves but D7 revisit weakens.",
            "- `weak_evidence`: primary metric improves only slightly.",
            "- `neutral`: primary metric does not improve meaningfully.",
            "- `quality_failure`: raw experiment data contains invalid variant values, so quality checks fail.",
            "",
        ]
    )
    return "\n".join(lines)


def restore_default_reports() -> None:
    run_command([sys.executable, "scripts/generate_dataset.py", "--scenario", "strong_positive"])
    run_command([sys.executable, "scripts/run_pipeline.py"])
    run_command([sys.executable, "scripts/run_quality_checks.py"])
    run_command([sys.executable, "scripts/run_experiment_analysis.py"])
    run_command([sys.executable, "scripts/generate_decision_memo.py"])
    run_command([sys.executable, "scripts/generate_review_report.py"])


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = [run_pipeline_for_scenario(scenario) for scenario in SCENARIOS]

    (REPORTS_DIR / "scenario_matrix.json").write_text(
        json.dumps({"scenarios": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (REPORTS_DIR / "scenario_matrix.md").write_text(build_markdown(rows), encoding="utf-8")

    restore_default_reports()

    print("\nScenario matrix")
    print("-" * 48)
    for row in rows:
        print(
            f"{row['scenario']:<16} {row['decision']:<12} "
            f"quality={row['quality_status']:<4} "
            f"lift={fmt_pct(row['absolute_lift'])} "
            f"d7={fmt_pct(row['d7_revisit_delta'])} "
            f"refund={fmt_pct(row['refund_rate_delta'])} "
            f"guardrail={row['guardrail_status']}"
        )
    print("-" * 48)
    print("Report: reports/scenario_matrix.md")


if __name__ == "__main__":
    main()
