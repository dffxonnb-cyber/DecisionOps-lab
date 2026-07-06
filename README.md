[![Verify DecisionOps Lab](https://github.com/dffxonnb-cyber/DecisionOps-lab/actions/workflows/verify.yml/badge.svg)](https://github.com/dffxonnb-cyber/DecisionOps-lab/actions/workflows/verify.yml)

# DecisionOps Lab

> Most portfolio projects stop after analysis.  
> DecisionOps Lab continues until a decision can be made.

DecisionOps Lab is a product analytics and analytics engineering portfolio project that turns synthetic product event data into SQL models, metric definitions, data quality checks, A/B test results, guardrail review, and final decision memos.

This project is intentionally not another domain-specific analysis project. It is designed to show how a data team can move from raw events to trustworthy metrics and product decisions.

---

## Current Evidence Snapshot

DecisionOps Lab runs end-to-end from synthetic raw data to a reviewer-facing decision report.

| Evidence | Result |
| --- | --- |
| Decision workflow | Ship / Retest / Hold / Investigate |
| Data quality | PASS / WARN / FAIL checks before interpretation |
| Primary metric | Activation Rate |
| Guardrail review | D7 revisit, refund rate, session behavior |
| SQL structure | Raw → staging → intermediate → mart |
| Verification | One-command local runner + GitHub Actions |

The workflow checks data quality first, compares the primary activation metric, reviews guardrails, and then generates a decision memo.

Generated artifacts:

- [`reports/quality_report.json`](reports/quality_report.json)
- [`reports/experiment_result.json`](reports/experiment_result.json)
- [`reports/decision_memo.md`](reports/decision_memo.md)
- [`reports/review_report.html`](reports/review_report.html)
- [`reports/scenario_matrix.json`](reports/scenario_matrix.json)
- [`reports/scenario_matrix.md`](reports/scenario_matrix.md)

Documentation guide:

- [`docs/V1_RELEASE_NOTES.md`](docs/V1_RELEASE_NOTES.md) — summarizes the completed V1 scope and V2 candidates.
- [`docs/V2_GUARDRAILS.md`](docs/V2_GUARDRAILS.md) — explains the V2-1 multi-guardrail decision workflow.
- [`docs/PORTFOLIO_PITCH.md`](docs/PORTFOLIO_PITCH.md) — translates the project into resume, portfolio, and interview language.
- [`docs/ARCHITECTURE_DIAGRAM.md`](docs/ARCHITECTURE_DIAGRAM.md) — visualizes the end-to-end workflow, SQL layers, decision flow, and scenario matrix.
- [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md) — summarizes the project as a portfolio case study.
- [`docs/REVIEW_GUIDE.md`](docs/REVIEW_GUIDE.md) — provides a 5-minute review path for portfolio reviewers.
- [`docs/SCENARIO_MODE.md`](docs/SCENARIO_MODE.md) — explains scenario generation and scenario matrix outputs.
- [`docs/DECISION_RULES.md`](docs/DECISION_RULES.md) — explains how quality, primary metric, and guardrails produce recommendations.
- [`docs/MART_LAYER.md`](docs/MART_LAYER.md) — explains final mart tables and their grains.

---

## 1. Project Question

**Can a data analyst build a reproducible workflow that checks data quality, defines product metrics, analyzes an experiment, and produces a decision memo?**

DecisionOps Lab answers this by implementing the following flow:

```text
raw product events
→ SQL staging models
→ intermediate analysis tables
→ mart layer
→ data quality report
→ experiment analysis
→ guardrail review
→ decision memo
→ reviewer report
```

---

## 2. Portfolio Positioning

Existing projects show domain-specific decision systems:

| Project | Role |
| --- | --- |
| Redveil | Risk review UX and decision artifacts |
| Shelter Signal | Public-data API service with freshness, cache, fallback, and PWA flow |
| LH Traffic Safety | Spatial risk scoring and field-review priority design |
| Starbucks Promotion | CRM event restructuring, prediction, recommendation, and dashboard story |
| DecisionOps Lab | SQL modeling, metric layer, quality check, experiment analysis, guardrail-aware decision workflow |

DecisionOps Lab fills the missing technical layer: **how raw data becomes a reliable decision workflow inside a data team.**

---

## 3. Product Scenario

The synthetic product is a routine / study habit app.

A user can:

```text
signup
→ onboarding_start
→ onboarding_complete
→ create_routine
→ complete_routine
→ return_visit
→ trial_start
→ paid_conversion
→ refund
```

The product team is testing a new onboarding experience.

**Experiment question:**  
Does Variant B increase the share of new users who create their first routine within 24 hours after signup?

---

## 4. Core Outputs

| Output | Description |
| --- | --- |
| Synthetic dataset | Reproducible product event data generated with a fixed seed |
| SQL models | DuckDB-based raw loading, staging models, intermediate tables, and final marts |
| Metric layer | Clear definitions for activation, retention, monetization, and guardrail metrics |
| Data quality report | PASS / WARN / FAIL checks for row count, nulls, accepted values, referential integrity, duplicates, and experiment balance |
| Experiment result | Variant A/B comparison, lift, statistical test, confidence interval, segment diagnostics, and guardrail review |
| Decision memo | Ship / Hold / Retest / Investigate recommendation based on evidence and guardrails |
| Reviewer report | Static HTML summary for quick portfolio review |

---

## 5. Tech Stack

| Area | Tools |
| --- | --- |
| Data generation | Python, pandas, NumPy |
| SQL engine | DuckDB |
| Experiment analysis | scipy, statsmodels |
| Quality checks | Python, pytest-ready structure |
| Reporting | Markdown, JSON, static HTML |
| Documentation | Markdown |

V1 starts with DuckDB and plain SQL. dbt Core can be added in a later V2 step after the decision workflow remains stable.

---

## 6. How to Run

Run the full verification workflow:

```bash
python scripts/run_full_verification.py
```

Or run the pipeline step by step:

```bash
python scripts/generate_dataset.py
python scripts/run_pipeline.py
python scripts/run_quality_checks.py
python scripts/run_experiment_analysis.py
python scripts/generate_decision_memo.py
python scripts/generate_review_report.py
python scripts/run_scenario_matrix.py
python -m pytest
```

Expected local artifacts:

- `data/raw/*.csv`
- `data/processed/decisionops.duckdb`
- `reports/quality_report.json`
- `reports/experiment_result.json`
- `reports/decision_memo.md`
- `reports/review_report.html`
- `reports/scenario_matrix.json`
- `reports/scenario_matrix.md`

---

## 7. Repository Structure

```text
DecisionOps-lab/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── scripts/
│   ├── generate_dataset.py
│   ├── run_pipeline.py
│   ├── run_quality_checks.py
│   ├── run_experiment_analysis.py
│   ├── generate_decision_memo.py
│   ├── generate_review_report.py
│   └── run_scenario_matrix.py
├── sql/
│   ├── staging/
│   ├── intermediate/
│   ├── marts/
│   └── metrics/
├── reports/
│   ├── quality_report.json
│   ├── experiment_result.json
│   ├── decision_memo.md
│   ├── review_report.html
│   ├── scenario_matrix.json
│   └── scenario_matrix.md
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── ARCHITECTURE.md
│   ├── METRICS.md
│   ├── DATA_QUALITY.md
│   ├── EXPERIMENT_DESIGN.md
│   ├── DECISION_RULES.md
│   ├── MART_LAYER.md
│   ├── V1_RELEASE_NOTES.md
│   └── V2_GUARDRAILS.md
└── tests/
```
