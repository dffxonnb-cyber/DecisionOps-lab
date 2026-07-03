# DecisionOps Lab Project Plan

## 1. One-line Definition

DecisionOps Lab is a product analytics and analytics engineering project that turns synthetic product event data into SQL marts, metric definitions, data quality checks, A/B test analysis, and final decision memos.

The goal is not to build another dashboard-only project. The goal is to show a realistic data-team workflow from raw data to a product decision.

---

## 2. Why This Project Exists

Most portfolio projects stop at analysis:

```text
load data
→ clean data
→ visualize data
→ write insights
```

DecisionOps Lab continues further:

```text
raw data
→ trusted marts
→ metric definitions
→ quality checks
→ experiment analysis
→ decision memo
```

This project fills the gap between data analysis and analytics engineering.

It is designed to prove the following:

1. Raw events can be transformed into reliable SQL marts.
2. Metrics can be defined clearly before they are interpreted.
3. Data quality should be checked before business decisions are made.
4. A/B test results should be interpreted with primary and guardrail metrics.
5. Analysis should end in a decision document, not only charts.

---

## 3. Product Scenario

The synthetic product is a routine / study habit app.

A user signs up, completes onboarding, creates a routine, completes routines, returns later, and may start a trial or convert to a paid plan.

The company is testing a new onboarding flow.

### Experiment Question

Does Variant B increase the share of users who create their first routine within 24 hours after signup?

### Primary Metric

Activation Rate: the share of users who create their first routine within 24 hours of signup.

### Guardrail Metrics

- D7 Retention
- Refund Rate
- Session Drop-off

---

## 4. Raw Data

The synthetic dataset will be generated with a fixed seed.

| Table | Description |
| --- | --- |
| `raw_users` | user profile, signup timestamp, acquisition channel, device type, age group |
| `raw_events` | product events such as signup, onboarding, create routine, complete routine, return visit |
| `raw_sessions` | session start, session end, duration, device type |
| `raw_experiments` | experiment assignment by user |
| `raw_payments` | trial start, paid conversion, refund events |

---

## 5. Modeling Layers

```text
raw
↓
staging
↓
intermediate
↓
mart
↓
metric layer
↓
decision memo
```

### Staging

Clean and standardize raw tables.

Expected models:

- `stg_users`
- `stg_events`
- `stg_sessions`
- `stg_experiments`
- `stg_payments`

### Intermediate

Build analysis-ready entities.

Expected models:

- `int_user_first_events`
- `int_user_activation`
- `int_user_retention`
- `int_experiment_user_metrics`
- `int_session_funnel`

### Mart

Build final tables for decision review.

Expected models:

- `mart_user_activation`
- `mart_funnel_daily`
- `mart_retention_cohort`
- `mart_experiment_result`
- `mart_segment_performance`
- `mart_decision_summary`

---

## 6. Main Project Phases

## Phase 1. Foundation

Goal: initialize repository structure and planning documents.

Deliverables:

- README
- Project plan
- Architecture document
- Metrics document
- Data quality document
- Experiment design document
- Decision memo document
- Requirements and `.gitignore`

Definition of done:

- A reviewer can understand the project purpose, scope, and planned pipeline within three minutes.

---

## Phase 2. Synthetic Dataset

Goal: generate reproducible product event data.

Tasks:

- Create `scripts/generate_dataset.py`
- Generate users, events, sessions, experiments, and payments
- Add deterministic seed
- Save CSVs under `data/raw/`
- Add sample data boundary documentation

Definition of done:

- Running one script recreates the same dataset.

---

## Phase 3. SQL Modeling

Goal: transform raw data into marts using DuckDB and SQL.

Tasks:

- Create DuckDB connection logic
- Load raw CSVs
- Execute staging SQL
- Execute intermediate SQL
- Execute mart SQL
- Write final database to `data/processed/decisionops.duckdb`

Definition of done:

- `python scripts/run_pipeline.py` builds all marts from scratch.

---

## Phase 4. Data Quality Checks

Goal: validate whether the data can be used for decision-making.

Tasks:

- Row count checks
- Null checks
- Accepted value checks
- Freshness checks
- Referential integrity checks
- Duplicate checks
- Experiment balance checks
- Metric sanity checks

Definition of done:

- `reports/quality_report.json` is generated with PASS / WARN / FAIL.

---

## Phase 5. Experiment Analysis

Goal: compare Variant A and Variant B.

Tasks:

- Calculate activation rate by variant
- Calculate absolute lift and relative lift
- Run statistical significance test
- Calculate confidence interval
- Check guardrail metrics
- Add segment diagnostics

Definition of done:

- `reports/experiment_result.json` summarizes the result and risk signals.

---

## Phase 6. Decision Memo Engine

Goal: convert quality and experiment results into a decision memo.

Tasks:

- Implement decision rules
- Generate Ship / Hold / Retest / Investigate / Partial Rollout recommendation
- Write reasons, cautions, and next actions
- Save result to `reports/decision_memo.md`

Definition of done:

- A reviewer can understand the decision without reading every SQL file.

---

## Phase 7. Dashboard or Static Report

Goal: create a quick review page.

Tasks:

- Show core metrics
- Show data quality status
- Show experiment result
- Show final decision memo

Definition of done:

- README links to a report that can be reviewed in three minutes.

---

## Phase 8. GitHub Actions Verification

Goal: make the pipeline reproducible in CI.

Tasks:

- Install dependencies
- Generate dataset
- Run SQL pipeline
- Run quality checks
- Run experiment analysis
- Generate decision memo
- Run tests

Definition of done:

- Push triggers verification workflow.

---

## 7. V1 Scope

V1 includes:

- Synthetic event data
- DuckDB SQL pipeline
- Core product metrics
- Data quality checks
- A/B test analysis
- Decision memo generation
- Basic CI verification

V1 excludes:

- Real user data
- Real business claims
- External paid services
- Complex dashboarding
- dbt Core, unless added in V2

---

## 8. V2 Ideas

Possible V2 improvements:

- dbt Core migration
- Metabase or Streamlit dashboard
- More advanced cohort retention
- More experiment types
- Data quality trend snapshots
- Decision memo templates for multiple product cases
- GitHub Pages report deployment
