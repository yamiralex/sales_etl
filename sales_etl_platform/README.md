# Sales ETL Platform

## Overview

This project implements a batch-oriented data platform that ingests daily store and sales files, validates and processes the data, and produces business-ready reporting datasets.

The solution was designed following modern Data Engineering best practices and demonstrates:

- Batch data ingestion
- Data quality validation
- End-to-end orchestration
- Data lineage and auditability
- Idempotent processing
- Medallion Architecture (Bronze → Silver → Gold)
- Reporting-ready datasets

---

## Technology Stack

| Layer | Technology |
|---------|---------|
| Orchestration | Apache Airflow |
| Data Warehouse | Snowflake |
| Transformations | dbt |
| Programming Language | Python |
| Storage | Local Filesystem (simulating object storage) |
| Architecture Pattern | Medallion Architecture |

---

# Quick Start

## 1. Clone Repository

```bash
git clone <repository_url>
cd sales_etl_platform
```

---

## 2. Create Configuration Files

Configuration files containing credentials are intentionally excluded from source control.

### Application Configuration

```bash
cp config/config.example.yaml config/config.yaml
```

Update the generated file with your Snowflake connection details.

### dbt Profile

```bash
cp dbt/profiles.example.yml dbt/profiles.yml
```

Update the generated profile with your Snowflake credentials.

---

## 3. Start Airflow Environment

```bash
docker compose up -d
```

Verify Airflow is running:

```text
http://localhost:8080
```

---

## 4. Generate Sample Data

```bash
python scripts/generate_fake_data.py
```

This generates sample files in the inbox folder:

```text
inbox/
├── stores_YYYYMMDD.csv
└── sales_YYYYMMDD.csv
```

---

## 5. Trigger the Pipeline

Open Airflow:

```text
http://localhost:8080
```

Trigger DAG:

```text
sales_daily_etl
```

---

## 6. Run dbt Manually (Optional)

```bash
dbt run
dbt test
```

---

# Project Structure

```text
sales_etl_platform
├── archive/                        # Archived processed files
├── config/
│   ├── config.example.yaml
│   └── config.yaml                 # Local only (gitignored)
├── dags/
│   └── sales_daily_etl.py
├── dbt/
│   ├── models/
│   │   ├── silver/
│   │   └── gold/
│   ├── tests/
│   ├── logs/
│   ├── target/
│   ├── profiles.example.yml
│   ├── profiles.yml                # Local only (gitignored)
│   └── dbt_project.yml
├── docs/
│   ├── architecture.md
│   ├── assumptions.md
│   └── questions_for_product.md
├── inbox/                          # Incoming source files
├── output/
├── scripts/
│   ├── ingest.py
│   └── generate_fake_data.py
├── docker-compose.yml
└── README.md
```

---

# Architecture Overview

```text
                   +----------------+
                   | Partner System |
                   +----------------+
                           |
                           v
                 stores_*.csv
                 sales_*.csv
                           |
                           v
                   +---------------+
                   | Inbox Folder  |
                   +---------------+
                           |
                           v
                 +------------------+
                 | Airflow DAG      |
                 | ingest_raw_files |
                 +------------------+
                           |
         +-----------------+------------------+
         |                                    |
         v                                    v
+----------------+                 +----------------+
| Snowflake      |                 | Archive        |
| Internal Stage |                 | Historical CSV |
+----------------+                 +----------------+
         |
         v
+----------------+
| Bronze (RAW)   |
| SALES          |
| STORES         |
| FILE_AUDIT     |
+----------------+
         |
         v
+----------------+
| Silver         |
| Validation     |
| Deduplication  |
+----------------+
         |
         v
+----------------+
| Gold           |
| Reporting      |
+----------------+
         |
         +-------------------------------+
         |               |               |
         v               v               v
   Report 1         Report 2       Report 3
```

---

# Medallion Architecture

## Bronze Layer (RAW)

Stores source data exactly as received from the partner.

### Tables

- RAW.STORES
- RAW.SALES
- RAW.FILE_AUDIT

### Responsibilities

- Preserve source data
- Maintain lineage
- Enable historical auditing
- Support reprocessing

---

## Silver Layer

Stores validated and business-ready entities.

### Tables

- SILVER_STORES
- SILVER_SALES

### Responsibilities

- Type casting
- Data standardization
- Validation
- Deduplication
- Business rule enforcement

---

## Gold Layer

Stores reporting-ready datasets.

### Tables

- REPORT_1_TRANSACTIONS_PROCESSED
- REPORT_2_SALES_BY_TRANSACTION_DATE
- REPORT_3_TOP_5_STORES

### Responsibilities

- Aggregation
- KPI generation
- Reporting consumption
- Executive dashboards

