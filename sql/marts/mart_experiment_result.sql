CREATE OR REPLACE TABLE mart_experiment_result AS
SELECT
    experiment_name,
    variant,
    COUNT(*) AS users,
    SUM(activated_24h) AS activated_users,
    AVG(activated_24h) AS activation_rate,
    AVG(revisited_d1) AS d1_revisit_rate,
    AVG(revisited_d3) AS d3_revisit_rate,
    AVG(revisited_d7) AS d7_revisit_rate,
    AVG(session_count) AS avg_sessions,
    AVG(avg_session_seconds) AS avg_session_seconds
FROM int_experiment_user_metrics
GROUP BY experiment_name, variant;
