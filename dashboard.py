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
import main

speichergroessen = main.speichergroessen
# Create empty lists for tabs and their corresponding contents
tabs = []
tab_contents = []

# Load data
df = pd.read_pickle(f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl')
# Leistungswerte von Wmin in Wh umrechnen
# SOC um Faktor 10 multiplizieren vom Bereich 0-1 auf 0-100 zukommen für die bessere Ansicht
df['Index'] =df.index
# df['Messdaten_Quatier'] = []
factor = 1
df['PowerGeneratedPV[Wh]'] = -df['PowerGeneratedPV'] / factor
df['PowerOutputPV[Wh]'] = df['PowerOutputPV'] / factor
df['GridPowerIn[Wh]'] = df['GridPowerIn'] / factor
df['GridPowerOut[Wh]'] = -df['GridPowerOut'] / factor
#df[f'Speichersimulation_{speichergroesse}Wh_eigenverbrauch'] =[]
for size in speichergroessen:
    df[f'p_delta_{size}Wh_eigenverbrauch[Wh]'] = df[f'p_delta_{size}Wh_eigenverbrauch'] / factor
    df[f'p_netzbezug_{size}Wh_eigenverbrauch[Wh]'] = df[f'p_netzbezug_{size}Wh_eigenverbrauch'] / factor
    df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'] = -df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'] / factor
    df[f'p_netzleistung_{size}Wh_eigenverbrauch[Wh]'] = df[f'p_netzleistung_{size}Wh_eigenverbrauch'] / factor
    df[f'current_soc_{size}Wh_eigenverbrauch'] = df[f'current_soc_{size}Wh_eigenverbrauch'] * 100

    #df[f'Speichersimulation_{size}Wh_netzdienlich'] = []

    df[f'p_delta_{size}Wh_netzdienlich[Wh]'] = df[f'p_delta_{size}Wh_netzdienlich'] / factor
    df[f'p_netzbezug_{size}Wh_netzdienlich[Wh]'] = df[f'p_netzbezug_{size}Wh_netzdienlich'] / factor
    df[f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'] = -df[f'p_netzeinspeisung_{size}Wh_netzdienlich'] / factor
    df[f'p_netzleistung_{size}Wh_netzdienlich[Wh]'] = df[f'p_netzleistung_{size}Wh_netzdienlich'] / factor
    df[f'current_soc_{size}Wh_netzdienlich'] = df[f'current_soc_{size}Wh_netzdienlich'] * 100

    # Multiplikation mit 100 und Glättung
    smoothed_eigenverbrauch = df[f'current_soc_{size}Wh_eigenverbrauch'].rolling(30).mean()
    smoothed_netzdienlich = df[f'current_soc_{size}Wh_netzdienlich'].rolling(30).mean()

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
                f"p_delta_{size}Wh_eigenverbrauch[Wh]",
                f"p_netzbezug_{size}Wh_eigenverbrauch[Wh]",
                f"p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]",
                f"p_netzleistung_{size}Wh_eigenverbrauch[Wh]",
                f"current_soc_{size}Wh_eigenverbrauch",
                f"p_delta_{size}Wh_netzdienlich[Wh]",
                f"p_netzbezug_{size}Wh_netzdienlich[Wh]",
                f"p_netzeinspeisung_{size}Wh_netzdienlich[Wh]",
                f"p_netzleistung_{size}Wh_netzdienlich[Wh]",
                f"current_soc_{size}Wh_netzdienlich"
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
        title=f'{size}kWh',
        xaxis=dict(showgrid=True, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=True, zeroline=True, showticklabels=False),
        plot_bgcolor='gray',
        hovermode='y', #  "closest", "x", "y", "none"
    )

    # Create figure
    fig = go.Figure(data=[table_trace], layout=layout)

    # Create a Tab object with the corresponding tab label
    tab = dcc.Tab(label=f'{size} kWh', value=f'Datenbetrachtung mit {size/1000}kWh')  # Use `{size}` for the tab label

    # Add the `fig` objects to the tab contents
    tab_content = dcc.Graph(figure=fig)

    # Append the tabs and contents to the respective lists
    tabs.append(tab)
    tab_contents.append(tab_content)

    # beispiel mehrere Spalten einer spalten zu ordnen
    """app.layout = dash_table.DataTable(
        columns=[
            {"name": ["", "Year"], "id": "year"},
            {"name": ["City", "Montreal"], "id": "montreal"},
            {"name": ["City", "Toronto"], "id": "toronto"},
            {"name": ["City", "Ottawa"], "id": "ottawa"},
            {"name": ["City", "Vancouver"], "id": "vancouver"},
            {"name": ["Climate", "Temperature"], "id": "temp"},
            {"name": ["Climate", "Humidity"], "id": "humidity"},
        ],"""
    # Show figure
    #fig.show()

# exit()

# Initialize the app
app = Dash(__name__)
app.layout = html.Div([
    dcc.Tabs(id='tabs', children=tabs),
    html.Div(id='tab-content', children=tab_contents)
])
exit()
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
