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
    H --> I[Multi-Guardrail Review]
    G --> J[Decision Memo]
    I --> J
    J --> K[Reviewer HTML Report]
    I --> L[Scenario Matrix]
    G --> L
    L --> M[Scenario Matrix Report]
    K --> N[Portfolio Reviewer]
    M --> N
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

    B --> M[int_user_monetization]
    J --> M

    K --> N[int_experiment_user_metrics]
    L --> N
    F --> N
    M --> N

    N --> O[mart_experiment_result]
    N --> P[mart_segment_performance]
    L --> Q[mart_retention_cohort]
    O --> R[mart_decision_summary]
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
    F -->|Yes| H{All guardrails pass?}
    H -->|No| G
    H -->|Yes| I[Ship]

    J[D7 revisit] --> H
    K[Refund rate] --> H
    L[Session activity] --> H
```

## Scenario Matrix Flow

```mermaid
flowchart TD
    A[run_scenario_matrix.py] --> B[strong_positive]
    A --> C[guardrail_risk]
    A --> D[refund_risk]
    A --> E[weak_evidence]
    A --> F[neutral]
    A --> G[quality_failure]

    B --> H[Ship]
    C --> I[Retest]
    D --> I
    E --> I
    F --> J[Hold]
    G --> K[Investigate]

    H --> L[scenario_matrix.md]
    I --> L
    J --> L
    K --> L
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
    I --> J[Upload decisionops-reports Artifact]
    J --> K[Verification Complete]
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
4. `docs/V2_GUARDRAILS.md`
5. `docs/MART_LAYER.md`
6. `scripts/run_full_verification.py`

## Claim Boundary

This architecture is designed for a public portfolio project using synthetic data. It demonstrates workflow design and reproducibility, not production infrastructure scale.
