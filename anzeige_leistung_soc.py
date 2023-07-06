import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.io as pio
from plotly.subplots import make_subplots
import os
import plotly.offline as pyo  # for offline ploting

'''This script is used to display the power and soc of the battery in the dashboard. 
Differnt size of batteries can be set up by speichergroesse. With fig, fig2, fig3 and fig4 the graphs are created. 
Visable one by once with show. All at once with fig_combined at a dash app. 
'''
speichergroesse = 30000
# Load data
df = pd.read_pickle(
    f'C:/Users/EE/Documents/Petau/bathesis_heimspeicher/documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl')
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
factor = 1  # or 60
df['PowerGeneratedPV[Wh]'] = -df['PowerGeneratedPV'] / factor
df['PowerOutputPV[Wh]'] = df['PowerOutputPV'] / factor
df['GridPowerIn[Wh]'] = df['GridPowerIn'] / factor
df['GridPowerOut[Wh]'] = -df['GridPowerOut'] / factor
df[f'p_delta_{speichergroesse}Wh_eigenverbrauch[Wh]'] = df[f'p_delta_{speichergroesse}Wh_eigenverbrauch'] / factor
df[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch[Wh]'] = df[
                                                                f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch'] / factor
df[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch[Wh]'] = -df[
    f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'] / factor
df[f'p_netzleistung_{speichergroesse}Wh_eigenverbrauch[Wh]'] = df[
                                                                   f'p_netzleistung_{speichergroesse}Wh_eigenverbrauch'] / factor
df[f'p_delta_{speichergroesse}Wh_netzdienlich[Wh]'] = df[f'p_delta_{speichergroesse}Wh_netzdienlich'] / factor
df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich[Wh]'] = df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] / factor
df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich[Wh]'] = -df[
    f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] / factor
df[f'p_netzleistung_{speichergroesse}Wh_netzdienlich[Wh]'] = df[
                                                                 f'p_netzleistung_{speichergroesse}Wh_netzdienlich'] / factor

# SOC um Faktor 10 multiplizieren vom Bereich 0-1 auf 0-100 zukommen für die bessere Ansicht
df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'] = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'] * 100
df[f'current_soc_{speichergroesse}Wh_netzdienlich'] = df[f'current_soc_{speichergroesse}Wh_netzdienlich'] * 100

df['Index'] = df.index

df = df.copy()
# for speichergroesse in speichergroessen:

# Multiplikation mit 100 und Glättung
smoothed_eigenverbrauch = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'].rolling(30).mean()
smoothed_netzdienlich = df[f'current_soc_{speichergroesse}Wh_netzdienlich'].rolling(30).mean()

# Plotly-Figur erstellen
fig = px.scatter(df,
                 x='Index',
                 y=[df['GridPowerIn[Wh]'] + df['GridPowerOut[Wh]'],
                    df[f'p_netzleistung_{speichergroesse}Wh_eigenverbrauch[Wh]'],
                    df[f'p_netzleistung_{speichergroesse}Wh_netzdienlich[Wh]'], ],
                 title=f'Leistung im Quartier mit {speichergroesse/1000} kWh',
                 labels={'Index': 'Zeit',
                         'value': 'Leistung [Wh]'},
                 )
fig.update_traces(name="ohne Speicher", selector=dict(name="wide_variable_0"))
fig.update_traces(name="Eigenverbrauch", selector=dict(name=f"p_netzleistung_{speichergroesse}Wh_eigenverbrauch[Wh]"))
fig.update_traces(name="Netzdienlich", selector=dict(name=f"p_netzleistung_{speichergroesse}Wh_netzdienlich[Wh]"))
fig.update_layout(legend=dict(
    title='Betriebsweisen'
))

fig2 = px.scatter(df,
                  x='Index',
                  y=['GridPowerIn[Wh]',
                     f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch[Wh]',
                     f'p_netzbezug_{speichergroesse}Wh_netzdienlich[Wh]',
                    ],
                  title=f'Leistungsbezug im Quartier mit {speichergroesse/1000} kWh',
                  labels={'Index': 'Zeit',
                          'value': 'Leistung [Wh]'},
                  )
