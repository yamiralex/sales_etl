select
    s.store_token
from {{ ref('silver_sales') }} s
left join {{ ref('silver_stores') }} st
    on s.store_token = st.store_token
where st.store_token is null