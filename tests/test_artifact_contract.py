from __future__ import annotations

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"
PROCESSED_DB = ROOT_DIR / "data" / "processed" / "decisionops.duckdb"


def test_processed_database_exists() -> None:
    assert PROCESSED_DB.exists(), "Expected data/processed/decisionops.duckdb to be generated."


def test_quality_report_passes() -> None:
    path = REPORTS_DIR / "quality_report.json"
    assert path.exists(), "Expected reports/quality_report.json to be generated."
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["status"] in {"PASS", "WARN"}
    assert report["summary"]["fail"] == 0


def test_experiment_result_has_expected_shape() -> None:
    path = REPORTS_DIR / "experiment_result.json"
    assert path.exists(), "Expected reports/experiment_result.json to be generated."
    result = json.loads(path.read_text(encoding="utf-8"))
    assert result["primary_metric"] == "activation_rate"
    assert "variant_a" in result
    assert "variant_b" in result
    assert result["absolute_lift"] > 0


def test_decision_memo_exists_and_contains_decision() -> None:
    path = REPORTS_DIR / "decision_memo.md"
    assert path.exists(), "Expected reports/decision_memo.md to be generated."
    text = path.read_text(encoding="utf-8")
    assert "## Decision" in text
    assert "## Evidence" in text


def test_review_report_exists() -> None:
    path = REPORTS_DIR / "review_report.html"
    assert path.exists(), "Expected reports/review_report.html to be generated."
    text = path.read_text(encoding="utf-8")
    assert "DecisionOps Lab" in text
    assert "Raw events to product decision" in text
