import pandas as pd
import os
import glob

# Define raw data directory
DATA_DIR = "data/raw"

# Find all CSV files
csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

print("=" * 70)
print("MUTUAL FUND DATA INGESTION")
print("=" * 70)

print(f"\nTotal CSV files found: {len(csv_files)}")

if len(csv_files) != 10:
    print("WARNING: Expected 10 CSV files!")

# Dictionary to store datasets
datasets = {}

# Load and inspect each dataset
for file in csv_files:

    filename = os.path.basename(file)

    print("\n" + "=" * 70)
    print(f"DATASET: {filename}")
    print("=" * 70)

    try:
        df = pd.read_csv(file)

        # Store dataset
        datasets[filename] = df

        # Display shape
        print("\nSHAPE:")
        print(df.shape)

        # Display data types
        print("\nDATA TYPES:")
        print(df.dtypes)

        # Display first 5 rows
        print("\nFIRST 5 ROWS:")
        print(df.head())

        # Basic anomaly checks
        print("\nDATA QUALITY CHECKS:")
        print("Missing values:")
        print(df.isnull().sum())

        print("\nDuplicate rows:", df.duplicated().sum())

    except Exception as e:
        print(f"Error loading {filename}: {e}")

print("\n" + "=" * 70)
print("DATA INGESTION COMPLETED")
print("=" * 70)
