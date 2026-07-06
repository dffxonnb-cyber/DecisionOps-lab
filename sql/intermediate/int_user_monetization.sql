CREATE OR REPLACE TABLE int_user_monetization AS
SELECT
    user_id,
    MAX(CASE WHEN payment_status = 'trial_start' THEN 1 ELSE 0 END) AS trial_started,
    MAX(CASE WHEN payment_status = 'paid_conversion' THEN 1 ELSE 0 END) AS paid_converted,
    MAX(CASE WHEN payment_status = 'refund' THEN 1 ELSE 0 END) AS refunded,
    SUM(CASE WHEN payment_status = 'paid_conversion' THEN amount ELSE 0 END) AS paid_amount,
    ABS(SUM(CASE WHEN payment_status = 'refund' THEN amount ELSE 0 END)) AS refund_amount
FROM stg_payments
GROUP BY user_id;
