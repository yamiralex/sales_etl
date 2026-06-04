
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select store_token
from SALES_DB.SILVER.silver_stores
where store_token is null



  
  
      
    ) dbt_internal_test