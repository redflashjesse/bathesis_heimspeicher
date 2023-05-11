import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.io as pio
from plotly.subplots import make_subplots

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
df['PowerGeneratedPV[Wh]'] = -df['PowerGeneratedPV'] / 60
df['PowerOutputPV[Wh]'] = df['PowerOutputPV'] / 60
df['GridPowerIn[Wh]'] = df['GridPowerIn'] / 60
df['GridPowerOut[Wh]'] = -df['GridPowerOut'] / 60
df['p_delta_12000Wh_eigenverbrauch[Wh]'] = df['p_delta_12000Wh_eigenverbrauch'] / 60
df['p_netzbezug_12000Wh_eigenverbrauch[Wh]'] = df['p_netzbezug_12000Wh_eigenverbrauch'] / 60
df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'] = -df['p_netzeinspeisung_12000Wh_eigenverbrauch'] / 60
df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'] = df['p_netzleistung_12000Wh_eigenverbrauch'] / 60
df['p_delta_12000Wh_netzdienlich[Wh]'] = df['p_delta_12000Wh_netzdienlich'] / 60
df['p_netzbezug_12000Wh_netzdienlich[Wh]'] = df['p_netzbezug_12000Wh_netzdienlich'] / 60
df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]'] = -df['p_netzeinspeisung_12000Wh_netzdienlich'] / 60
df['p_netzleistung_12000Wh_netzdienlich[Wh]'] = df['p_netzleistung_12000Wh_netzdienlich'] / 60

# SOC um Faktor 10 multiplizieren vom Bereich 0-1 auf 0-100 zukommen für die bessere Ansicht
df['current_soc_12000Wh_eigenverbrauch'] = df['current_soc_12000Wh_eigenverbrauch'] * 100
df['current_soc_12000Wh_netzdienlich'] = df['current_soc_12000Wh_netzdienlich'] * 100

df['Index'] = df.index

# Multiplikation mit 100 und Glättung
smoothed_eigenverbrauch = df['current_soc_12000Wh_eigenverbrauch'].rolling(30).mean()
smoothed_netzdienlich = df['current_soc_12000Wh_netzdienlich'].rolling(30).mean()

# Plotly-Figur erstellen
fig = px.scatter(df, x=df.index,
                 y=[
                    (df['GridPowerIn[Wh]'] - (df['PowerGeneratedPV[Wh]'] + df['GridPowerOut[Wh]'])),
                    (df['GridPowerIn[Wh]'] + df['GridPowerOut[Wh]']),
                    df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'],
                    df['p_netzleistung_12000Wh_netzdienlich[Wh]'],
                    ],
                 # color='source',
                 # range_y=[-20,20],
                 # hover_name=[df.index],
                     #'Leistung ohne Speicher', 'Leistung nach eigenverbrauch', 'Leistung nach netzdienlich'],
                 # hover_data=['soc_scaled']
                 title='Leistung im Quartier',
                 labels={
                     'x': 'Zeit',
                     'y': 'Leistung [Wh]'
                    },
                 marginal_y='violin',
                 #marginal_y='boxplot'
                 )
fig.update_traces(name="Grid Power", selector=dict(name="y0"))
fig.update_layout(legend=dict(
    title='Leistungsanteil'
))

fig2 = px.scatter(df, x=df.index,
                 y=['GridPowerIn[Wh]',
                    'p_netzbezug_12000Wh_netzdienlich[Wh]',
                    'p_netzbezug_12000Wh_eigenverbrauch[Wh]',
                    ],
                 # color='source',
                 # range_y=[-20,20],
                 # hover_name=[df.index],
                     #'Leistung ohne Speicher', 'Leistung nach eigenverbrauch', 'Leistung nach netzdienlich'],
                 # hover_data=['soc_scaled']
                 title='Leistungsbezug im Quartier',
                 labels={
                     'x': 'Zeit',
                     'y': 'Leistung [Wh]',
                     'variable': 'Legende',
                    },
                 marginal_y='violin',
                 )
fig2.update_traces(name="Grid Power", selector=dict(name="y0"))
fig2.update_layout(legend=dict(
    title='Veränderung der Leistungen durch Speicher'
))

fig3 = px.scatter(df, x='Index',
                 y=['GridPowerOut[Wh]',
                    'p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]',
                    'p_netzeinspeisung_12000Wh_netzdienlich[Wh]',
                    ],
                 # color='source',
                 # range_y=[-20,20],
                 # hover_name=[df.index],
                     #'Leistung ohne Speicher', 'Leistung nach eigenverbrauch', 'Leistung nach netzdienlich'],
                 # hover_data=['soc_scaled']
                 title='Einspeiseleistung im Quartier',
                 labels={
                     'Index': 'Zeit',
                     'value': 'Leistung [Wh]',
                     'variable': 'Legende',
                     'wide_variable_0': 'Leistung ohne Speicher',
                     'p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]': 'Leistung nach Eigenverbrauch',
                     'p_netzeinspeisung_12000Wh_netzdienlich[Wh]': 'Leistung nach Netzdienlich',
                    },
                 marginal_y='violin',
                 )



fig4 = px.line(df, x='Index',
               y=[smoothed_eigenverbrauch, smoothed_netzdienlich],
               labels={'Index': 'Zeit',
                       'value': 'SoC in Prozent',
                       'variable': 'Betriebsweise Speicher'},
               markers=True,
               title='SOC-Verlauf zwischen Eigenverbrauch und Netzdienlichkeit')


# Dash-App erstellen
"""app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Leistung im Quartier'),
    dcc.Graph(id='live-graph', figure=fig),
    html.H2('Leistungsänderung im Quartier'),
    dcc.Graph(id='live-graph', figure=fig2),
    html.H3('Leistungsänderung im Quartier'),
    dcc.Graph(id='live-graph', figure=fig3),
    html.H4('Leistungsänderung im Quartier'),
    dcc.Graph(id='live-graph', figure=fig4),
])"""

# Erstellen Sie einige Beispiel-Figuren
fig_go = go.Figure(fig)
fig2_go = go.Figure(fig2)
fig3_go = go.Figure(fig3)
fig4_go = go.Figure(fig4)

# Erstellen Sie ein gemeinsames Ausgabefeld mit Subplots
fig_combined = make_subplots(rows=4, cols=1, subplot_titles=("Netzleistung","SOC-Verlauf", "Netzbezug", "Netzeinspeisung"))
fig_combined.add_trace(fig_go.data[0], row=1, col=1)
fig_combined.add_trace(fig4_go.data[0], row=1, col=1)
fig_combined.add_trace(fig2_go.data[0], row=3, col=1)
fig_combined.add_trace(fig3_go.data[0], row=4, col=1)
#fig_combined.marker.color=['red','blue','green']


# Zeigen Sie das kombinierte Ausgabefeld an
#fig_combined.show()
#fig.show()
#fig2.show()
fig3.show()
#fig4.show()
# Speichern Sie das Dashboard als HTML-Datei
# pio.write_html(fig_combined, file="dash-plotly_as_html/Leistungsanzeige.html", auto_open=True)

if __name__ == '__main__':
    app.run_server(debug=True)
