CREATE OR REPLACE TABLE customer_churn AS

SELECT
    customer_id,
    enrollment_date,
    cancellation_date,
    has_cancellation,

    -- Cohort
    DATE_TRUNC('month', enrollment_date) AS cohort_month,

    -- Cancellation month
    DATE_TRUNC('month', cancellation_date) AS cancellation_month,

    -- Tenure in months at cancellation
    CASE
        WHEN cancellation_date IS NOT NULL
        THEN DATE_DIFF('month', enrollment_date, cancellation_date)
        ELSE NULL
    END AS months_to_cancellation,

    -- Churn status
    CASE
        WHEN cancellation_date IS NOT NULL THEN 'churned'
        ELSE 'not_churned'
    END AS churn_status

FROM dim_customer;