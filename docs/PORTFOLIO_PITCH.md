# Portfolio Pitch

This document translates DecisionOps Lab into resume, portfolio, and interview language.

## Resume One-Liner

Built an end-to-end product analytics workflow that transforms synthetic product events into SQL marts, data quality checks, A/B experiment evidence, D7 guardrail review, decision memos, scenario matrix validation, and CI-verified reports.

## Portfolio Card Description

DecisionOps Lab is a reproducible product analytics and analytics engineering project. It models raw product events through DuckDB SQL layers, validates data quality, analyzes an onboarding A/B test, checks D7 revisit as a guardrail, and generates decision-ready reports. Scenario mode verifies that the workflow can produce Ship, Retest, Hold, and Investigate outcomes instead of being hard-coded to one result.

## 30-Second Interview Version

DecisionOps Lab is a product analytics project built around decision-making, not just analysis. I generated synthetic event data for a routine app, modeled it through raw, staging, intermediate, and mart layers in DuckDB, then added quality checks, A/B experiment analysis, D7 revisit guardrails, and decision memos. I also added scenario testing and GitHub Actions so the workflow is reproducible and proves different recommendations under different data conditions.

## 1-Minute Interview Version

I built DecisionOps Lab to show how raw product data can become decision-ready evidence. The synthetic product is a routine app testing a new onboarding variant. The pipeline generates raw event data, loads it into DuckDB, builds staging/intermediate/mart SQL tables, runs quality checks, and analyzes activation lift between Variant A and Variant B. I also added D7 revisit as a guardrail, because a short-term activation increase can be misleading if retention weakens. The final output is a decision memo and HTML reviewer report. To prove the decision logic is not hard-coded, I added scenario mode with strong-positive, guardrail-risk, weak-evidence, neutral, and quality-failure cases. GitHub Actions runs the full verification workflow.

## 2-Minute Interview Version

DecisionOps Lab is a product analytics and analytics engineering portfolio project focused on the layer between analysis and product decision-making.

The product scenario is a routine or study habit app testing a new onboarding experience. The primary metric is whether a new user creates a routine within 24 hours. But I did not want the project to simply say “activation went up, therefore ship.” So I added D7 revisit as a guardrail and built decision rules around quality, primary metric evidence, and guardrail behavior.

The technical flow starts with a deterministic synthetic dataset generator. It creates raw users, events, sessions, experiments, and payments. The SQL pipeline loads those files into DuckDB and builds raw, staging, intermediate, and mart tables. The mart layer includes experiment results, segment performance, retention cohorts, and decision summary tables.

After modeling, the workflow runs quality checks for row counts, uniqueness, nulls, accepted values, relations, experiment balance, and metric ranges. Then the experiment analysis calculates activation lift, p-value, confidence interval, segment diagnostics, and D7 revisit delta. The recommendation is generated as a decision memo and displayed in a static reviewer report.

The most important part is scenario mode. I added five synthetic scenarios: strong_positive, guardrail_risk, weak_evidence, neutral, and quality_failure. This proves that the workflow can produce Ship, Retest, Hold, and Investigate outcomes depending on the data condition. The full workflow is reproducible with one command and verified through GitHub Actions.

## Role-Specific Positioning

### Product Analyst

Emphasize:

- Experiment interpretation
- Primary metric and guardrail design
- Decision memo generation
- Scenario-based recommendation logic

Suggested line:

> I designed the analysis around product decision-making: activation was the primary metric, D7 revisit was the guardrail, and the final output was a recommendation memo rather than just a chart.

### Analytics Engineer

Emphasize:

- Raw / staging / intermediate / mart SQL structure
- DuckDB modeling
- Data quality contracts
- Reproducible verification runner

Suggested line:

> I separated raw data, staging models, intermediate models, and final marts so downstream reports depend on stable analytical tables rather than one-off queries.

### Data Analyst

Emphasize:

- SQL modeling
- A/B testing
- Metric definition
- Segment diagnostics
- Quality checks before interpretation

Suggested line:

> I built a reproducible workflow that checks whether the data can be trusted before interpreting experiment results.

### Product Manager / Data-Driven Planning

Emphasize:

- Recommendation logic
- Claim boundary
- Guardrail thinking
- Scenario planning

Suggested line:

> I wanted to show how data can support a decision without overstating the claim, so the project includes explicit decision rules and claim boundaries.

## Technical Keywords

```text
Product Analytics
Analytics Engineering
A/B Testing
Experiment Analysis
Guardrail Metrics
Activation Rate
D7 Retention / Revisit
Data Quality Checks
Decision Memo
DuckDB
SQL Modeling
Mart Layer
Scenario Testing
GitHub Actions
Reproducible Pipeline
Synthetic Data
```

## Strongest Talking Points

1. The project does not stop at analysis; it produces a decision memo.
2. It checks data quality before interpreting experiment evidence.
3. It uses D7 revisit as a guardrail against short-term metric chasing.
4. It includes SQL mart tables, not just pandas analysis.
5. It uses scenario mode to prove that the decision logic changes across conditions.
6. It is reproducible locally and in GitHub Actions.

## Short Korean Pitch

DecisionOps Lab은 단순히 A/B 테스트 결과를 보여주는 프로젝트가 아니라, raw 이벤트 데이터를 SQL 모델링, 품질 검증, 실험 분석, 가드레일 검토, 의사결정 메모까지 연결한 Product Analytics / Analytics Engineering 프로젝트입니다. 특히 activation이 올라도 D7 재방문이 무너지면 바로 Ship하지 않도록 guardrail을 두었고, 여러 synthetic scenario를 통해 Ship, Retest, Hold, Investigate 판단이 실제로 갈리는지 검증했습니다.

## Claim Boundary

This project uses synthetic data. The claim is not real product performance. The claim is that the workflow is reproducible, reviewable, and structured around trustworthy decision-making.