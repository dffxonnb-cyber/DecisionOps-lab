# Decision Rules

DecisionOps Lab turns experiment evidence into a recommendation only after checking data quality and guardrail behavior.

The project uses synthetic data, so the rules are not business policy. They are a portfolio demonstration of how an analytics workflow can separate evidence from recommendation.

## Inputs

The recommendation uses these inputs:

| Input | Source | Purpose |
| --- | --- | --- |
| Data quality status | `reports/quality_report.json` | Prevents using broken data as evidence |
| Primary metric | `activation_rate` | Measures whether Variant B improves first-routine creation |
| Statistical evidence | p-value and confidence interval | Checks whether the lift is strong enough to trust |
| Guardrail metric | `d7_revisit_rate` | Checks whether short-term activation hurts later revisit behavior |

## Decision Table

| Condition | Recommendation |
| --- | --- |
| Data quality fails | Investigate |
| Primary metric improves with strong evidence and D7 revisit check passes | Ship |
| Primary metric improves but evidence is weak | Retest |
| Primary metric improves but D7 revisit check warns | Retest |
| Primary metric does not improve | Hold |

## Current Rule Logic

```text
IF data quality fails:
    Investigate
ELSE IF activation lift > 0 AND p-value < 0.05 AND D7 revisit check passes:
    Ship
ELSE IF activation lift > 0:
    Retest
ELSE:
    Hold
```

## Why D7 Revisit Is a Guardrail

Activation can improve while later user behavior gets worse. For example, a more aggressive onboarding flow may push users to create a routine quickly, but reduce the chance that they return later.

That is why DecisionOps Lab does not use activation alone. It also checks whether Variant B weakens D7 revisit behavior.

## Scenario Examples

| Scenario | Expected Recommendation | Reason |
| --- | --- | --- |
| `strong_positive` | Ship | Activation improves and D7 revisit stays stable |
| `guardrail_risk` | Retest | Activation improves, but D7 revisit weakens |
| `weak_evidence` | Retest | Activation improvement is too small or weak |
| `neutral` | Hold | Activation does not improve meaningfully |

## Claim Boundary

These rules are intentionally simple. They demonstrate a decision workflow, not a universal experimentation policy.