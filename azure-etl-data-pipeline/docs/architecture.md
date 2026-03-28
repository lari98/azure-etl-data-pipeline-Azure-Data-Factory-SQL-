# Pipeline Architecture

## Overview
This ETL pipeline follows Azure Data Factory (ADF) design patterns, implemented locally with Python for portability and demonstration purposes.

## Pipeline Flow

```
┌──────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                          │
│                   (pipeline.py)                          │
└─────────┬───────────┬──────────────┬────────────────────┘
          │           │              │
    ┌─────▼─────┐ ┌───▼────┐  ┌─────▼──────┐
    │  EXTRACT  │ │VALIDATE│  │ TRANSFORM  │
    │           │ │        │  │            │
    │ CSV files │ │ Schema │  │ Clean data │
    │ JSON API  │ │ Nulls  │  │ Build dims │
    │ DB tables │ │ Dupes  │  │ SCD Type 2 │
    │           │ │ RefInt │  │ Fact table │
    └─────┬─────┘ └───┬────┘  └─────┬──────┘
          │           │              │
          ▼           ▼              ▼
    ┌─────────────────────────────────────┐
    │              LOAD                    │
    │                                      │
    │  Star Schema Data Warehouse (CSV)    │
    │  fact_sales + dim_date/customer/     │
    │  product/channel                     │
    └──────────────────────────────────────┘
```

## Components

### 1. Extractors (extractors.py)
- Mirrors ADF Copy Activity
- Multi-source support: CSV, JSON, API simulation
- Generates realistic DACH e-commerce data

### 2. Validators (validators.py)
- Schema validation
- Null rate checks with configurable thresholds
- Duplicate detection
- Referential integrity verification
- Business rule enforcement

### 3. Transformers (transformers.py)
- Data cleaning and standardization
- Date dimension generation
- Customer dimension with SCD Type 2 preparation
- Product dimension enrichment
- Fact table construction with surrogate keys

### 4. Loaders (loaders.py)
- Star schema warehouse loading
- CSV export for BI tool compatibility
- Idempotent (safe to re-run)

### 5. Utilities (utils.py)
- YAML configuration loading
- Logging setup
- Watermark tracking for incremental loads
- Pipeline metrics collection

## Configuration
All pipeline settings are in `config/pipeline_config.yaml`, including source paths, quality thresholds, and warehouse settings.

## Azure Data Factory Mapping
| Local Component | ADF Equivalent |
|-----------------|----------------|
| pipeline.py | ADF Pipeline |
| extractors.py | Copy Activity |
| validators.py | Data Flow (validation) |
| transformers.py | Mapping Data Flow |
| loaders.py | Copy Activity (sink) |
| pipeline_config.yaml | Linked Services + Datasets |
| watermarks.yaml | Watermark tracking |
| pipeline.log | ADF Monitor |
