from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

ACTIVITY_FILE = RAW_DIR / "customer_flight_activity.csv"
CUSTOMER_FILE = RAW_DIR / "customer_loyalty_history.csv"

OUTPUT_FILE = PROCESSED_DIR / "fact_customer_month.parquet"


# -------------------------------------------------------------------
# Load data
# -------------------------------------------------------------------

print("=" * 80)
print("LOADING RAW DATA")
print("=" * 80)

activity = pd.read_csv(ACTIVITY_FILE)
customers = pd.read_csv(CUSTOMER_FILE)

print(f"Activity rows loaded: {len(activity):,}")
print(f"Customer rows loaded: {len(customers):,}")


# -------------------------------------------------------------------
# Create date fields
# -------------------------------------------------------------------

activity["activity_date"] = pd.to_datetime(
    activity["Year"].astype(str)
    + "-"
    + activity["Month"].astype(str)
    + "-01"
)

customers["enrollment_date"] = pd.to_datetime(
    customers["Enrollment Year"].astype(str)
    + "-"
    + customers["Enrollment Month"].astype(str)
    + "-01"
)

customers["cancellation_date"] = pd.to_datetime(
    customers["Cancellation Year"].astype("Int64").astype(str)
    + "-"
    + customers["Cancellation Month"].astype("Int64").astype(str)
    + "-01",
    errors="coerce",
)


# -------------------------------------------------------------------
# Remove exact duplicate activity rows
# -------------------------------------------------------------------

print("\n" + "=" * 80)
print("REMOVING EXACT DUPLICATES")
print("=" * 80)

duplicate_count = activity.duplicated().sum()

print(f"Exact duplicate rows found: {duplicate_count:,}")

activity = activity.drop_duplicates().copy()

print(f"Rows after duplicate removal: {len(activity):,}")


# -------------------------------------------------------------------
# Join customer lifecycle dates
# -------------------------------------------------------------------

print("\n" + "=" * 80)
print("JOINING CUSTOMER LIFECYCLE DATES")
print("=" * 80)

lifecycle = customers[
    [
        "Loyalty Number",
        "enrollment_date",
        "cancellation_date",
    ]
].copy()

activity = activity.merge(
    lifecycle,
    on="Loyalty Number",
    how="left",
    validate="many_to_one",
)

print(f"Rows after lifecycle join: {len(activity):,}")


# -------------------------------------------------------------------
# Temporal quality flags
# -------------------------------------------------------------------

activity["is_pre_enrollment"] = (
    activity["activity_date"] < activity["enrollment_date"]
)

activity["is_post_cancellation"] = (
    activity["cancellation_date"].notna()
    & (activity["activity_date"] > activity["cancellation_date"])
)


# -------------------------------------------------------------------
# Aggregate to customer-month
# -------------------------------------------------------------------

print("\n" + "=" * 80)
print("AGGREGATING TO CUSTOMER-MONTH")
print("=" * 80)

metric_columns = [
    "Total Flights",
    "Distance",
    "Points Accumulated",
    "Points Redeemed",
    "Dollar Cost Points Redeemed",
]

group_columns = [
    "Loyalty Number",
    "activity_date",
    "Year",
    "Month",
]

fact_customer_month = (
    activity
    .groupby(group_columns, as_index=False)
    .agg(
        total_flights=("Total Flights", "sum"),
        distance=("Distance", "sum"),
        points_accumulated=("Points Accumulated", "sum"),
        points_redeemed=("Points Redeemed", "sum"),
        dollar_cost_points_redeemed=(
            "Dollar Cost Points Redeemed",
            "sum",
        ),
        source_activity_rows=("Loyalty Number", "size"),
        pre_enrollment_rows=("is_pre_enrollment", "sum"),
        post_cancellation_rows=("is_post_cancellation", "sum"),
    )
)


# -------------------------------------------------------------------
# Convert row counts to boolean flags
# -------------------------------------------------------------------

fact_customer_month["has_pre_enrollment_activity"] = (
    fact_customer_month["pre_enrollment_rows"] > 0
)

fact_customer_month["has_post_cancellation_activity"] = (
    fact_customer_month["post_cancellation_rows"] > 0
)


# -------------------------------------------------------------------
# Basic activity flags
# -------------------------------------------------------------------

fact_customer_month["has_flight_activity"] = (
    fact_customer_month["total_flights"] > 0
)

fact_customer_month["has_points_accumulated"] = (
    fact_customer_month["points_accumulated"] > 0
)

fact_customer_month["has_points_redeemed"] = (
    fact_customer_month["points_redeemed"] > 0
)


# -------------------------------------------------------------------
# Select final columns
# -------------------------------------------------------------------

fact_customer_month = fact_customer_month[
    [
        "Loyalty Number",
        "activity_date",
        "Year",
        "Month",
        "total_flights",
        "distance",
        "points_accumulated",
        "points_redeemed",
        "dollar_cost_points_redeemed",
        "source_activity_rows",
        "pre_enrollment_rows",
        "post_cancellation_rows",
        "has_pre_enrollment_activity",
        "has_post_cancellation_activity",
        "has_flight_activity",
        "has_points_accumulated",
        "has_points_redeemed",
    ]
].copy()


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

print("\n" + "=" * 80)
print("CLEANED DATA VALIDATION")
print("=" * 80)

print(f"Customer-month rows: {len(fact_customer_month):,}")
print(
    "Unique customer-month keys: "
    f"{fact_customer_month[['Loyalty Number', 'Year', 'Month']].drop_duplicates().shape[0]:,}"
)

duplicate_customer_months = fact_customer_month.duplicated(
    subset=["Loyalty Number", "Year", "Month"]
).sum()

print(f"Duplicate customer-month keys: {duplicate_customer_months:,}")

print(
    "Customers represented: "
    f"{fact_customer_month['Loyalty Number'].nunique():,}"
)

print(
    "Pre-enrollment customer-months: "
    f"{fact_customer_month['has_pre_enrollment_activity'].sum():,}"
)

print(
    "Post-cancellation customer-months: "
    f"{fact_customer_month['has_post_cancellation_activity'].sum():,}"
)

print(
    "Customer-months with flight activity: "
    f"{fact_customer_month['has_flight_activity'].sum():,}"
)

print(
    "Customer-months with points redeemed: "
    f"{fact_customer_month['has_points_redeemed'].sum():,}"
)


# -------------------------------------------------------------------
# Save
# -------------------------------------------------------------------

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

fact_customer_month.to_parquet(
    OUTPUT_FILE,
    index=False,
)

print("\n" + "=" * 80)
print("OUTPUT")
print("=" * 80)

print(f"Saved: {OUTPUT_FILE}")
print(f"Rows: {len(fact_customer_month):,}")
print(f"Columns: {len(fact_customer_month.columns)}")
