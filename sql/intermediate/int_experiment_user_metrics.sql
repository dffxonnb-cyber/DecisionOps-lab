CREATE OR REPLACE TABLE int_experiment_user_metrics AS
WITH session_summary AS (
    SELECT
        user_id,
        COUNT(*) AS session_count,
        AVG(duration_seconds) AS avg_session_seconds
    FROM stg_sessions
    GROUP BY user_id
)
SELECT
    a.*,
    COALESCE(r.revisited_d1, 0) AS revisited_d1,
    COALESCE(r.revisited_d3, 0) AS revisited_d3,
    COALESCE(r.revisited_d7, 0) AS revisited_d7,
    COALESCE(s.session_count, 0) AS session_count,
    COALESCE(s.avg_session_seconds, 0) AS avg_session_seconds,
    COALESCE(m.trial_started, 0) AS trial_started,
    COALESCE(m.paid_converted, 0) AS paid_converted,
    COALESCE(m.refunded, 0) AS refunded,
    COALESCE(m.paid_amount, 0) AS paid_amount,
    COALESCE(m.refund_amount, 0) AS refund_amount
FROM int_user_activation a
LEFT JOIN int_user_retention r ON a.user_id = r.user_id
LEFT JOIN session_summary s ON a.user_id = s.user_id
LEFT JOIN int_user_monetization m ON a.user_id = m.user_id;
