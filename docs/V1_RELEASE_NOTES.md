# V1 Release Notes

DecisionOps Lab V1 is the first complete version of the project.

The goal of V1 is to demonstrate a reproducible product analytics workflow that moves from raw product events to quality-checked experiment evidence, guardrail review, decision memo generation, scenario testing, and CI verification.

## V1 Status

```text
Status: Complete
Verification: Local + GitHub Actions
Primary demo scenario: strong_positive
```

## What V1 Includes

| Area | Completed |
| --- | --- |
| Synthetic data generation | Yes |
| Scenario mode | Yes |
| DuckDB SQL pipeline | Yes |
| Staging SQL models | Yes |
| Intermediate SQL models | Yes |
| Final mart tables | Yes |
| Data quality checks | Yes |
| A/B experiment analysis | Yes |
| D7 revisit guardrail | Yes |
| Decision memo generation | Yes |
| Reviewer HTML report | Yes |
| Scenario matrix | Yes |
| Pytest contract tests | Yes |
| GitHub Actions verification | Yes |
| Reviewer documentation | Yes |

## Main Workflow

```text
synthetic raw data
→ DuckDB raw tables
→ staging SQL
→ intermediate SQL
→ mart SQL
→ quality checks
→ experiment analysis
→ guardrail review
→ decision memo
→ reviewer report
→ scenario matrix
→ tests
→ GitHub Actions
```

## Main Artifacts

| Artifact | Purpose |
| --- | --- |
| `reports/review_report.html` | Main reviewer-facing report |
| `reports/scenario_matrix.md` | Scenario matrix summary |
| `reports/quality_report.json` | Quality check artifact |
| `reports/experiment_result.json` | Experiment and guardrail artifact |
| `reports/decision_memo.md` | Evidence-to-recommendation memo |

## Scenario Outcomes

V1 verifies that the decision workflow is not hard-coded to a single result.

| Scenario | Expected Decision | Meaning |
| --- | --- | --- |
| `strong_positive` | Ship | Activation improves and D7 revisit remains stable |
| `guardrail_risk` | Retest | Activation improves but D7 revisit weakens |
| `weak_evidence` | Retest | Activation improves only slightly |
| `neutral` | Hold | Activation does not improve meaningfully |
| `quality_failure` | Investigate | Data quality fails before evidence can be trusted |

## Final Mart Tables

| Mart | Purpose |
| --- | --- |
| `mart_experiment_result` | Variant-level experiment result summary |
| `mart_segment_performance` | Segment-level performance diagnostics |
| `mart_retention_cohort` | Signup-week retention summary |
| `mart_decision_summary` | One-row decision evidence summary per scenario |

## Verification

Run the full local verification workflow:

```bash
python scripts/run_full_verification.py
```

This command rebuilds the default report artifacts, runs all scenario cases, and executes the test suite.

GitHub Actions runs the same full verification runner on push and pull request.

## What V1 Demonstrates

V1 demonstrates these capabilities:

- SQL-based product analytics modeling
- Raw / staging / intermediate / mart layer separation
- Data quality checks before evidence interpretation
- A/B test analysis with statistical evidence
- Guardrail metric thinking with D7 revisit
- Decision memo generation
- Scenario-based validation of recommendation logic
- Reproducibility through local command and CI
- Portfolio-ready documentation and review flow

## Known Boundaries

V1 uses synthetic data. It does not claim real product performance, real user behavior, or real business impact.

The claim is about workflow design, reproducibility, data modeling, quality checks, and decision communication.

## V2 Candidates

Possible future improvements:

- Migrate SQL models to dbt Core.
- Add a lightweight dashboard from mart tables.
- Add richer cohort analysis.
- Add saved sample data for no-regeneration review.
- Add more quality failure scenarios.
- Add visual report export or GitHub Pages publishing.
- Add event-level data dictionary.

## V1 Closeout Summary

DecisionOps Lab V1 is complete as a portfolio-ready analytics workflow. Further work should be treated as V2 rather than continuous V1 patching.