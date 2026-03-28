"""
Unit tests for ETL pipeline components.
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from extractors import generate_customers, generate_products, generate_channels
from transformers import clean_transactions, build_dim_date, build_dim_customer
from validators import DataQualityReport, validate_nulls, validate_duplicates


class TestExtractors:
    def test_generate_customers_count(self):
        df = generate_customers(100)
        assert len(df) == 100

    def test_customer_columns(self):
        df = generate_customers(10)
        required = ["customer_id", "first_name", "last_name", "city", "country", "segment"]
        for col in required:
            assert col in df.columns

    def test_customer_ids_unique(self):
        df = generate_customers(500)
        assert df["customer_id"].nunique() == 500

    def test_customer_countries(self):
        df = generate_customers(1000)
        assert set(df["country"].unique()).issubset({"DE", "AT", "CH"})

    def test_generate_products(self):
        products = generate_products(50)
        assert len(products) > 0
        assert all("product_id" in p for p in products)
        assert all(p["price_eur"] > 0 for p in products)

    def test_generate_channels(self):
        df = generate_channels()
        assert len(df) == 5
        assert "channel_id" in df.columns


class TestTransformers:
    def test_clean_transactions(self):
        df = pd.DataFrame({
            "transaction_id": ["T1", "T2", "T3"],
            "order_date": ["2024-01-01 10:00:00", "2024-01-02 11:00:00", "2024-01-03 12:00:00"],
            "status": ["completed", "returned", "cancelled"],
            "total_amount_eur": [100.0, 50.0, 30.0],
            "payment_method": ["Credit_Card", " paypal ", "BANK_TRANSFER"],
        })
        cleaned = clean_transactions(df)
        assert "is_return" in cleaned.columns
        assert "net_amount_eur" in cleaned.columns
        assert cleaned.loc[cleaned["status"] == "returned", "net_amount_eur"].iloc[0] == -50.0

    def test_build_dim_date(self):
        dim = build_dim_date("2024-01-01", "2024-01-31")
        assert len(dim) == 31
        assert "date_key" in dim.columns
        assert "month_name_de" in dim.columns

    def test_build_dim_customer(self):
        customers = pd.DataFrame({
            "customer_id": ["C001"],
            "first_name": ["Max"],
            "last_name": ["Müller"],
            "email": ["max@test.com"],
            "city": ["Berlin"],
            "country": ["DE"],
            "segment": ["Premium"],
            "registration_date": ["2024-01-01"],
            "is_active": [True],
        })
        dim = build_dim_customer(customers)
        assert "customer_key" in dim.columns
        assert "full_name" in dim.columns
        assert dim["full_name"].iloc[0] == "Max Müller"
        assert dim["region"].iloc[0] == "Deutschland"


class TestValidators:
    def test_quality_report(self):
        report = DataQualityReport("test")
        report.add_check("check1", "PASS")
        report.add_check("check2", "FAIL", "error")
        summary = report.summary()
        assert summary["passed"] == 1
        assert summary["failed"] == 1

    def test_validate_nulls_pass(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        report = DataQualityReport("test")
        validate_nulls(df, ["a", "b"], report=report)
        assert report.failed == 0

    def test_validate_nulls_fail(self):
        df = pd.DataFrame({"a": [1, None, None, None, None]})
        report = DataQualityReport("test")
        validate_nulls(df, ["a"], threshold=0.05, report=report)
        assert report.failed == 1

    def test_validate_duplicates_pass(self):
        df = pd.DataFrame({"id": [1, 2, 3]})
        report = DataQualityReport("test")
        validate_duplicates(df, ["id"], report=report)
        assert report.failed == 0

    def test_validate_duplicates_fail(self):
        df = pd.DataFrame({"id": [1, 1, 2, 2, 2, 3, 3, 3, 3, 4]})
        report = DataQualityReport("test")
        validate_duplicates(df, ["id"], threshold=0.001, report=report)
        assert report.failed == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
