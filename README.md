# DecisionOps Lab

> Most portfolio projects stop after analysis.  
> DecisionOps Lab continues until a decision can be made.

DecisionOps Lab is a product analytics and analytics engineering portfolio project that turns synthetic product event data into SQL marts, metric definitions, data quality checks, A/B test results, and final decision memos.

This project is intentionally not another domain-specific analysis project. It is designed to show how a data team can move from raw events to trustworthy metrics and product decisions.

---

## 1. Project Question

**Can a data analyst build a reproducible workflow that checks data quality, defines product metrics, analyzes an experiment, and produces a decision memo?**

DecisionOps Lab answers this by implementing the following flow:

```text
raw product events
→ SQL staging models
→ intermediate analysis tables
→ mart tables
→ metric layer
→ data quality report
→ experiment analysis
→ decision memo
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
| DecisionOps Lab | SQL mart, metric layer, quality check, experiment analysis, and decision workflow |

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
| SQL marts | DuckDB-based staging, intermediate, mart, and metric tables |
| Metric layer | Clear definitions for activation, retention, conversion, and guardrail metrics |
| Data quality report | PASS / WARN / FAIL checks for row count, nulls, accepted values, freshness, referential integrity, duplicates, and experiment balance |
| Experiment result | Variant A/B activation comparison, lift, statistical test, confidence interval, and segment diagnostics |
| Decision memo | Ship / Hold / Retest / Investigate / Partial Rollout recommendation with reasons and cautions |
| Verification workflow | GitHub Actions pipeline for dataset generation, SQL modeling, quality checks, and tests |

---

## 5. Tech Stack

| Area | Tools |
| --- | --- |
| Data generation | Python, pandas, NumPy |
| SQL engine | DuckDB |
| Experiment analysis | scipy, statsmodels |
| Quality checks | Python, pytest |
| Reporting | Markdown, JSON, optional Streamlit or static HTML |
| Automation | GitHub Actions |
| Documentation | Markdown |

V1 starts with DuckDB and plain SQL. dbt Core can be added in V2 after the core pipeline is stable.

---

## 6. Planned Repository Structure

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
│   └── generate_decision_memo.py
├── sql/
│   ├── staging/
│   ├── intermediate/
│   ├── marts/
│   └── metrics/
├── reports/
│   ├── quality_report.json
│   ├── experiment_result.json
│   └── decision_memo.md
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── ARCHITECTURE.md
│   ├── METRICS.md
│   ├── DATA_QUALITY.md
│   ├── EXPERIMENT_DESIGN.md
│   └── DECISION_MEMO.md
├── tests/
│   └── test_quality_checks.py
└── .github/
    └── workflows/
        └── verify.yml
```

---

## 7. V1 Definition of Done

V1 is complete when the repository can run the following flow from scratch:

```bash
python scripts/generate_dataset.py
python scripts/run_pipeline.py
python scripts/run_quality_checks.py
python scripts/run_experiment_analysis.py
python scripts/generate_decision_memo.py
pytest
```

Expected final artifacts:

- `data/raw/*.csv`
- `data/processed/decisionops.duckdb`
- `reports/quality_report.json`
- `reports/experiment_result.json`
- `reports/decision_memo.md`

---

## 8. Decision Logic

The final recommendation is not based on a single metric.

| Condition | Decision |
| --- | --- |
| Data quality fails | Investigate |
| Primary metric improves, statistically meaningful, guardrails stable | Ship |
| Primary metric improves but evidence is weak | Retest |
| Primary metric improves but guardrail metric worsens | Hold |
| Lift differs heavily by segment | Partial Rollout or Segment Follow-up |

---

## 9. Claim Boundary

This project uses synthetic data. It does not claim real product performance, real user behavior, or real business impact.

What it does claim:

- A reproducible product analytics workflow
- SQL-based metric modeling
- Data quality checks before decision-making
- Experiment interpretation with guardrails
- Decision memo generation from analytical evidence

---

## 10. Project Status

Current status: **planning and foundation stage**

Next step: build the documentation foundation and repository scaffold.
