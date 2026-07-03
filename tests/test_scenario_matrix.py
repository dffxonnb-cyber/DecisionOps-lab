from __future__ import annotations

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"
SCENARIO_MATRIX_PATH = REPORTS_DIR / "scenario_matrix.json"


def load_matrix() -> list[dict]:
    assert SCENARIO_MATRIX_PATH.exists(), "Expected reports/scenario_matrix.json to be generated."
    payload = json.loads(SCENARIO_MATRIX_PATH.read_text(encoding="utf-8"))
    return payload["scenarios"]


def test_scenario_matrix_has_all_expected_scenarios() -> None:
    rows = load_matrix()
    scenarios = {row["scenario"] for row in rows}
    assert scenarios == {"strong_positive", "guardrail_risk", "weak_evidence", "neutral"}


def test_scenario_matrix_has_multiple_decision_outcomes() -> None:
    rows = load_matrix()
    decisions = {row["decision"] for row in rows}
    assert {"Ship", "Retest", "Hold"}.issubset(decisions)


def test_scenario_expected_decisions() -> None:
    rows = {row["scenario"]: row for row in load_matrix()}
    assert rows["strong_positive"]["decision"] == "Ship"
    assert rows["guardrail_risk"]["decision"] == "Retest"
    assert rows["weak_evidence"]["decision"] == "Retest"
    assert rows["neutral"]["decision"] == "Hold"


def test_guardrail_risk_is_not_shipped() -> None:
    rows = {row["scenario"]: row for row in load_matrix()}
    guardrail_risk = rows["guardrail_risk"]
    assert guardrail_risk["guardrail_status"] == "WARN"
    assert guardrail_risk["d7_revisit_delta"] < -0.01
    assert guardrail_risk["decision"] != "Ship"
