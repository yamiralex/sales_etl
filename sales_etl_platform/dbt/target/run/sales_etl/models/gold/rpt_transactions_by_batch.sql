
  
    

create or replace transient table SALES_DB.GOLD.rpt_transactions_by_batch
    
    
    
    as (with sales as (

    select *
    from SALES_DB.SILVER.silver_sales

),

audit as (

    select *
    from SALES_DB.RAW.file_audit
    where file_type = 'SALES'

)

select
    current_date() as snapshot_date,
    s.batch_date,
    max(a.rows_loaded) as total_processed_raw_transactions,
    count_if(s.is_valid_record) as valid_transactions,
    count_if(not s.is_valid_record) as invalid_transactions,
    max(a.load_timestamp)::date as processing_date
from sales s
left join audit a
    on s.batch_date = a.batch_date
group by
    s.batch_date
qualify row_number() over (
    order by s.batch_date desc
) <= 40
    )
;


  