CREATE OR REPLACE TABLE stg_users AS
SELECT
    CAST(user_id AS VARCHAR) AS user_id,
    CAST(signup_at AS TIMESTAMP) AS signup_at,
    CAST(acquisition_channel AS VARCHAR) AS acquisition_channel,
    CAST(device_type AS VARCHAR) AS device_type,
    CAST(age_group AS VARCHAR) AS age_group,
    DATE_TRUNC('day', CAST(signup_at AS TIMESTAMP))::DATE AS signup_date,
    DATE_TRUNC('week', CAST(signup_at AS TIMESTAMP))::DATE AS signup_week
FROM raw_users;
