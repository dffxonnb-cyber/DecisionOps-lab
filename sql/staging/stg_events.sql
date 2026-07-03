CREATE OR REPLACE TABLE stg_events AS
SELECT
    event_id,
    user_id,
    session_id,
    event_name,
    CAST(event_time AS TIMESTAMP) AS event_time,
    CAST(event_sequence AS INTEGER) AS event_sequence,
    CAST(DATE_TRUNC('day', CAST(event_time AS TIMESTAMP)) AS DATE) AS event_date
FROM raw_events;
