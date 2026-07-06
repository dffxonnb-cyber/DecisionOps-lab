# V2-1 Multi-Guardrail Decision Workflow

DecisionOps Lab V2-1 extends the V1 decision workflow from a single D7 revisit guardrail into a multi-guardrail review.

The goal is to show that the project does not recommend `Ship` only because the primary metric improves. A product decision should consider whether the improvement creates downstream risk.

## Decision Principle

```text
quality first
→ primary metric evidence
→ retention guardrail
→ monetization guardrail
→ engagement guardrail
→ recommendation
```

## Guardrails

| Guardrail | Metric | Risk Checked |
| --- | --- | --- |
| Retention | `d7_revisit_rate` | Variant B may increase activation but weaken later return behavior. |
| Monetization quality | `refund_rate` | Variant B may push users into worse-fit conversion behavior. |
| Engagement behavior | `avg_session_seconds` | Variant B may push users through onboarding too aggressively. |

## Portfolio Thresholds

These thresholds are intentionally simple. They are portfolio-level decision rules, not universal business policy.

| Guardrail | PASS / WARN Rule |
| --- | --- |
| D7 revisit | WARN if Variant B delta is below -1 percentage point. |
| Refund rate | WARN if Variant B delta is above +1 percentage point. |
| Session duration | WARN if Variant B average session duration drops by more than 5%. |

## Recommendation Logic

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

## Main Artifacts

| Artifact | Purpose |
| --- | --- |
| `reports/experiment_result.json` | Stores primary metric evidence and multi-guardrail output. |
| `reports/decision_memo.md` | Explains the recommendation and guardrail review. |
| `reports/review_report.html` | Shows the reviewer-facing multi-guardrail summary. |
| `reports/scenario_matrix.md` | Verifies that the workflow can produce multiple decisions. |

## Claim Boundary

This project uses synthetic data. V2-1 does not claim real product performance, real user behavior, or real business impact.

The claim is that the workflow is reproducible, reviewable, and structured around safer product decision-making.
