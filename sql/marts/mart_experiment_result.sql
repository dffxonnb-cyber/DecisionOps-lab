CREATE OR REPLACE TABLE mart_experiment_result AS
SELECT
    scenario,
    experiment_name,
    variant,
    COUNT(*) AS users,
    SUM(activated_24h) AS activated_users,
    AVG(activated_24h) AS activation_rate,
    AVG(revisited_d1) AS d1_revisit_rate,
    AVG(revisited_d3) AS d3_revisit_rate,
    AVG(revisited_d7) AS d7_revisit_rate,
    AVG(session_count) AS avg_sessions,
    AVG(avg_session_seconds) AS avg_session_seconds,
    SUM(trial_started) AS trial_users,
    AVG(trial_started) AS trial_start_rate,
    SUM(paid_converted) AS paid_users,
    AVG(paid_converted) AS paid_conversion_rate,
    SUM(refunded) AS refunded_users,
    AVG(refunded) AS refund_rate,
    SUM(paid_amount) AS total_paid_amount,
    SUM(refund_amount) AS total_refund_amount
FROM int_experiment_user_metrics
GROUP BY scenario, experiment_name, variant;
