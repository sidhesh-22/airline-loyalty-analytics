from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = PROJECT_ROOT / "data" / "raw"


# ---------------------------------------------------------
# Load raw files
# ---------------------------------------------------------

files = {
    "data_dictionary": RAW_DATA / "data_dictionary.csv",
    "calendar": RAW_DATA / "calendar.csv",
    "customer_flight_activity": RAW_DATA / "customer_flight_activity.csv",
    "customer_loyalty_history": RAW_DATA / "customer_loyalty_history.csv",
}


dataframes = {}

for name, path in files.items():
    print("=" * 80)
    print(f"DATASET: {name}")
    print("=" * 80)
    print(f"Path: {path}")

    df = pd.read_csv(path)
    dataframes[name] = df

    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]:,}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if len(missing) == 0:
        print("  None")
    else:
        print(missing)

    print("\nDuplicate rows:")
    print(f"  {df.duplicated().sum():,}")

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    print()