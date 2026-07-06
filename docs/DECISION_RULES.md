# Decision Rules

DecisionOps Lab turns experiment evidence into a recommendation only after checking data quality, primary metric evidence, and guardrail behavior.

The project uses synthetic data, so the rules are not business policy. They are a portfolio demonstration of how an analytics workflow can separate evidence from recommendation.

## Inputs

The recommendation uses these inputs:

| Input | Source | Purpose |
| --- | --- | --- |
| Data quality status | `reports/quality_report.json` | Prevents using broken data as evidence |
| Primary metric | `activation_rate` | Measures whether Variant B improves first-routine creation |
| Statistical evidence | p-value and confidence interval | Checks whether the lift is strong enough to trust |
| Retention guardrail | `d7_revisit_rate` | Checks whether short-term activation hurts later revisit behavior |
| Monetization guardrail | `refund_rate` | Checks whether the treatment creates worse-fit monetization behavior |
| Engagement guardrail | `avg_sessions` | Checks whether the new flow reduces session activity |

## Decision Table

| Condition | Recommendation |
| --- | --- |
| Data quality fails | Investigate |
| Primary metric improves with strong evidence and all guardrails pass | Ship |
| Primary metric improves but evidence is weak | Retest |
| Primary metric improves but any guardrail warns | Retest |
| Primary metric does not improve | Hold |

## Current Rule Logic

```text
IF data quality fails:
    Investigate
ELSE IF activation lift > 0 AND p-value < 0.05 AND all guardrails pass:
    Ship
ELSE IF activation lift > 0:
    Retest
ELSE:
    Hold
```

## Why Multi-Guardrail Review Matters

Activation can improve while later user behavior gets worse. For example, a more aggressive onboarding flow may push users to create a routine quickly, but reduce the chance that they return later.

V2-1 extends the guardrail review beyond D7 revisit. It also checks refund rate and session activity so the recommendation is not based only on a short-term primary metric lift.

## Guardrail Thresholds

These thresholds are intentionally simple and portfolio-level.

| Guardrail | WARN Rule |
| --- | --- |
| D7 revisit | Variant B delta < -1 percentage point |
| Refund rate | Variant B delta > +1 percentage point |
| Session activity | Variant B average sessions per user drops by more than 5% |

## Scenario Examples

| Scenario | Expected Recommendation | Reason |
| --- | --- | --- |
| `strong_positive` | Ship | Activation improves and guardrails stay stable |
| `guardrail_risk` | Retest | Activation improves, but D7 revisit weakens |
| `weak_evidence` | Retest | Activation improvement is too small or weak |
| `neutral` | Hold | Activation does not improve meaningfully |
| `quality_failure` | Investigate | Quality checks fail before evidence can be trusted |

## Claim Boundary

These rules are intentionally simple. They demonstrate a decision workflow, not a universal experimentation policy.
