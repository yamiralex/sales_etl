# Sales ETL Platform

## Overview

This project implements a batch-oriented data platform that ingests daily store and sales files, validates and processes the data, and produces business-ready reporting datasets.

The solution was designed following modern Data Engineering principles:

- Apache Airflow for orchestration
- Snowflake as Data Warehouse
- dbt for transformations and data quality
- Python for ingestion
- Medallion Architecture (Bronze → Silver → Gold)
- Auditability and lineage
- Idempotent processing

---

## Technology Stack

| Layer | Technology |
|---------|---------|
| Orchestration | Apache Airflow |
| Data Warehouse | Snowflake |
| Transformations | dbt |
| Language | Python |
| Storage | Local Filesystem (simulating object storage) |
| Architecture Pattern | Medallion Architecture |

---

## Project Structure

sales_etl_platform/

├── archive/

├── config/

│ └── config.yaml

├── dags/

│ └── sales_daily_etl.py

├── dbt/

│ ├── models/

│ │ ├── silver/

│ │ └── gold/

│ ├── tests/

│ ├── dbt_project.yml

│ └── profiles.yml

├── docs/

│ ├── architecture.md

│ ├── assumptions.md

│ └── questions_for_product.md

├── inbox/

├── output/

├── scripts/

│ ├── ingest.py

│ └── generate_fake_data.py

├── docker-compose.yml

└── README.md

---

## Architecture Overview

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

## Medallion Architecture

### Bronze Layer (RAW)

Stores source data exactly as received from the partner.

Tables:

- RAW.STORES
- RAW.SALES
- RAW.FILE_AUDIT

Responsibilities:

- Preserve source data
- Maintain lineage
- Support reprocessing

---

### Silver Layer

Stores validated and deduplicated business entities.

Tables:

- silver_stores
- silver_sales

Responsibilities:

- Type casting
- Validation
- Deduplication
- Business rule enforcement

---

### Gold Layer

Stores reporting-ready datasets.

Tables:

- report_1_transactions_processed
- report_2_sales_by_transaction_date
- report_3_top_5_stores

Responsibilities:

- Aggregation
- KPI generation
- Business consumption

---

## Data Quality

The project includes automated dbt tests:

### Generic Tests

- not_null
- unique

### Custom Tests

- valid_store_token
- unique_transaction

---

## Idempotency Strategy

Duplicate loads are prevented through:

### Snowflake COPY INTO

```sql
COPY INTO ...
FORCE = FALSE
```

### Business-Level Deduplication

Duplicate transaction detection:

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

## File Archival

After successful processing:

Inbox:

```text
stores_20260604.csv
sales_20260604.csv
```

becomes:

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

This guarantees:

- Historical retention
- Reprocessing capability
- Compliance with assessment requirements

---

## Running the Platform

### Generate Test Data

```bash
python scripts/generate_fake_data.py
```

### Trigger Airflow Pipeline

```bash
Open Airflow UI

http://localhost:8080

Trigger DAG:

sales_daily_etl
```

### Execute dbt

```bash
dbt run

dbt test
```

---

## Deliverables

### Output 1

Transactions Processed by Batch Date

### Output 2

Sales by Transaction Date

### Output 3

Top 5 Sales Storess