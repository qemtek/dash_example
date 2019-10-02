import dash_core_components as dcc
import plotly.graph_objects as go


def performance_metric_dropdown():
    performance_metric_dropdown = dcc.Dropdown(
                    id='yaxis',
                    options=[
                        {'label': 'Accuracy', 'value': 'accuracy'},
                        {'label': 'Precision', 'value': 'precision'},
                        {'label': 'Recall', 'value': 'recall'},
                        {'label': 'F2_Score', 'value': 'f2_score'},
                    ],
                    placeholder='Accuracy',
                    value='accuracy'
                )
    return performance_metric_dropdown


def churn_rate_normal(df_churn_rate2, available_countries):
    churn_rate_normal = [dcc.Graph(  # Default shows model accuracy
                id='scatter_churn',
                figure={
                    'data': [
                        go.Scatter(
                            x=df_churn_rate2[
                                df_churn_rate2['country_code'] ==
                                country].index,
                            y=df_churn_rate2[
                                df_churn_rate2['country_code'] ==
                                country]['churn_rate'] * 100,
                            mode='lines+markers',
                            name=country
                        ) for country in available_countries
                    ],
                    'layout': go.Layout(
                        title='Churn Rate',
                        xaxis={'title': 'Date', 'type': 'category'},
                        yaxis={'title': 'Churn Rate [%]', 'range': [0, 100]},
                        height=500)
                })]
    return churn_rate_normal


def churn_rate_latest(df_churn_rate, available_countries):
    churn_rate_latest = [
                dcc.Graph(  # Default shows model accuracy
                id='scatter_churn_latest',
                figure={
                    'data': [
                        go.Scatter(
                            x=df_churn_rate[
                                df_churn_rate['country_code'] ==
                                country].index,
                            y=df_churn_rate[
                                df_churn_rate['country_code'] ==
                                country]['current_churn_rate'] * 100,
                            mode='lines+markers',
                            name=country
                        ) for country in available_countries
                    ],
                    'layout': go.Layout(
                        title='Churn Rate Weekly (New Churned by Week)',
                        xaxis={'title': 'Date', 'type': 'category'},
                        yaxis={'title': 'Churn Rate [%]', 'range': [0, 10]},
                        height=500
                    )
                })
            ]
    return churn_rate_latest


