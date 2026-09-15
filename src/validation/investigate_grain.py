from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = PROJECT_ROOT / "data" / "raw"

flight = pd.read_csv(
    RAW_DATA / "customer_flight_activity.csv"
)


# ---------------------------------------------------------
# Find customer-months with multiple rows
# ---------------------------------------------------------

group_cols = [
    "Loyalty Number",
    "Year",
    "Month",
]

counts = (
    flight
    .groupby(group_cols)
    .size()
    .reset_index(name="row_count")
)

multi_months = counts[
    counts["row_count"] > 1
].sort_values(
    ["row_count", "Loyalty Number", "Year", "Month"],
    ascending=[False, True, True, True],
)


print("=" * 80)
print("CUSTOMER-MONTHS WITH MULTIPLE RECORDS")
print("=" * 80)

print(f"Total multi-row customer-months: {len(multi_months):,}")

print("\nFirst 20:")
print(multi_months.head(20).to_string(index=False))


# ---------------------------------------------------------
# Show actual records
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("ACTUAL RECORDS FOR SAMPLE MULTI-ROW CUSTOMER-MONTHS")
print("=" * 80)

samples = multi_months.head(10)

for _, row in samples.iterrows():

    customer = row["Loyalty Number"]
    year = row["Year"]
    month = row["Month"]

    print(
        f"\nCustomer={customer}, "
        f"Year={year}, "
        f"Month={month}"
    )

    records = flight[
        (flight["Loyalty Number"] == customer)
        & (flight["Year"] == year)
        & (flight["Month"] == month)
    ]

    print(records.to_string(index=False))


# ---------------------------------------------------------
# Distribution of rows per customer-month
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("ROWS PER CUSTOMER-MONTH DISTRIBUTION")
print("=" * 80)

print(
    counts["row_count"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ---------------------------------------------------------
# Compare exact duplicates vs different records
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("MULTI-ROW CUSTOMER-MONTHS: EXACT VS DIFFERENT")
print("=" * 80)

activity_columns = [
    "Total Flights",
    "Distance",
    "Points Accumulated",
    "Points Redeemed",
    "Dollar Cost Points Redeemed",
]

variation = (
    flight
    .groupby(group_cols)[activity_columns]
    .nunique()
)

variation["has_different_values"] = (
    variation.max(axis=1) > 1
)

multi_variation = variation.join(
    counts.set_index(group_cols)
)

print(
    multi_variation[
        multi_variation["row_count"] > 1
    ]["has_different_values"]
    .value_counts()
    .rename({
        False: "All values identical",
        True: "At least one value differs",
    })
    .to_string()
)


# ---------------------------------------------------------
# Customer - Month with different values
# ---------------------------------------------------------


print("=" * 80)
print("SAMPLE CUSTOMER-MONTHS WITH DIFFERING VALUES")
print("=" * 80)

# Identify customer-months where at least one activity value differs
activity_cols = [
    "Total Flights",
    "Distance",
    "Points Accumulated",
    "Points Redeemed",
    "Dollar Cost Points Redeemed",
]

grouped = flight.groupby(
    ["Loyalty Number", "Year", "Month"],
    dropna=False
)

different_groups = []

for key, group in grouped:
    if len(group) > 1:
        if group[activity_cols].drop_duplicates().shape[0] > 1:
            different_groups.append(key)

print(f"Total differing customer-months: {len(different_groups)}")
print()

# Show first 20 examples
for customer, year, month in different_groups[:20]:
    print(f"Customer={customer}, Year={year}, Month={month}")
    
    sample = flight[
        (flight["Loyalty Number"] == customer)
        & (flight["Year"] == year)
        & (flight["Month"] == month)
    ]
    
    print(sample.to_string(index=False))
    print("-" * 80)
