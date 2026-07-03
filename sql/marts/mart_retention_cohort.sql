CREATE OR REPLACE TABLE mart_retention_cohort AS
SELECT
    signup_week,
    COUNT(*) AS users,
    AVG(revisited_d1) AS d1_revisit_rate,
    AVG(revisited_d3) AS d3_revisit_rate,
    AVG(revisited_d7) AS d7_revisit_rate
FROM int_user_retention
GROUP BY signup_week
ORDER BY signup_week;
