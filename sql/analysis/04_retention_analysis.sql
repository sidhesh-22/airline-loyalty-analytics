-- ============================================================
-- Retention Analysis
-- Grain: one row per cohort and month since cohort
-- ============================================================

CREATE OR REPLACE TABLE retention_metrics AS

SELECT
    cohort_month,
    months_since_cohort,
    cohort_size,
    active_customers,
    retention_rate,

    -- Number of customers no longer active
    cohort_size - active_customers AS inactive_customers

FROM cohort_monthly_metrics
ORDER BY
    cohort_month,
    months_since_cohort;