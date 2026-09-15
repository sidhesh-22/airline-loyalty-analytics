CREATE OR REPLACE TABLE customer_segments AS

WITH customer_metrics AS (

    SELECT
        f.customer_id,

        -- Activity coverage
        COUNT(*) AS observed_months,

        COUNT(*) FILTER (
            WHERE f.total_flights > 0
        ) AS active_months,

        -- Flight behavior
        SUM(f.total_flights) AS total_flights,
        SUM(f.distance) AS total_distance,

        AVG(f.total_flights) AS avg_monthly_flights,
        AVG(f.distance) AS avg_monthly_distance,

        -- Points behavior
        SUM(f.points_accumulated) AS total_points_accumulated,
        SUM(f.points_redeemed) AS total_points_redeemed,

        COUNT(*) FILTER (
            WHERE f.points_redeemed > 0
        ) AS redemption_months,

        -- Customer value / profile
        d.clv,
        d.loyalty_card,
        d.enrollment_type,
        d.has_cancellation

    FROM fact_customer_month f

    INNER JOIN dim_customer d
        ON f.customer_id = d.customer_id

    GROUP BY
        f.customer_id,
        d.clv,
        d.loyalty_card,
        d.enrollment_type,
        d.has_cancellation
),

scored AS (

    SELECT
        *,

        -- Relative behavioral rankings
        PERCENT_RANK() OVER (
            ORDER BY total_flights
        ) AS flights_percentile,

        PERCENT_RANK() OVER (
            ORDER BY active_months
        ) AS activity_percentile,

        PERCENT_RANK() OVER (
            ORDER BY total_distance
        ) AS distance_percentile,

        PERCENT_RANK() OVER (
            ORDER BY clv
        ) AS clv_percentile

    FROM customer_metrics
),

final AS (

    SELECT
        *,

        -- Overall engagement score
        ROUND(
            100 * (
                flights_percentile
                + activity_percentile
                + distance_percentile
            ) / 3,
            2
        ) AS engagement_score,

        -- Customer value segment
        CASE
            WHEN clv_percentile >= 0.75 THEN 'High Value'
            WHEN clv_percentile >= 0.50 THEN 'Mid-High Value'
            WHEN clv_percentile >= 0.25 THEN 'Mid-Low Value'
            ELSE 'Low Value'
        END AS value_segment

    FROM scored
)

SELECT
    customer_id,
    observed_months,
    active_months,

    total_flights,
    total_distance,
    avg_monthly_flights,
    avg_monthly_distance,

    total_points_accumulated,
    total_points_redeemed,
    redemption_months,

    clv,
    loyalty_card,
    enrollment_type,
    has_cancellation,

    flights_percentile,
    activity_percentile,
    distance_percentile,
    clv_percentile,

    engagement_score,

    CASE
        WHEN engagement_score >= 75 THEN 'Highly Engaged'
        WHEN engagement_score >= 50 THEN 'Engaged'
        WHEN engagement_score >= 25 THEN 'Low Engagement'
        ELSE 'Very Low Engagement'
    END AS engagement_segment,

    value_segment

FROM final;