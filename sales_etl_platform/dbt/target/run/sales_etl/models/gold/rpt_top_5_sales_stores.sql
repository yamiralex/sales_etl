
  
    

create or replace transient table SALES_DB.GOLD.rpt_top_5_sales_stores
    
    
    
    as (with sales as (

    select *
    from SALES_DB.SILVER.silver_sales

),

stores as (

    select *
    from SALES_DB.SILVER.silver_stores

),

daily_sales as (

    select
        cast(
            transaction_timestamp as date
        ) as transaction_date,
        store_token,
        sum(amount) as total_sales
    from sales
    group by 1,2

),

ranked as (

    select
        *,
        dense_rank() over (
            partition by transaction_date
            order by total_sales desc
        ) as rank_id

    from daily_sales

)

select
    current_date() as snapshot_date,
    r.transaction_date,
    r.rank_id,
    r.total_sales,
    r.store_token,
    s.store_name
from ranked r
join stores s
    on r.store_token = s.store_token
where rank_id <= 5
qualify row_number() over (
    order by transaction_date desc
) <= 50
    )
;


  