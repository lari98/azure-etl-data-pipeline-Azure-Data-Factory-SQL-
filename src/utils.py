"""
Utility functions for the ETL pipeline.
Logging, configuration loading, and helper functions.
"""

import logging
import yaml
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def load_config(config_path=None):
    """Load pipeline configuration from YAML."""
    if config_path is None:
        config_path = os.path.join(BASE_DIR, "config", "pipeline_config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_logging(config=None):
    """Configure logging for pipeline execution."""
    log_level = "INFO"
    log_file = os.path.join(BASE_DIR, "data", "pipeline.log")

    if config:
        log_level = config.get("logging", {}).get("level", "INFO")
        log_file = os.path.join(BASE_DIR, config.get("logging", {}).get("file", "data/pipeline.log"))

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("etl_pipeline")


def get_watermark(table_name, watermark_file=None):
    """Get the last processed timestamp for incremental loading."""
    if watermark_file is None:
        watermark_file = os.path.join(BASE_DIR, "data", "watermarks.yaml")

    if not os.path.exists(watermark_file):
        return None

    with open(watermark_file, "r") as f:
        watermarks = yaml.safe_load(f) or {}

    return watermarks.get(table_name)


def set_watermark(table_name, timestamp, watermark_file=None):
    """Update the watermark after successful processing."""
    if watermark_file is None:
        watermark_file = os.path.join(BASE_DIR, "data", "watermarks.yaml")

    watermarks = {}
    if os.path.exists(watermark_file):
        with open(watermark_file, "r") as f:
            watermarks = yaml.safe_load(f) or {}

    watermarks[table_name] = str(timestamp)

    with open(watermark_file, "w") as f:
        yaml.dump(watermarks, f)


class PipelineMetrics:
    """Track pipeline execution metrics."""

    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {}

    def record(self, stage, metric, value):
        if stage not in self.metrics:
            self.metrics[stage] = {}
        self.metrics[stage][metric] = value

    def summary(self):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return {
            "execution_time_sec": round(elapsed, 2),
            "stages": self.metrics,
        }