---

# Data Flow

## Step 1 – File Arrival

Daily files are received from an external partner.

Examples:

```text
stores_20260604.csv
sales_20260604.csv
```

Files are placed into:

```text
inbox/
```

---

## Step 2 – Ingestion

Airflow orchestrates ingestion using Python.

The ingestion process:

- Validates file naming conventions
- Uploads files to Snowflake internal stage
- Executes COPY INTO commands
- Registers metadata in audit tables
- Archives successfully processed files

---

## Step 3 – Transformations

dbt transforms raw data through:

```text
RAW → SILVER → GOLD
```

Transformation responsibilities:

- Validation
- Deduplication
- Aggregation
- Business reporting

---

## Step 4 – Reporting

Business-ready datasets are produced for analytics consumption.

---

# Data Quality Controls

The platform enforces quality controls at multiple layers.

## Ingestion Layer

Controls include:

- File naming validation
- Batch date extraction
- Audit tracking
- Archive management
- Load timestamp tracking

---

## Transformation Layer

dbt tests validate:

### Generic Tests

- `not_null`
- `unique`
- `relationships`

### Custom Business Tests

- Valid store token validation
- Duplicate transaction detection
- Referential integrity validation

Failed tests prevent promotion to downstream layers.

---

# Idempotency Strategy

The platform is designed to safely support reprocessing.

## Snowflake COPY INTO

```sql
COPY INTO target_table
FROM @stage
FORCE = FALSE;
```

This prevents duplicate file ingestion from Snowflake stages.

---

## Business-Level Deduplication

Duplicate transaction detection is performed using:

```text
(store_token, transaction_id)
```

Latest record wins:

```sql
ROW_NUMBER() OVER (
    PARTITION BY store_token, transaction_id
    ORDER BY load_timestamp DESC
)
```

---

# Auditability

The platform tracks all ingestion activity.

Audit information includes:

- Source file name
- Batch date
- Load timestamp
- Row counts
- Processing status

Stored in:

```text
RAW.FILE_AUDIT
```

This supports:

- Operational monitoring
- Historical traceability
- Reprocessing workflows

---

# File Archival

After successful processing, files are archived.

Before:

```text
inbox/
├── stores_20260604.csv
└── sales_20260604.csv
```

After:

```text
archive/
├── stores/
│   └── 20260604/
│       └── stores_20260604.csv
│
└── sales/
    └── 20260604/
        └── sales_20260604.csv
```

Benefits:

- Historical retention
- Reprocessing capability
- Audit compliance
- Operational traceability

---

# Key Engineering Decisions

## Why Snowflake?

- Native support for batch ingestion
- Internal stages and COPY INTO
- Separation of storage and compute
- Scalable architecture

---

## Why dbt?

- SQL-first transformations
- Built-in testing framework
- Lineage visibility
- Reproducible data pipelines

---

## Why Airflow?

- Industry-standard orchestration
- Scheduling and dependency management
- Observability and monitoring
- Extensible workflow design

---

## Why Medallion Architecture?

- Clear separation of responsibilities
- Improved maintainability
- Better data quality controls
- Simplified troubleshooting

---

# Business Deliverables

## Report 1 – Transactions Processed by Batch Date

Provides:

- Number of transactions processed
- Batch monitoring metrics
- Operational KPI visibility

---

## Report 2 – Sales by Transaction Date

Provides:

- Daily revenue trends
- Transaction performance
- Historical sales analysis

---

## Report 3 – Top 5 Stores by Sales

Provides:

- Store ranking by revenue
- Performance benchmarking
- Executive reporting metrics

---

# Security

The following files are intentionally excluded from version control:

```text
config/config.yaml
dbt/profiles.yml
archive/
inbox/
dbt/logs/
dbt/target/
```

This prevents:

- Credential exposure
- Runtime artifact commits
- Local environment leakage

---

# Additional Documentation

Additional design documentation is available in:

```text
docs/
├── architecture.md
├── assumptions.md
└── questions_for_product.md
```

These documents provide:

- Architectural decisions
- Assumptions made during implementation
- Product and business clarification questions

---

# Future Improvements

Potential enhancements include:

- Object storage integration (S3, Azure Blob, GCS)
- CI/CD pipeline for dbt deployments
- Infrastructure as Code (Terraform)
- Data observability tooling
- Automated schema evolution
- Incremental processing patterns
- Dashboard integration (Power BI, Tableau, Looker)

---

# Disclaimer

This project was developed as a technical assessment and portfolio demonstration.

All data used in this repository is synthetic and generated for demonstration purposes only. No real customer, employee, or business data is included.

# Author

Yamir Palacios

Staff Data Engineer | Data Architect

Technical Assessment Submission