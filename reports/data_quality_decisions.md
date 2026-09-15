# Data Quality Decisions

This document records analytical decisions made during data validation and preparation.

The purpose is to make data transformations auditable and reproducible.

---

## Decision 1 — Exact Duplicate Activity Rows

**Issue**

The raw flight activity table contains 1,922 exact duplicate rows.

**Evidence**

392,936 raw rows contain 1,922 redundant duplicate copies.

**Decision**

Remove exact duplicate copies during the cleaning process.

**Reason**

Identical records provide no additional information and would cause activity metrics to be overstated.

**Implementation**

`drop_duplicates()` is applied before customer-month aggregation.

---

## Decision 2 — Multiple Activity Records per Customer-Month

**Issue**

The raw activity table contains 3,847 customer-month combinations with multiple source records.

**Evidence**

1,904 groups contain identical values and 1,943 groups contain differing values.

Inspection of differing examples shows activity measures that appear additive within the same customer-month.

**Decision**

Aggregate activity records to one customer-month record.

**Reason**

The project requires a customer-month analytical grain for cohort, retention, churn, and lifecycle analysis.

Activity measures are summed within customer-month:

- Total Flights
- Distance
- Points Accumulated
- Points Redeemed
- Dollar Cost Points Redeemed

---

## Decision 3 — Zero-Activity Records

**Issue**

Some source records contain zero flights, zero distance, and zero accumulated points.

**Decision**

Retain zero-activity records.

**Reason**

An observed inactive month is different from a month for which no observation exists. This distinction is important for retention and inactivity analysis.

---

## Decision 4 — Points Redeemed Without Current-Period Accumulation

**Issue**

2,948 source rows contain points redeemed while points accumulated in that row are zero.

**Decision**

Retain the records.

**Reason**

Points may have been accumulated in previous periods. Current-period accumulation is not equivalent to a customer's available points balance.

No rule is applied requiring points redeemed to be less than or equal to points accumulated in the same period.

---

## Decision 5 — Points Accumulated vs. Distance

**Issue**

5,445 source rows have points accumulated values that differ from distance.

**Decision**

Retain the source values.

**Reason**

There is no established business rule in the available data that requires points accumulated to equal distance.

The source metric is therefore treated as authoritative.

---

## Decision 6 — Pre-Enrollment Activity

**Issue**

Activity exists before the customer's recorded enrollment date.

**Evidence**

52,874 customer-month records contain pre-enrollment activity after aggregation.

**Decision**

Retain the records and flag them.

**Reason**

The source data does not provide enough information to determine whether these observations represent an error, a difference in enrollment semantics, or another source-system behavior.

Deleting them would alter the observed source history.

Lifecycle analyses should explicitly decide whether these records are included.

---

## Decision 7 — Post-Cancellation Activity

**Issue**

Activity exists after the customer's recorded cancellation date.

**Evidence**

33,988 customer-month records contain post-cancellation activity after aggregation.

**Decision**

Retain the records and flag them.

**Reason**

The source data does not establish why activity appears after cancellation.

Deleting the records would hide a source-data characteristic before its meaning is understood.

Lifecycle analyses should explicitly decide whether these records are included.

---

## Decision 8 — Missing Salary

**Issue**

4,238 customers have missing salary values.

**Decision**

Preserve salary as `NULL`.

**Reason**

Missing salary does not mean zero salary. Replacing missing values with zero would introduce false information.

A salary availability indicator may be used when segmentation requires income information.

---

## Decision 9 — Missing Cancellation Date

**Issue**

14,670 customers have no recorded cancellation year or month.

**Decision**

Treat the cancellation date as NULL / no recorded cancellation.

**Reason**

There is no basis for imputing a cancellation date.

These customers should not automatically be classified as cancelled.

---

## Decision 10 — Historical Dates

**Issue**

The calendar and customer history contain dates from 2012 through 2018.

**Decision**

Preserve the original dates.

**Reason**

Changing historical dates would alter the source data and potentially distort cohort and tenure calculations.

The analytical model will instead create appropriate date dimensions and observation-window logic.

---

## Decision 11 — Customer Key

**Issue**

The activity and loyalty history datasets need to be joined.

**Evidence**

Both datasets contain the same 16,737 unique loyalty numbers, with no unmatched keys.

**Decision**

Use `Loyalty Number` as the customer business key.

**Reason**

Referential integrity was validated successfully.

---

## Decision 12 — Analytical Grain

**Decision**

The primary activity fact table has the following grain:

> One row per customer per calendar month.

**Business key**

`Loyalty Number + Year + Month`

**Reason**

This grain supports the project's planned cohort, retention, churn, lifecycle, and segmentation analyses while avoiding duplicated activity caused by the finer-grained raw records.

---

## Guiding Principle

Raw data is immutable.

Cleaning decisions are implemented through reproducible code rather than manual modification of source files.

When the meaning of an anomaly cannot be established from the available data, the preferred approach is to preserve the observation, flag it, and make the treatment explicit in downstream analysis.
