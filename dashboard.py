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

# Load data
df = pd.read_pickle(f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl')
"""Index(['PowerGeneratedPV', 'PowerOutputPV', 'GridPowerIn', 'GridPowerOut',
       'p_delta_12000Wh_eigenverbrauch', 'current_soc_12000Wh_eigenverbrauch',
       'soc_delta_12000Wh_eigenverbrauch',
       'p_netzbezug_12000Wh_eigenverbrauch',
       'p_netzeinspeisung_12000Wh_eigenverbrauch',
       'p_netzleistung_12000Wh_eigenverbrauch', 'p_delta_12000Wh_netzdienlich',
       'current_soc_12000Wh_netzdienlich', 'soc_delta_12000Wh_netzdienlich',
       'p_netzbezug_12000Wh_netzdienlich',
       'p_netzeinspeisung_12000Wh_netzdienlich',
       'p_netzleistung_12000Wh_netzdienlich'],
      dtype='object')
print(df.columns)
exit()# """

"""df_optidx_list = pd.read_pickle(f'documents/liste_von_optidx_netzdienlich.pkl')
print(df_optidx_list)
df_optidx_list.to_csv(f'documents/liste_von_optidx_netzdienlich.csv')
exit()"""
# Initialize the app
app = Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1(children='Speichersimulation Optimiert Netzdienlich'),

    # Table of data
    html.H2(children='Messwerte im Quartier und simulierte Werte gruppiert nach Speichergrößen'),
    dash_table.DataTable(data=df.to_dict('records'),
                         page_size=20), # style_table={'overflowY': 'scroll', 'maxHeight': '500px'},

    # Sum of each column
    html.H2(children='Sum of Each Column'),
    html.Div(children=[
        html.Div(children=[html.H3(column), html.H4((df[column].sum()/60))])
        for column in df.columns
    ]),

    """html.H2(children='Power as a Function of Time (Leistungsverlauf)'),
    dcc.Graph(
        id='power-vs-time',
        figure={
            'data': [
                #go.Scatter(x=df.index, y=df['GridPowerIn'], name='ohne Speicher', mode='markers'),
                #go.Scatter(x=df.index, y=df['GridPowerOut'], name='ohne Speicher', mode='markers'),
                go.Scatter(x=df.index, y=df['p_netzleistung_12000Wh_eigenverbrauch'], name='Eigenverbrauch',
                           mode='markers'),
                go.Scatter(x=df.index, y=df['p_netzleistung_12000Wh_netzdienlich'], name='Netzdienlich', mode='markers')
            ],
            'layout': go.Layout(title='Power as a Function of Time', xaxis_title='Time', yaxis_title='Power (Wmin)')
        }
    )""",

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
    # Histogram of storage sizes (Eigenverbrauch)
    html.H2(children='Histogram of Storage Sizes (Eigenverbrauch)'),
    dcc.Graph(
        id='storage-size-eigenverbrauch',
        figure=px.histogram(df,
                            x=['p_netzbezug_12000Wh_eigenverbrauch',
                               'p_netzeinspeisung_12000Wh_eigenverbrauch',
                               'p_netzleistung_12000Wh_eigenverbrauch'],
                            nbins=150
                            )
    ),

    # Histogram of storage sizes (Netzdienlich)
    html.H2(children='Histogram of Storage Sizes (Netzdienlich)'),
    dcc.Graph(
        id='storage-size-netzdienlich',
        figure=px.histogram(df,
                            x=['p_netzbezug_12000Wh_netzdienlich',
                               'p_netzeinspeisung_12000Wh_netzdienlich',
                               'p_netzleistung_12000Wh_netzdienlich'],
                            nbins=150
                            )
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
