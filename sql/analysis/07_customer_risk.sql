CREATE OR REPLACE TABLE customer_risk AS

WITH lifecycle_activity AS (

    SELECT
        customer_id,

        COALESCE(
            BOOL_OR(
                is_lifecycle_month
                AND has_flight_activity
            ),
            FALSE
        ) AS has_lifecycle_flight_activity,

        COALESCE(
            BOOL_OR(
                is_lifecycle_month
                AND has_points_redeemed
            ),
            FALSE
        ) AS has_lifecycle_points_redeemed

    FROM customer_monthly_status

    GROUP BY customer_id
)

SELECT
    s.customer_id,

    -- Customer profile
    d.gender,
    d.education,
    d.marital_status,
    d.loyalty_card,
    d.enrollment_type,
    d.has_cancellation,
    d.clv,

    -- Behavioral metrics
    s.observed_months,
    s.active_months,
    s.total_flights,
    s.total_distance,
    s.avg_monthly_flights,
    s.avg_monthly_distance,
    s.total_points_accumulated,
    s.total_points_redeemed,
    s.redemption_months,

    -- Lifecycle activity
    COALESCE(
        l.has_lifecycle_flight_activity,
        FALSE
    ) AS has_lifecycle_flight_activity,

    COALESCE(
        l.has_lifecycle_points_redeemed,
        FALSE
    ) AS has_lifecycle_points_redeemed,

    -- Segmentation
    s.engagement_score,
    s.engagement_segment,
    s.value_segment,

    -- Churn
    c.churn_status,
    c.months_to_cancellation,

    -- Model output
    r.churn_probability,
    r.predicted_churn_010,
    r.risk_band

FROM customer_segments s

LEFT JOIN dim_customer d
    ON s.customer_id = d.customer_id

LEFT JOIN customer_churn c
    ON s.customer_id = c.customer_id

LEFT JOIN lifecycle_activity l
    ON s.customer_id = l.customer_id

LEFT JOIN read_parquet(
    'data/processed/customer_churn_risk.parquet'
) r
    ON s.customer_id = r.customer_id;
    