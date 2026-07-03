CREATE OR REPLACE TABLE stg_sessions AS
SELECT
    session_id,
    user_id,
    CAST(session_start AS TIMESTAMP) AS session_start,
    CAST(session_end AS TIMESTAMP) AS session_end,
    CAST(duration_seconds AS INTEGER) AS duration_seconds,
    device_type,
    session_type,
    CAST(DATE_TRUNC('day', CAST(session_start AS TIMESTAMP)) AS DATE) AS session_date
FROM raw_sessions;
