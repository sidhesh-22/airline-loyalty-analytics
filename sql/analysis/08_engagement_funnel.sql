CREATE OR REPLACE TABLE engagement_funnel AS

WITH customer_engagement AS (

    SELECT
        c.customer_id,

        -- Every customer in dim_customer is enrolled
        TRUE AS is_enrolled,

        -- At least one flight during the valid lifecycle period
        COALESCE(
            BOOL_OR(
                f.is_lifecycle_month
                AND f.has_flight_activity
            ),
            FALSE
        ) AS has_flight_activity,

        -- At least one redemption during the valid lifecycle period
        COALESCE(
            BOOL_OR(
                f.is_lifecycle_month
                AND f.has_points_redeemed
            ),
            FALSE
        ) AS has_points_redeemed

    FROM dim_customer c

    LEFT JOIN customer_monthly_status f
        ON c.customer_id = f.customer_id

    GROUP BY c.customer_id
),

funnel_counts AS (

    SELECT
        COUNT(*) AS enrolled_customers,

        COUNT(*) FILTER (
            WHERE has_flight_activity
        ) AS active_flight_customers,

        COUNT(*) FILTER (
            WHERE has_flight_activity
              AND has_points_redeemed
        ) AS points_redeemers

    FROM customer_engagement
)

SELECT
    1 AS stage_order,
    'Enrolled' AS stage,
    enrolled_customers AS customers,
    100.0 AS pct_of_enrolled
FROM funnel_counts

UNION ALL

SELECT
    2 AS stage_order,
    'Active Flight Customer' AS stage,
    active_flight_customers AS customers,
    ROUND(
        100.0 * active_flight_customers / enrolled_customers,
        2
    ) AS pct_of_enrolled
FROM funnel_counts

UNION ALL

SELECT
    3 AS stage_order,
    'Points Redeemer' AS stage,
    points_redeemers AS customers,
    ROUND(
        100.0 * points_redeemers / enrolled_customers,
        2
    ) AS pct_of_enrolled
FROM funnel_counts

ORDER BY stage_order;
