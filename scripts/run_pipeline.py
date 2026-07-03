"""Run the DecisionOps Lab SQL modeling pipeline.

This script loads generated raw CSV files into DuckDB, runs SQL models in
dependency order, and writes a local analytics database to
`data/processed/decisionops.duckdb`.
"""

from __future__ import annotations

from pathlib import Path

import duckdb


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DB_PATH = PROCESSED_DIR / "decisionops.duckdb"

RAW_FILES = {
    "raw_users": RAW_DIR / "raw_users.csv",
    "raw_events": RAW_DIR / "raw_events.csv",
    "raw_sessions": RAW_DIR / "raw_sessions.csv",
    "raw_experiments": RAW_DIR / "raw_experiments.csv",
    "raw_payments": RAW_DIR / "raw_payments.csv",
}

SQL_MODEL_ORDER = [
    "sql/staging/stg_users.sql",
    "sql/staging/stg_events.sql",
    "sql/staging/stg_sessions.sql",
    "sql/staging/stg_experiments.sql",
    "sql/staging/stg_payments.sql",
    "sql/intermediate/int_user_activation.sql",
    "sql/intermediate/int_user_retention.sql",
    "sql/intermediate/int_experiment_user_metrics.sql",
    "sql/intermediate/int_session_funnel.sql",
    "sql/marts/mart_experiment_result.sql",
    "sql/marts/mart_segment_performance.sql",
    "sql/marts/mart_retention_cohort.sql",
    "sql/marts/mart_decision_summary.sql",
]


def validate_raw_files() -> None:
    missing = [str(path.relative_to(ROOT_DIR)) for path in RAW_FILES.values() if not path.exists()]
    if missing:
        missing_text = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(
            "Missing raw CSV files. Run `python scripts/generate_dataset.py` first.\n"
            f"Missing files:\n{missing_text}"
        )


def load_raw_tables(connection: duckdb.DuckDBPyConnection) -> None:
    for table_name, csv_path in RAW_FILES.items():
        csv_posix = csv_path.as_posix()
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{csv_posix}', header = true);
            """
        )


def run_sql_models(connection: duckdb.DuckDBPyConnection) -> None:
    for relative_path in SQL_MODEL_ORDER:
        sql_path = ROOT_DIR / relative_path
        if not sql_path.exists():
            print(f"skip missing SQL model: {relative_path}")
            continue
        sql = sql_path.read_text(encoding="utf-8")
        connection.execute(sql)
        print(f"ran {relative_path}")


def print_table_counts(connection: duckdb.DuckDBPyConnection) -> None:
    tables = [row[0] for row in connection.execute("SHOW TABLES").fetchall()]
    print("\nBuilt DuckDB tables")
    print("-" * 56)
    for table in sorted(tables):
        count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:<36} {count:>10,} rows")
    print("-" * 56)
    print(f"Database: {DB_PATH.relative_to(ROOT_DIR)}")


def main() -> None:
    validate_raw_files()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    with duckdb.connect(str(DB_PATH)) as connection:
        load_raw_tables(connection)
        run_sql_models(connection)
        print_table_counts(connection)


if __name__ == "__main__":
    main()
