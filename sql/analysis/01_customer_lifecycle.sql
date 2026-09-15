CREATE OR REPLACE TABLE customer_lifecycle AS

SELECT
    c.customer_id,

    -- Customer lifecycle dates
    c.enrollment_date,
    c.cancellation_date,
    c.has_cancellation AS has_recorded_cancellation,

    -- Observed activity window
    MIN(f.activity_date) AS first_observed_activity_date,
    MAX(f.activity_date) AS last_observed_activity_date,

    -- Activity coverage
    COUNT(f.activity_date) AS observed_months,
    COUNT(f.activity_date) FILTER (
        WHERE f.has_flight_activity
    ) AS active_flight_months,

    -- Lifetime observed activity
    COALESCE(SUM(f.total_flights), 0) AS total_flights,
    COALESCE(SUM(f.distance), 0) AS total_distance,
    COALESCE(SUM(f.points_accumulated), 0) AS total_points_accumulated,
    COALESCE(SUM(f.points_redeemed), 0) AS total_points_redeemed,
    COALESCE(SUM(f.dollar_cost_points_redeemed), 0) AS total_dollar_cost_points_redeemed

FROM dim_customer c

LEFT JOIN fact_customer_month f
    ON c.customer_id = f.customer_id

GROUP BY
    c.customer_id,
    c.enrollment_date,
    c.cancellation_date,
    c.has_cancellation;