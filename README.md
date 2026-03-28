# Azure ETL Data Pipeline

## Overview
A production-grade ETL (Extract, Transform, Load) data pipeline simulating Azure Data Factory patterns for processing e-commerce transaction data. Demonstrates data engineering best practices including incremental loading, data validation, slowly changing dimensions (SCD Type 2), and a star schema data warehouse.

## Key Features
- **Multi-source ingestion**: CSV, JSON, and API-simulated data sources
- **Incremental loading**: Processes only new/changed records using watermark tracking
- **Data quality checks**: Schema validation, null checks, business rule enforcement
- **SCD Type 2**: Tracks historical changes in dimension tables
- **Star schema warehouse**: Fact and dimension tables optimized for analytics
- **Logging & monitoring**: Comprehensive pipeline execution logs
- **Idempotent runs**: Safe to re-run without data duplication

## Tech Stack
- **Python 3.10+** — Core pipeline logic
- **pandas / SQLAlchemy** — Data transformation and ORM
- **SQLite** — Local data warehouse (mirrors Snowflake/Azure SQL patterns)
- **pytest** — Unit and integration tests
- **YAML** — Pipeline configuration

## Architecture
```
[Raw Sources]  →  [Staging Layer]  →  [Transformation]  →  [Data Warehouse]
  CSV/JSON          Validated            Business Logic      Star Schema
  API data          Type-cast            Aggregations        Fact + Dims
                    Deduped              SCD Type 2          Analytics-ready
```

## Project Structure
```
azure-etl-data-pipeline/
├── src/
│   ├── pipeline.py              # Main orchestrator
│   ├── extractors.py            # Data source extractors
│   ├── transformers.py          # Business logic transformations
│   ├── loaders.py               # Data warehouse loaders
│   ├── validators.py            # Data quality framework
│   └── utils.py                 # Logging, config, helpers
├── config/
│   └── pipeline_config.yaml     # Pipeline settings
├── data/
│   ├── raw/                     # Source data files
│   ├── staging/                 # Intermediate processed data
│   └── warehouse/               # Final warehouse tables (CSV export)
├── tests/
│   └── test_pipeline.py         # Unit tests
├── requirements.txt
└── README.md
```

## Quick Start
```bash
pip install -r requirements.txt

# Generate sample e-commerce data
python src/extractors.py

# Run full ETL pipeline
python src/pipeline.py

# Run data quality checks
python src/validators.py

# Run tests
pytest tests/ -v
```

## Data Model (Star Schema)
```
                    ┌─────────────┐
                    │ dim_customer │
                    └──────┬──────┘
                           │
┌──────────┐    ┌──────────┴──────────┐    ┌─────────────┐
│ dim_date  ├────┤   fact_sales        ├────┤ dim_product  │
└──────────┘    └──────────┬──────────┘    └─────────────┘
                           │
                    ┌──────┴──────┐
                    │ dim_channel  │
                    └─────────────┘
```

## Relevance to DACH Market
- Mirrors Azure Data Factory pipeline patterns used across German enterprises
- Implements data engineering practices required by companies like SAP, Siemens, BMW
- Star schema design aligns with BI tool integration (Power BI, Tableau)
- Data quality framework reflects German regulatory standards (GDPR data governance)

## Author
Muhammad Umer Lari — Data Analyst | Analytics Engineer
