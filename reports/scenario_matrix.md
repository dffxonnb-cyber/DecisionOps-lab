# Scenario Matrix

DecisionOps Lab runs the same pipeline across multiple synthetic experiment scenarios.

| Scenario | Quality | A Activation | B Activation | Lift | D7 Delta | Refund Delta | Session Guardrail | Overall Guardrail | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| strong_positive | PASS | 30.15% | 34.12% | 3.97% | 0.97% | -0.02% | PASS | PASS | Ship |
| guardrail_risk | PASS | 31.17% | 34.50% | 3.34% | -16.11% | 0.08% | WARN | WARN | Retest |
| refund_risk | PASS | 29.44% | 35.20% | 5.76% | 0.14% | 1.84% | PASS | WARN | Retest |
| weak_evidence | PASS | 30.02% | 30.69% | 0.67% | 0.46% | 0.14% | PASS | PASS | Retest |
| neutral | PASS | 29.17% | 28.85% | -0.32% | -0.90% | 0.00% | PASS | PASS | Hold |
| quality_failure | FAIL | 29.27% | 34.06% | 4.79% | 1.20% | -0.10% | PASS | PASS | Investigate |

## Scenario Purpose

- `strong_positive`: primary metric improves and guardrails remain stable.
- `guardrail_risk`: primary metric improves but D7 revisit weakens.
- `refund_risk`: primary metric improves but refund rate increases enough to warn.
- `weak_evidence`: primary metric improves only slightly.
- `neutral`: primary metric does not improve meaningfully.
- `quality_failure`: raw experiment data contains invalid variant values, so quality checks fail.
