CREATE OR REPLACE TABLE stg_payments AS
SELECT
    payment_id,
    user_id,
    payment_status,
    CAST(payment_time AS TIMESTAMP) AS payment_time,
    CAST(amount AS INTEGER) AS amount,
    CAST(DATE_TRUNC('day', CAST(payment_time AS TIMESTAMP)) AS DATE) AS payment_date
FROM raw_payments;
