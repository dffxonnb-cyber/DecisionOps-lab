# Scenario Mode

DecisionOps Lab includes scenario mode to verify that the workflow is not tied to one fixed experiment outcome.

The same pipeline can generate different synthetic product situations, run the SQL models, check data quality, analyze the experiment, and summarize the final recommendation.

## Why Scenario Mode Exists

A single positive result can make a portfolio project look hard-coded. Scenario mode shows that the decision workflow changes when the data-generating condition changes.

The goal is to prove this pattern:

```text
same pipeline
+ different synthetic conditions
= different decision outcomes
```

## Supported Scenarios

| Scenario | Purpose | Expected Outcome |
| --- | --- | --- |
| `strong_positive` | Variant B improves activation and guardrails remain stable | Ship |
| `guardrail_risk` | Variant B improves activation but D7 revisit weakens | Retest |
| `refund_risk` | Variant B improves activation but refund rate increases | Retest |
| `weak_evidence` | Variant B improves activation only slightly | Retest |
| `neutral` | Variant B does not improve activation meaningfully | Hold |
| `quality_failure` | Raw experiment data contains invalid variant values | Investigate |

## How to Run One Scenario

```bash
python scripts/generate_dataset.py --scenario strong_positive
python scripts/run_pipeline.py
python scripts/run_quality_checks.py
python scripts/run_experiment_analysis.py
python scripts/generate_decision_memo.py
python scripts/generate_review_report.py
pytest
```

Change the scenario name to run a different condition:

```bash
python scripts/generate_dataset.py --scenario refund_risk
```

## How to Run the Full Matrix

```bash
python scripts/run_scenario_matrix.py
pytest
```

This creates:

```text
reports/scenario_matrix.json
reports/scenario_matrix.md
```

After the matrix is generated, the script restores the default `strong_positive` report artifacts so the main reviewer report still represents the primary demonstration case.

## Scenario Matrix Output

The scenario matrix summarizes the decision workflow across six generated conditions:

| Field | Meaning |
| --- | --- |
| `scenario` | Synthetic condition used to generate the data |
| `quality_status` | Data quality result before interpreting the experiment |
| `variant_a_activation` | Baseline activation rate |
| `variant_b_activation` | Treatment activation rate |
| `absolute_lift` | Treatment minus baseline activation rate |
| `d7_revisit_delta` | Treatment minus baseline D7 revisit rate |
| `refund_rate_delta` | Treatment minus baseline refund rate |
| `session_activity_status` | PASS or WARN for the session activity guardrail |
| `guardrail_status` | PASS or WARN for the overall multi-guardrail review |
| `decision` | Final recommendation from the decision rule |

## Guardrail Risk Scenarios

The `guardrail_risk` scenario demonstrates that activation lift should not be enough to Ship if D7 revisit behavior weakens.

The `refund_risk` scenario demonstrates that activation lift should not be enough to Ship if refund behavior worsens.

Expected behavior:

```text
activation lift > 0
quality_status = PASS or WARN
guardrail_status = WARN
final decision = Retest
```

## Quality Failure Scenario

The `quality_failure` scenario intentionally places invalid variant values in the raw experiment assignment table.

This allows the project to demonstrate a critical rule: when data quality fails, the workflow should not treat the experiment result as decision-ready evidence.

Expected behavior:

```text
quality_status = FAIL
final decision = Investigate
```

## Claim Boundary

Scenario mode does not simulate real product behavior. It is a reproducible way to test whether the analytics workflow handles multiple decision situations.
