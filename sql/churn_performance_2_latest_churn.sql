Select
    yr,
    wk,
    (yr::varchar(4) || lpad(wk::varchar(2), 2, '0'))::int period,
    country_code,
    round(sum(case when churned = 1 and last_churned = 0 then 1 else 0 end)::float/
    sum(case when churned = 1 or churned = 0 then 1 else 0 end), 4) current_churn_rate
from
    (
    Select
        yr,
        wk,
        country_code,
        customer_id,
        churned,
        lag(churned, 1) over (partition by customer_id, country_code order by yr, wk) last_churned
    from
         -- For now we are taking the max of the churn label, so we can keep the view weekly rather than daily.
        (
            Select
                sto.wk,
                sto.yr,
                sto.country_code,
                sto.customer_id,
                max(case when days_since_last_order > threshold_in_days then 1 else 0 end) churned
            from
                data_science.customer_churn_users usr
            left join
                data_science.customer_features_stock sto
            on
                usr.id = sto.id
            left join
                data_science.customer_churn_definition def
            on
                sto.country_code = def.country_code
            where
                ((sto.yr::varchar(4)||lpad(sto.wk, 2, '0')::varchar(2))::int > {latest_period}::int
            and
                usr.date > dateadd('day', -date_part(dow, current_date)::int - 84, current_date))
            and
                included = 1
        group by 1,2,3,4
        ) t1
    ) t1
where
    last_churned is not NULL
group by 1, 2, 3, 4;