fig2.update_traces(name="ohne Speicher", selector=dict(name="GridPowerIn[Wh]"))
fig2.update_traces(name="Eigenverbrauch", selector=dict(name=f"p_netzbezug_{speichergroesse}Wh_eigenverbrauch[Wh]"))
fig2.update_traces(name="Netzdienlich", selector=dict(name=f"p_netzbezug_{speichergroesse}Wh_netzdienlich[Wh]"))
fig2.update_layout(legend=dict(
    title=f'Betriebsweisen'
))

fig3 = px.scatter(df,
                  x='Index',
                  y=['GridPowerOut[Wh]',
                     f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch[Wh]',
                     f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich[Wh]',
                     ],
                  title=f'Einspeiseleistung im Quartier mit {speichergroesse/1000} kWh',
                  labels={
                      'Index': 'Zeit',
                      'value': 'Leistung [Wh]',
                      'variable': 'Betriebsweisen',
                  },
                  # color= ['red','blue','green']
                  )
fig3.update_traces(name="ohne Speicher", selector=dict(name="GridPowerOut[Wh]"))
fig3.update_traces(name="Eigenverbrauch", selector=dict(name=f"p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch[Wh]"))
fig3.update_traces(name="Netzdienlich", selector=dict(name=f"p_netzeinspeisung_{speichergroesse}Wh_netzdienlich[Wh]"))

fig4 = px.line(df, x='Index',
               y=[smoothed_eigenverbrauch, smoothed_netzdienlich],
               labels={'Index': 'Zeit',
                       'value': 'SoC in Prozent',
                       'variable': f'Betriebsweise {speichergroesse/1000}kWh Speicher',
                       },

               markers=True,
               title='SOC-Verlauf zwischen Eigenverbrauch und Netzdienlichkeit',
               #color={'wide_variable_0': 'red', 'wide_variable_1': 'green'},
               #color= ['red','green']
               )

fig4.update_traces(name="Eigenverbrauch", selector=dict(name="wide_variable_0"))
fig4.update_traces(name="Netzdienlich", selector=dict(name="wide_variable_1"))

# set the title
#fig4.update_layout(title=dict(text='SOC-Verlauf zwischen Eigenverbrauch und Netzdienlichkeit', font=dict(size=24)))

# set the x,y-axis labels
fig.update_layout(xaxis=dict(title_font=dict(size=24), tickfont=dict(size=22)),
                  yaxis=dict(title_font=dict(size=24), tickfont=dict(size=22)))
fig2.update_layout(xaxis=dict(title_font=dict(size=24), tickfont=dict(size=22)),
                  yaxis=dict(title_font=dict(size=24), tickfont=dict(size=22)))
fig3.update_layout(xaxis=dict(title_font=dict(size=24), tickfont=dict(size=22)),
                  yaxis=dict(title_font=dict(size=24), tickfont=dict(size=22)))
fig4.update_layout(xaxis=dict(title_font=dict(size=24), tickfont=dict(size=22)),
                  yaxis=dict(title_font=dict(size=24), tickfont=dict(size=22)))

# set the legend title and font size
fig.update_layout(legend=dict(font=dict(size=16)))
fig2.update_layout(legend=dict(font=dict(size=16)))
fig3.update_layout(legend=dict(font=dict(size=16)))
fig4.update_layout(legend=dict(font=dict(size=16)))

