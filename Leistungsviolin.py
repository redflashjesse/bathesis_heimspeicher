# Import packages
from dash import Dash, html, dcc
import pandas as pd
from dash import dash_table
# from plotly.subplots import make_subplots
import plotly.graph_objs as go
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
import plotly.express as px


dcc.Graph(
        id='power-vs-time',
        figure={
            'data': [
                go.Scatter(x=df.index, y=df['GridPowerIn'], name='ohne Speicher', mode='markers'),
                go.Violin(x=df.index, y=df['GridPowerIn'], name='ohne Speicher', yaxis='y2'),
                go.Scatter(x=df.index, y=df['GridPowerOut'], name='ohne Speicher', mode='markers'),
                go.Violin(x=df.index, y=df['GridPowerOut'], name='ohne Speicher', yaxis='y2'),
                go.Scatter(x=df.index, y=df['p_netzleistung_12000Wh_eigenverbrauch'], name='Eigenverbrauch', mode='markers'),
                go.Violin(x=df.index, y=df['p_netzleistung_12000Wh_eigenverbrauch'], name='Eigenverbrauch', yaxis='y2'),
                go.Scatter(x=df.index, y=df['p_netzleistung_12000Wh_netzdienlich'], name='Netzdienlich', mode='markers'),
                go.Violin(x=df.index, y=df['p_netzleistung_12000Wh_netzdienlich'], name='Netzdienlich', yaxis='y2')
            ],
            'layout': go.Layout(
                title='Power as a Function of Time',
                xaxis={'title': 'Time'},
                yaxis={'title': 'Power (Wmin)'},
                yaxis2={'title': 'Power (Wmin)', 'overlaying': 'y', 'side': 'right'}
            )
        }
    ),