# Architecture Design

## Objective

Build a reliable daily batch processing platform capable of:

- Ingesting daily files
- Preserving historical information
- Validating incoming data
- Deduplicating transactions
- Producing business reports

---

## End-to-End Flow

```text
Partner
   |
   v
Inbox Folder
   |
   v
Airflow Ingestion
   |
   +--> Snowflake Stage
   |
   +--> RAW Tables
   |
   +--> FILE_AUDIT
   |
   +--> Archive
   |
   v
DBT Silver
   |
   +--> Validation
   +--> Type Casting
   +--> Deduplication
   |
   v
DBT Gold
   |
   +--> Report 1
   +--> Report 2
   +--> Report 3
```

---

## Ingestion Layer

Responsibilities:

- Discover files
- Upload to Snowflake Stage
- Load raw tables
- Register audit metadata
- Archive processed files

Technology:

- Python
- Snowflake Connector
- Airflow

---

## Bronze Layer

Purpose:

Store source information exactly as received.

Tables:

- RAW.STORES
- RAW.SALES
- RAW.FILE_AUDIT

Characteristics:

- Minimal transformations
- Full lineage
- Reprocessing support

---

## Silver Layer

Purpose:

Create trusted business entities.

Transformations:

- Data type conversions
- Validation
- Duplicate removal

Models:

- silver_stores
- silver_sales

---

## Gold Layer

Purpose:

Provide reporting-ready datasets.

Models:

- report_1_transactions_processed
- report_2_sales_by_transaction_date
- report_3_top_5_stores

---

## Data Lineage

```text
RAW.STORES
        \
         \
          > silver_stores
                         \
                          \
                           > report_3_top_5_stores

RAW.SALES
        \
         \
          > silver_sales
                  |
                  +--> report_1_transactions_processed
                  |
                  +--> report_2_sales_by_transaction_date
                  |
                  +--> report_3_top_5_stores
```

---

## Key Design Decisions

### Audit Table

Purpose:

- Operational visibility
- Monitoring
- Troubleshooting

---

### Archive Strategy

Purpose:

- Historical retention
- Replay capability
- Compliance with requirements

---

### Idempotent Processing

Prevent duplicate ingestion:

```sql
FORCE = FALSE
```

Prevent duplicate business records:

```sql
ROW_NUMBER()
```