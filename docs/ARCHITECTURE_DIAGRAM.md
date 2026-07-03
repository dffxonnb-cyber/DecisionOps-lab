# Architecture Diagram

This document gives a visual overview of DecisionOps Lab.

The goal is to make the workflow easy to understand before reading the code.

## End-to-End Workflow

```mermaid
flowchart TD
    A[generate_dataset.py] --> B[Raw CSV Files]
    B --> C[DuckDB Raw Tables]
    C --> D[SQL Staging Models]
    D --> E[SQL Intermediate Models]
    E --> F[SQL Mart Tables]
    F --> G[Data Quality Checks]
    F --> H[Experiment Analysis]
    G --> I[Decision Memo]
    H --> I
    I --> J[Reviewer HTML Report]
    H --> K[Scenario Matrix]
    G --> K
    K --> L[Scenario Matrix Report]
    J --> M[Portfolio Reviewer]
    L --> M
```

## SQL Modeling Layers

```mermaid
flowchart LR
    A[raw_users] --> B[stg_users]
    C[raw_events] --> D[stg_events]
    E[raw_sessions] --> F[stg_sessions]
    G[raw_experiments] --> H[stg_experiments]
    I[raw_payments] --> J[stg_payments]

    B --> K[int_user_activation]
    D --> K
    H --> K

    B --> L[int_user_retention]
    D --> L

    K --> M[int_experiment_user_metrics]
    L --> M
    F --> M

    M --> N[mart_experiment_result]
    M --> O[mart_segment_performance]
    L --> P[mart_retention_cohort]
    N --> Q[mart_decision_summary]
```

## Decision Rule Flow

```mermaid
flowchart TD
    A[Start] --> B{Data quality status}
    B -->|FAIL| C[Investigate]
    B -->|PASS or WARN| D{Activation lift greater than 0?}
    D -->|No| E[Hold]
    D -->|Yes| F{p-value less than 0.05?}
    F -->|No| G[Retest]
    F -->|Yes| H{D7 revisit check passes?}
    H -->|No| G
    H -->|Yes| I[Ship]
```

## Scenario Matrix Flow

```mermaid
flowchart TD
    A[run_scenario_matrix.py] --> B[strong_positive]
    A --> C[guardrail_risk]
    A --> D[weak_evidence]
    A --> E[neutral]
    A --> F[quality_failure]

    B --> G[Ship]
    C --> H[Retest]
    D --> H
    E --> I[Hold]
    F --> J[Investigate]

    G --> K[scenario_matrix.md]
    H --> K
    I --> K
    J --> K
```

## Verification Flow

```mermaid
flowchart TD
    A[run_full_verification.py] --> B[Generate Default Dataset]
    B --> C[Run SQL Pipeline]
    C --> D[Run Quality Checks]
    D --> E[Run Experiment Analysis]
    E --> F[Generate Decision Memo]
    F --> G[Generate Reviewer Report]
    G --> H[Run Scenario Matrix]
    H --> I[Run Pytest]
    I --> J[Verification Complete]
```

## Main Commands

Run the full workflow locally:

```bash
python scripts/run_full_verification.py
```

Run only the scenario matrix:

```bash
python scripts/run_scenario_matrix.py
```

Run the default strong-positive case manually:

```bash
python scripts/generate_dataset.py --scenario strong_positive
python scripts/run_pipeline.py
python scripts/run_quality_checks.py
python scripts/run_experiment_analysis.py
python scripts/generate_decision_memo.py
python scripts/generate_review_report.py
pytest
```

## What to Review First

Recommended review order:

1. `reports/review_report.html`
2. `reports/scenario_matrix.md`
3. `docs/DECISION_RULES.md`
4. `docs/MART_LAYER.md`
5. `scripts/run_full_verification.py`

## Claim Boundary

This architecture is designed for a public portfolio project using synthetic data. It demonstrates workflow design and reproducibility, not production infrastructure scale.