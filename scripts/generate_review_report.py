"""Generate a simple reviewer HTML report from DecisionOps artifacts.

Inputs:
- reports/quality_report.json
- reports/experiment_result.json
- reports/decision_memo.md
- data/processed/decisionops.duckdb

Output:
- reports/review_report.html
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import duckdb


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"
QUALITY_PATH = REPORTS_DIR / "quality_report.json"
EXPERIMENT_PATH = REPORTS_DIR / "experiment_result.json"
MEMO_PATH = REPORTS_DIR / "decision_memo.md"
HTML_PATH = REPORTS_DIR / "review_report.html"
DB_PATH = ROOT_DIR / "data" / "processed" / "decisionops.duckdb"
MART_TABLES = [
    "mart_experiment_result",
    "mart_segment_performance",
    "mart_retention_cohort",
    "mart_decision_summary",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.relative_to(ROOT_DIR)}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.relative_to(ROOT_DIR)}")
    return path.read_text(encoding="utf-8")


def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2%}"


def fmt_number(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.2f}"


def fetch_mart_counts() -> dict[str, int]:
    if not DB_PATH.exists():
        return {}

    with duckdb.connect(str(DB_PATH)) as connection:
        existing_tables = {row[0] for row in connection.execute("SHOW TABLES").fetchall()}
        counts = {}
        for table in MART_TABLES:
            if table in existing_tables:
                counts[table] = int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        return counts


def build_mart_rows(mart_counts: dict[str, int]) -> str:
    if not mart_counts:
        return '<tr><td colspan="2">No mart tables found. Run the SQL pipeline first.</td></tr>'

    rows = []
    for table in MART_TABLES:
        value = mart_counts.get(table)
        if value is None:
            rows.append(f"<tr><th>{html.escape(table)}</th><td>missing</td></tr>")
        else:
            rows.append(f"<tr><th>{html.escape(table)}</th><td>{value:,} rows</td></tr>")
    return "\n".join(rows)


def build_guardrail_rows(experiment: dict[str, Any]) -> str:
    guardrails = experiment.get("guardrails", {})
    rows = []

    d7 = guardrails.get("d7_revisit", {})
    rows.append(
        "<tr>"
        "<th>D7 revisit rate</th>"
        f"<td>{fmt_pct(d7.get('variant_a'))}</td>"
        f"<td>{fmt_pct(d7.get('variant_b'))}</td>"
        f"<td>{fmt_pct(d7.get('delta'))}</td>"
        f"<td>{html.escape(str(d7.get('status', 'UNKNOWN')))}</td>"
        "</tr>"
    )

    refund = guardrails.get("refund_rate", {})
    rows.append(
        "<tr>"
        "<th>Refund rate</th>"
        f"<td>{fmt_pct(refund.get('variant_a'))}</td>"
        f"<td>{fmt_pct(refund.get('variant_b'))}</td>"
        f"<td>{fmt_pct(refund.get('delta'))}</td>"
        f"<td>{html.escape(str(refund.get('status', 'UNKNOWN')))}</td>"
        "</tr>"
    )

    session = guardrails.get("session_activity", {})
    rows.append(
        "<tr>"
        "<th>Avg sessions per user</th>"
        f"<td>{fmt_number(session.get('variant_a'))}</td>"
        f"<td>{fmt_number(session.get('variant_b'))}</td>"
        f"<td>{fmt_number(session.get('delta'))}</td>"
        f"<td>{html.escape(str(session.get('status', 'UNKNOWN')))}</td>"
        "</tr>"
    )

    rows.append(
        "<tr>"
        "<th>Overall</th>"
        "<td colspan=\"2\">Multi-guardrail review</td>"
        f"<td colspan=\"2\">{html.escape(str(experiment.get('guardrail_status', 'UNKNOWN')))}</td>"
        "</tr>"
    )

    return "\n".join(rows)


def build_html(quality: dict[str, Any], experiment: dict[str, Any], memo: str, mart_counts: dict[str, int]) -> str:
    variant_a = experiment.get("variant_a", {})
    variant_b = experiment.get("variant_b", {})
    decision = "Unknown"
    lines = memo.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## Decision" and index + 2 < len(lines):
            decision = lines[index + 2].strip()
            break

    escaped_memo = html.escape(memo)
    guardrail_status = html.escape(str(experiment.get("guardrail_status", "UNKNOWN")))
    mart_rows = build_mart_rows(mart_counts)
    guardrail_rows = build_guardrail_rows(experiment)

    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>DecisionOps Lab Review Report</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      background: #111827;
      color: #e5e7eb;
      line-height: 1.6;
    }}
    main {{
      max-width: 980px;
      margin: 0 auto;
      padding: 48px 24px;
    }}
    h1, h2 {{
      line-height: 1.2;
    }}
    .hero {{
      border: 1px solid #374151;
      background: #1f2937;
      border-radius: 20px;
      padding: 28px;
      margin-bottom: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin: 24px 0;
    }}
    .card {{
      border: 1px solid #374151;
      background: #0f172a;
      border-radius: 16px;
      padding: 18px;
      margin-bottom: 24px;
    }}
    .label {{
      color: #9ca3af;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .value {{
      font-size: 28px;
      font-weight: 700;
      margin-top: 8px;
    }}
    .note {{
      color: #cbd5e1;
      font-size: 14px;
      margin-top: 8px;
    }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      border: 1px solid #374151;
      background: #020617;
      border-radius: 16px;
      padding: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
    }}
    th, td {{
      border-bottom: 1px solid #374151;
      padding: 10px;
      text-align: left;
    }}
    th {{
      color: #9ca3af;
      font-weight: 600;
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <p class="label">DecisionOps Lab · V2-1</p>
    <h1>Raw events to product decision</h1>
    <p>This report summarizes data quality, mart layer outputs, experiment evidence, multi-guardrail status, and the final memo generated from synthetic product event data.</p>
  </section>

  <section class="grid">
    <div class="card"><div class="label">Decision</div><div class="value">{html.escape(decision)}</div></div>
    <div class="card"><div class="label">Quality</div><div class="value">{html.escape(str(quality.get('status', 'UNKNOWN')))}</div></div>
    <div class="card"><div class="label">Guardrail</div><div class="value">{guardrail_status}</div><div class="note">D7 + refund + session activity</div></div>
    <div class="card"><div class="label">Mart tables</div><div class="value">{len(mart_counts)}</div></div>
    <div class="card"><div class="label">A activation</div><div class="value">{fmt_pct(variant_a.get('activation_rate'))}</div></div>
    <div class="card"><div class="label">B activation</div><div class="value">{fmt_pct(variant_b.get('activation_rate'))}</div></div>
    <div class="card"><div class="label">Absolute lift</div><div class="value">{fmt_pct(experiment.get('absolute_lift'))}</div></div>
    <div class="card"><div class="label">Refund delta</div><div class="value">{fmt_pct(experiment.get('refund_rate_delta'))}</div></div>
    <div class="card"><div class="label">p-value</div><div class="value">{float(experiment.get('p_value', 1)):.4f}</div></div>
  </section>

  <section class="card">
    <h2>Mart Layer Summary</h2>
    <table>
      {mart_rows}
    </table>
  </section>

  <section class="card">
    <h2>Quality Summary</h2>
    <table>
      <tr><th>Status</th><td>{html.escape(str(quality.get('status', 'UNKNOWN')))}</td></tr>
      <tr><th>Pass</th><td>{quality.get('summary', {}).get('pass', 0)}</td></tr>
      <tr><th>Warn</th><td>{quality.get('summary', {}).get('warn', 0)}</td></tr>
      <tr><th>Fail</th><td>{quality.get('summary', {}).get('fail', 0)}</td></tr>
    </table>
  </section>

  <section class="card">
    <h2>Guardrail Summary</h2>
    <table>
      <tr><th>Metric</th><th>Variant A</th><th>Variant B</th><th>Delta</th><th>Status</th></tr>
      {guardrail_rows}
    </table>
  </section>

  <section>
    <h2>Decision Memo</h2>
    <pre>{escaped_memo}</pre>
  </section>
</main>
</body>
</html>
""".strip()


def main() -> None:
    quality = load_json(QUALITY_PATH)
    experiment = load_json(EXPERIMENT_PATH)
    memo = load_text(MEMO_PATH)
    mart_counts = fetch_mart_counts()
    html_report = build_html(quality, experiment, memo, mart_counts)
    HTML_PATH.write_text(html_report, encoding="utf-8")

    print("\nReviewer report")
    print("-" * 48)
    print(f"Report: {HTML_PATH.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
