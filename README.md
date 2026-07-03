# DecisionOps Lab

> Most portfolio projects stop after analysis.  
> DecisionOps Lab continues until a decision can be made.

DecisionOps Lab is a product analytics and analytics engineering portfolio project that turns synthetic product event data into SQL models, metric definitions, data quality checks, A/B test results, and final decision memos.

This project is intentionally not another domain-specific analysis project. It is designed to show how a data team can move from raw events to trustworthy metrics and product decisions.

---

## V1 Evidence Snapshot

DecisionOps Lab V1.5 now runs end-to-end from synthetic raw data to a reviewer-facing decision report.

| Evidence | Result |
| --- | --- |
| Decision | **Ship** |
| Data quality | **PASS** |
| D7 revisit check | **PASS** |
| Primary metric | **Activation Rate** |
| Secondary check | **D7 Revisit Rate** |
| Variant A activation | **29.32%** |
| Variant B activation | **34.58%** |
| Absolute lift | **+5.26 percentage points** |
| p-value | **0.0000** |
| Raw users | **10,000** |
| Raw events | **41,402** |
| Raw sessions | **18,153** |

V1.5 checks data quality first, compares the primary activation metric, reviews D7 revisit as a secondary stability check, and then generates a decision memo.

Generated artifacts:

- [`reports/quality_report.json`](reports/quality_report.json)
- [`reports/experiment_result.json`](reports/experiment_result.json)
- [`reports/decision_memo.md`](reports/decision_memo.md)
- [`reports/review_report.html`](reports/review_report.html)

Documentation guide:

- [`docs/ARCHITECTURE_DIAGRAM.md`](docs/ARCHITECTURE_DIAGRAM.md) ? visualizes the end-to-end workflow, SQL layers, decision flow, and scenario matrix.
- [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md) ? summarizes the project as a portfolio case study.
- [`docs/REVIEW_GUIDE.md`](docs/REVIEW_GUIDE.md) ? provides a 5-minute review path for portfolio reviewers.
- [`docs/SCENARIO_MODE.md`](docs/SCENARIO_MODE.md) ? explains scenario generation and scenario matrix outputs.
- [`docs/DECISION_RULES.md`](docs/DECISION_RULES.md) ? explains how quality, primary metric, and D7 revisit produce recommendations.
- [`docs/MART_LAYER.md`](docs/MART_LAYER.md) ? explains final mart tables and their grains.


--- | --- |
| Decision | **Ship** |
| Data quality | **PASS** |
| Variant A activation | **29.32%** |
| Variant B activation | **34.58%** |
| Absolute lift | **+5.26 percentage points** |
| p-value | **0.0000** |
| Raw users | **10,000** |
| Raw events | **41,402** |
| Raw sessions | **18,153** |

Generated artifacts:

- [`reports/quality_report.json`](reports/quality_report.json)
- [`reports/experiment_result.json`](reports/experiment_result.json)
- [`reports/decision_memo.md`](reports/decision_memo.md)
- [`reports/review_report.html`](reports/review_report.html)

---

## 1. Project Question

**Can a data analyst build a reproducible workflow that checks data quality, defines product metrics, analyzes an experiment, and produces a decision memo?**

DecisionOps Lab answers this by implementing the following flow:

```text
raw product events
→ SQL staging models
→ intermediate analysis tables
→ metric layer
→ data quality report
→ experiment analysis
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
| DecisionOps Lab | SQL modeling, metric layer, quality check, experiment analysis, and decision workflow |

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
```

The product team is testing a new onboarding experience.

**Experiment question:**  
Does Variant B increase the share of new users who create their first routine within 24 hours after signup?

---

## 4. Core Outputs

| Output | Description |
| --- | --- |
| Synthetic dataset | Reproducible product event data generated with a fixed seed |
| SQL models | DuckDB-based raw loading, staging models, and intermediate analysis tables |
| Metric layer | Clear definitions for activation, retention, conversion, and guardrail metrics |
| Data quality report | PASS / WARN / FAIL checks for row count, nulls, accepted values, referential integrity, duplicates, and experiment balance |
| Experiment result | Variant A/B activation comparison, lift, statistical test, confidence interval, and segment diagnostics |
| Decision memo | Ship / Hold / Retest / Investigate recommendation based on evidence |
| Reviewer report | HTML summary for quick portfolio review |

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

V1 starts with DuckDB and plain SQL. dbt Core can be added in V2 after the core pipeline is stable.

---

## 6. How to Run

```bash
python scripts/generate_dataset.py
python scripts/run_pipeline.py
python scripts/run_quality_checks.py
python scripts/run_experiment_analysis.py
python scripts/generate_decision_memo.py
python scripts/generate_review_report.py
```

Expected local artifacts:

- `data/raw/*.csv`
- `data/processed/decisionops.duckdb`
- `reports/quality_report.json`
- `reports/experiment_result.json`
- `reports/decision_memo.md`
- `reports/review_report.html`

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
│   └── generate_review_report.py
├── sql/
│   ├── staging/
│   ├── intermediate/
│   ├── marts/
│   └── metrics/
├── reports/
│   ├── quality_report.json
│   ├── experiment_result.json
│   ├── decision_memo.md
│   └── review_report.html
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── ARCHITECTURE.md
│   ├── METRICS.md
│   ├── DATA_QUALITY.md
│   ├── EXPERIMENT_DESIGN.md
│   └── DECISION_MEMO.md
└── tests/
```

---

## 8. Current Data Flow

```text
Synthetic product events
↓
Raw CSV files
↓
DuckDB raw tables
↓
SQL staging models
↓
Intermediate user/session/experiment models
↓
Data quality report
↓
Experiment result
↓
Decision memo
↓
Reviewer HTML report
```

---

## 9. Decision Logic

The final recommendation is not based on a single metric.

| Condition | Decision |
| --- | --- |
| Data quality fails | Investigate |
| Primary metric improves with strong evidence | Ship |
| Primary metric improves but evidence is weak | Retest |
| Primary metric does not improve | Hold |

---

## 10. Claim Boundary

This project uses synthetic data. It does not claim real product performance, real user behavior, or real business impact.

What it does claim:

- A reproducible product analytics workflow
- SQL-based data modeling
- Data quality checks before decision-making
- Experiment interpretation with statistical evidence
- Decision memo generation from analytical evidence
- Reviewer-facing report generation

---

## 11. Project Status

Current status: **V1 end-to-end pipeline complete**

Completed:

- Synthetic dataset generation
- DuckDB loading and SQL staging/intermediate models
- Data quality checks
- Experiment analysis
- Decision memo generation
- Reviewer HTML report generation

Next improvements:

- Add GitHub Actions verification workflow
- Improve retention SQL model
- Add final mart tables
- Add tests for quality check logic
- Add optional dashboard or GitHub Pages deployment
