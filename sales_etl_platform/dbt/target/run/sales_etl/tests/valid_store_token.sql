
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  select
    s.store_token
from SALES_DB.SILVER.silver_sales s
left join SALES_DB.SILVER.silver_stores st
    on s.store_token = st.store_token
where st.store_token is null
  
  
      
    ) dbt_internal_test