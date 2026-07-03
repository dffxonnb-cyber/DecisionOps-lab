# Scenario Matrix

DecisionOps Lab runs the same pipeline across multiple synthetic experiment scenarios.

| Scenario | Quality | A Activation | B Activation | Lift | D7 Delta | Guardrail | Decision |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| strong_positive | PASS | 30.15% | 34.12% | 3.97% | 0.97% | PASS | Ship |
| guardrail_risk | PASS | 31.17% | 34.50% | 3.34% | -16.11% | WARN | Retest |
| weak_evidence | PASS | 30.02% | 30.69% | 0.67% | 0.46% | PASS | Retest |
| neutral | PASS | 29.17% | 28.85% | -0.32% | -0.90% | PASS | Hold |
| quality_failure | FAIL | 29.27% | 34.06% | 4.79% | 1.20% | PASS | Investigate |

## Scenario Purpose

- `strong_positive`: primary metric improves and D7 revisit remains stable.
- `guardrail_risk`: primary metric improves but D7 revisit weakens.
- `weak_evidence`: primary metric improves only slightly.
- `neutral`: primary metric does not improve meaningfully.
- `quality_failure`: raw experiment data contains invalid variant values, so quality checks fail.
