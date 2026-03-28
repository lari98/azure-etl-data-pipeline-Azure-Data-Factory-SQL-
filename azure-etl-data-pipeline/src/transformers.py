"""
Data Transformers
Business logic transformations: cleaning, enrichment, dimension building,
SCD Type 2 handling, and fact table construction.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def clean_transactions(df):
    """Clean and standardize transaction data."""
    cleaned = df.copy()

    # Parse dates
    cleaned["order_date"] = pd.to_datetime(cleaned["order_date"])

    # Remove cancelled transactions from fact table (keep for audit)
    active = cleaned[cleaned["status"] != "cancelled"].copy()

    # Standardize payment methods
    cleaned["payment_method"] = cleaned["payment_method"].str.lower().str.strip()

    # Flag returns
    cleaned["is_return"] = cleaned["status"] == "returned"

    # Calculate net amount (returns are negative)
    cleaned["net_amount_eur"] = cleaned.apply(
        lambda r: -r["total_amount_eur"] if r["status"] == "returned" else r["total_amount_eur"],
        axis=1,
    )

    return cleaned


def build_dim_date(start_date="2024-01-01", end_date="2025-12-31"):
    """Build date dimension table."""
    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    dim_date = pd.DataFrame({
        "date_key": dates.strftime("%Y%m%d").astype(int),
        "full_date": dates,
        "year": dates.year,
        "quarter": dates.quarter,
        "month": dates.month,
        "month_name": dates.strftime("%B"),
        "month_name_de": dates.strftime("%B").map({
            "January": "Januar", "February": "Februar", "March": "März",
            "April": "April", "May": "Mai", "June": "Juni",
            "July": "Juli", "August": "August", "September": "September",
            "October": "Oktober", "November": "November", "December": "Dezember",
        }),
        "week": dates.isocalendar().week.astype(int),
        "day_of_week": dates.dayofweek,
        "day_name": dates.strftime("%A"),
        "is_weekend": dates.dayofweek >= 5,
        "is_month_end": dates.is_month_end,
        "fiscal_year": dates.year,  # Simplified: fiscal = calendar
        "fiscal_quarter": dates.quarter,
    })
    return dim_date


def build_dim_customer(customers_df):
    """Build customer dimension with SCD Type 2 preparation."""
    dim = customers_df.copy()
    dim["customer_key"] = range(1, len(dim) + 1)
    dim["effective_from"] = dim["registration_date"]
    dim["effective_to"] = "9999-12-31"
    dim["is_current"] = True

    # Add derived attributes
    dim["full_name"] = dim["first_name"] + " " + dim["last_name"]
    dim["region"] = dim["country"].map({
        "DE": "Deutschland",
        "AT": "Österreich",
        "CH": "Schweiz",
    })

    return dim


def build_dim_product(products_json_path):
    """Build product dimension from JSON source."""
    with open(products_json_path, "r") as f:
        products = json.load(f)

    dim = pd.DataFrame(products)
    dim["product_key"] = range(1, len(dim) + 1)
    dim["margin_eur"] = (dim["price_eur"] - dim["cost_eur"]).round(2)
    dim["margin_pct"] = ((dim["margin_eur"] / dim["price_eur"]) * 100).round(1)

    # Price tier
    dim["price_tier"] = pd.cut(
        dim["price_eur"],
        bins=[0, 25, 100, 250, float("inf")],
        labels=["Budget", "Mid-Range", "Premium", "Luxury"],
    )

    return dim


def build_dim_channel(channels_df):
    """Build channel dimension."""
    dim = channels_df.copy()
    dim["channel_key"] = range(1, len(dim) + 1)
    return dim


def build_fact_sales(transactions_df, dim_customer, dim_product, dim_channel):
    """Build fact_sales table with surrogate keys."""
    fact = transactions_df.copy()

    # Map natural keys to surrogate keys
    cust_map = dim_customer.set_index("customer_id")["customer_key"].to_dict()
    prod_map = dim_product.set_index("product_id")["product_key"].to_dict()
    chan_map = dim_channel.set_index("channel_id")["channel_key"].to_dict()

    fact["customer_key"] = fact["customer_id"].map(cust_map)
    fact["product_key"] = fact["product_id"].map(prod_map)
    fact["channel_key"] = fact["channel_id"].map(chan_map)
    fact["date_key"] = pd.to_datetime(fact["order_date"]).dt.strftime("%Y%m%d").astype(int)

    # Select fact table columns
    fact_cols = [
        "transaction_id", "date_key", "customer_key", "product_key", "channel_key",
        "quantity", "unit_price_eur", "discount_pct", "total_amount_eur",
        "net_amount_eur", "shipping_cost_eur", "payment_method", "status", "is_return",
    ]

    # Drop rows with unmapped keys
    fact = fact.dropna(subset=["customer_key", "product_key", "channel_key"])
    fact[["customer_key", "product_key", "channel_key"]] = fact[["customer_key", "product_key", "channel_key"]].astype(int)

    return fact[fact_cols]


def transform_all(raw_dir):
    """Run all transformations."""
    print("\n[TRANSFORM] Applying business logic...")

    # Load raw data
    transactions = pd.read_csv(os.path.join(raw_dir, "transactions.csv"))
    customers = pd.read_csv(os.path.join(raw_dir, "customers.csv"))
    channels = pd.read_csv(os.path.join(raw_dir, "channels.csv"))
    products_path = os.path.join(raw_dir, "products.json")

    # Clean
    transactions = clean_transactions(transactions)
    print(f"  Cleaned transactions: {len(transactions):,} records")

    # Build dimensions
    dim_date = build_dim_date()
    dim_customer = build_dim_customer(customers)
    dim_product = build_dim_product(products_path)
    dim_channel = build_dim_channel(channels)

    print(f"  dim_date: {len(dim_date):,} rows")
    print(f"  dim_customer: {len(dim_customer):,} rows")
    print(f"  dim_product: {len(dim_product)} rows")
    print(f"  dim_channel: {len(dim_channel)} rows")

    # Build fact table
    fact_sales = build_fact_sales(transactions, dim_customer, dim_product, dim_channel)
    print(f"  fact_sales: {len(fact_sales):,} rows")

    return {
        "dim_date": dim_date,
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_channel": dim_channel,
        "fact_sales": fact_sales,
    }
