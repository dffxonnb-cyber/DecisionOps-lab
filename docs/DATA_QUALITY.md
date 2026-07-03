# Data Quality

## 1. Quality Principle

DecisionOps Lab does not allow a business decision to be made from untrusted data.

The data quality layer answers:

> Can this dataset be used for experiment interpretation and product decision-making?

If quality fails, the final decision should be `Investigate`, not `Ship`.

---

## 2. Quality Status

| Status | Meaning | Decision Impact |
| --- | --- | --- |
| PASS | Data is usable for analysis and decision review | Decision can proceed |
| WARN | Data is usable but requires caution | Decision can proceed with caution |
| FAIL | Data is not trustworthy enough | Decision should be Investigate |

---

## 3. Planned Checks

## 3-1. Row Count Check

Core tables should not be empty.

Required tables:

- `raw_users`
- `raw_events`
- `raw_sessions`
- `raw_experiments`
- `raw_payments`

Failure example:

```text
raw_events row_count = 0
→ FAIL
```

---

## 3-2. Null Check

Critical columns should not contain null values.

| Table | Critical Columns |
| --- | --- |
| raw_users | user_id, signup_at |
| raw_events | event_id, user_id, event_name, event_time |
| raw_sessions | session_id, user_id, session_start |
| raw_experiments | user_id, experiment_name, variant |
| raw_payments | user_id, payment_status, payment_time |

---

## 3-3. Accepted Values Check

Categorical values should be inside known sets.

### event_name

Allowed values:

- signup
- onboarding_start
- onboarding_complete
- create_routine
- complete_routine
- return_visit
- trial_start
- paid_conversion
- refund

### variant

Allowed values:

- A
- B

### device_type

Allowed values:

- mobile
- desktop
- tablet

### acquisition_channel

Allowed values:

- organic
- paid_search
- social
- referral

---

## 3-4. Freshness Check

Synthetic data should include events through the expected end date.

In V1, freshness is defined as:

```text
max(event_time) >= configured_end_date - 1 day
```

If the latest event is too old, quality status becomes WARN or FAIL depending on severity.

---

## 3-5. Referential Integrity Check

Every event user_id should exist in `raw_users`.

```text
raw_events.user_id ⊆ raw_users.user_id
```

Every experiment assignment should also refer to a known user.

```text
raw_experiments.user_id ⊆ raw_users.user_id
```

---

## 3-6. Duplicate Check

Primary IDs should be unique.

| Table | Unique Key |
| --- | --- |
| raw_users | user_id |
| raw_events | event_id |
| raw_sessions | session_id |

Duplicates in critical keys should fail the quality report.

---

## 3-7. Experiment Balance Check

The experiment should not be extremely imbalanced.

Expected assignment ratio:

```text
A: 45% ~ 55%
B: 45% ~ 55%
```

If the ratio is outside the expected range, status becomes WARN or FAIL.

---

## 3-8. Metric Sanity Check

Some metrics should stay within reasonable ranges.

| Metric | Expected Range |
| --- | --- |
| Activation Rate | 0% ~ 100% |
| D7 Retention | 0% ~ 100% |
| Refund Rate | 0% ~ 100% |
| Paid Conversion Rate | 0% ~ 100% |

Extreme values can indicate generation, modeling, or aggregation errors.

---

## 4. Quality Report Format

The quality script should generate `reports/quality_report.json`.

Example:

```json
{
  "status": "PASS",
  "generated_at": "2026-07-03T00:00:00+09:00",
  "checks": [
    {
      "name": "row_count_raw_events",
      "status": "PASS",
      "observed": 120000,
      "message": "raw_events is not empty"
    }
  ],
  "summary": {
    "pass": 8,
    "warn": 0,
    "fail": 0
  }
}
```

---

## 5. Decision Boundary

Quality status controls decision eligibility.

```text
quality_status = FAIL
→ decision = Investigate
```

```text
quality_status = WARN
→ decision can proceed, but memo must include caution
```

```text
quality_status = PASS
→ decision can proceed normally
```
