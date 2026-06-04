select
    store_token,
    transaction_id,
    count(*)
from SALES_DB.SILVER.silver_sales
group by
    store_token,
    transaction_id
having count(*) > 1