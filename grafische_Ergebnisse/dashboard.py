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
# Leistungswerte von Wmin in Wh umrechnen
# SOC um Faktor 10 multiplizieren vom Bereich 0-1 auf 0-100 zukommen für die bessere Ansicht
df['Index'] =df.index
# df['Messdaten_Quatier'] = []
df['PowerGeneratedPV[Wh]'] = -df['PowerGeneratedPV'] / 60
df['PowerOutputPV[Wh]'] = df['PowerOutputPV'] / 60
df['GridPowerIn[Wh]'] = df['GridPowerIn'] / 60
df['GridPowerOut[Wh]'] = -df['GridPowerOut'] / 60
#df[f'Speichersimulation_{speichergroesse}Wh_eigenverbrauch'] =[]
df['p_delta_12000Wh_eigenverbrauch[Wh]'] = df['p_delta_12000Wh_eigenverbrauch'] / 60
df['p_netzbezug_12000Wh_eigenverbrauch[Wh]'] = df['p_netzbezug_12000Wh_eigenverbrauch'] / 60
df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'] = -df['p_netzeinspeisung_12000Wh_eigenverbrauch'] / 60
df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'] = df['p_netzleistung_12000Wh_eigenverbrauch'] / 60
df['current_soc_12000Wh_eigenverbrauch'] = df['current_soc_12000Wh_eigenverbrauch'] * 100
#df[f'Speichersimulation_{speichergroesse}Wh_netzdienlich'] =[]
df['p_delta_12000Wh_netzdienlich[Wh]'] = df['p_delta_12000Wh_netzdienlich'] / 60
df['p_netzbezug_12000Wh_netzdienlich[Wh]'] = df['p_netzbezug_12000Wh_netzdienlich'] / 60
df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]'] = -df['p_netzeinspeisung_12000Wh_netzdienlich'] / 60
df['p_netzleistung_12000Wh_netzdienlich[Wh]'] = df['p_netzleistung_12000Wh_netzdienlich'] / 60
df['current_soc_12000Wh_netzdienlich'] = df['current_soc_12000Wh_netzdienlich'] * 100

# Multiplikation mit 100 und Glättung
smoothed_eigenverbrauch = df['current_soc_12000Wh_eigenverbrauch'].rolling(30).mean()
smoothed_netzdienlich = df['current_soc_12000Wh_netzdienlich'].rolling(30).mean()

"""df_optidx_list = pd.read_pickle(f'documents/liste_von_optidx_netzdienlich.pkl')
print(df_optidx_list)
df_optidx_list.to_csv(f'documents/liste_von_optidx_netzdienlich.csv')
exit()"""

# table of the hole simulation

# Round all numbers in the dataframe to 4 decimal places
df = df.round(4)
#rows of intresst
columnslist = [
            "Index",
            "PowerGeneratedPV[Wh]",
            "PowerOutputPV[Wh]",
            "GridPowerIn[Wh]",
            "GridPowerOut[Wh]",
            "p_delta_12000Wh_eigenverbrauch[Wh]",
            "p_netzbezug_12000Wh_eigenverbrauch[Wh]",
            "p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]",
            "p_netzleistung_12000Wh_eigenverbrauch[Wh]",
            "current_soc_12000Wh_eigenverbrauch",
            "p_delta_12000Wh_netzdienlich[Wh]",
            "p_netzbezug_12000Wh_netzdienlich[Wh]",
            "p_netzeinspeisung_12000Wh_netzdienlich[Wh]",
            "p_netzleistung_12000Wh_netzdienlich[Wh]",
            "current_soc_12000Wh_netzdienlich"
           ]
# Create table trace
table_trace = go.Table(
    header=dict(values=list(columnslist),
                fill_color='lightblue',
                align='center'),
    cells=dict(values=[df[col] for col in columnslist],
               fill_color='white',
               align='center'))

# Customize the layout of the table
layout = go.Layout(
    width=3000, # Set the width of the table to fit the screen
    height=600, # Set the height of the table to allow for scrolling
    margin=dict(l=20, r=20, t=20, b=20), # Add margins to the table
    xaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=True, zeroline=True, showticklabels=False),
    plot_bgcolor='gray',
    hovermode='y', #  "closest", "x", "y", "none"
)

# Create figure
fig = go.Figure(data=[table_trace], layout=layout)

"""fig1 = go.Figure({
    'data': [
        go.Scatter(x=df.index, y=df['GridPowerIn[Wh]'], name='ohne Speicher', mode='markers'),
        go.Violin(x=df.index, y=df['GridPowerIn[Wh]'], name='ohne Speicher', yaxis='y2'),
        go.Scatter(x=df.index, y=df['GridPowerOut[Wh]'], name='ohne Speicher', mode='markers'),
        go.Violin(x=df.index, y=df['GridPowerOut[Wh]'], name='ohne Speicher', yaxis='y2'),
        go.Scatter(x=df.index, y=df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'], name='Eigenverbrauch', mode='markers'),
        go.Violin(x=df.index, y=df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'], name='Eigenverbrauch', yaxis='y2'),
        go.Scatter(x=df.index, y=df['p_netzleistung_12000Wh_netzdienlich[Wh]'], name='Netzdienlich', mode='markers'),
        go.Violin(x=df.index, y=df['p_netzleistung_12000Wh_netzdienlich[Wh]'], name='Netzdienlich', yaxis='y2')
    ],
    'layout': go.Layout(
        title='Power as a Function of Time',
        xaxis={'title': 'Time'},
        yaxis={'title': 'Power (Wh)'},
        yaxis2={'title': 'Power (Wh)', 'overlaying': 'y', 'side': 'right'}
    )
})"""
# Show figure
fig.show()

# exit()

# Initialize the app
app = Dash(__name__)

# Define app layout
app.layout = html.Div([
    html.H1(children='Speichersimulation Optimiert Netzdienlich'),

    # Table of data
    html.H2(children='Messwerte im Quartier und simulierte Werte gruppiert nach Speichergrößen'),
    dash_table.DataTable(data=df.to_dict('records'),
                         page_size=20), # style_table={'overflowY': 'scroll', 'maxHeight': '500px'},

    html.H2(children='Power as a Function of Time (Leistungsverlauf)'),
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
    ),
    html.H3(children='Differenz zwischen Eigenverbrauch')
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
