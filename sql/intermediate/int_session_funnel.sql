CREATE OR REPLACE TABLE int_session_funnel AS
SELECT
    user_id,
    session_id,
    MIN(event_time) AS first_event_at,
    MAX(event_time) AS last_event_at,
    MAX(CASE WHEN event_name = 'signup' THEN 1 ELSE 0 END) AS has_signup,
    MAX(CASE WHEN event_name = 'onboarding_start' THEN 1 ELSE 0 END) AS has_onboarding_start,
    MAX(CASE WHEN event_name = 'onboarding_complete' THEN 1 ELSE 0 END) AS has_onboarding_complete,
    MAX(CASE WHEN event_name = 'create_routine' THEN 1 ELSE 0 END) AS has_create_routine,
    MAX(CASE WHEN event_name = 'complete_routine' THEN 1 ELSE 0 END) AS has_complete_routine
FROM stg_events
GROUP BY user_id, session_id;
