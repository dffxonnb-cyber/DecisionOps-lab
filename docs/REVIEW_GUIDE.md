# Reviewer Guide

This guide is for someone reviewing DecisionOps Lab quickly.

DecisionOps Lab is not a dashboard-only analytics project. It demonstrates an end-to-end product analytics workflow: raw product events become SQL models, data quality checks, experiment evidence, multi-guardrail review, decision memo, scenario matrix, and reviewer-facing artifacts.

## 5-Minute Review Path

Start here:

1. Read the README evidence snapshot.
2. Open `reports/review_report.html` for the main reviewer-facing report.
3. Open `reports/scenario_matrix.md` to see how the decision rule behaves across scenarios.
4. Read `docs/V2_GUARDRAILS.md` to understand the multi-guardrail workflow.
5. Read `docs/DECISION_RULES.md` to understand the recommendation logic.
6. Read `docs/MART_LAYER.md` to understand the final SQL mart structure.

## Main Artifacts

| Artifact | Purpose |
| --- | --- |
| `reports/review_report.html` | Main reviewer report for the default strong-positive case |
| `reports/scenario_matrix.md` | Scenario-level summary across Ship, Retest, Hold, and Investigate outcomes |
| `reports/quality_report.json` | Data quality results |
| `reports/experiment_result.json` | A/B test and multi-guardrail evidence |
| `reports/decision_memo.md` | Final recommendation memo with Guardrail Review |

## Verification Command

Run the full workflow with one command:

```bash
python scripts/run_full_verification.py
```

This command rebuilds the default dataset, runs the SQL pipeline, checks data quality, analyzes the experiment, generates the memo and reviewer report, runs the full scenario matrix, and executes tests.

## What This Project Demonstrates

| Area | Evidence in Repo |
| --- | --- |
| Analytics engineering | Staging, intermediate, and mart SQL layers |
| Product analytics | Activation, retention, monetization, experiment, and guardrail metrics |
| Data quality | PASS / WARN / FAIL quality report before interpretation |
| Experiment analysis | A/B lift, p-value, confidence interval, segment diagnostics, and guardrail review |
| Decision workflow | Ship / Retest / Hold / Investigate recommendation logic |
| Reproducibility | One-command verification and GitHub Actions workflow |
| Communication | Decision memo and reviewer-facing HTML report |

## Scenario Matrix

The scenario matrix shows that the project is not hard-coded to one result.

| Scenario | Expected Decision | Why It Matters |
| --- | --- | --- |
| `strong_positive` | Ship | Primary metric improves and guardrails remain stable |
| `guardrail_risk` | Retest | Primary metric improves but D7 revisit weakens |
| `refund_risk` | Retest | Primary metric improves but refund rate worsens |
| `weak_evidence` | Retest | Primary metric improves only slightly |
| `neutral` | Hold | Primary metric does not improve meaningfully |
| `quality_failure` | Investigate | Data quality fails before evidence can be trusted |

## Suggested Interview Talking Point

A useful summary:

> I built DecisionOps Lab to show the layer between raw analysis and product decision-making. The workflow checks data quality before interpreting an experiment, uses retention, refund, and session behavior as guardrails against short-term metric chasing, and runs multiple synthetic scenarios to prove the recommendation logic is not hard-coded.

## Claim Boundary

The project uses synthetic data. It does not claim real product performance, real business impact, or real user behavior. The claim is about workflow design, reproducibility, data modeling, and decision communication.
