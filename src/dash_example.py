import dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import logging
import pandas as pd
import numpy as np

from src.utils import run_query

logging.basicConfig(level=logging.INFO)

# Create a server instance
server = Flask(__name__)
# Create an app instance
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

# ========================== Data Retrieval ============================== #

df = run_query("select * from team_fixtures where season = '19/20'")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Create measures of offensive and defensive strength for each team
offensive_strength = df.groupby('team_name')['goals_for'].mean()
defensive_strength = 1/df.groupby('team_name')['goals_against'].mean()
# Normalise
offensive_strength = offensive_strength/max(offensive_strength)
defensive_strength = defensive_strength/max(defensive_strength)
df1 = pd.DataFrame(data=pd.concat([offensive_strength, defensive_strength], axis=1)).reset_index()
df1.columns = ['team_name', 'offensive_strength', 'defensive_strength']

# Create a new dataset which looks at the cumulative points of a team
df2 = pd.concat([df['team_name'], df['date'], df.groupby('team_name')['points'].cumsum()], axis=1)

# ========================== Define Dropdowns ======================== #

def team_selector_dropdown(teams):
    options = []
    for team in teams:
        options.append({'label': team, 'value': team})
    team_selector_dropdown = dcc.Dropdown(
        id='team_selector',
        options=options,
        placeholder='Arsenal',  # Starting label
        value='Arsenal'  # Starting value
    )
    return team_selector_dropdown


# ========================== App Layout ============================== #

# This section defines how the app looks, which we can control using dbc.Row and dbc.Col.
# Each visualisation is defined inside a column, and each column is defined inside a row.

app.layout = html.Div(
    children=[
        dbc.Row([
            dbc.Col([
                # html.H1 -> Header
                html.H1(children="Offensive and Defensive Strength - PL 19/20 Season"),
                # html.Div -> Text paragraph
                html.Div(
                    "Included here is a comparison of the offensive and defensive "
                    "strength of teams so far in the premier league 19/20 season"
                ),
                ])
            ]
        ),
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='off_def_str',
                    figure={  # Create the plot here using one of the objects plotly.graph_objects
                        'data': [go.Scatter(
                            x=np.array(row[1]['defensive_strength']),
                            y=np.array(row[1]['offensive_strength']),
                            mode='markers',
                            name=row[1]['team_name']
                        ) for row in df1.iterrows()],
                        'layout': go.Layout(  # Define things like title and plot dimensions here
                            title='Offensive vs Defensive Strength',
                            clickmode='event+select',
                            height=600
                        )
                    })],
                width=6),
        ]),
        dbc.Row([
            dbc.Col([
                html.H1('Team Selector'),
                team_selector_dropdown(list(df1['team_name']))
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='rolling_points_total')
            ])
        ])
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
@app.callback(Output("rolling_points_total", "figure"), [Input("team_selector", "value")])
def update_graphic(team):
    df_selected = df2[df2['team_name'] == team].reset_index(drop=True)
    df_selected = df_selected.sort_values('date')
    return {
        "data": [
            go.Scatter(
                x=df_selected['date'],
                y=df_selected['points'],
                mode="lines+markers",
                name=team,
            )
        ],
        "layout": go.Layout(
            title="Rolling Points Total - {}".format(team.capitalize()),
            xaxis={"title": "Date"},
            yaxis={"title": "Cumulative Points"},
            height=500,
        ),
    }


if __name__ == "__main__":
    # Run the server, set debug to True if you want the script to
    # automatically re-run when you make changes to this file. If you edit the
    # file while it is loading it will instantly run again when it finishes so be careful!
    app.run_server(debug=False, port=8050)
