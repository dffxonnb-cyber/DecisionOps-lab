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
from statsmodels.stats.proportion import confint_proportions_2indep, proportions_ztest


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "processed" / "decisionops.duckdb"
REPORTS_DIR = ROOT_DIR / "reports"
EXPERIMENT_RESULT_PATH = REPORTS_DIR / "experiment_result.json"


D7_REVISIT_WARN_THRESHOLD = -0.01
REFUND_RATE_WARN_THRESHOLD = 0.01
SESSION_DURATION_RELATIVE_WARN_THRESHOLD = -0.05


def pct(value: float) -> float:
    return round(float(value), 6)


def fetch_scenario(connection: duckdb.DuckDBPyConnection) -> str:
    value = connection.execute("SELECT MIN(scenario) FROM int_experiment_user_metrics").fetchone()[0]
    return str(value or "unknown")


def fetch_variant_summary(connection: duckdb.DuckDBPyConnection) -> dict[str, dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT
            variant,
            COUNT(*) AS users,
            SUM(activated_24h) AS activated_users,
            AVG(activated_24h) AS activation_rate,
            AVG(revisited_d1) AS d1_revisit_rate,
            AVG(revisited_d3) AS d3_revisit_rate,
            AVG(revisited_d7) AS d7_revisit_rate,
            AVG(session_count) AS avg_sessions,
            AVG(avg_session_seconds) AS avg_session_seconds,
            SUM(trial_started) AS trial_users,
            AVG(trial_started) AS trial_start_rate,
            SUM(paid_converted) AS paid_users,
            AVG(paid_converted) AS paid_conversion_rate,
            SUM(refunded) AS refunded_users,
            AVG(refunded) AS refund_rate,
            SUM(paid_amount) AS total_paid_amount,
            SUM(refund_amount) AS total_refund_amount
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
            "d1_revisit_rate": pct(row[4]),
            "d3_revisit_rate": pct(row[5]),
            "d7_revisit_rate": pct(row[6]),
            "avg_sessions": pct(row[7]),
            "avg_session_seconds": pct(row[8]),
            "trial_users": int(row[9]),
            "trial_start_rate": pct(row[10]),
            "paid_users": int(row[11]),
            "paid_conversion_rate": pct(row[12]),
            "refunded_users": int(row[13]),
            "refund_rate": pct(row[14]),
            "total_paid_amount": int(row[15] or 0),
            "total_refund_amount": int(row[16] or 0),
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
            AVG(activated_24h) AS activation_rate,
            AVG(revisited_d7) AS d7_revisit_rate
        FROM int_experiment_user_metrics
        GROUP BY {dimension}, variant
        ORDER BY {dimension}, variant
        """
    ).fetchall()

    grouped: dict[str, dict[str, Any]] = {}
    for segment, variant, users, activated_users, activation_rate, d7_revisit_rate in rows:
        grouped.setdefault(str(segment), {})[str(variant)] = {
            "users": int(users),
            "activated_users": int(activated_users),
            "activation_rate": pct(activation_rate),
            "d7_revisit_rate": pct(d7_revisit_rate),
        }

    output: list[dict[str, Any]] = []
    for segment, variants in grouped.items():
        if "A" not in variants or "B" not in variants:
            continue
        rate_a = variants["A"]["activation_rate"]
        rate_b = variants["B"]["activation_rate"]
        d7_a = variants["A"]["d7_revisit_rate"]
        d7_b = variants["B"]["d7_revisit_rate"]
        output.append(
            {
                "dimension": dimension,
                "segment": segment,
                "variant_a": variants["A"],
                "variant_b": variants["B"],
                "absolute_lift": pct(rate_b - rate_a),
                "relative_lift": pct((rate_b - rate_a) / rate_a) if rate_a else None,
                "d7_revisit_delta": pct(d7_b - d7_a),
            }
        )

    return output


def build_guardrails(a: dict[str, Any], b: dict[str, Any]) -> dict[str, dict[str, Any]]:
    d7_revisit_delta = b["d7_revisit_rate"] - a["d7_revisit_rate"]
    refund_rate_delta = b["refund_rate"] - a["refund_rate"]
    session_seconds_delta = b["avg_session_seconds"] - a["avg_session_seconds"]
    session_seconds_relative_delta = session_seconds_delta / a["avg_session_seconds"] if a["avg_session_seconds"] else None

    return {
        "d7_revisit": {
            "metric": "d7_revisit_rate",
            "variant_a": a["d7_revisit_rate"],
            "variant_b": b["d7_revisit_rate"],
            "delta": pct(d7_revisit_delta),
            "status": "PASS" if d7_revisit_delta >= D7_REVISIT_WARN_THRESHOLD else "WARN",
            "threshold": "WARN if Variant B delta < -1 percentage point",
        },
        "refund_rate": {
            "metric": "refund_rate",
            "variant_a": a["refund_rate"],
            "variant_b": b["refund_rate"],
            "delta": pct(refund_rate_delta),
            "status": "PASS" if refund_rate_delta <= REFUND_RATE_WARN_THRESHOLD else "WARN",
            "threshold": "WARN if Variant B delta > +1 percentage point",
        },
        "session_duration": {
            "metric": "avg_session_seconds",
            "variant_a": a["avg_session_seconds"],
            "variant_b": b["avg_session_seconds"],
            "delta": pct(session_seconds_delta),
            "relative_delta": pct(session_seconds_relative_delta) if session_seconds_relative_delta is not None else None,
            "status": "PASS"
            if session_seconds_relative_delta is None
            or session_seconds_relative_delta >= SESSION_DURATION_RELATIVE_WARN_THRESHOLD
            else "WARN",
            "threshold": "WARN if Variant B average session duration drops by more than 5%",
        },
    }


def summarize_guardrails(guardrails: dict[str, dict[str, Any]]) -> str:
    return "WARN" if any(item["status"] == "WARN" for item in guardrails.values()) else "PASS"


def analyze() -> dict[str, Any]:
    if not DB_PATH.exists():
        raise FileNotFoundError("DuckDB file not found. Run `python scripts/run_pipeline.py` first.")

    with duckdb.connect(str(DB_PATH)) as connection:
        scenario = fetch_scenario(connection)
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
        d7_revisit_delta = b["d7_revisit_rate"] - a["d7_revisit_rate"]
        refund_rate_delta = b["refund_rate"] - a["refund_rate"]
        avg_session_seconds_delta = b["avg_session_seconds"] - a["avg_session_seconds"]
        avg_session_seconds_relative_delta = (
            avg_session_seconds_delta / a["avg_session_seconds"] if a["avg_session_seconds"] else None
        )

        guardrails = build_guardrails(a, b)
        guardrail_status = summarize_guardrails(guardrails)

        segments = []
        for dimension in ["acquisition_channel", "device_type", "age_group"]:
            segments.extend(fetch_segment_summary(connection, dimension))

    if absolute_lift > 0 and p_value < 0.05 and guardrail_status == "PASS":
        suggested_decision = "Ship"
    elif absolute_lift > 0:
        suggested_decision = "Retest"
    else:
        suggested_decision = "Hold"

    return {
        "scenario": scenario,
        "experiment_name": "onboarding_v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "primary_metric": "activation_rate",
        "guardrail_metric": "multi_guardrail",
        "variant_a": a,
        "variant_b": b,
        "absolute_lift": pct(absolute_lift),
        "relative_lift": pct(relative_lift) if relative_lift is not None else None,
        "d7_revisit_delta": pct(d7_revisit_delta),
        "refund_rate_delta": pct(refund_rate_delta),
        "avg_session_seconds_delta": pct(avg_session_seconds_delta),
        "avg_session_seconds_relative_delta": pct(avg_session_seconds_relative_delta)
        if avg_session_seconds_relative_delta is not None
        else None,
        "guardrails": guardrails,
        "guardrail_status": guardrail_status,
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
    print(f"Scenario:             {result['scenario']}")
    print(f"Variant A activation: {result['variant_a']['activation_rate']:.2%}")
    print(f"Variant B activation: {result['variant_b']['activation_rate']:.2%}")
    print(f"Absolute lift:        {result['absolute_lift']:.2%}")
    print(f"Relative lift:        {result['relative_lift']:.2%}")
    print(f"D7 revisit delta:     {result['d7_revisit_delta']:.2%}")
    print(f"Refund rate delta:    {result['refund_rate_delta']:.2%}")
    print(f"Session seconds delta:{result['avg_session_seconds_delta']:.2f}")
    print(f"Guardrail status:     {result['guardrail_status']}")
    print(f"p-value:              {result['p_value']:.4f}")
    print(f"Suggested decision:   {result['suggested_decision']}")
    print("-" * 56)
    print(f"Report: {EXPERIMENT_RESULT_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
