
  
    

create or replace transient table SALES_DB.SILVER.silver_stores
    
    
    
    as (with source as (

    select *
    from SALES_DB.RAW.stores

),

deduped as (

    select *
    from source
    qualify row_number() over (
        partition by store_token
        order by load_timestamp desc
    ) = 1

)

select *
from deduped
    )
;


  