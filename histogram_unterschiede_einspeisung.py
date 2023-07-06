# Importiere benötigte Module
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html


speichergroesse = 12000
# Load data
df = pd.read_pickle(f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl')
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
df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'] = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'] * 100
df[f'current_soc_{speichergroesse}Wh_netzdienlich'] = df[f'current_soc_{speichergroesse}Wh_netzdienlich'] * 100

df['Index'] = df.index

# Erstelle das Scatter-Plot
# differenz_betriebsweise = df[(df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'] - df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]']) <= 10]
schwellenwert = -400
einspeisung_eigen_speichergroesse = df[df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'] <= schwellenwert]
einspeisung_netz_speichergroesse = df[df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]'] <= schwellenwert]
differenz_betriebsweise  = einspeisung_eigen_speichergroesse-einspeisung_netz_speichergroesse
fig = px.scatter(df, x=df.index, y=df['GridPowerOut[Wh]'],
                 color=df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'] - df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]'],
                 # marginal_x='violin'
                 )

# Passe das Layout an
fig.update_layout(
    title="Netzdienlich vs. Eigenverbrauch",
    xaxis_title="Zeit",
    yaxis_title="Netzeinspeisung (Netzdienlich und Eigenverbrauch)"
)

# Zeige das Scatter-Plot an
fig.show()


# Erstelle das Dash-Layout
app = dash.Dash(__name__)

# Erstelle das Scatter-Plot
leistungsaenderung_eigenverbrauch = df['GridPowerOut[Wh]'] - df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]']
leistungsaenderung_netzdienlich = df['GridPowerOut[Wh]'] - df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]']
fig = px.scatter(df, x=df.index,
                 y=[#leistungsaenderung_eigenverbrauch,
                    leistungsaenderung_netzdienlich,
                    ])
fig2 = px.scatter(df, x=df.index,
                 y=[# df['GridPowerOut[Wh]'],
                    leistungsaenderung_eigenverbrauch - leistungsaenderung_netzdienlich,
                    ])
# Passe das Layout des Scatter-Plots an
fig.update_layout(
    title="Vergleich: Eigenverbrauch - Netzdienlich",
    xaxis_title="Zeit",
    yaxis_title="Leistung (Eigenverbrauch - Netzdienlich)"
)
fig2.update_layout(
    title="Differenz: Eigenverbrauch - Netzdienlich",
    xaxis_title="Zeit",
    yaxis_title="Leistung (Eigenverbrauch - Netzdienlich)"
)

# Erstelle das Dash-Layout
app.layout = html.Div(children=[
    html.H1(children='Differenz zwischen Eigenverbrauch - Netzdienlich'),
    dcc.Graph(
        id='scatter-plot',
        figure=fig
    )
])

# Starte die Dash-App
if __name__ == '__main__':
    app.run_server(debug=True)
