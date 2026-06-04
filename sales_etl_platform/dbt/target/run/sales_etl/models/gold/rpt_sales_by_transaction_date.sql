
  
    

create or replace transient table SALES_DB.GOLD.rpt_sales_by_transaction_date
    
    
    
    as (with sales as (

    select *
    from SALES_DB.SILVER.silver_sales

),

daily as (

    select
        current_date() as snapshot_date,
        cast(transaction_timestamp as date)
            as transaction_date,
        count(distinct store_token)
            as stores_with_transactions,
        sum(amount)
            as total_sales_amount,
        avg(amount)
            as total_sales_average
    from sales
    group by 2

),

monthly as (

    select
        *,
        sum(total_sales_amount) over (
            partition by
                date_trunc(
                    month,
                    transaction_date
                )
            order by transaction_date
        ) as monthly_accumulated_sales
    from daily
    
)

select *
from monthly
qualify row_number() over (
    order by transaction_date desc
) <= 40
    )
;


  