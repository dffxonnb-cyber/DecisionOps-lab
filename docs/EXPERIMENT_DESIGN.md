# Experiment Design

## 1. Experiment Question

Does the new onboarding flow, Variant B, increase the share of new users who create their first routine within 24 hours after signup?

---

## 2. Experiment Context

The product is a routine / study habit app.

New users are randomly assigned to one of two onboarding experiences:

| Variant | Description |
| --- | --- |
| A | Existing onboarding flow |
| B | New onboarding flow with clearer first-routine guidance |

The product team wants to decide whether Variant B should be shipped to all new users.

---

## 3. Hypotheses

### Null Hypothesis

Variant B does not improve activation rate compared with Variant A.

### Alternative Hypothesis

Variant B improves activation rate compared with Variant A.

---

## 4. Metric Setup

## 4-1. Primary Metric

Activation Rate

```text
activation_rate = users who created first routine within 24 hours / assigned users
```

## 4-2. Secondary Metrics

- Onboarding Completion Rate
- Routine Completion Rate
- Trial Start Rate

## 4-3. Guardrail Metrics

- D7 Retention
- Refund Rate
- Session Drop-off

Guardrail metrics are used to ensure the experiment does not improve activation by harming later user quality.

---

## 5. Assignment Unit

The experiment unit is `user_id`.

Each user should be assigned to exactly one variant for the experiment.

Expected assignment:

```text
user_id → experiment_name → variant
```

---

## 6. Statistical Analysis

V1 will use a two-proportion test for activation rate difference.

Planned outputs:

| Output | Description |
| --- | --- |
| activation_a | Activation rate for Variant A |
| activation_b | Activation rate for Variant B |
| absolute_lift | activation_b - activation_a |
| relative_lift | absolute_lift / activation_a |
| p_value | Statistical evidence for difference |
| confidence_interval | Uncertainty range for lift |
| sample_size_a | Number of assigned users in A |
| sample_size_b | Number of assigned users in B |

---

## 7. Segment Diagnostics

The experiment result should be checked by segment.

Planned segments:

- acquisition_channel
- device_type
- age_group

Segment diagnostics can reveal cases where the overall result hides uneven effects.

Example:

```text
Overall: Ship
Paid Search: weak lift
Organic: strong lift
Mobile: strong lift
Desktop: neutral
```

This does not automatically change the decision, but it can add caution or recommend follow-up analysis.

---

## 8. Decision Rules

| Evidence | Decision |
| --- | --- |
| Data quality FAIL | Investigate |
| Activation improves, p-value < 0.05, guardrails stable | Ship |
| Activation improves, p-value between 0.05 and 0.10, guardrails stable | Retest |
| Activation improves, but D7 retention or refund rate worsens | Hold |
| Activation does not improve | Hold |
| Strong lift only in some segments | Partial Rollout or Segment Follow-up |

---

## 9. Experiment Result Artifact

The analysis script should create `reports/experiment_result.json`.

Example:

```json
{
  "experiment_name": "onboarding_v2",
  "primary_metric": "activation_rate",
  "variant_a": {
    "users": 5000,
    "activated_users": 1910,
    "activation_rate": 0.382
  },
  "variant_b": {
    "users": 5000,
    "activated_users": 2185,
    "activation_rate": 0.437
  },
  "absolute_lift": 0.055,
  "relative_lift": 0.144,
  "p_value": 0.018,
  "guardrails": {
    "d7_retention_delta": 0.002,
    "refund_rate_delta": 0.000
  },
  "suggested_decision": "Ship"
}
```

---

## 10. Claim Boundary

This experiment is synthetic.

The project does not claim that a real onboarding flow improved. It claims that the workflow can calculate, check, interpret, and document an experiment result.