# show the figure
fig.show()
fig2.show()
fig3.show()
fig4.show()
exit()
print(f'--- Save figures as png at images ---')
# write_image is not working, takes too long
# save fig power diagram as png and html
#fig.write_image(f"images/fig{speichergroesse/1000}kWh.png")
#fig2.write_image(f"images/fig2{speichergroesse/1000}kWh.png")
#fig3.write_image(f"images/fig3{speichergroesse/1000}kWh.png")
#fig4.to_image(format='png', engine='kaleido', width=800, height=600, scale=1)
#fig4.write_image(f"images/fig4{speichergroesse/1000}kWh.png")
# print png are done
print(f'--- Save figures as html at images ---')
fig.write_html(f"./images/Jahreslistung_{speichergroesse/1000}kWh.html")
fig2.write_html(f"./images/Leistungsbezug_{speichergroesse/1000}kWh.html")
fig3.write_html(f"./images/Einspeiseleistung_{speichergroesse/1000}kWh.html")
fig4.write_html(f"./images/SOC-Verlauf_{speichergroesse/1000}kWh.html")
# print html are done
'''print(f'--- Save pyo as html at images ---')
pyo.plot(fig, filename=f"./images/fig{speichergroesse/1000}kWh1.html", auto_open=True)
pyo.plot(fig2, filename=f"./images/fig2{speichergroesse/1000}kWh1.html", auto_open=True)
pyo.plot(fig3, filename=f"./images/fig3{speichergroesse/1000}kWh1.html", auto_open=True)
pyo.plot(fig4, filename=f"./images/fig4{speichergroesse/1000}kWh1.html", auto_open=True)'''
print(f'--- Done, open dashboard ---')

# Dash-App erstellen
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Leistung im Quartier'),
    dcc.Graph(id='live-graph', figure=fig),
    html.H2('Leistungsänderung im Quartier'),
    dcc.Graph(id='live-graph', figure=fig2),
    html.H3('Leistungsänderung im Quartier'),
    dcc.Graph(id='live-graph', figure=fig3),
    html.H4('Leistungsänderung im Quartier'),
    dcc.Graph(id='live-graph', figure=fig4),
])

# set exsample figure
fig_go = go.Figure(fig)
fig2_go = go.Figure(fig2)
fig3_go = go.Figure(fig3)
fig4_go = go.Figure(fig4)

# save fig power diagram as png
fig_go.write_image(f"./images/fig_go{speichergroesse/1000}kwh.png")

# save fig2 power diagram as png
fig2_go.write_image(f"./images/fig2_go{speichergroesse/1000}kWh.png")

# save fig3 power diagram as png
fig3_go.write_image(f"./images/fig3_go{speichergroesse/1000}kWh.png")

# save fig4 power diagram as png
fig4_go.write_image(f"./images/fig4_go{speichergroesse/1000}kWh.png")

# Erstellen Sie ein gemeinsames Ausgabefeld mit Subplots
fig_combined = make_subplots(rows=4, cols=1,
                             subplot_titles=("Netzleistung",
                                             "SOC-Verlauf",
                                             "Netzbezug",
                                             "Netzeinspeisung"))


fig_combined.add_trace(fig_go.data[0], row=1, col=1)
fig_combined.add_trace(fig_go.data[1], row=1, col=1)
fig_combined.add_trace(fig_go.data[2], row=1, col=1)

fig_combined.add_trace(fig2_go.data[0], row=2, col=1)
fig_combined.add_trace(fig2_go.data[1], row=2, col=1)
fig_combined.add_trace(fig2_go.data[2], row=2, col=1)

fig_combined.add_trace(fig3_go.data[0], row=3, col=1)
fig_combined.add_trace(fig3_go.data[1], row=3, col=1)

fig_combined.add_trace(fig4_go.data[0], row=4, col=1)
fig_combined.add_trace(fig4_go.data[1], row=4, col=1)
fig_combined.add_trace(fig4_go.data[2], row=4, col=1)
#fig_combined.data.marker.color = ['red', 'blue', 'green']

print('Computed new Plots.')

# Speichern Sie das Dashboard als HTML-Datei
pio.write_html(fig_combined, file="./export/Leistungsanzeige.html", auto_open=True)
print('Wrote to html.')

if __name__ == '__main__':
    app.run_server(debug=True)
