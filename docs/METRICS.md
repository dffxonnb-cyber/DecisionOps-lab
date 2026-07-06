# Metrics

## 1. Metric Layer Principle

DecisionOps Lab treats metrics as product definitions, not just calculations.

Every metric should answer:

1. What decision does this metric support?
2. What is the exact denominator?
3. What is the exact numerator?
4. What time window does it use?
5. What are the known limitations?

---

## 2. Core Product Metrics

| Metric | Definition | Decision Use |
| --- | --- | --- |
| Signup Count | Number of users who signed up in a period | Top-of-funnel volume |
| Onboarding Start Rate | Users who started onboarding / signed-up users | Onboarding entry health |
| Onboarding Completion Rate | Users who completed onboarding / users who started onboarding | Onboarding friction |
| Activation Rate | Users who created first routine within 24 hours / signed-up users | Primary activation metric |
| D1 Retention | Users who returned one day after signup / signed-up users | Early retention |
| D3 Retention | Users who returned within three days after signup / signed-up users | Short-term habit signal |
| D7 Retention | Users who returned within seven days after signup / signed-up users | Guardrail retention metric |
| Routine Completion Rate | Completed routines / created routines | Routine usefulness |
| Trial Start Rate | Trial users / signed-up users | Monetization entry |
| Paid Conversion Rate | Paid users / assigned users | Monetization conversion |
| Refund Rate | Refunded users / assigned users | Monetization quality guardrail |
| Average Sessions | Average sessions per experiment user | Engagement behavior guardrail |

---

## 3. Experiment Metrics

### 3-1. Primary Metric

**Activation Rate**

A user is activated if they create their first routine within 24 hours after signup.

```text
activation_rate = activated_users / assigned_users
```

This is the primary metric because the onboarding experiment is designed to help users reach their first meaningful action faster.

### 3-2. Secondary Metrics

| Metric | Purpose |
| --- | --- |
| Onboarding Completion Rate | Checks whether the new flow reduces onboarding friction |
| Routine Completion Rate | Checks whether created routines are actually used |
| Trial Start Rate | Checks whether activation connects to monetization intent |
| Paid Conversion Rate | Checks whether activated users move toward paid intent |

### 3-3. Guardrail Metrics

| Metric | Risk |
| --- | --- |
| D7 Retention / Revisit | Activation can increase while return behavior drops |
| Refund Rate | Conversion can increase with worse user fit |
| Average Sessions | New onboarding can reduce session activity after signup |

---

## 4. Segment Dimensions

Experiment results should be checked across segments.

| Segment | Example Values |
| --- | --- |
| Acquisition Channel | organic, paid_search, social, referral |
| Device Type | mobile, desktop, tablet |
| Age Group | 10s, 20s, 30s, 40s+ |
| Signup Cohort | signup date or week |

Segment diagnostics should not replace the main experiment result. They are used to find risk, uneven lift, or follow-up test opportunities.

---

## 5. Decision Thresholds

V2-1 uses simple portfolio-level thresholds.

| Condition | Interpretation |
| --- | --- |
| Activation lift > 0 and p-value < 0.05 and all guardrails pass | Strong positive evidence |
| Activation lift > 0 and p-value between 0.05 and 0.10 | Directionally positive but weak |
| Activation lift <= 0 | No positive evidence |
| D7 revisit delta < -1 percentage point | Retention guardrail risk |
| Refund rate delta > +1 percentage point | Monetization quality risk |
| Average sessions per user drops by more than 5% | Engagement behavior risk |
| Data quality status is FAIL | Decision should not proceed |

These thresholds are portfolio-level simplifications, not universal business rules.

---

## 6. Metric Claim Boundary

Because this project uses synthetic data, metric results do not represent real product performance.

The value of the project is in the workflow:

- metric definitions
- SQL implementation
- data quality checks
- experiment interpretation
- guardrail-aware decision memo generation
