import pandas as pd

FILE = "data/raw/customer_flight_activity.csv"

df = pd.read_csv(FILE)

numeric_cols = [
    "Total Flights",
    "Distance",
    "Points Accumulated",
    "Points Redeemed",
    "Dollar Cost Points Redeemed",
]

print("=" * 80)
print("ACTIVITY METRIC VALIDATION")
print("=" * 80)

# -------------------------------------------------------------------
# 1. Negative values
# -------------------------------------------------------------------

print("\nNEGATIVE VALUES")
print("-" * 80)

for col in numeric_cols:
    count = (df[col] < 0).sum()
    print(f"{col}: {count}")

# -------------------------------------------------------------------
# 2. Basic metric ranges
# -------------------------------------------------------------------

print("\nMETRIC RANGES")
print("-" * 80)

print(df[numeric_cols].describe().T[
    ["min", "max", "mean", "50%", "std"]
].to_string())

# -------------------------------------------------------------------
# 3. Relationship between flights and distance
# -------------------------------------------------------------------

print("\nZERO FLIGHTS WITH POSITIVE DISTANCE")
print("-" * 80)

count = (
    (df["Total Flights"] == 0)
    & (df["Distance"] > 0)
).sum()

print(f"Rows: {count}")

# -------------------------------------------------------------------
# 4. Zero flights with accumulated points
# -------------------------------------------------------------------

print("\nZERO FLIGHTS WITH POSITIVE ACCUMULATED POINTS")
print("-" * 80)

count = (
    (df["Total Flights"] == 0)
    & (df["Points Accumulated"] > 0)
).sum()

print(f"Rows: {count}")

# -------------------------------------------------------------------
# 5. Redemption without accumulated points
# -------------------------------------------------------------------

print("\nREDEMPTION WITHOUT ACCUMULATED POINTS")
print("-" * 80)

count = (
    (df["Points Redeemed"] > 0)
    & (df["Points Accumulated"] == 0)
).sum()

print(f"Rows: {count}")

# -------------------------------------------------------------------
# 6. Redemption cost without redemption points
# -------------------------------------------------------------------

print("\nREDEMPTION COST WITHOUT REDEEMED POINTS")
print("-" * 80)

count = (
    (df["Dollar Cost Points Redeemed"] > 0)
    & (df["Points Redeemed"] == 0)
).sum()

print(f"Rows: {count}")

# -------------------------------------------------------------------
# 7. Flights vs distance relationship
# -------------------------------------------------------------------

print("\nFLIGHTS > 0 BUT DISTANCE = 0")
print("-" * 80)

count = (
    (df["Total Flights"] > 0)
    & (df["Distance"] == 0)
).sum()

print(f"Rows: {count}")

# -------------------------------------------------------------------
# 8. Points accumulated vs distance
# -------------------------------------------------------------------

print("\nPOINTS ACCUMULATED != DISTANCE")
print("-" * 80)

count = (
    df["Points Accumulated"] != df["Distance"]
).sum()

print(f"Rows: {count}")

# -------------------------------------------------------------------
# 9. Exact duplicate count
# -------------------------------------------------------------------

print("\nEXACT DUPLICATES")
print("-" * 80)

print(f"Duplicate rows: {df.duplicated().sum()}")
