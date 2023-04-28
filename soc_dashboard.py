# Import packages
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, html, dcc
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

# Leistungswerte von Wmin in Wh umrechnen
df['PowerGeneratedPV[Wh]'] = df['PowerGeneratedPV'] / 60
df['PowerOutputPV[Wh]'] = df['PowerOutputPV'] / 60
df['GridPowerIn[Wh]'] = df['GridPowerIn'] / 60
df['GridPowerOut[Wh]'] = df['GridPowerOut'] / 60
df['p_delta_12000Wh_eigenverbrauch[Wh]'] = df['p_delta_12000Wh_eigenverbrauch'] / 60
df['p_netzbezug_12000Wh_eigenverbrauch[Wh]'] = df['p_netzbezug_12000Wh_eigenverbrauch'] / 60
df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'] = df['p_netzeinspeisung_12000Wh_eigenverbrauch'] / 60
df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'] = df['p_netzleistung_12000Wh_eigenverbrauch'] / 60
df['p_delta_12000Wh_netzdienlich[Wh]'] = df['p_delta_12000Wh_netzdienlich'] / 60
df['p_netzbezug_12000Wh_netzdienlich[Wh]'] = df['p_netzbezug_12000Wh_netzdienlich'] / 60
df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]'] = df['p_netzeinspeisung_12000Wh_netzdienlich'] / 60
df['p_netzleistung_12000Wh_netzdienlich[Wh]'] = df['p_netzleistung_12000Wh_netzdienlich'] / 60

# SOC um Faktor 10 multiplizieren vom Bereich 0-1 auf 0-100 zukommen für die bessere Ansicht
df['current_soc_12000Wh_eigenverbrauch_0-100'] = df['current_soc_12000Wh_eigenverbrauch'] * 100
df['current_soc_12000Wh_netzdienlich_0-100'] = df['current_soc_12000Wh_netzdienlich'] * 100

df['Index'] = df.index

# Multiplikation mit 100 und Glättung
smoothed_eigenverbrauch = df['current_soc_12000Wh_eigenverbrauch'].rolling(60).mean() * 100
smoothed_netzdienlich = df['current_soc_12000Wh_netzdienlich'].rolling(60).mean() * 100

# Scatter plot erstellen
fig = px.line(df, x='Index', y=[smoothed_eigenverbrauch, smoothed_netzdienlich],
                 labels={'Index': 'Zeit', 'value': 'SoC', 'variable': 'Betriebsweise Speicher'},
                 # marginal_y='violin',
                 title='SOC-Verlauf zwischen Eigenverbrauch und Netzdienlichkeit')
fig.show()
exit()
# Initialize the app
app = Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1('Verlauf des SoC des Speichers nach Netzdienlichkeit und Eigenverbrauch'),
    dcc.Graph(id='live-graph', figure=fig),
])
if __name__ == '__main__':
    app.run_server(debug=True)