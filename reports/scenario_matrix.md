# Scenario Matrix

DecisionOps Lab runs the same pipeline across multiple synthetic experiment scenarios.

| Scenario | Quality | A Activation | B Activation | Lift | D7 Delta | Refund Delta | Session Delta | Session Guardrail | Overall Guardrail | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| strong_positive | PASS | 30.15% | 34.12% | 3.97% | 0.97% | -0.02% | 1.93% | PASS | PASS | Ship |
| guardrail_risk | PASS | 31.17% | 34.50% | 3.34% | -16.11% | 0.08% | -16.09% | WARN | WARN | Retest |
| refund_risk | PASS | 29.44% | 35.20% | 5.76% | 0.14% | 1.84% | -0.17% | PASS | WARN | Retest |
| session_activity_risk | PASS | 29.52% | 34.75% | 5.23% | -11.52% | 0.08% | -10.65% | WARN | WARN | Retest |
| weak_evidence | PASS | 30.02% | 30.69% | 0.67% | 0.46% | 0.14% | 0.44% | PASS | PASS | Retest |
| neutral | PASS | 29.17% | 28.85% | -0.32% | -0.90% | 0.00% | -0.81% | PASS | PASS | Hold |
| quality_failure | FAIL | 29.27% | 34.06% | 4.79% | 1.20% | -0.10% | 1.60% | PASS | PASS | Investigate |

## Scenario Purpose

- `strong_positive`: primary metric improves and guardrails remain stable.
- `guardrail_risk`: primary metric improves but D7 revisit weakens.
- `refund_risk`: primary metric improves but refund rate increases enough to warn.
- `session_activity_risk`: primary metric improves but average sessions per user drop enough to warn.
- `weak_evidence`: primary metric improves only slightly.
- `neutral`: primary metric does not improve meaningfully.
- `quality_failure`: raw experiment data contains invalid variant values, so quality checks fail.
