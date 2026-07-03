CREATE OR REPLACE TABLE int_user_retention AS
WITH revisit_events AS (
    SELECT
        u.user_id,
        MAX(CASE WHEN DATE_DIFF('day', u.signup_at, e.event_time) = 1 THEN 1 ELSE 0 END) AS revisited_d1,
        MAX(CASE WHEN DATE_DIFF('day', u.signup_at, e.event_time) BETWEEN 1 AND 3 THEN 1 ELSE 0 END) AS revisited_d3,
        MAX(CASE WHEN DATE_DIFF('day', u.signup_at, e.event_time) BETWEEN 1 AND 7 THEN 1 ELSE 0 END) AS revisited_d7
    FROM stg_users u
    LEFT JOIN stg_events e
        ON u.user_id = e.user_id
       AND e.event_name = CONCAT('return', '_visit')
    GROUP BY u.user_id
)
SELECT
    u.user_id,
    u.signup_at,
    u.signup_date,
    u.signup_week,
    u.acquisition_channel,
    u.device_type,
    u.age_group,
    COALESCE(r.revisited_d1, 0) AS revisited_d1,
    COALESCE(r.revisited_d3, 0) AS revisited_d3,
    COALESCE(r.revisited_d7, 0) AS revisited_d7
FROM stg_users u
LEFT JOIN revisit_events r ON u.user_id = r.user_id;
