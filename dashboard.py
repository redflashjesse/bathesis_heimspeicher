# Import packages
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output

# Load data
df = pd.read_pickle('documents/speichersimulation_optimiert_netzdienlich.pkl')

# Initialize the app
app = Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1(children='Speichersimulation Optimiert Netzdienlich'),

    # Table of data
    html.H2(children='Messwerte im Quartier und simulierte Werte gruppiert nach Speichergrößen'),
    dash_table.DataTable(data=df.to_dict('records'),
                         page_size=30),

    # Sum of each column
    html.H2(children='Sum of Each Column'),
    html.Div(children=[
        html.Div(children=[html.H3(column), html.H4(df[column].sum())])
        for column in df.columns
    ]),

    # Power as a function of time (Leistungsverlauf)
    html.H2(children='Power as a Function of Time (Leistungsverlauf)'),
    dcc.Graph(
        id='power-vs-time',
        figure={
            'data': [
                go.Scatter(x=df.index, y=df['p_delta_12000Wh_eigenverbrauch'], name='Eigenverbrauch'),
                go.Scatter(x=df.index, y=df['p_delta_12000Wh_netzdienlich'], name='Netzdienlich')
            ],
            'layout': go.Layout(title='Power as a Function of Time', xaxis_title='Time', yaxis_title='Power (W)')
        }
    ),

    # Histogram of storage sizes (Eigenverbrauch)
    html.H2(children='Histogram of Storage Sizes (Eigenverbrauch)'),
    dcc.Graph(
        id='storage-size-eigenverbrauch',
        figure=px.histogram(df, x='current_soc_12000Wh_eigenverbrauch', nbins=50)
    ),

    # Histogram of storage sizes (Netzdienlich)
    html.H2(children='Histogram of Storage Sizes (Netzdienlich)'),
    dcc.Graph(
        id='storage-size-netzdienlich',
        figure=px.histogram(df, x='current_soc_12000Wh_netzdienlich', nbins=50)
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
