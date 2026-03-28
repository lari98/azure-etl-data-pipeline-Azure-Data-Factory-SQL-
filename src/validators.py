"""
Data Quality Validation Framework
Implements schema validation, null checks, referential integrity,
and business rule enforcement following data governance best practices.
"""

import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger("etl_pipeline.validators")


class DataQualityReport:
    """Collects and reports data quality findings."""

    def __init__(self, source_name):
        self.source_name = source_name
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_check(self, check_name, status, details=""):
        self.checks.append({
            "check": check_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        })
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        else:
            self.warnings += 1

    def summary(self):
        total = self.passed + self.failed + self.warnings
        return {
            "source": self.source_name,
            "total_checks": total,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "pass_rate": round(self.passed / total * 100, 1) if total > 0 else 0,
        }

    def print_report(self):
        s = self.summary()
        print(f"\n  Quality Report: {s['source']}")
        print(f"  {'='*40}")
        print(f"  Total Checks: {s['total_checks']}")
        print(f"  Passed: {s['passed']} | Failed: {s['failed']} | Warnings: {s['warnings']}")
        print(f"  Pass Rate: {s['pass_rate']}%")
        for c in self.checks:
            icon = "+" if c["status"] == "PASS" else "x" if c["status"] == "FAIL" else "!"
            print(f"    [{icon}] {c['check']}: {c['status']} {c['details']}")


def validate_schema(df, expected_columns, report):
    """Validate DataFrame has expected columns."""
    missing = set(expected_columns) - set(df.columns)
    extra = set(df.columns) - set(expected_columns)

    if not missing:
        report.add_check("Schema - Required columns", "PASS")
    else:
        report.add_check("Schema - Required columns", "FAIL", f"Missing: {missing}")

    if extra:
        report.add_check("Schema - Extra columns", "WARN", f"Extra: {extra}")


def validate_nulls(df, critical_columns, threshold=0.05, report=None):
    """Check null rates against threshold."""
    for col in critical_columns:
        if col not in df.columns:
            continue
        null_rate = df[col].isnull().mean()
        if null_rate == 0:
            report.add_check(f"Nulls - {col}", "PASS", "0% nulls")
        elif null_rate <= threshold:
            report.add_check(f"Nulls - {col}", "WARN", f"{null_rate*100:.2f}% nulls")
        else:
            report.add_check(f"Nulls - {col}", "FAIL", f"{null_rate*100:.2f}% nulls (threshold: {threshold*100}%)")


def validate_duplicates(df, key_columns, threshold=0.001, report=None):
    """Check for duplicate records on key columns."""
    dupes = df.duplicated(subset=key_columns).sum()
    dupe_rate = dupes / len(df)

    if dupe_rate == 0:
        report.add_check(f"Duplicates - {key_columns}", "PASS", "No duplicates")
    elif dupe_rate <= threshold:
        report.add_check(f"Duplicates - {key_columns}", "WARN", f"{dupes} duplicates ({dupe_rate*100:.3f}%)")
    else:
        report.add_check(f"Duplicates - {key_columns}", "FAIL", f"{dupes} duplicates ({dupe_rate*100:.3f}%)")


def validate_referential_integrity(fact_df, fact_key, dim_df, dim_key, report=None):
    """Check that all foreign keys in fact table exist in dimension table."""
    fact_values = set(fact_df[fact_key].unique())
    dim_values = set(dim_df[dim_key].unique())
    orphans = fact_values - dim_values

    if not orphans:
        report.add_check(f"Referential Integrity - {fact_key}", "PASS")
    else:
        report.add_check(f"Referential Integrity - {fact_key}", "FAIL",
                         f"{len(orphans)} orphan keys found")


def validate_business_rules(df, report):
    """Apply business-specific validation rules."""
    # Price must be positive
    if "unit_price_eur" in df.columns:
        neg_prices = (df["unit_price_eur"] <= 0).sum()
        if neg_prices == 0:
            report.add_check("Business Rule - Positive prices", "PASS")
        else:
            report.add_check("Business Rule - Positive prices", "FAIL", f"{neg_prices} non-positive prices")

    # Quantity must be positive integer
    if "quantity" in df.columns:
        bad_qty = (df["quantity"] <= 0).sum()
        if bad_qty == 0:
            report.add_check("Business Rule - Positive quantity", "PASS")
        else:
            report.add_check("Business Rule - Positive quantity", "FAIL", f"{bad_qty} invalid quantities")

    # Total amount consistency
    if all(col in df.columns for col in ["unit_price_eur", "quantity", "discount_pct", "total_amount_eur"]):
        expected = (df["unit_price_eur"] * df["quantity"] * (1 - df["discount_pct"] / 100)).round(2)
        mismatches = (abs(df["total_amount_eur"] - expected) > 0.01).sum()
        if mismatches == 0:
            report.add_check("Business Rule - Amount consistency", "PASS")
        else:
            report.add_check("Business Rule - Amount consistency", "WARN",
                             f"{mismatches} amount mismatches")

    # Date range validation
    if "order_date" in df.columns:
        dates = pd.to_datetime(df["order_date"])
        future_dates = (dates > datetime.now()).sum()
        if future_dates == 0:
            report.add_check("Business Rule - No future dates", "PASS")
        else:
            report.add_check("Business Rule - No future dates", "FAIL", f"{future_dates} future dates")


def run_all_validations(transactions_df, customers_df, products_df, channels_df):
    """Run complete validation suite."""
    print("\n[VALIDATE] Running data quality checks...")

    # Transactions
    txn_report = DataQualityReport("Transactions")
    validate_schema(transactions_df,
                    ["transaction_id", "order_date", "customer_id", "product_id",
                     "channel_id", "quantity", "unit_price_eur", "total_amount_eur"],
                    txn_report)
    validate_nulls(transactions_df,
                   ["transaction_id", "order_date", "customer_id", "product_id"],
                   report=txn_report)
    validate_duplicates(transactions_df, ["transaction_id"], report=txn_report)
    validate_referential_integrity(transactions_df, "customer_id", customers_df, "customer_id", txn_report)
    validate_referential_integrity(transactions_df, "product_id", products_df, "product_id", txn_report)
    validate_referential_integrity(transactions_df, "channel_id", channels_df, "channel_id", txn_report)
    validate_business_rules(transactions_df, txn_report)
    txn_report.print_report()

    # Customers
    cust_report = DataQualityReport("Customers")
    validate_schema(customers_df,
                    ["customer_id", "first_name", "last_name", "city", "country", "segment"],
                    cust_report)
    validate_nulls(customers_df, ["customer_id", "first_name", "last_name"], report=cust_report)
    validate_duplicates(customers_df, ["customer_id"], report=cust_report)
    cust_report.print_report()

    return txn_report, cust_report
