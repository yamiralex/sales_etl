# Questions for Product Team

## File Headers

Can files arrive without headers?

If yes:

- How should header detection be performed?

---

## Invalid Records

Should invalid records:

- Be discarded?
- Be quarantined?
- Be reported separately?

---

## Duplicate Transactions

When duplicate transactions arrive with different values:

Should the latest version always win?

Or should reconciliation rules exist?

---

## Historical Retention

How long should archived files be retained?

Possible options:

- 90 days
- 1 year
- Indefinitely

---

## Output Delivery

How should reports be consumed?

Options:

- Snowflake tables
- CSV files
- BI dashboards
- APIs

---

## SLA Requirements

What are the expected SLAs?

Examples:

- Data available by 8 AM
- Data available within 1 hour after file arrival

---

## Data Volume Growth

Expected future scale:

- Number of stores
- Daily transactions
- Retention period

This impacts future partitioning and optimization strategies.