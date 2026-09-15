-- ============================================================
-- Cohort Analysis
-- Grain: one row per cohort month and activity month
-- Focus: customers enrolled during 2017
-- ============================================================

CREATE OR REPLACE TABLE cohort_monthly_metrics AS

WITH cohort_customers AS (

    SELECT
        customer_id,
        DATE_TRUNC('month', enrollment_date) AS cohort_month
    FROM dim_customer
    WHERE enrollment_date >= DATE '2017-01-01'
      AND enrollment_date < DATE '2018-01-01'

),

cohort_sizes AS (

    SELECT
        cohort_month,
        COUNT(*) AS cohort_size
    FROM cohort_customers
    GROUP BY cohort_month

),

monthly_activity AS (

    SELECT
        cc.cohort_month,
        cms.activity_date,
        cc.customer_id,
        cms.has_flight_activity
    FROM cohort_customers cc

    INNER JOIN customer_monthly_status cms
        ON cc.customer_id = cms.customer_id

    WHERE cms.is_lifecycle_month = TRUE

),

cohort_activity AS (

    SELECT
        cohort_month,
        activity_date,
        COUNT(DISTINCT customer_id) FILTER (
            WHERE has_flight_activity = TRUE
        ) AS active_customers
    FROM monthly_activity
    GROUP BY
        cohort_month,
        activity_date

)

SELECT
    ca.cohort_month,
    cs.cohort_size,
    ca.activity_date,
    DATE_DIFF(
        'month',
        ca.cohort_month,
        ca.activity_date
    ) AS months_since_cohort,
    ca.active_customers,
    ROUND(
        100.0 * ca.active_customers / cs.cohort_size,
        2
    ) AS retention_rate

FROM cohort_activity ca

INNER JOIN cohort_sizes cs
    ON ca.cohort_month = cs.cohort_month

WHERE DATE_DIFF(
    'month',
    ca.cohort_month,
    ca.activity_date
) BETWEEN 0 AND 11

ORDER BY
    ca.cohort_month,
    months_since_cohort;