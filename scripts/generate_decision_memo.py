"""Generate a simple markdown memo from quality and experiment reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"
QUALITY_PATH = REPORTS_DIR / "quality_report.json"
EXPERIMENT_PATH = REPORTS_DIR / "experiment_result.json"
MEMO_PATH = REPORTS_DIR / "decision_memo.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.relative_to(ROOT_DIR)}")
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def fmt_number(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}"


def pick_result(quality: dict[str, Any], experiment: dict[str, Any]) -> str:
    quality_status = quality.get("status", "FAIL")
    lift = float(experiment.get("absolute_lift", 0))
    p_value = float(experiment.get("p_value", 1))
    guardrail_status = experiment.get("guardrail_status", "WARN")

    if quality_status == "FAIL":
        return "Investigate"
    if lift > 0 and p_value < 0.05 and guardrail_status == "PASS":
        return "Ship"
    if lift > 0:
        return "Retest"
    return "Hold"


def build_guardrail_review(experiment: dict[str, Any]) -> list[str]:
    guardrails = experiment.get("guardrails", {})
    d7 = guardrails.get("d7_revisit", {})
    refund = guardrails.get("refund_rate", {})
    session = guardrails.get("session_activity", {})

    return [
        f"- D7 revisit: {d7.get('status', 'UNKNOWN')} (delta: {fmt_pct(d7.get('delta'))})",
        f"- Refund rate: {refund.get('status', 'UNKNOWN')} (delta: {fmt_pct(refund.get('delta'))})",
        f"- Session activity: {session.get('status', 'UNKNOWN')} (delta: {fmt_number(session.get('delta'))} sessions per user)",
        f"- Overall guardrail status: {experiment.get('guardrail_status', 'UNKNOWN')}",
    ]


def build_summary(result: str) -> str:
    if result == "Ship":
        return (
            "Variant B improved the primary metric with strong evidence, and the multi-guardrail review did not show "
            "retention, refund, or engagement risk beyond the portfolio thresholds."
        )
    if result == "Retest":
        return (
            "Variant B moved the primary metric upward, but the evidence or guardrail review is not strong enough "
            "to use the result as a product default yet."
        )
    if result == "Investigate":
        return "Quality checks did not pass, so the result needs investigation before use."
    return "Variant B did not provide enough positive evidence on the primary metric."


def build_next_actions(result: str) -> list[str]:
    if result == "Ship":
        return [
            "1. Review segment diagnostics before rollout.",
            "2. Monitor activation, D7 revisit, refund rate, and session activity after launch.",
            "3. Keep the claim limited to this synthetic workflow demonstration.",
        ]
    if result == "Retest":
        return [
            "1. Identify which guardrail or evidence signal blocks Ship.",
            "2. Review segment diagnostics for uneven lift or risk concentration.",
            "3. Run a follow-up test before changing the product default.",
        ]
    if result == "Investigate":
        return [
            "1. Fix the failing quality checks first.",
            "2. Rebuild the dataset and rerun the full workflow.",
            "3. Do not interpret experiment evidence until quality status passes.",
        ]
    return [
        "1. Keep Variant A as the default.",
        "2. Review whether the treatment hypothesis should be redesigned.",
        "3. Use segment diagnostics only as follow-up evidence, not as the main result.",
    ]


def build_memo(quality: dict[str, Any], experiment: dict[str, Any]) -> str:
    result = pick_result(quality, experiment)
    variant_a = experiment.get("variant_a", {})
    variant_b = experiment.get("variant_b", {})
    ci = experiment.get("confidence_interval_absolute_lift", {})
    scenario = experiment.get("scenario", "unknown")

    lines = [
        "# Decision Memo: Onboarding Variant B",
        "",
        "## Scenario",
        "",
        str(scenario),
        "",
        "## Decision",
        "",
        result,
        "",
        "## Summary",
        "",
        build_summary(result),
        "",
        "## Evidence",
        "",
        f"- Variant A activation: {fmt_pct(variant_a.get('activation_rate'))}",
        f"- Variant B activation: {fmt_pct(variant_b.get('activation_rate'))}",
        f"- Absolute lift: {fmt_pct(experiment.get('absolute_lift'))}",
        f"- Relative lift: {fmt_pct(experiment.get('relative_lift'))}",
        f"- p-value: {float(experiment.get('p_value', 1)):.4f}",
        f"- Confidence interval: {fmt_pct(ci.get('low'))} to {fmt_pct(ci.get('high'))}",
        f"- Quality status: {quality.get('status', 'UNKNOWN')}",
        "",
        "## Guardrail Review",
        "",
        *build_guardrail_review(experiment),
        "",
        "## Next Actions",
        "",
        *build_next_actions(result),
        "",
        "## Claim Boundary",
        "",
        "This memo uses synthetic data and demonstrates the workflow, not real product performance.",
        "",
        "## Generated At",
        "",
        datetime.now(timezone.utc).isoformat(),
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    quality = load_json(QUALITY_PATH)
    experiment = load_json(EXPERIMENT_PATH)
    memo = build_memo(quality, experiment)
    MEMO_PATH.write_text(memo, encoding="utf-8")

    print("\nDecision memo")
    print("-" * 48)
    print(f"scenario: {experiment.get('scenario', 'unknown')}")
    print(f"decision: {pick_result(quality, experiment)}")
    print("-" * 48)
    print(f"Memo: {MEMO_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
