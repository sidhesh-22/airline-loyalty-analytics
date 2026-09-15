from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = PROJECT_ROOT / "data" / "raw"


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

flight = pd.read_csv(
    RAW_DATA / "customer_flight_activity.csv"
)

loyalty = pd.read_csv(
    RAW_DATA / "customer_loyalty_history.csv"
)


# ---------------------------------------------------------
# Basic key checks
# ---------------------------------------------------------

print("=" * 80)
print("1. CUSTOMER KEY CHECK")
print("=" * 80)

flight_customers = set(flight["Loyalty Number"].unique())
loyalty_customers = set(loyalty["Loyalty Number"].unique())

print(f"Unique customers in flight activity: {len(flight_customers):,}")
print(f"Unique customers in loyalty history: {len(loyalty_customers):,}")

flight_only = flight_customers - loyalty_customers
loyalty_only = loyalty_customers - flight_customers

print(f"Customers in flight activity but not loyalty history: {len(flight_only):,}")
print(f"Customers in loyalty history but not flight activity: {len(loyalty_only):,}")


# ---------------------------------------------------------
# Exact duplicate investigation
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("2. EXACT DUPLICATES")
print("=" * 80)

duplicate_mask = flight.duplicated(keep=False)
duplicates = flight.loc[duplicate_mask].copy()

print(f"Rows involved in exact duplicate groups: {len(duplicates):,}")
print(f"Number of duplicate rows beyond first occurrence: {flight.duplicated().sum():,}")

print("\nSample duplicate groups:")

duplicate_counts = (
    flight
    .groupby(list(flight.columns))
    .size()
    .reset_index(name="row_count")
    .query("row_count > 1")
    .sort_values("row_count", ascending=False)
)

print(duplicate_counts.head(10).to_string(index=False))


# ---------------------------------------------------------
# Customer-month grain
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("3. CUSTOMER-MONTH GRAIN")
print("=" * 80)

customer_month_counts = (
    flight
    .groupby(["Loyalty Number", "Year", "Month"])
    .size()
    .reset_index(name="row_count")
)

multi_row_months = customer_month_counts[
    customer_month_counts["row_count"] > 1
]

print(
    f"Unique customer-month combinations: "
    f"{len(customer_month_counts):,}"
)

print(
    f"Customer-month combinations with multiple rows: "
    f"{len(multi_row_months):,}"
)

print(
    f"Maximum rows for one customer-month: "
    f"{customer_month_counts['row_count'].max()}"
)


# ---------------------------------------------------------
# Multiple customer-month records with different values
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("4. MULTIPLE CUSTOMER-MONTH RECORDS WITH DIFFERENT VALUES")
print("=" * 80)

activity_columns = [
    "Total Flights",
    "Distance",
    "Points Accumulated",
    "Points Redeemed",
    "Dollar Cost Points Redeemed",
]

monthly_variation = (
    flight
    .groupby(["Loyalty Number", "Year", "Month"])[activity_columns]
    .nunique()
)

different_value_months = monthly_variation[
    monthly_variation.max(axis=1) > 1
]

print(
    "Customer-month combinations containing different "
    f"values across rows: {len(different_value_months):,}"
)

if len(different_value_months) > 0:
    examples = different_value_months.head(10).reset_index()
    print("\nExamples:")
    print(examples.to_string(index=False))


# ---------------------------------------------------------
# Create activity date
# ---------------------------------------------------------

flight["Activity Date"] = pd.to_datetime(
    flight["Year"].astype(str)
    + "-"
    + flight["Month"].astype(str)
    + "-01"
)

loyalty["Enrollment Date"] = pd.to_datetime(
    loyalty["Enrollment Year"].astype(str)
    + "-"
    + loyalty["Enrollment Month"].astype(str)
    + "-01"
)

loyalty["Cancellation Date"] = pd.to_datetime(
    loyalty["Cancellation Year"].fillna(9999).astype(int).astype(str)
    + "-"
    + loyalty["Cancellation Month"].fillna(12).astype(int).astype(str)
    + "-01",
    errors="coerce",
)


# ---------------------------------------------------------
# Enrollment consistency
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("5. ACTIVITY BEFORE ENROLLMENT")
print("=" * 80)

flight_with_enrollment = flight.merge(
    loyalty[
        [
            "Loyalty Number",
            "Enrollment Date",
            "Cancellation Date",
        ]
    ],
    on="Loyalty Number",
    how="left",
)

before_enrollment = flight_with_enrollment[
    flight_with_enrollment["Activity Date"]
    < flight_with_enrollment["Enrollment Date"]
]

print(
    f"Activity rows before recorded enrollment: "
    f"{len(before_enrollment):,}"
)

print(
    "Unique customers affected: "
    f"{before_enrollment['Loyalty Number'].nunique():,}"
)


# ---------------------------------------------------------
# Post-cancellation activity
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("6. ACTIVITY AFTER CANCELLATION")
print("=" * 80)

has_cancellation = flight_with_enrollment["Cancellation Date"].notna()

after_cancellation = flight_with_enrollment[
    has_cancellation
    & (
        flight_with_enrollment["Activity Date"]
        > flight_with_enrollment["Cancellation Date"]
    )
]

print(
    f"Activity rows after recorded cancellation: "
    f"{len(after_cancellation):,}"
)

print(
    "Unique customers affected: "
    f"{after_cancellation['Loyalty Number'].nunique():,}"
)


# ---------------------------------------------------------
# Missing values in loyalty data
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("7. LOYALTY HISTORY MISSING VALUES")
print("=" * 80)

missing = loyalty.isna().sum()
missing = missing[missing > 0].sort_values(ascending=False)

print(missing)


# ---------------------------------------------------------
# Value ranges
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("8. NUMERIC RANGE CHECKS")
print("=" * 80)

numeric_columns = [
    "Total Flights",
    "Distance",
    "Points Accumulated",
    "Points Redeemed",
    "Dollar Cost Points Redeemed",
]

for column in numeric_columns:
    print(
        f"{column}: "
        f"min={flight[column].min():,.2f}, "
        f"max={flight[column].max():,.2f}, "
        f"mean={flight[column].mean():,.2f}"
    )


# ---------------------------------------------------------
# Categorical values
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("9. CUSTOMER CATEGORIES")
print("=" * 80)

categorical_columns = [
    "Gender",
    "Education",
    "Marital Status",
    "Loyalty Card",
    "Enrollment Type",
]

for column in categorical_columns:
    print(f"\n{column}:")
    print(loyalty[column].value_counts(dropna=False).to_string())


print("\n" + "=" * 80)
print("QUALITY INVESTIGATION COMPLETE")
print("=" * 80)
