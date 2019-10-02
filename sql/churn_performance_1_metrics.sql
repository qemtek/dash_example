with cte as
    (
    select
        t1.customer_id,
        t1.yr, t1.wk,
        (t1.yr::varchar(4) || lpad(t1.wk::varchar(2), 2, '0'))::int period,
        t1.country_code,
        churn_prediction,
        will_1_churn as churn_actual,
        churn_probability,
        churn_segment
    from
        data_science.customer_churn_users t1
    left join
        data_science.customer_churn_predictions t2
    on t1.id = t2.id
    left join
        data_science.customer_churn_labels t3
    on t1.id = t3.id
    left join
        data_science.customer_features_stock t4
    on t1.id = t4.id
    where included = 1
    and churn_prediction is not NULL
    --and will_1_churn is not NULL
    and t4.is_active = 1
    -- For testing, just return the rows for latest period to save time
    and
        period::int > {latest_period}::int
    )
Select
    base.country_code, base.yr, base.wk, base.period,
    sum(1) total_predictions,
    sum(case when churn_actual = 1 and churn_prediction = 1 then 1 end) true_positives,
    sum(case when churn_actual = 0 and churn_prediction = 0 then 1 end) true_negatives,
    sum(case when churn_actual = 0 and churn_prediction = 1 then 1 end) false_positives,
    sum(case when churn_actual = 1 and churn_prediction = 0 then 1 end) false_negatives,
    round(sum(case when churn_prediction = churn_actual then 1 end)::float/
    nullif(total_predictions, 0), 4) accuracy,
    avg(churn_actual::float) churn_rate,
    round(true_positives::float/nullif(total_predictions, 0), 4) true_positive_rate,
    round(true_negatives::float/nullif(total_predictions, 0), 4) true_negative_rate,
    round(false_positives::float/nullif(total_predictions, 0), 4) false_positive_rate,
    round(false_negatives::float/nullif(total_predictions, 0), 4) false_negative_rate,
    round(true_positives::float/nullif((true_positives+false_positives), 0) , 4) as precision,
    round(true_positives::float/nullif((true_positives+false_negatives), 0) , 4) as recall,
    round((2*precision*recall)/nullif((precision+recall), 0), 4) f2_score
from
    (
    select
       distinct yr, wk, period, cc.country_code
    from
        (select distinct yr, wk, period from cte) t1
    cross join
        (select distinct country_code from data_science.customer_churn_definition) cc
    ) base
left join
    cte t1
on base.period = t1.period
and base.country_code = t1.country_code
group by 1,2,3,4;

