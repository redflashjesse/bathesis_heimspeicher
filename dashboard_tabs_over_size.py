import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table
import pandas as pd
import main
from pprint import pprint
import plotly.graph_objs as go
import plotly.express as px


speichergroessen = main.speichergroessen
#                   list(range(6_000, # start
#                               30_000, # end
#                               2_000)) # step # in Wh

# size = speichergroessen[10]
schwellenwert = 500

base_color = 'info'
eigen_color = 'primary'
netz_color = 'secondary'

# Load data
df = pd.read_pickle(
    f'./documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl')


def factorize_df(df):
    
    # Leistungswerte von Wmin in Wh umrechnen
    df['Index'] = df.index
    factor = 1  # or 60
    df['PowerGeneratedPV[Wh]'] = -df['PowerGeneratedPV'] / factor
    df['PowerOutputPV[Wh]'] = df['PowerOutputPV'] / factor
    df['GridPowerIn[Wh]'] = df['GridPowerIn'] / factor
    df['GridPowerOut[Wh]'] = -df['GridPowerOut'] / factor

    for size in speichergroessen:
        # Leistungswerte von Wmin in Wh umrechnen (abhängig von der Speicherkapazität)
        df[f'p_delta_{size}Wh_eigenverbrauch[Wh]'] = df[f'p_delta_{size}Wh_eigenverbrauch'] / factor
        df[f'p_netzbezug_{size}Wh_eigenverbrauch[Wh]'] = \
            df[f'p_netzbezug_{size}Wh_eigenverbrauch'] / factor
        df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'] = \
            -df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'] / factor
        df[f'p_netzleistung_{size}Wh_eigenverbrauch[Wh]'] = \
            df[f'p_netzleistung_{size}Wh_eigenverbrauch'] / factor
        df[f'p_delta_{size}Wh_netzdienlich[Wh]'] = \
            df[f'p_delta_{size}Wh_netzdienlich'] / factor
        df[f'p_netzbezug_{size}Wh_netzdienlich[Wh]'] = \
            df[f'p_netzbezug_{size}Wh_netzdienlich'] / factor
        df[f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'] = \
            -df[f'p_netzeinspeisung_{size}Wh_netzdienlich'] / factor
        df[f'p_netzleistung_{size}Wh_netzdienlich[Wh]'] = \
            df[f'p_netzleistung_{size}Wh_netzdienlich'] / factor

        # SOC um Faktor 100 multiplizieren, um vom Bereich 0-1 auf 0-100 zukommen für die bessere Ansicht
        df[f'current_soc_{size}Wh_eigenverbrauch'] = df[f'current_soc_{size}Wh_eigenverbrauch'] * 100
        df[f'current_soc_{size}Wh_netzdienlich'] = df[f'current_soc_{size}Wh_netzdienlich'] * 100
        # Round all numbers in the dataframe to 4 decimal places
    df = df.round(4)
    # rows of intresst
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
    return df, columnslist
df, columnslist = factorize_df(df)
def tab_contents(df,speichergroessen,columnslist):
    # Create an empty list to hold the tab contents
    tabs = []
    tab_contents = []

    # Loop over the storage sizes
    for size in speichergroessen:
        # Create the tab content for the current size
        data = df
        tab_content = html.Div([
            # Table of data
            html.H2(children=f'Messwerte für {size/1000} kWh Speichergröße'),
            dash_table.DataTable(data=data.to_dict('records'), page_size=20),

            # Power vs. Time graph
            html.H2(children='Netzanschlusspunkt (Leistungsverlauf)'),
            dcc.Graph(
                id=f'power-vs-time-{size}',
                figure={
                    'data': [
                        go.Scatter(x=data.index, y=data[f'p_netzleistung_{size}Wh_eigenverbrauch[Wh]'],
                                   name='Eigenverbrauch', mode='markers'),
                        go.Scatter(x=data.index, y=data[f'p_netzleistung_{size}Wh_netzdienlich[Wh]'],
                                   name='Netzdienlich', mode='markers')
                    ],
                    'layout': go.Layout(title='Power as a Function of Time', xaxis_title='Time',
                                        yaxis_title='Power (Wmin)')
                }
            ),

            # Histogram of storage sizes (Eigenverbrauch)
            html.H2(children='Histogram (Eigenverbrauch)'),
            dcc.Graph(
                id=f'storage-size-eigenverbrauch-{size}',
                figure=px.histogram(data,
                                    x=[f'p_netzbezug_{size}Wh_eigenverbrauch[Wh]',
                                       f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]',
                                       f'p_netzleistung_{size}Wh_eigenverbrauch[Wh]'],
                                    nbins=150
                                    )
            ),

            # Histogram of storage sizes (Netzdienlich)
            html.H2(children='Histogram (Netzdienlich)'),
            dcc.Graph(
                id=f'storage-size-netzdienlich-{size}',
                figure=px.histogram(data,
                                    x=[f'p_netzbezug_{size}Wh_netzdienlich[Wh]',
                                       f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]',
                                       f'p_netzleistung_{size}Wh_netzdienlich[Wh]'],
                                    nbins=150
                                    )
            ),

            html.H3(children='Differenz zwischen Eigenverbrauch')
        ])

        ## Create a Tab object with the corresponding tab label
        tab = dcc.Tab(label=f'{size} kWh', value=f'Betrachtung für {size/1000}kWh')  # Use `{size}` for the tab label


        # Append the tabs and contents to the respective lists
        tabs.append(tab)
        tab_contents.append(tab_content)
    return tab_contents,tabs

tab_contents,tabs = tab_contents(df,speichergroessen,columnslist)
# Create the app
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div([
    html.H1(children='Vergleich der Speichergrößen und deren Auswirkung auf den Eigenverbrauch und Netzdienlichkeit'),
    html.Div([dcc.Tabs([*tab_contents],) # Use the spread operator to unpack the list of tab contents
            ],
             style={'width': '100%'}, # Use the full width of the screen
             content_style={'width': '100%', 'borderLeft': '1px solid #d6d6d6',
                            'borderRight': '1px solid #d6d6d6', 'borderBottom': '1px solid #d6d6d6'},
             parent_style={'maxWidth': '1000px', 'margin': '0 auto'} # Limit the width of the tabs container
            ),
])

# set a title for the app
app.title = 'Speichergrößenvergleich'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True),
