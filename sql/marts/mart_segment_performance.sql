CREATE OR REPLACE TABLE mart_segment_performance AS
WITH by_channel AS (
    SELECT
        scenario,
        'acquisition_channel' AS segment_dimension,
        acquisition_channel AS segment_value,
        variant,
        COUNT(*) AS users,
        AVG(activated_24h) AS activation_rate,
        AVG(revisited_d7) AS d7_revisit_rate
    FROM int_experiment_user_metrics
    GROUP BY scenario, acquisition_channel, variant
),
by_device AS (
    SELECT
        scenario,
        'device_type' AS segment_dimension,
        device_type AS segment_value,
        variant,
        COUNT(*) AS users,
        AVG(activated_24h) AS activation_rate,
        AVG(revisited_d7) AS d7_revisit_rate
    FROM int_experiment_user_metrics
    GROUP BY scenario, device_type, variant
),
by_age AS (
    SELECT
        scenario,
        'age_group' AS segment_dimension,
        age_group AS segment_value,
        variant,
        COUNT(*) AS users,
        AVG(activated_24h) AS activation_rate,
        AVG(revisited_d7) AS d7_revisit_rate
    FROM int_experiment_user_metrics
    GROUP BY scenario, age_group, variant
)
SELECT * FROM by_channel
UNION ALL
SELECT * FROM by_device
UNION ALL
SELECT * FROM by_age;
