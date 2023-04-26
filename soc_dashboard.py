# Import packages
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, html, dcc

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

# Datetime-Spalte formatieren
df['timestamp'] = pd.to_datetime(df.index)

# Initialize the app
app = Dash(__name__)

# Layout definieren
app.layout = html.Div(children=[
    html.H1(children='Verlauf des SoC des Speichers nach Netzdienlichkeit und Eigenverbrauch'),

    # Plot für Netzdienlichkeit
    dcc.Graph(
        id='soc-netzdienlichkeit',
        figure={
            'data': [
                go.Scatter(
                    x=df['timestamp'],
                    y=df['current_soc_12000Wh_netzdienlich'],
                    mode='markers', # 'lines',
                    name='Netzdienlich'
                )
            ],
            'layout': go.Layout(
                xaxis={'title': 'Zeit'},
                yaxis={'title': 'SoC'},
                title='Netzdienlich'
            )
        }
    ),

    # Plot für Eigenverbrauch
    dcc.Graph(
        id='soc-eigenverbrauch',
        figure={
            'data': [
                go.Scatter(
                    x=df['timestamp'],
                    y=df['current_soc_12000Wh_eigenverbrauch'],
                    mode='markers', #'lines',
                    name='Eigenverbrauch'
                )
            ],
            'layout': go.Layout(
                xaxis={'title': 'Zeit'},
                yaxis={'title': 'SoC'},
                title='Eigenverbrauch'
            )
        }
    ),
    # Violin-Plot
    html.Div(
        dcc.Graph(
            id='violin-plot',
            figure={
                'data': [
                    go.Violin(
                        y=df['current_soc_12000Wh_netzdienlich'],
                        name='Netzdienlich',
                        side='positive',
                        box_visible=True,
                        meanline_visible=True,
                        jitter=0.05,
                        points='all',
                        scalemode='count'
                    ),
                    go.Violin(
                        y=df['current_soc_12000Wh_eigenverbrauch'],
                        name='Eigenverbrauch',
                        side='negative',
                        box_visible=True,
                        meanline_visible=True,
                        jitter=0.05,
                        points='all',
                        scalemode='count'
                    )
                ],
                'layout': go.Layout(
                    title='Verteilung des SoC des Speichers nach Netzdienlichkeit und Eigenverbrauch',
                    xaxis={'title': 'Kategorie'},
                    yaxis={'title': 'SoC'},
                    violinmode='overlay'
                )
            }
        )
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)