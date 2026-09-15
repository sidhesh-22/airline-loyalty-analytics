-- ============================================================
-- Customer Monthly Status
-- Grain: one row per customer per observed calendar month
-- ============================================================

DROP TABLE IF EXISTS customer_monthly_status;

CREATE TABLE customer_monthly_status AS

SELECT
    f.customer_id,
    f.activity_date,
    f.year,
    f.month,

    -- Customer lifecycle dates
    c.enrollment_date,
    c.cancellation_date,

    -- Cohort
    DATE_TRUNC('month', c.enrollment_date)::DATE AS cohort_month,

    -- Months elapsed since enrollment
    DATE_DIFF(
        'month',
        DATE_TRUNC('month', c.enrollment_date),
        DATE_TRUNC('month', f.activity_date)
    ) AS months_since_enrollment,

    -- Activity measures
    f.total_flights,
    f.distance,
    f.points_accumulated,
    f.points_redeemed,
    f.dollar_cost_points_redeemed,

    -- Activity indicators
    f.has_flight_activity,
    f.has_points_accumulated,
    f.has_points_redeemed,

    -- Source-data quality flags
    f.has_pre_enrollment_activity,
    f.has_post_cancellation_activity,

    -- Lifecycle eligibility
    CASE
        WHEN f.activity_date < c.enrollment_date
            THEN FALSE
        WHEN c.cancellation_date IS NOT NULL
             AND f.activity_date > c.cancellation_date
            THEN FALSE
        ELSE TRUE
    END AS is_lifecycle_month,

    -- Monthly lifecycle status
    CASE
        WHEN f.activity_date < c.enrollment_date
            THEN 'pre_enrollment'

        WHEN c.cancellation_date IS NOT NULL
             AND f.activity_date > c.cancellation_date
            THEN 'post_cancellation'

        WHEN f.has_flight_activity
            THEN 'active'

        ELSE 'inactive'
    END AS monthly_status

FROM fact_customer_month f

INNER JOIN dim_customer c
    ON f.customer_id = c.customer_id;