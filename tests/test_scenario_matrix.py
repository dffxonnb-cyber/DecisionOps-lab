from __future__ import annotations

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"
SCENARIO_MATRIX_PATH = REPORTS_DIR / "scenario_matrix.json"
EXPERIMENT_RESULT_PATH = REPORTS_DIR / "experiment_result.json"


def load_matrix() -> list[dict]:
    assert SCENARIO_MATRIX_PATH.exists(), "Expected reports/scenario_matrix.json to be generated."
    payload = json.loads(SCENARIO_MATRIX_PATH.read_text(encoding="utf-8"))
    return payload["scenarios"]


def load_experiment_result() -> dict:
    assert EXPERIMENT_RESULT_PATH.exists(), "Expected reports/experiment_result.json to be generated."
    return json.loads(EXPERIMENT_RESULT_PATH.read_text(encoding="utf-8"))


def test_scenario_matrix_has_all_expected_scenarios() -> None:
    rows = load_matrix()
    scenarios = {row["scenario"] for row in rows}
    assert scenarios == {"strong_positive", "guardrail_risk", "weak_evidence", "neutral", "quality_failure"}


def test_scenario_matrix_has_multiple_decision_outcomes() -> None:
    rows = load_matrix()
    decisions = {row["decision"] for row in rows}
    assert {"Ship", "Retest", "Hold", "Investigate"}.issubset(decisions)


def test_scenario_expected_decisions() -> None:
    rows = {row["scenario"]: row for row in load_matrix()}
    assert rows["strong_positive"]["decision"] == "Ship"
    assert rows["guardrail_risk"]["decision"] == "Retest"
    assert rows["weak_evidence"]["decision"] == "Retest"
    assert rows["neutral"]["decision"] == "Hold"
    assert rows["quality_failure"]["decision"] == "Investigate"


def test_guardrail_risk_is_not_shipped() -> None:
    rows = {row["scenario"]: row for row in load_matrix()}
    guardrail_risk = rows["guardrail_risk"]
    assert guardrail_risk["guardrail_status"] == "WARN"
    assert guardrail_risk["d7_revisit_delta"] < -0.01
    assert guardrail_risk["decision"] != "Ship"


def test_quality_failure_is_not_interpreted_as_ship() -> None:
    rows = {row["scenario"]: row for row in load_matrix()}
    quality_failure = rows["quality_failure"]
    assert quality_failure["quality_status"] == "FAIL"
    assert quality_failure["decision"] == "Investigate"


def test_experiment_result_contains_multi_guardrail_schema() -> None:
    result = load_experiment_result()
    guardrails = result["guardrails"]

    assert result["guardrail_metric"] == "multi_guardrail"
    assert result["guardrail_status"] in {"PASS", "WARN"}
    assert {"d7_revisit", "refund_rate", "session_activity"}.issubset(guardrails)
    assert "refund_rate_delta" in result
    assert "avg_sessions_delta" in result

    for guardrail in guardrails.values():
        assert guardrail["status"] in {"PASS", "WARN"}
        assert "metric" in guardrail
        assert "delta" in guardrail
        assert "threshold" in guardrail


def test_multi_guardrail_ship_requires_all_guardrails_to_pass() -> None:
    result = load_experiment_result()
    if result["suggested_decision"] == "Ship":
        assert result["guardrail_status"] == "PASS"
        assert all(item["status"] == "PASS" for item in result["guardrails"].values())
