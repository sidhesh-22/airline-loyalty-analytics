CREATE OR REPLACE TABLE dim_customer AS

SELECT
    "Loyalty Number" AS customer_id,
    "Country" AS country,
    "Province" AS province,
    "City" AS city,
    "Postal Code" AS postal_code,
    "Gender" AS gender,
    "Education" AS education,
    "Salary" AS salary,
    "Marital Status" AS marital_status,
    "Loyalty Card" AS loyalty_card,
    "CLV" AS clv,
    "Enrollment Type" AS enrollment_type,
    "Enrollment Year" AS enrollment_year,
    "Enrollment Month" AS enrollment_month,
    "Cancellation Year" AS cancellation_year,
    "Cancellation Month" AS cancellation_month,

    MAKE_DATE(
        "Enrollment Year",
        "Enrollment Month",
        1
    ) AS enrollment_date,

    CASE
        WHEN "Cancellation Year" IS NOT NULL
         AND "Cancellation Month" IS NOT NULL
        THEN MAKE_DATE(
            "Cancellation Year",
            "Cancellation Month",
            1
        )
        ELSE NULL
    END AS cancellation_date,

    CASE
        WHEN "Salary" IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS has_salary,

    CASE
        WHEN "Cancellation Year" IS NOT NULL
         AND "Cancellation Month" IS NOT NULL
        THEN TRUE
        ELSE FALSE
    END AS has_cancellation

FROM stg_customer_loyalty_history;