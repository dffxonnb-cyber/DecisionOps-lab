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


def pick_result(quality: dict[str, Any], experiment: dict[str, Any]) -> str:
    quality_status = quality.get("status", "FAIL")
    lift = float(experiment.get("absolute_lift", 0))
    p_value = float(experiment.get("p_value", 1))

    if quality_status == "FAIL":
        return "Investigate"
    if lift > 0 and p_value < 0.05:
        return "Ship"
    if lift > 0:
        return "Retest"
    return "Hold"


def build_memo(quality: dict[str, Any], experiment: dict[str, Any]) -> str:
    result = pick_result(quality, experiment)
    variant_a = experiment.get("variant_a", {})
    variant_b = experiment.get("variant_b", {})
    ci = experiment.get("confidence_interval_absolute_lift", {})

    if result == "Ship":
        summary = "Variant B improved the primary metric with strong evidence, and quality checks passed."
    elif result == "Retest":
        summary = "Variant B moved the primary metric upward, but evidence should be strengthened."
    elif result == "Investigate":
        summary = "Quality checks did not pass, so the result needs investigation before use."
    else:
        summary = "Variant B did not provide enough positive evidence on the primary metric."

    lines = [
        "# Decision Memo: Onboarding Variant B",
        "",
        "## Decision",
        "",
        result,
        "",
        "## Summary",
        "",
        summary,
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
        "## Next Actions",
        "",
        "1. Review the quality and experiment artifacts.",
        "2. Check segment diagnostics before changing the product default.",
        "3. Continue monitoring the primary metric after the next product change.",
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
    print(f"decision: {pick_result(quality, experiment)}")
    print("-" * 48)
    print(f"Memo: {MEMO_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
