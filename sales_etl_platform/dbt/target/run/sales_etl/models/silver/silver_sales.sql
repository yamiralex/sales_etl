
  
    

create or replace transient table SALES_DB.SILVER.silver_sales
    
    
    
    as (with source as (

    select *
    from SALES_DB.RAW.sales

),

typed as (

    select
        store_token,
        transaction_id,
        receipt_token,
        try_to_timestamp(
            transaction_time,
            'YYYYMMDD"T"HH24MISS.FF3'
        ) as transaction_timestamp,
        try_to_number(amount,11,2) as amount,
        user_role,
        batch_date,
        source_file,
        load_timestamp
    from source

),

validated as (

    select
        *,
        case
            when amount is null then false
            when transaction_timestamp is null then false
            when store_token is null then false
            when transaction_id is null then false
            else true
        end as is_valid_record
    from typed

),

deduped as (

    select *
    from validated
    qualify row_number() over (
        partition by
            store_token,
            transaction_id
        order by
            load_timestamp desc
    ) = 1
)

select *
from deduped
    )
;


  