"""
Main ETL Pipeline Orchestrator
Coordinates Extract -> Validate -> Transform -> Load workflow.
Mirrors Azure Data Factory pipeline execution patterns.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from utils import load_config, setup_logging, PipelineMetrics
from extractors import extract_all
from validators import run_all_validations
from transformers import transform_all
from loaders import load_to_warehouse

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def run_pipeline():
    """Execute the full ETL pipeline."""
    config = load_config()
    logger = setup_logging(config)
    metrics = PipelineMetrics()

    print("=" * 60)
    print(f"ETL PIPELINE: {config['pipeline']['name']} v{config['pipeline']['version']}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # --- EXTRACT ---
    logger.info("Starting extraction phase")
    customers, products, channels, transactions = extract_all()
    metrics.record("extract", "customers", len(customers))
    metrics.record("extract", "products", len(products))
    metrics.record("extract", "transactions", len(transactions))

    # --- VALIDATE ---
    logger.info("Starting validation phase")
    import pandas as pd
    products_df = pd.DataFrame(products)
    txn_report, cust_report = run_all_validations(transactions, customers, products_df, channels)

    if txn_report.failed > 0:
        logger.warning(f"Transaction validation: {txn_report.failed} checks failed")
    metrics.record("validate", "txn_checks_passed", txn_report.passed)
    metrics.record("validate", "txn_checks_failed", txn_report.failed)

    # --- TRANSFORM ---
    logger.info("Starting transformation phase")
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    datasets = transform_all(raw_dir)
    for name, df in datasets.items():
        metrics.record("transform", name, len(df))

    # --- LOAD ---
    logger.info("Starting load phase")
    warehouse_dir = load_to_warehouse(datasets)

    # --- SUMMARY ---
    summary = metrics.summary()
    print(f"\n{'=' * 60}")
    print("PIPELINE EXECUTION SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Execution Time: {summary['execution_time_sec']}s")
    for stage, m in summary["stages"].items():
        print(f"  [{stage.upper()}]")
        for key, val in m.items():
            print(f"    {key}: {val:,}" if isinstance(val, (int, float)) else f"    {key}: {val}")

    print(f"\nPipeline completed successfully at {datetime.now().strftime('%H:%M:%S')}")
    logger.info("Pipeline completed successfully")

    return summary


if __name__ == "__main__":
    run_pipeline()
