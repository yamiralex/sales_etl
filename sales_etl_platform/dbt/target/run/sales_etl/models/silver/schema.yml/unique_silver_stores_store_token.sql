
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    store_token as unique_field,
    count(*) as n_records

from SALES_DB.SILVER.silver_stores
where store_token is not null
group by store_token
having count(*) > 1



  
  
      
    ) dbt_internal_test