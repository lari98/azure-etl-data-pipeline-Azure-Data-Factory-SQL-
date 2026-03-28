"""
Data Extractors
Generates and extracts data from multiple sources (CSV, JSON, API simulation).
Simulates Azure Data Factory Copy Activity patterns.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

np.random.seed(42)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")


def generate_customers(n=2000):
    """Generate customer dimension data (DACH region focused)."""
    cities_de = ["Berlin", "München", "Hamburg", "Frankfurt", "Köln", "Stuttgart",
                 "Düsseldorf", "Leipzig", "Dresden", "Nürnberg", "Hannover", "Bremen"]
    cities_at = ["Wien", "Graz", "Linz", "Salzburg", "Innsbruck"]
    cities_ch = ["Zürich", "Bern", "Basel", "Genf", "Lausanne"]

    all_cities = [(c, "DE") for c in cities_de] + [(c, "AT") for c in cities_at] + [(c, "CH") for c in cities_ch]

    first_names = ["Max", "Anna", "Lukas", "Sophie", "Leon", "Marie", "Felix", "Laura",
                   "Jonas", "Lena", "Tim", "Julia", "Paul", "Sarah", "David", "Lisa",
                   "Moritz", "Emma", "Jan", "Mia", "Niklas", "Clara", "Simon", "Elena"]
    last_names = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer",
                  "Wagner", "Becker", "Hoffmann", "Schäfer", "Koch", "Bauer",
                  "Richter", "Klein", "Wolf", "Schröder", "Neumann", "Braun"]

    segments = ["Premium", "Standard", "Budget"]
    segment_weights = [0.15, 0.55, 0.30]

    records = []
    for i in range(n):
        city, country = all_cities[np.random.randint(0, len(all_cities))]
        reg_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 730))
        records.append({
            "customer_id": f"C{i+1:05d}",
            "first_name": np.random.choice(first_names),
            "last_name": np.random.choice(last_names),
            "email": f"customer{i+1}@example.com",
            "city": city,
            "country": country,
            "segment": np.random.choice(segments, p=segment_weights),
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "is_active": np.random.random() > 0.1,
        })
    return pd.DataFrame(records)


def generate_products(n=150):
    """Generate product catalog as JSON (simulates API response)."""
    categories = {
        "Elektronik": ["Laptop", "Tablet", "Smartphone", "Kopfhörer", "Monitor", "Tastatur", "Maus"],
        "Haushalt": ["Staubsauger", "Kaffeemaschine", "Mixer", "Toaster", "Wasserkocher"],
        "Sport": ["Laufschuhe", "Fahrrad", "Yogamatte", "Hanteln", "Fitnesstracker"],
        "Büro": ["Schreibtisch", "Bürostuhl", "Drucker", "Aktenvernichter", "Whiteboard"],
        "Mode": ["Jacke", "Hemd", "Schuhe", "Tasche", "Uhr"],
    }

    brands = ["TechPro", "HomePlus", "SportMax", "OfficeLine", "StyleWorks",
              "SmartGear", "EcoHome", "FitLife", "DeskMaster", "UrbanWear"]

    products = []
    pid = 1
    for cat, items in categories.items():
        for _ in range(n // len(categories)):
            item = np.random.choice(items)
            brand = np.random.choice(brands)
            base_price = np.random.uniform(15, 500)
            products.append({
                "product_id": f"P{pid:05d}",
                "product_name": f"{brand} {item}",
                "category": cat,
                "brand": brand,
                "price_eur": round(base_price, 2),
                "cost_eur": round(base_price * np.random.uniform(0.4, 0.7), 2),
                "weight_kg": round(np.random.uniform(0.1, 15), 2),
                "is_available": np.random.random() > 0.05,
                "created_date": (datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 500))).strftime("%Y-%m-%d"),
            })
            pid += 1
    return products


def generate_channels():
    """Generate sales channel dimension."""
    return pd.DataFrame([
        {"channel_id": "CH01", "channel_name": "Website", "channel_type": "Online"},
        {"channel_id": "CH02", "channel_name": "Mobile App", "channel_type": "Online"},
        {"channel_id": "CH03", "channel_name": "Marketplace", "channel_type": "Online"},
        {"channel_id": "CH04", "channel_name": "Retail Store", "channel_type": "Offline"},
        {"channel_id": "CH05", "channel_name": "Phone Order", "channel_type": "Offline"},
    ])


def generate_transactions(customers_df, products, channels_df, n=50000):
    """Generate transaction data (simulates daily e-commerce activity)."""
    customer_ids = customers_df["customer_id"].tolist()
    product_ids = [p["product_id"] for p in products]
    product_prices = {p["product_id"]: p["price_eur"] for p in products}
    channel_ids = channels_df["channel_id"].tolist()
    channel_weights = [0.35, 0.25, 0.20, 0.12, 0.08]

    statuses = ["completed", "returned", "cancelled"]
    status_weights = [0.88, 0.07, 0.05]

    payment_methods = ["credit_card", "paypal", "bank_transfer", "klarna", "apple_pay"]
    payment_weights = [0.35, 0.25, 0.15, 0.15, 0.10]

    records = []
    for i in range(n):
        order_date = datetime(2024, 7, 1) + timedelta(
            days=np.random.randint(0, 365),
            hours=np.random.randint(6, 23),
            minutes=np.random.randint(0, 60),
        )
        prod_id = np.random.choice(product_ids)
        quantity = np.random.choice([1, 1, 1, 2, 2, 3])
        unit_price = product_prices[prod_id]
        discount_pct = np.random.choice([0, 0, 0, 5, 10, 15, 20])
        total = round(unit_price * quantity * (1 - discount_pct / 100), 2)

        # Seasonal patterns: higher sales in Nov-Dec
        if order_date.month in [11, 12]:
            if np.random.random() > 0.3:
                continue  # Skip some to re-weight

        records.append({
            "transaction_id": f"T{i+1:07d}",
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": np.random.choice(customer_ids),
            "product_id": prod_id,
            "channel_id": np.random.choice(channel_ids, p=channel_weights),
            "quantity": quantity,
            "unit_price_eur": unit_price,
            "discount_pct": discount_pct,
            "total_amount_eur": total,
            "payment_method": np.random.choice(payment_methods, p=payment_weights),
            "status": np.random.choice(statuses, p=status_weights),
            "shipping_cost_eur": round(np.random.choice([0, 3.99, 4.99, 6.99]), 2),
        })

    return pd.DataFrame(records)


def extract_all():
    """Extract/generate all source data."""
    os.makedirs(RAW_DIR, exist_ok=True)

    print("[EXTRACT] Generating source data...")

    # Customers (CSV)
    customers = generate_customers()
    customers.to_csv(os.path.join(RAW_DIR, "customers.csv"), index=False)
    print(f"  Customers: {len(customers):,} records")

    # Products (JSON - simulates API response)
    products = generate_products()
    with open(os.path.join(RAW_DIR, "products.json"), "w") as f:
        json.dump(products, f, indent=2)
    print(f"  Products: {len(products)} records")

    # Channels (CSV)
    channels = generate_channels()
    channels.to_csv(os.path.join(RAW_DIR, "channels.csv"), index=False)
    print(f"  Channels: {len(channels)} records")

    # Transactions (CSV - main fact data)
    transactions = generate_transactions(customers, products, channels)
    transactions.to_csv(os.path.join(RAW_DIR, "transactions.csv"), index=False)
    print(f"  Transactions: {len(transactions):,} records")

    return customers, products, channels, transactions


if __name__ == "__main__":
    extract_all()
