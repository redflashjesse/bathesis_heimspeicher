import plotly.express as px
import pandas as pd
import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

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
df['current_soc_12000Wh_eigenverbrauch'] = df['current_soc_12000Wh_eigenverbrauch'] * 100
df['current_soc_12000Wh_netzdienlich'] = df['current_soc_12000Wh_netzdienlich'] * 100

df['Index'] = df.index


# Plotly-Figur erstellen
fig = px.scatter(df, x=df.index,
                 y=[(df['GridPowerIn[Wh]']+ df['GridPowerOut[Wh]']),
                    df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'],
                    df['p_netzleistung_12000Wh_netzdienlich[Wh]']],
                 # color='source',
                 range_y=[0, 1000],
                 #hover_name=[df.index],
                     #'Leistung ohne Speicher', 'Leistung nach eigenverbrauch', 'Leistung nach netzdienlich'],
                 # hover_data=['soc_scaled']
                 )
"""
fig.add_trace(px.line(df, x=df.index,
                      y='current_soc_12000Wh_eigenverbrauch',
                      name='SOC Eigenverbrauch')['data'][0])
fig.update_traces(name='SOC', selector=dict(name='line'))
fig.add_trace(px.line(df, x=df.index,
                      y='current_soc_12000Wh_netzdienlich',
                      name='SOC Netzdienlichkeit')['data'][0])
fig.update_traces(name='SOC', selector=dict(name='line'))
fig.update_layout(yaxis_title='Power (kWh)',
                  yaxis2_title='SOC (%)',
                  yaxis2=dict(side='right', overlaying='y',
                              range=[0, 100], tickvals=[0, 20, 40, 60, 80, 100]))"""

# Dash-App erstellen
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='live-graph', figure=fig),
])

if __name__ == '__main__':
    app.run_server(debug=True)
