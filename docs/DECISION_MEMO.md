# Decision Memo

## 1. Purpose

DecisionOps Lab ends with a decision memo, not just an analysis result.

The memo should answer:

> Based on data quality, experiment evidence, and guardrail metrics, what should the product team do next?

---

## 2. Decision Types

| Decision | Meaning |
| --- | --- |
| Ship | Roll out the tested variant |
| Hold | Do not roll out the tested variant |
| Retest | Run another experiment with more data or improved design |
| Investigate | Pause decision-making because data quality or metric behavior is suspicious |
| Partial Rollout | Ship only to selected segments or cohorts |

---

## 3. Decision Inputs

The decision memo uses three evidence groups.

### 3-1. Data Quality

Input artifact:

```text
reports/quality_report.json
```

Key fields:

- overall status
- failed checks
- warning checks
- freshness result
- experiment balance result

### 3-2. Experiment Result

Input artifact:

```text
reports/experiment_result.json
```

Key fields:

- activation rate by variant
- absolute lift
- relative lift
- p-value
- confidence interval
- sample size

### 3-3. Guardrail Metrics

Key guardrails:

- D7 retention delta
- refund rate delta
- session drop-off delta

---

## 4. Decision Rule Order

Decision rules should be evaluated in this order.

### Rule 1. Data Quality Gate

```text
if quality_status == FAIL:
    decision = Investigate
```

No experiment result should override a failed quality gate.

### Rule 2. Guardrail Gate

```text
if guardrail_metric_worsened_meaningfully:
    decision = Hold
```

A primary metric win should not hide downstream harm.

### Rule 3. Primary Metric Evidence

```text
if primary_metric_lift > 0 and p_value < 0.05:
    decision = Ship
elif primary_metric_lift > 0 and p_value < 0.10:
    decision = Retest
else:
    decision = Hold
```

### Rule 4. Segment Risk

If some segments have strong negative results, the memo should add caution or suggest partial rollout.

---

## 5. Memo Template

```text
# Decision Memo: Onboarding Variant B

## Decision

Ship Variant B

## Summary

Variant B improved activation rate without meaningful guardrail decline. Data quality checks passed, and the experiment result is strong enough to support rollout.

## Evidence

- Activation Rate A: 38.2%
- Activation Rate B: 43.7%
- Absolute Lift: +5.5 percentage points
- Relative Lift: +14.4%
- p-value: 0.018
- D7 Retention Delta: +0.2 percentage points
- Refund Rate Delta: no meaningful change
- Data Quality Status: PASS

## Cautions

- Paid acquisition users showed weaker lift than organic users.
- D14 retention should be monitored after rollout.

## Next Actions

1. Roll out Variant B to 100% of new users.
2. Monitor D14 retention and refund rate after rollout.
3. Run follow-up analysis for paid acquisition users.

## Claim Boundary

This memo is based on synthetic data and demonstrates the decision workflow, not real product performance.
```

---

## 6. Memo Quality Standard

A decision memo should be:

- short enough to read quickly
- specific about the decision
- clear about evidence
- honest about cautions
- explicit about next actions
- careful about claim boundary

The memo should not overclaim statistical certainty or business impact.

---

## 7. Portfolio Value

This memo is the bridge between analytics and product judgment.

It shows that the project does not stop at charts or metrics. It produces a usable decision artifact.
