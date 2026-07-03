CREATE OR REPLACE TABLE mart_decision_summary AS
WITH variant_metrics AS (
    SELECT
        variant,
        users,
        activated_users,
        activation_rate,
        d7_revisit_rate
    FROM mart_experiment_result
),
comparison AS (
    SELECT
        a.users AS variant_a_users,
        b.users AS variant_b_users,
        a.activation_rate AS variant_a_activation_rate,
        b.activation_rate AS variant_b_activation_rate,
        b.activation_rate - a.activation_rate AS activation_absolute_lift,
        CASE
            WHEN a.activation_rate = 0 THEN NULL
            ELSE (b.activation_rate - a.activation_rate) / a.activation_rate
        END AS activation_relative_lift,
        a.d7_revisit_rate AS variant_a_d7_revisit_rate,
        b.d7_revisit_rate AS variant_b_d7_revisit_rate,
        b.d7_revisit_rate - a.d7_revisit_rate AS d7_revisit_delta
    FROM variant_metrics a
    CROSS JOIN variant_metrics b
    WHERE a.variant = 'A'
      AND b.variant = 'B'
)
SELECT
    'onboarding_v2' AS experiment_name,
    variant_a_users,
    variant_b_users,
    variant_a_activation_rate,
    variant_b_activation_rate,
    activation_absolute_lift,
    activation_relative_lift,
    variant_a_d7_revisit_rate,
    variant_b_d7_revisit_rate,
    d7_revisit_delta,
    CASE
        WHEN activation_absolute_lift > 0 AND d7_revisit_delta >= -0.01 THEN 'ready_for_review'
        WHEN activation_absolute_lift > 0 THEN 'needs_follow_up'
        ELSE 'not_supported'
    END AS evidence_status
FROM comparison;
