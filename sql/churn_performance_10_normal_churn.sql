Select
    country_code,
    period,
    churn_rate,
    period_rank
from
    (
    select
        t0.country_code,
        t1.period,
        t2.churn_rate,
        row_number() over(partition by t0.country_code order by t1.period desc) period_rank
    from
        (select distinct country_code
            from data_science.customer_churn_definition) t0
    cross join
        (select distinct (yr::varchar(4) || lpad(wk::varchar(2), 2, '0'))::int period
            from data_science.customer_churn_users
            where
                (period >= 201913 and period > {latest_period}::int)
        ) t1
    left join
        (
        Select
            t1.country_code,
            t1.yr::varchar(4) || lpad(t1.wk::varchar(2), 2, '0') period,
            round(avg(will_1_churn::float), 4) churn_rate
        from
             data_science.customer_churn_users t1
        left join
            data_science.customer_churn_labels t2
        on
            t1.id = t2.id
        left join
            data_science.customer_churn_predictions t3
            -- ToDo: Add stock features and filter for active
        on
            t1.id = t3.id
        where
            t2.will_1_churn is not NULL
        and
            t3.churn_prediction is not NULL
        and
            included = 1
        and
            ((t1.yr::varchar(4)||lpad(t1.wk, 2, '0')::varchar(2))::int >= 201913
        and
            (t1.yr::varchar(4)||lpad(t1.wk, 2, '0')::varchar(2))::int > {latest_period}::int)
        group by 1, 2
        ) t2
    on
        t2.period = t1.period
    and
        t2.country_code = t0.country_code

    ) t1
where period_rank <= 20