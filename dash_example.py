import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import logging

from data_loading_functions import get_churn_metrics, \
    get_latest_churn_rate, get_normal_churn_rate
from graphics import performance_metric_dropdown, \
    churn_rate_normal, churn_rate_latest

logging.basicConfig(level=logging.INFO)

# Create a server instance
server = Flask(__name__)
# Create an app instance
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

# ========================== Data Retrieval ============================== #

# Set download to true if you want the data to be completely refreshed
download = False
# Set debug to True to use data from a previous run instead of downloading (much faster)
debug = True
# Define the countries we want data for
selected_countries = ["ES", "IT", "AR", "PE"]
# Convert these countries into a comma separated string,
# which we can inject into a SQL query
selected_countries_string = "','".join(selected_countries)
selected_countries_string = "'" + selected_countries_string + "'"

# Get Country level data
df_metrics = get_churn_metrics(download=download, debug=debug)
# Get latest churn rate (customers moving from not churned to churned by week)
df_churn_rate = get_latest_churn_rate(download=download, debug=debug)
# Get normal churn rate (% of churned customers in any given week)
df_churn_rate2 = get_normal_churn_rate(download=download, debug=debug)

# Get a list of the countries present in the data (in case there
# is no data for some of our selected countries)
available_countries = df_metrics["country_code"].unique()


# ========================== App Layout ============================== #

# This section defines how the app looks, which we can control using dbc.Row and dbc.Col.
# Each visualisation is defined inside a column, and each column is defined inside a row.

app.layout = html.Div(
    children=[
        dbc.Row([
            dbc.Col([
                # html.H1 -> Header
                html.H1(children="Customer Churn - Model Performance Dashboard"),
                # html.Div -> Text paragraph
                html.Div(
                    "Welcome to the model performance dashboard for the Customer "
                    "Churn project. Here you can find all information relating to "
                    "the performance of the model in each country."
                ),
                # html.Br -> Empty line
                html.Br(),
                # html.H4 -> Smaller header (H1, H2, H3 and H4 are all headers)
                html.H4(children="Performance Metric Selector"),
                ])
            ]
        ),
        dbc.Row([
            dbc.Col(churn_rate_normal(df_churn_rate2, available_countries), width=6),
            dbc.Col(churn_rate_latest(df_churn_rate, available_countries), width=6)
        ]),
        dbc.Row([
            dbc.Col([performance_metric_dropdown(), html.Br(), dcc.Graph(id="scatter")], width=6)
        ]),
    ]
)


# ========================== App Callbacks ============================== #

# App callbacks are functions that modify your visualisations in response to user input.
# User input can come from buttons, dropdowns and any other interactive element you place inside
# your visualisation. You define a callback using the @app.callback handler and specifying your
# input (what the user clicks on to trigger the callback) and the output (what is modified when
# the callback is triggered.

# In the example below we are modifying the 'figure' element of a graph with the id 'scatter' in
# response to a user selecting something (value) in the dropdown menu with the id 'yaxis'

# Metric Type Dropdown
@app.callback(Output("scatter", "figure"), [Input("yaxis", "value")])
def update_graphic(yaxis):
    print(available_countries)
    return {
        "data": [
            go.Scatter(
                x=df_metrics[df_metrics["country_code"] == country].index,
                y=df_metrics[df_metrics["country_code"] == country][yaxis] * 100,
                mode="lines+markers",
                name=country,
            )
            for country in available_countries
        ],
        "layout": go.Layout(
            title="Model Performance - {}".format(yaxis.capitalize()),
            xaxis={"title": "Date", "type": "category"},
            yaxis={"title": yaxis.capitalize() + " [%]", "range": [0, 100]},
            height=500,
        ),
    }


if __name__ == "__main__":
    # Run the server, set debug to True if you want the script to
    # automatically re-run when you make changes to this file. If you edit the
    # file while it is loading it will instantly run again when it finishes so be careful!
    app.run_server(debug=False, port=8050)
