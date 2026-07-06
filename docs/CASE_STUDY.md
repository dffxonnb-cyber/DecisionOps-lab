# DecisionOps Lab Case Study

DecisionOps Lab is a product analytics and analytics engineering portfolio project. It turns synthetic product event data into SQL models, quality checks, experiment evidence, multi-guardrail review, decision memos, scenario testing, and reviewer-facing reports.

## One-Line Summary

I built a reproducible workflow that moves from raw product events to a decision-ready experiment recommendation, with data quality checks and retention, refund, and session activity guardrails before any final recommendation is made.

## Problem

Many analytics portfolio projects stop at a chart, dashboard, or model score. That makes it hard to evaluate whether the analysis could support a real product decision.

DecisionOps Lab asks a different question:

> Can an analytics workflow turn raw event data into a reproducible, quality-checked, guardrail-aware experiment memo?

## Product Scenario

The synthetic product is a routine / study habit app.

A new onboarding variant is being tested. The product team wants to know whether Variant B increases the share of new users who create their first routine within 24 hours after signup.

However, the project does not use activation alone. It also checks D7 revisit, refund rate, and session activity as guardrails.

## Core Design

```text
raw product events
→ DuckDB raw tables
→ SQL staging models
→ SQL intermediate models
→ SQL mart tables
→ quality checks
→ experiment analysis
→ multi-guardrail review
→ decision memo
→ reviewer report
→ scenario matrix
```

## What I Built

| Layer | Output |
| --- | --- |
| Data generation | Reproducible synthetic raw CSVs with scenario modes |
| SQL modeling | Staging, intermediate, and mart tables in DuckDB |
| Quality checks | PASS / WARN / FAIL report before interpretation |
| Experiment analysis | Activation lift, p-value, confidence interval, segment diagnostics |
| Guardrail review | D7 revisit, refund rate, session activity, and overall guardrail status |
| Decision memo | Ship / Retest / Hold / Investigate recommendation |
| Reviewer report | Static HTML report for quick portfolio review |
| Scenario matrix | Seven synthetic scenarios to test decision behavior |
| CI verification | GitHub Actions workflow using one full verification runner |

## Key Artifacts

| Artifact | Why It Matters |
| --- | --- |
| `reports/review_report.html` | Shows the main result in a reviewer-friendly format |
| `reports/scenario_matrix.md` | Shows that the decision rule changes across scenarios |
| `reports/quality_report.json` | Shows data quality checks before interpretation |
| `reports/experiment_result.json` | Stores experiment and multi-guardrail evidence |
| `reports/decision_memo.md` | Converts evidence into a recommendation memo |
| `scripts/run_full_verification.py` | Rebuilds and tests the whole workflow with one command |

## Scenario Matrix

The scenario matrix is the strongest evidence that the project is not hard-coded to a single result.

| Scenario | Expected Decision | Purpose |
| --- | --- | --- |
| `strong_positive` | Ship | Activation improves and guardrails remain stable |
| `guardrail_risk` | Retest | Activation improves but D7 revisit weakens |
| `refund_risk` | Retest | Activation improves but refund rate worsens |
| `session_activity_risk` | Retest | Activation improves but average sessions per user drop |
| `weak_evidence` | Retest | Activation improves only slightly |
| `neutral` | Hold | Activation does not improve meaningfully |
| `quality_failure` | Investigate | Data quality fails before evidence can be trusted |

## Decision Logic

The workflow does not treat every positive lift as decision-ready.

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

## Why This Project Matters

This project demonstrates more than analysis. It demonstrates the decision layer around analysis.

A reviewer can see that the project handles:

- metric definition
- SQL modeling
- quality checks
- statistical evidence
- retention, refund, and engagement guardrail interpretation
- scenario testing
- one-command reproducibility
- decision communication

## Tradeoffs

| Tradeoff | Reason |
| --- | --- |
| Synthetic data instead of real user data | Keeps the project public-safe and reproducible |
| DuckDB instead of a production warehouse | Keeps the workflow lightweight and reviewer-friendly |
| Simple decision rules | Makes the recommendation logic transparent |
| Static HTML instead of BI dashboard | Prioritizes reproducible artifacts over tool-specific UI |

## Possible Next Improvements

Possible next improvements:

- Publish the reviewer report through GitHub Pages.
- Add a lightweight dashboard from the mart layer.
- Add more quality failure modes.
- Add cohort-level experiment analysis.
- Add saved sample data for reviewers who do not want to regenerate the dataset.

## Interview Pitch

A concise way to explain this project:

> DecisionOps Lab is a reproducible product analytics workflow. I generated synthetic product event data, modeled it through raw, staging, intermediate, and mart layers, checked data quality, analyzed an onboarding experiment, used D7 revisit, refund rate, and session activity as guardrails, and generated decision memos and reviewer reports. I also added scenario testing so the workflow proves Ship, Retest, Hold, and Investigate outcomes instead of always producing one fixed result.

## Claim Boundary

DecisionOps Lab uses synthetic data. It does not claim real product performance or real business impact. The claim is about workflow design, reproducibility, analytics engineering structure, and decision communication.
