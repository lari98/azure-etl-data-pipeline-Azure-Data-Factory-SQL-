"""
Data Warehouse Loaders
Loads transformed data into the analytics warehouse (SQLite for demo).
Supports full refresh and incremental loading patterns.
"""

import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def load_to_warehouse(datasets, warehouse_dir=None):
    """Load all datasets to warehouse as CSV files (portable format)."""
    if warehouse_dir is None:
        warehouse_dir = os.path.join(BASE_DIR, "data", "warehouse")
    os.makedirs(warehouse_dir, exist_ok=True)

    print("\n[LOAD] Writing to data warehouse...")

    for name, df in datasets.items():
        df_out = df.copy()
        # Convert datetime columns
        for col in df_out.select_dtypes(include=["datetime64"]).columns:
            df_out[col] = df_out[col].astype(str)
        for col in df_out.select_dtypes(include=["category"]).columns:
            df_out[col] = df_out[col].astype(str)

        csv_path = os.path.join(warehouse_dir, f"{name}.csv")
        df_out.to_csv(csv_path, index=False)
        print(f"  {name}: {len(df_out):,} rows -> {csv_path}")

    print(f"\n  Warehouse location: {warehouse_dir}")
    print("  Load complete!")

    return warehouse_dir
