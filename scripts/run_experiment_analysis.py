"""Analyze onboarding experiment results for DecisionOps Lab.

Outputs:
- reports/experiment_result.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "processed" / "decisionops.duckdb"
REPORTS_DIR = ROOT_DIR / "reports"
EXPERIMENT_RESULT_PATH = REPORTS_DIR / "experiment_result.json"


def pct(value: float) -> float:
    return round(float(value), 6)


def fetch_variant_summary(connection: duckdb.DuckDBPyConnection) -> dict[str, dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT
            variant,
            COUNT(*) AS users,
            SUM(activated_24h) AS activated_users,
            AVG(activated_24h) AS activation_rate,
            AVG(session_count) AS avg_sessions,
            AVG(avg_session_seconds) AS avg_session_seconds
        FROM int_experiment_user_metrics
        GROUP BY variant
        ORDER BY variant
        """
    ).fetchall()

    return {
        row[0]: {
            "users": int(row[1]),
            "activated_users": int(row[2]),
            "activation_rate": pct(row[3]),
            "avg_sessions": pct(row[4]),
            "avg_session_seconds": pct(row[5]),
        }
        for row in rows
    }


def fetch_segment_summary(connection: duckdb.DuckDBPyConnection, dimension: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        f"""
        SELECT
            {dimension} AS segment,
            variant,
            COUNT(*) AS users,
            SUM(activated_24h) AS activated_users,
            AVG(activated_24h) AS activation_rate
        FROM int_experiment_user_metrics
        GROUP BY {dimension}, variant
        ORDER BY {dimension}, variant
        """
    ).fetchall()

    grouped: dict[str, dict[str, Any]] = {}
    for segment, variant, users, activated_users, activation_rate in rows:
        grouped.setdefault(str(segment), {})[str(variant)] = {
            "users": int(users),
            "activated_users": int(activated_users),
            "activation_rate": pct(activation_rate),
        }

    output: list[dict[str, Any]] = []
    for segment, variants in grouped.items():
        if "A" not in variants or "B" not in variants:
            continue
        rate_a = variants["A"]["activation_rate"]
        rate_b = variants["B"]["activation_rate"]
        output.append(
            {
                "dimension": dimension,
                "segment": segment,
                "variant_a": variants["A"],
                "variant_b": variants["B"],
                "absolute_lift": pct(rate_b - rate_a),
                "relative_lift": pct((rate_b - rate_a) / rate_a) if rate_a else None,
            }
        )

    return output


def analyze() -> dict[str, Any]:
    if not DB_PATH.exists():
        raise FileNotFoundError("DuckDB file not found. Run `python scripts/run_pipeline.py` first.")

    with duckdb.connect(str(DB_PATH)) as connection:
        summary = fetch_variant_summary(connection)
        if "A" not in summary or "B" not in summary:
            raise ValueError("Experiment result requires both Variant A and Variant B.")

        a = summary["A"]
        b = summary["B"]

        counts = [b["activated_users"], a["activated_users"]]
        nobs = [b["users"], a["users"]]
        z_stat, p_value = proportions_ztest(count=counts, nobs=nobs, alternative="larger")

        ci_low, ci_high = confint_proportions_2indep(
            count1=b["activated_users"],
            nobs1=b["users"],
            count2=a["activated_users"],
            nobs2=a["users"],
            method="wald",
        )

        absolute_lift = b["activation_rate"] - a["activation_rate"]
        relative_lift = absolute_lift / a["activation_rate"] if a["activation_rate"] else None

        segments = []
        for dimension in ["acquisition_channel", "device_type", "age_group"]:
            segments.extend(fetch_segment_summary(connection, dimension))

    suggested_decision = "Ship" if absolute_lift > 0 and p_value < 0.05 else "Retest" if absolute_lift > 0 else "Hold"

    return {
        "experiment_name": "onboarding_v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "primary_metric": "activation_rate",
        "variant_a": a,
        "variant_b": b,
        "absolute_lift": pct(absolute_lift),
        "relative_lift": pct(relative_lift) if relative_lift is not None else None,
        "z_stat": pct(z_stat),
        "p_value": pct(p_value),
        "confidence_interval_absolute_lift": {
            "low": pct(ci_low),
            "high": pct(ci_high),
        },
        "segment_diagnostics": segments,
        "suggested_decision": suggested_decision,
        "claim_boundary": "Synthetic data only. This result demonstrates the experiment workflow, not real product performance.",
    }


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    result = analyze()
    EXPERIMENT_RESULT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nExperiment analysis")
    print("-" * 56)
    print(f"Variant A activation: {result['variant_a']['activation_rate']:.2%}")
    print(f"Variant B activation: {result['variant_b']['activation_rate']:.2%}")
    print(f"Absolute lift:        {result['absolute_lift']:.2%}")
    print(f"Relative lift:        {result['relative_lift']:.2%}")
    print(f"p-value:              {result['p_value']:.4f}")
    print(f"Suggested decision:   {result['suggested_decision']}")
    print("-" * 56)
    print(f"Report: {EXPERIMENT_RESULT_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
