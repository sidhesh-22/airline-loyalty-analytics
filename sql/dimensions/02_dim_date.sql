CREATE OR REPLACE TABLE dim_date AS

SELECT
    "Date" AS date,
    EXTRACT(YEAR FROM "Date")::INTEGER AS year,
    EXTRACT(QUARTER FROM "Date")::INTEGER AS quarter,
    EXTRACT(MONTH FROM "Date")::INTEGER AS month,
    STRFTIME("Date", '%B') AS month_name,
    EXTRACT(DAY FROM "Date")::INTEGER AS day,
    DAYOFWEEK("Date")::INTEGER AS day_of_week,
    STRFTIME("Date", '%A') AS day_name,

    DATE_TRUNC('year', "Date") AS start_of_year,
    DATE_TRUNC('quarter', "Date") AS start_of_quarter,
    DATE_TRUNC('month', "Date") AS start_of_month

FROM stg_calendar;