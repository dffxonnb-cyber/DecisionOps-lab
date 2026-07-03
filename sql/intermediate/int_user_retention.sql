CREATE OR REPLACE TABLE int_user_retention AS
SELECT
    user_id,
    signup_at,
    signup_date,
    signup_week,
    acquisition_channel,
    device_type,
    age_group
FROM stg_users;
