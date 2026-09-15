# Data Quality Report

## 1. Overview

This project uses the Maven Analytics Airline Loyalty Program dataset.

The raw data consists of four CSV files:

- `data_dictionary.csv`
- `calendar.csv`
- `customer_flight_activity.csv`
- `customer_loyalty_history.csv`

The data was profiled and validated before any transformations were applied.

The raw files are treated as immutable source data. Cleaning and analytical transformations are performed separately and written to `data/processed/`.

---

## 2. Raw Dataset Profile

### Data Dictionary

- Rows: 24
- Columns: 3
- Missing values in `Table`: 22
- Duplicate rows: 0

The missing `Table` values are expected because the dictionary groups fields under table names rather than repeating the table name on every row.

### Calendar

- Rows: 2,557
- Columns: 4
- Date range: January 1, 2012 to December 31, 2018
- Missing values: 0
- Duplicate rows: 0

The historical date range is preserved. Dates are not shifted or replaced with a more recent period.

### Customer Flight Activity

- Raw rows: 392,936
- Columns: 8
- Unique customers: 16,737
- Exact duplicate rows: 1,922
- Unique customer-month combinations: 389,065

### Customer Loyalty History

- Rows: 16,737
- Columns: 16
- Duplicate rows: 0
- Missing salary values: 4,238
- Missing cancellation dates: 14,670
- Customers with recorded cancellation dates: 2,067

---

## 3. Referential Integrity

The customer key is `Loyalty Number`.

The flight activity and loyalty history datasets contain the same 16,737 unique customer identifiers.

No unmatched customer identifiers were found between the two datasets.

This supports joining the activity and customer tables using `Loyalty Number`.

---

## 4. Activity Data Grain

The raw flight activity data does not have a unique customer-month grain.

There are:

- 389,065 unique customer-month combinations
- 3,847 customer-month combinations with multiple source records
- 3,823 customer-month combinations with two records
- 24 customer-month combinations with three records

Among the 3,847 multi-row customer-month combinations:

- 1,904 contain identical activity values
- 1,943 contain differing activity values

Inspection of the differing records showed additive-looking activity measures within a customer-month. For example, separate records can contain different flight activity and points redemption activity for the same customer and month.

Therefore, the analytical fact table uses customer-month as its grain.

---

## 5. Duplicate Records

The raw activity table contains 1,922 exact duplicate rows.

These records provide no additional information and would inflate activity metrics if retained.

Exact duplicate copies are therefore removed during the cleaning process.

---

## 6. Activity Metric Validation

No negative values were found in the activity metrics.

The following relationships were also checked:

- No rows have flights greater than zero with zero distance.
- No rows have zero flights with positive distance.
- No rows have zero flights with positive accumulated points.
- No rows have positive redemption cost with zero points redeemed.

There are 2,948 rows where points are redeemed while current-period points accumulated are zero. This is retained because customers can redeem points accumulated during previous periods.

There are 5,445 rows where points accumulated differs from distance. This is also retained because there is no established business rule requiring these measures to be equal.

Source values are therefore preserved rather than recalculated.

---

## 7. Temporal Data Quality

Activity dates were compared with customer enrollment and cancellation dates.

### Pre-enrollment activity

- 52,874 customer-month records are flagged for pre-enrollment activity.

These records are retained and flagged rather than deleted.

### Post-cancellation activity

- 33,988 customer-month records contain activity after the recorded cancellation date after customer-month aggregation.

These records are retained and flagged rather than deleted.

The source data is preserved because these observations may reflect source-system semantics or data-generation behavior that cannot be established from the available fields alone.

They will be excluded or handled explicitly in lifecycle analyses where appropriate.

---

## 8. Missing Values

### Salary

4,238 customers have a missing salary.

Missing salary is preserved as `NULL`. It is not replaced with zero because zero salary would represent a different business meaning.

A salary availability indicator is planned for analytical use.

### Cancellation Date

14,670 customers have no cancellation year or month.

These records are treated as having no recorded cancellation rather than imputing a cancellation date.

---

## 9. Zero-Activity Records

Zero-activity records are retained.

A recorded month with zero flights and zero activity is analytically different from the absence of a customer-month record.

This distinction is important for retention and inactivity analysis.

---

## 10. Processed Activity Dataset

The cleaned activity pipeline:

1. Loads the raw activity and customer history files.
2. Removes exact duplicate activity rows.
3. Creates an activity date.
4. Joins enrollment and cancellation dates.
5. Creates temporal quality flags.
6. Aggregates activity to customer-month grain.
7. Creates activity indicators.
8. Writes the result to Parquet.

Output:

`data/processed/fact_customer_month.parquet`

Result:

- Rows: 389,065
- Columns: 17
- Unique customer-month keys: 389,065
- Duplicate customer-month keys: 0
- Customers represented: 16,737

---

## 11. Principle

No transformation is applied without documenting the reason for it.

The raw data remains unchanged, while analytical transformations are performed in reproducible code.
