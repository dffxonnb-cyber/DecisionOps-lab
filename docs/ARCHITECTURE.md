# Architecture

## 1. Architecture Goal

DecisionOps Lab is designed as a reproducible local analytics pipeline.

The architecture should answer one question:

> Can a reviewer clone the repository, run the pipeline, and see how raw product events become a decision memo?

---

## 2. End-to-End Flow

```text
Synthetic data generator
    ↓
Raw CSV files
    ↓
DuckDB load step
    ↓
SQL staging layer
    ↓
SQL intermediate layer
    ↓
SQL mart layer
    ↓
Metric layer outputs
    ↓
Data quality checks
    ↓
Experiment analysis
    ↓
Decision memo
    ↓
Optional report / dashboard
```

---

## 3. Core Components

| Component | Purpose |
| --- | --- |
| `scripts/generate_dataset.py` | Creates reproducible synthetic source data |
| `scripts/run_pipeline.py` | Loads raw CSVs into DuckDB and runs SQL models |
| `scripts/run_quality_checks.py` | Checks data validity before decision-making |
| `scripts/run_experiment_analysis.py` | Calculates experiment metrics and statistical evidence |
| `scripts/generate_decision_memo.py` | Converts evidence into a decision memo |
| `sql/staging/` | Cleans and standardizes raw tables |
| `sql/intermediate/` | Builds analysis-ready entities |
| `sql/marts/` | Produces final business-facing tables |
| `sql/metrics/` | Defines reusable metric queries |
| `reports/` | Stores quality, experiment, and decision artifacts |
| `.github/workflows/verify.yml` | Runs reproducibility checks in CI |

---

## 4. Data Layer Design

### 4-1. Raw Layer

Raw data is generated as CSV files under `data/raw/`.

Raw files should be treated as source data. They can contain realistic messiness, such as:

- delayed events
- incomplete sessions
- variant imbalance
- refund edge cases
- device and acquisition channel differences

### 4-2. Staging Layer

Staging SQL should do minimal cleaning:

- rename columns if needed
- cast timestamps
- standardize accepted values
- remove impossible rows only when clearly invalid
- preserve source-level grain

### 4-3. Intermediate Layer

Intermediate models should build reusable analytical entities:

- first event per user
- first routine creation
- activation window
- retention flags
- experiment user metrics
- session-level funnel steps

### 4-4. Mart Layer

Marts should be final, reviewer-friendly tables:

- user activation mart
- funnel daily mart
- retention cohort mart
- experiment result mart
- segment performance mart
- decision summary mart

---

## 5. Artifact Strategy

DecisionOps Lab should not require a live database or paid service.

The project should produce local artifacts that can be inspected directly:

| Artifact | Format | Purpose |
| --- | --- | --- |
| Raw data | CSV | Source-like synthetic data |
| Processed database | DuckDB | Queryable local analytics DB |
| Quality report | JSON | Data trust status |
| Experiment result | JSON | A/B test evidence |
| Decision memo | Markdown | Business decision summary |
| Optional dashboard | HTML or Streamlit | Reviewer-friendly interface |

---

## 6. Failure Handling Principle

The pipeline should not blindly produce a Ship decision.

If data quality fails, decision generation should return `Investigate`.

```text
quality_status = FAIL
→ decision = Investigate
```

If data quality passes but experiment evidence is weak, the decision can become `Retest`.

```text
quality_status = PASS
primary_metric_lift > 0
statistical_evidence = weak
→ decision = Retest
```

---

## 7. V1 Architecture Boundary

V1 uses:

- Python
- pandas
- DuckDB
- SQL files
- JSON / Markdown reports
- pytest
- GitHub Actions

V1 does not require:

- Slack
- Notion
- paid APIs
- cloud warehouse
- real company data
- production infrastructure

This is intentional. The project is designed for a job-seeker portfolio while still reflecting real analytics engineering patterns.
