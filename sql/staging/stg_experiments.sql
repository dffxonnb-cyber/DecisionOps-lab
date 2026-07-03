CREATE OR REPLACE TABLE stg_experiments AS
SELECT
    user_id,
    experiment_name,
    variant,
    CAST(assigned_at AS TIMESTAMP) AS assigned_at
FROM raw_experiments;
