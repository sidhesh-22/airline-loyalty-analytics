CREATE OR REPLACE TABLE stg_calendar AS
SELECT *
FROM read_csv_auto(
    'data/raw/calendar.csv',
    header = true
);

CREATE OR REPLACE TABLE stg_customer_flight_activity AS
SELECT *
FROM read_csv_auto(
    'data/raw/customer_flight_activity.csv',
    header = true
);

CREATE OR REPLACE TABLE stg_customer_loyalty_history AS
SELECT *
FROM read_csv_auto(
    'data/raw/customer_loyalty_history.csv',
    header = true
);

CREATE OR REPLACE TABLE stg_data_dictionary AS
SELECT *
FROM read_csv_auto(
    'data/raw/data_dictionary.csv',
    header = true
);