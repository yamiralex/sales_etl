
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select amount
from SALES_DB.SILVER.silver_sales
where amount is null



  
  
      
    ) dbt_internal_test