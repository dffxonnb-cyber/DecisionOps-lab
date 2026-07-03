CREATE OR REPLACE TABLE int_user_activation AS
WITH first_routine AS (
    SELECT
        user_id,
        MIN(event_time) AS first_routine_created_at
    FROM stg_events
    WHERE event_name = 'create_routine'
    GROUP BY user_id
)
SELECT
    u.user_id,
    u.signup_at,
    u.signup_date,
    u.signup_week,
    u.acquisition_channel,
    u.device_type,
    u.age_group,
    x.experiment_name,
    x.variant,
    f.first_routine_created_at,
    CASE
        WHEN f.first_routine_created_at IS NOT NULL
         AND DATE_DIFF('hour', u.signup_at, f.first_routine_created_at) <= 24
        THEN 1 ELSE 0
    END AS activated_24h
FROM stg_users u
LEFT JOIN stg_experiments x ON u.user_id = x.user_id
LEFT JOIN first_routine f ON u.user_id = f.user_id;
