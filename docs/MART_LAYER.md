# Mart Layer

DecisionOps Lab separates intermediate modeling tables from final analysis marts.

The mart layer exists so that reviewer-facing artifacts and downstream analysis do not depend directly on raw events or low-level transformation logic.

## Data Flow

```text
raw CSV files
→ DuckDB raw tables
→ staging models
→ intermediate models
→ mart models
→ quality / experiment / memo / report artifacts
```

## Mart Tables

| Mart | Grain | Purpose |
| --- | --- | --- |
| `mart_experiment_result` | One row per scenario, experiment, and variant | Summarizes A/B performance, retention, monetization, and engagement guardrails by variant |
| `mart_segment_performance` | One row per scenario, segment dimension, segment value, and variant | Compares activation and D7 revisit by segment |
| `mart_retention_cohort` | One row per signup week | Summarizes D1, D3, and D7 revisit behavior by cohort |
| `mart_decision_summary` | One row per scenario and experiment | Collects key metrics needed for recommendation review |

## Why This Layer Matters

Without final marts, analysis scripts often query raw or intermediate tables directly. That makes the project harder to review and harder to reuse.

The mart layer gives the project a cleaner analytics engineering structure:

```text
model once
reuse many times
```

## Table Details

### `mart_experiment_result`

This table summarizes experiment performance by variant.

Key fields:

```text
scenario
experiment_name
variant
users
activated_users
activation_rate
d1_revisit_rate
d3_revisit_rate
d7_revisit_rate
avg_sessions
avg_session_seconds
trial_users
trial_start_rate
paid_users
paid_conversion_rate
refunded_users
refund_rate
total_paid_amount
total_refund_amount
```

### `mart_segment_performance`

This table makes segment diagnostics easier to inspect.

Supported segment dimensions:

```text
acquisition_channel
device_type
age_group
```

Key fields:

```text
scenario
segment_dimension
segment_value
variant
users
activation_rate
d7_revisit_rate
```

### `mart_retention_cohort`

This table summarizes revisit behavior by signup week.

Key fields:

```text
signup_week
users
d1_revisit_rate
d3_revisit_rate
d7_revisit_rate
```

### `mart_decision_summary`

This table compresses the experiment into the metrics needed for final recommendation review.

Key fields:

```text
scenario
experiment_name
variant_a_activation_rate
variant_b_activation_rate
activation_absolute_lift
activation_relative_lift
variant_a_d7_revisit_rate
variant_b_d7_revisit_rate
d7_revisit_delta
evidence_status
```

## Reviewer Report Integration

The reviewer HTML report reads the DuckDB database and displays the mart layer summary. This shows that the final artifacts are backed by SQL-modeled tables rather than one-off calculations.

V2-1 also uses the expanded experiment mart to support multi-guardrail review across retention, monetization quality, and engagement behavior.

## Claim Boundary

The mart layer is designed for portfolio review and reproducibility. It is not a production warehouse schema.
