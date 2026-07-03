"""Run data quality checks for DecisionOps Lab.

Outputs:
- reports/quality_report.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "processed" / "decisionops.duckdb"
REPORTS_DIR = ROOT_DIR / "reports"
QUALITY_REPORT_PATH = REPORTS_DIR / "quality_report.json"


@dataclass
class CheckResult:
    name: str
    status: str
    observed: Any
    message: str


def run_scalar(connection: duckdb.DuckDBPyConnection, query: str) -> Any:
    return connection.execute(query).fetchone()[0]


def add_check(results: list[CheckResult], name: str, status: str, observed: Any, message: str) -> None:
    results.append(CheckResult(name=name, status=status, observed=observed, message=message))


def check_table_row_count(connection: duckdb.DuckDBPyConnection, results: list[CheckResult], table: str) -> None:
    count = run_scalar(connection, f"SELECT COUNT(*) FROM {table}")
    status = "PASS" if count > 0 else "FAIL"
    add_check(results, f"row_count_{table}", status, count, f"{table} has {count:,} rows")


def check_unique_key(connection: duckdb.DuckDBPyConnection, results: list[CheckResult], table: str, key: str) -> None:
    duplicates = run_scalar(
        connection,
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT {key}, COUNT(*) AS row_count
            FROM {table}
            GROUP BY {key}
            HAVING COUNT(*) > 1
        )
        """,
    )
    status = "PASS" if duplicates == 0 else "FAIL"
    add_check(results, f"unique_{table}_{key}", status, duplicates, f"{table}.{key} duplicate groups: {duplicates}")


def check_nulls(connection: duckdb.DuckDBPyConnection, results: list[CheckResult], table: str, column: str) -> None:
    null_count = run_scalar(connection, f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
    status = "PASS" if null_count == 0 else "FAIL"
    add_check(results, f"null_{table}_{column}", status, null_count, f"{table}.{column} null count: {null_count}")


def check_allowed_values(
    connection: duckdb.DuckDBPyConnection,
    results: list[CheckResult],
    table: str,
    column: str,
    allowed_values: list[str],
) -> None:
    quoted = ", ".join(f"'{value}'" for value in allowed_values)
    invalid_count = run_scalar(
        connection,
        f"SELECT COUNT(*) FROM {table} WHERE {column} NOT IN ({quoted})",
    )
    status = "PASS" if invalid_count == 0 else "FAIL"
    add_check(
        results,
        f"accepted_values_{table}_{column}",
        status,
        invalid_count,
        f"{table}.{column} invalid value count: {invalid_count}",
    )


def check_relation(
    connection: duckdb.DuckDBPyConnection,
    results: list[CheckResult],
    child_table: str,
    parent_table: str,
    key: str,
) -> None:
    missing = run_scalar(
        connection,
        f"""
        SELECT COUNT(*)
        FROM {child_table} c
        LEFT JOIN {parent_table} p
            ON c.{key} = p.{key}
        WHERE p.{key} IS NULL
        """,
    )
    status = "PASS" if missing == 0 else "FAIL"
    add_check(
        results,
        f"relation_{child_table}_{parent_table}_{key}",
        status,
        missing,
        f"{child_table}.{key} values missing from {parent_table}: {missing}",
    )


def check_experiment_balance(connection: duckdb.DuckDBPyConnection, results: list[CheckResult]) -> None:
    rows = connection.execute(
        """
        SELECT variant, COUNT(*) AS users
        FROM stg_experiments
        GROUP BY variant
        ORDER BY variant
        """
    ).fetchall()
    counts = {variant: count for variant, count in rows}
    total = sum(counts.values())
    b_share = counts.get("B", 0) / total if total else 0
    status = "PASS" if 0.45 <= b_share <= 0.55 else "WARN"
    add_check(
        results,
        "experiment_balance_onboarding_v2",
        status,
        {"counts": counts, "b_share": round(b_share, 4)},
        f"Variant B share is {b_share:.2%}",
    )


def check_metric_range(connection: duckdb.DuckDBPyConnection, results: list[CheckResult]) -> None:
    activation_rate = run_scalar(connection, "SELECT AVG(activated_24h) FROM int_user_activation")
    status = "PASS" if 0 <= activation_rate <= 1 else "FAIL"
    add_check(
        results,
        "metric_range_activation_rate",
        status,
        round(float(activation_rate), 4),
        f"Activation rate is {activation_rate:.2%}",
    )


def build_report(results: list[CheckResult]) -> dict[str, Any]:
    fail_count = sum(1 for result in results if result.status == "FAIL")
    warn_count = sum(1 for result in results if result.status == "WARN")
    pass_count = sum(1 for result in results if result.status == "PASS")

    if fail_count > 0:
        status = "FAIL"
    elif warn_count > 0:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "pass": pass_count,
            "warn": warn_count,
            "fail": fail_count,
            "total": len(results),
        },
        "checks": [asdict(result) for result in results],
    }


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError("DuckDB file not found. Run `python scripts/run_pipeline.py` first.")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results: list[CheckResult] = []

    with duckdb.connect(str(DB_PATH)) as connection:
        for table in [
            "raw_users",
            "raw_events",
            "raw_sessions",
            "raw_experiments",
            "raw_payments",
            "stg_users",
            "stg_events",
            "int_user_activation",
        ]:
            check_table_row_count(connection, results, table)

        check_unique_key(connection, results, "raw_users", "user_id")
        check_unique_key(connection, results, "raw_events", "event_id")
        check_unique_key(connection, results, "raw_sessions", "session_id")

        check_nulls(connection, results, "raw_users", "user_id")
        check_nulls(connection, results, "raw_events", "event_id")
        check_nulls(connection, results, "raw_events", "user_id")
        check_nulls(connection, results, "raw_events", "event_name")
        check_nulls(connection, results, "raw_experiments", "variant")

        check_allowed_values(connection, results, "raw_experiments", "variant", ["A", "B"])
        check_allowed_values(connection, results, "raw_users", "device_type", ["mobile", "desktop", "tablet"])
        check_allowed_values(connection, results, "raw_users", "acquisition_channel", ["organic", "paid_search", "social", "referral"])

        check_relation(connection, results, "raw_events", "raw_users", "user_id")
        check_relation(connection, results, "raw_experiments", "raw_users", "user_id")

        check_experiment_balance(connection, results)
        check_metric_range(connection, results)

    report = build_report(results)
    QUALITY_REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nData quality report")
    print("-" * 48)
    print(f"status: {report['status']}")
    print(f"pass:   {report['summary']['pass']}")
    print(f"warn:   {report['summary']['warn']}")
    print(f"fail:   {report['summary']['fail']}")
    print("-" * 48)
    print(f"Report: {QUALITY_REPORT_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
