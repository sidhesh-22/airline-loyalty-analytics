CREATE OR REPLACE TABLE fact_customer_month AS

SELECT
    "Loyalty Number" AS customer_id,
    activity_date,
    "Year" AS year,
    "Month" AS month,
    total_flights,
    distance,
    points_accumulated,
    points_redeemed,
    dollar_cost_points_redeemed,
    source_activity_rows,
    pre_enrollment_rows,
    post_cancellation_rows,
    has_pre_enrollment_activity,
    has_post_cancellation_activity,
    has_flight_activity,
    has_points_accumulated,
    has_points_redeemed
FROM read_parquet(
    'data/processed/fact_customer_month.parquet'
);