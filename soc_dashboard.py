# Import packages
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, html, dcc
import plotly.express as px
import main

speichergroessen = main.speichergroessen

# list(range(6_000, # start
#                               30_000, # end
#                               2_000)) # step # in Wh
# Load data
df = pd.read_pickle(f'C:/Users/EE/Documents/Petau/bathesis_heimspeicher/documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl')
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
figs=[]
for speichergroesse in speichergroessen:
    # Leistungswerte von Wmin in Wh umrechnen
    factor = 1 # or 60
    df['PowerGeneratedPV[Wh]'] = -df['PowerGeneratedPV'] / factor
    df['PowerOutputPV[Wh]'] = df['PowerOutputPV'] / factor
    df['GridPowerIn[Wh]'] = df['GridPowerIn'] / factor
    df['GridPowerOut[Wh]'] = -df['GridPowerOut'] / factor
    df[f'p_delta_{speichergroesse}Wh_eigenverbrauch[Wh]'] = df[f'p_delta_{speichergroesse}Wh_eigenverbrauch'] / factor
    df[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch[Wh]'] = df[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch'] / factor
    df[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch[Wh]'] = -df[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'] / factor
    df[f'p_netzleistung_{speichergroesse}Wh_eigenverbrauch[Wh]'] = df[f'p_netzleistung_{speichergroesse}Wh_eigenverbrauch'] / factor
    df[f'p_delta_{speichergroesse}Wh_netzdienlich[Wh]'] = df[f'p_delta_{speichergroesse}Wh_netzdienlich'] / factor
    df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich[Wh]'] = df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] / factor
    df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich[Wh]'] = -df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] / factor
    df[f'p_netzleistung_{speichergroesse}Wh_netzdienlich[Wh]'] = df[f'p_netzleistung_{speichergroesse}Wh_netzdienlich'] / factor

    # SOC um Faktor 10 multiplizieren vom Bereich 0-1 auf 0-100 zukommen für die bessere Ansicht
    df[f'current_soc_{speichergroesse}Wh_eigenverbrauch_0-100'] = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'] * 100
    df[f'current_soc_{speichergroesse}Wh_netzdienlich_0-100'] = df[f'current_soc_{speichergroesse}Wh_netzdienlich'] * 100

    df['Index'] = df.index

    # Multiplikation mit 100 und Glättung
    eigenverbrauch_soc = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'].rolling(60).mean() * 100
    netzdienlich_soc = df[f'current_soc_{speichergroesse}Wh_netzdienlich'].rolling(60).mean() * 100

    # Scatter plot erstellen
    fig = px.line(df, x='Index', y=[eigenverbrauch_soc, netzdienlich_soc],
                     labels={'Index': 'Zeit', 'value': 'SoC', 'variable': 'Betriebsweise Speicher'}, markers=True,
                     #marginal_y='violin',
                     title=f'SOC-Verlauf zwischen Eigenverbrauch und Netzdienlichkeit mit {speichergroesse/1000}kWh')
    figs.append(dcc.Graph(id='live-graph', figure=fig))
#figs.show()
# fig2 = px.histogram(data=df, x='Index', y=(df['p_delta_12000Wh_netzdienlich[Wh]']-df['p_delta_12000Wh_eigenverrbrauch[Wh]')])
# exit()
# Initialize the app
app = Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1('Verlauf des SoC des Speichers nach Netzdienlichkeit und Eigenverbrauch'),
    dcc.Tabs([*figs,]),
])
if __name__ == '__main__':
    app.run_server(debug=True)