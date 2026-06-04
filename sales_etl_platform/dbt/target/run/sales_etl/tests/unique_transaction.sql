
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  select
    store_token,
    transaction_id,
    count(*)
from SALES_DB.SILVER.silver_sales
group by
    store_token,
    transaction_id
having count(*) > 1
  
  
      
    ) dbt_internal_test