# Assumptions

## File Headers

Assumption:

Files contain headers.

Reason:

Specification states headers may or may not be present.

For MVP implementation, headers are assumed.

Future enhancement:

Automatic header detection.

---

## Duplicate Transactions

Business Key:

```text
store_token + transaction_id
```

Rule:

Keep latest received record.

Implementation:

```sql
ROW_NUMBER()
OVER (
    PARTITION BY store_token, transaction_id
    ORDER BY load_timestamp DESC
)
```

---

## Invalid Records

Assumption:

Invalid records are retained in Bronze.

Reason:

Preserve lineage and enable future investigation.

Silver layer flags invalid records.

---

## Empty Daily Delivery

Assumption:

Partner may deliver zero files.

Behavior:

Pipeline completes successfully.

Example:

```text
Files Processed = 0
```

---

## Late Arriving Data

Assumption:

Late arriving files are accepted.

Reports are rebuilt from historical data each execution.

---

## Store Dimension

Assumption:

Stores data is additive.

Previously received stores may appear again in future files.

Latest version is retained.