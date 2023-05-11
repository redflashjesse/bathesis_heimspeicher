import dash
import dash_bootstrap_components as dbc
from dash import html
from pandas.io.formats.style import coloring_args
import matplotlib.pyplot as plt
import pandas as pd
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



sum_pv_gen = (df['PowerGeneratedPV[Wh]'].sum()/1000).round(2)
sum_einspeisung = (df['GridPowerOut[Wh]'].sum()/1000).round(2)
pvdiketnutzung_kwh = sum_pv_gen - sum_einspeisung
power_in_wh__sum = (df['GridPowerIn[Wh]'].sum()/1000).round(2)

autakie_ohne = (pvdiketnutzung_kwh/(df['GridPowerIn[Wh]'].sum()/1000+pvdiketnutzung_kwh)).round(3)*100
summe_netzbezug_kWh = [f"Summe Netzbezug",
                       (f"{(power_in_wh__sum)}kWh"),
                       "für das Jahr 2021"
                       ]
summe_netzeinspeisung_kWh = [f"Summe Netzeinspeisung", f"{(sum_einspeisung)}kWh", "für das Jahr 2021"]
summe_pvertrag_kWh = [f"Summe PV Ertrag", f"{(sum_pv_gen)}kWh", "für das Jahr 2021"]
summe_pvdirketnutzung_kWh = [f"Summe PV Direktnutzung", f"{pvdiketnutzung_kwh}kWh", "für das Jahr 2021"]
autaktie_bestand = [f"Autaktie", f"{(autakie_ohne)} %", "für das Jahr 2021"]

sum_netzbezug_12000Wh_eigen = ((df['p_netzbezug_12000Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_netzeinspeisung_12000Wh_eigen = ((df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_netzleistung_12000Wh_eigen = ((df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_speicherleistung_12000Wh_eigen = ((df[df[f'p_delta_{speichergroesse}Wh_eigenverbrauch[Wh]'] > 0][
               f'p_delta_{speichergroesse}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_pvleistung_nutzung_12000Wh_eigen = (power_in_wh__sum-sum_netzbezug_12000Wh_eigen)+pvdiketnutzung_kwh
autakie_12000Wh_eigen = (sum_pvleistung_nutzung_12000Wh_eigen/(df[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch[Wh]'].sum()/1000+sum_pvleistung_nutzung_12000Wh_eigen)).round(5)*100

summe_netzbezug_kWh_speichergroesse_Wh_eigenverbrauch = [f"Summe Netzbezug mit Speicher {speichergroesse}Wh", f"{sum_netzbezug_12000Wh_eigen}kWh", "eigenverbrauchsoptimiert"]
summe_netzeinspeisung_kWh_speichergroesse_Wh_eigenverbrauch = [f"Summe Netzeinspeisung mit Speicher {speichergroesse}Wh", f"{sum_netzeinspeisung_12000Wh_eigen}kWh", "eigenverbrauchsoptimiert"]
summe_netzleistung_kWh_speichergroesse_Wh_eigenverbrauch = [f"Nettosumme der Leistung zum Netz mit Speicher {speichergroesse}Wh", f"{sum_netzleistung_12000Wh_eigen}kWh", "eigenverbrauchsoptimiert"]
summe_speicherleistung_kWh_speichergroesse_Wh_eigenverbrauch = [f"Summe Speicherleistung mit Speicher {speichergroesse}Wh", f"{sum_speicherleistung_12000Wh_eigen}kWh", "eigenverbrauchsoptimiert"]
autaktie_speichergroesse_Wh_eigenverbrauch = [f"Autaktiegrad mit Speicher {speichergroesse}Wh", f"{autakie_12000Wh_eigen} %", "eigenverbrauchsoptimiert"]

sum_netzbezug_12000Wh_netz = ((df['p_netzbezug_12000Wh_netzdienlich[Wh]'].sum() / 1000).round(2))
sum_netzeinspeisung_12000Wh_netz = ((df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]'].sum() / 1000).round(2))
sum_netzleistung_12000Wh_netz = ((df['p_netzleistung_12000Wh_netzdienlich[Wh]'].sum() / 1000).round(2))
sum_speicherleistung_12000Wh_netz = ((df[df[f'p_delta_{speichergroesse}Wh_netzdienlich[Wh]'] > 0][
               f'p_delta_{speichergroesse}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_pvleistung_nutzung_12000Wh_netz = (power_in_wh__sum-sum_netzbezug_12000Wh_netz)+pvdiketnutzung_kwh
autakie_12000Wh_netz = (sum_pvleistung_nutzung_12000Wh_netz/(df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich[Wh]'].sum()/1000+sum_pvleistung_nutzung_12000Wh_netz)).round(5)*100

summe_netzbezug_kWh_speichergroesse_Wh_netzdienlich = [f"Summe Netzbezug mit Speicher {speichergroesse}Wh", f"{sum_netzbezug_12000Wh_netz}kWh", "netzdienlich optimiert"]
summe_netzeinspeisung_kWh_speichergroesse_Wh_netzdienlich = [f"Summe Netzeinspeisung mit Speicher {speichergroesse}Wh", f"{sum_netzeinspeisung_12000Wh_netz}kWh", "netzdienlich optimiert"]
summe_netzleistung_kWh_speichergroesse_Wh_netzdienlich = [f"Nettosumme der Leistung zum Netz mit Speicher {speichergroesse}Wh", f"{sum_netzleistung_12000Wh_netz}kWh", "netzdienlich optimiert"]
#summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich = [f"Summe Speicherleistung mit Speicher {speichergroesse}Wh", f"{((df[df[f'p_delta_{speichergroesse}Wh_netzdienlich[Wh]'] > 0][f'p_delta_{speichergroesse}Wh_netzdienlich[Wh]'].sum()/1000).round(2))}kWh", "netzdienlich optimiert"]
summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich = [f"Summe Speicherleistung mit Speicher {speichergroesse}Wh", f"{sum_speicherleistung_12000Wh_netz}kWh", "netzdienlich optimiert"]
autaktie_speichergroesse_Wh_netzdienlich = [f"Autaktiegrad mit Speicher {speichergroesse}Wh", f"{autakie_12000Wh_netz} %", "netzdienlich optimiert"]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_card(title, content, text, color):
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H4(title, className="card-title"),
                html.Br(),
                html.H2(content, className="card-subtitle"),
                html.Br(),
                html.P(text, className="card-text"),
                html.Br(),
            ]
        ),
        color=color, # "primary", "secondary", "success", "warning", "danger", "info", "light" und "dark". Du kannst aber auch jede gültige CSS-Farbe als String verwenden.
        inverse=True
    )
    return(card)

card01 = create_card(summe_netzbezug_kWh[0], summe_netzbezug_kWh[1],summe_netzbezug_kWh[2], "info")
card02 = create_card(summe_netzeinspeisung_kWh[0],summe_netzeinspeisung_kWh[1],summe_netzeinspeisung_kWh[2], "info")
card03 = create_card(summe_pvertrag_kWh[0],summe_pvertrag_kWh[1],summe_pvertrag_kWh[2], "info")
card04 = create_card(summe_pvdirketnutzung_kWh[0],summe_pvdirketnutzung_kWh[1],summe_pvdirketnutzung_kWh[2], "info")
card05 = create_card(autaktie_bestand[0], autaktie_bestand[1],autaktie_bestand[2], "info")
card06 = create_card("Number of Comment on Articles", "None Comments", "Hinweis", "info")

card11 = create_card(summe_netzbezug_kWh_speichergroesse_Wh_eigenverbrauch[0], summe_netzbezug_kWh_speichergroesse_Wh_eigenverbrauch[1], summe_netzbezug_kWh_speichergroesse_Wh_eigenverbrauch[2], "primary")
card12 = create_card(summe_netzeinspeisung_kWh_speichergroesse_Wh_eigenverbrauch[0], summe_netzeinspeisung_kWh_speichergroesse_Wh_eigenverbrauch[1], summe_netzeinspeisung_kWh_speichergroesse_Wh_eigenverbrauch[2], "primary")
card13 = create_card(summe_netzleistung_kWh_speichergroesse_Wh_eigenverbrauch[0], summe_netzleistung_kWh_speichergroesse_Wh_eigenverbrauch[1], summe_netzleistung_kWh_speichergroesse_Wh_eigenverbrauch[2], "primary")
card14 = create_card(summe_speicherleistung_kWh_speichergroesse_Wh_eigenverbrauch[0], summe_speicherleistung_kWh_speichergroesse_Wh_eigenverbrauch[1], summe_speicherleistung_kWh_speichergroesse_Wh_eigenverbrauch[2], "primary")
card15 = create_card(autaktie_speichergroesse_Wh_eigenverbrauch[0], autaktie_speichergroesse_Wh_eigenverbrauch[1], autaktie_speichergroesse_Wh_eigenverbrauch[2], "primary")
card16 = create_card("Number of Comment on Articles", "None Comments", "Hinweis", "info")

card21 = create_card(summe_netzbezug_kWh_speichergroesse_Wh_netzdienlich[0], summe_netzbezug_kWh_speichergroesse_Wh_netzdienlich[1], summe_netzbezug_kWh_speichergroesse_Wh_netzdienlich[2], "secondary")
card22 = create_card(summe_netzeinspeisung_kWh_speichergroesse_Wh_netzdienlich[0], summe_netzeinspeisung_kWh_speichergroesse_Wh_netzdienlich[1], summe_netzeinspeisung_kWh_speichergroesse_Wh_netzdienlich[2], "secondary")
card23 = create_card(summe_netzleistung_kWh_speichergroesse_Wh_netzdienlich[0], summe_netzleistung_kWh_speichergroesse_Wh_netzdienlich[1], summe_netzleistung_kWh_speichergroesse_Wh_netzdienlich[2], "secondary")
card24 = create_card(summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich[0], summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich[1], summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich[2], "secondary")
card25 = create_card(autaktie_speichergroesse_Wh_netzdienlich[0], autaktie_speichergroesse_Wh_netzdienlich[1], autaktie_speichergroesse_Wh_netzdienlich[2], "secondary")
card26 = create_card("Number of Comment on Articles", "None Comments", "Hinweis", "info")

app.layout = html.Div([
    dbc.Row([
        dbc.Col(card01, width=2),
        dbc.Col(card02, width=2),
        dbc.Col(card03, width=2),
        dbc.Col(card04, width=2),
        dbc.Col(card05, width=2),
        #dbc.Col(card06, width=2),
    ]),
    dbc.Row([
        dbc.Col(card11, width=2),
        dbc.Col(card12, width=2),
        dbc.Col(card13, width=2),
        dbc.Col(card14, width=2),
        dbc.Col(card15, width=2),
        #dbc.Col(card16, width=2),
    ]),
    dbc.Row([

        dbc.Col(card21, width=2),
        dbc.Col(card22, width=2),
        dbc.Col(card23, width=2),
        dbc.Col(card24, width=2),
        dbc.Col(card25, width=2),
        #dbc.Col(card26, width=2),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)



"""- One of the following named colorscales:
            ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
             'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
             'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
             'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
             'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
             'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
             'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
             'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
             'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
             'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
             'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
             'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
             'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
             'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
             'ylorrd']"""




exit()


import pandas as pd
import matplotlib.pyplot as plt
"""
# Annahme: Daten zur Stromversorgung und -erzeugung werden als CSV-Dateien bereitgestellt
# mit zwei Spalten "Zeitstempel" und "Wert" für Netzbezug und Netzeinspeisung
# Speicherdaten werden in einem separaten CSV-File gespeichert

import pandas as pd

# Laden Sie die Daten aus den CSV-Dateien in Pandas DataFrame-Objekte
netzbezug = pd.read_csv("netzbezug.csv")
netzeinspeisung = pd.read_csv("netzeinspeisung.csv")
speicher = pd.read_csv("speicher.csv")

# Definieren Sie die Kapazität des Speichers in kWh und die Wirkungsgradverluste bei der Speicherung
speicherkapazitaet = 10
speicherverluste = 0.05  # 5% Verlust bei der Speicherung

# Definieren Sie den Mindest- und Maximalwert für den Speicher in Prozent der Kapazität
speicher_min = 10
speicher_max = 90

# Finden Sie die maximalen Einspeisungswerte pro Tag
netzeinspeisung_pro_tag = netzeinspeisung.resample('D', on='Zeitstempel').max()

# Finden Sie die Zeitpunkte, an denen die Einspeisung am höchsten ist
einspeisung_hoechstwerte = netzeinspeisung_pro_tag[
    netzeinspeisung_pro_tag['Wert'] == netzeinspeisung_pro_tag['Wert'].max()]


# Definieren Sie eine Funktion zum Laden des Speichers
def speicher_laden(ladewert, aktueller_speicherstand):
    neuer_speicherstand = aktueller_speicherstand + ladewert - (ladewert * speicherverluste)
    if neuer_speicherstand > speicherkapazitaet * (speicher_max / 100):
        neuer_speicherstand = speicherkapazitaet * (speicher_max / 100)
    return neuer_speicherstand


# Loop durch die Zeilen der Daten und aktualisieren den Speicherstand basierend auf der Stromversorgung und -erzeugung
for index, row in netzbezug.iterrows():
    # Finden Sie den höchsten Einspeisungswert für diesen Tag
    tages_einspeisung_hoechstwert = einspeisung_hoechstwerte.loc[row['Zeitstempel'].strftime('%Y-%m-%d')]['Wert']

    # Überprüfen Sie, ob der Speicher in einem Bereich von 10 bis 90 Prozent seiner Kapazität betrieben wird
    if speicher.loc[index]['Wert'] < speicherkapazitaet * (speicher_min / 100):
        # Laden Sie den Speicher, wenn die Einspeisung am höchsten ist
        if row['Wert'] < tages_einspeisung_hoechstwert:
            speicher.loc[index]['Wert'] = speicher_laden(tages_einspeisung_hoechstwert - row
"""



# Parameter für die Simulation
SPEICHER_KAPAZITAET = 10  # kWh
MIN_KAPAZITAET = 1  # kWh
MAX_KAPAZITAET = 9  # kWh
MAX_EINSP_ZEIT = '12:00'  # maximale Einspeisezeit der Photovoltaikanlage
DATEN_DATEI = 'stromdaten.csv'

# Laden der Stromdaten
stromdaten = pd.read_csv(DATEN_DATEI, parse_dates=['Zeit'], index_col='Zeit')

# Berechnung des Stromverbrauchs und der Stromerzeugung
verbrauch = stromdaten['Netzbezug'] - stromdaten['Netzeinspeisung']
pv_erzeugung = stromdaten['Photovoltaik']

# Initialisierung des Speichers
speicher_ladung = 0
speicher_ladung_max = SPEICHER_KAPAZITAET * MAX_KAPAZITAET
speicher_ladung_min = SPEICHER_KAPAZITAET * MIN_KAPAZITAET
speicher_ladung_hist = []

# Schleife über alle Tage im Jahr
for tag in verbrauch.index.date.unique():
    # Filterung der Daten für den aktuellen Tag
    verbrauch_tag = verbrauch.loc[tag]
    pv_erzeugung_tag = pv_erzeugung.loc[tag]

    # Bestimmung des maximalen Einspeisezeitpunkts
    max_einspeisezeit = pd.Timestamp(f'{tag} {MAX_EINSP_ZEIT}')

    # Filterung der PV-Erzeugung bis zum maximalen Einspeisezeitpunkt
    pv_erzeugung_tag = pv_erzeugung_tag.loc[pv_erzeugung_tag.index <= max_einspeisezeit]

    # Bestimmung der maximalen Einspeisung
    max_einspeisung = pv_erzeugung_tag.sum()

    # Berechnung der Ladung des Speichers
    speicher_ladung += max_einspeisung - verbrauch_tag.sum()

    # Begrenzung der Speicherladung auf das erlaubte Minimum und Maximum
    speicher_ladung = min(max(speicher_ladung, speicher_ladung_min), speicher_ladung_max)

    # Speichern der Speicherladung für die spätere Visualisierung
    speicher_ladung_hist.append(speicher_ladung)

# Visualisierung der Speicherladung über das Jahr
plt.plot(verbrauch.index.date.unique(), speicher_ladung_hist)
plt.xlabel('Datum')
plt.ylabel('Speicherladung (kWh)')
plt.show()



# Laden der Daten in ein Pandas-DataFrame
data = pd.read_csv('netzbezug_netzeinspeisung.csv')

# Definition der Speicherkapazität
speicher_kapazitaet = 12  # kWh

# Definition der Grenzen für den Ladezustand des Speichers
min_ladezustand = 0.1
max_ladezustand = 0.9

# Iteration über die Zeilen des DataFrame
for index, row in data.iterrows():
    # Berechnung der aktuellen Leistungsbilanz
    leistungsbilanz = row['Netzeinspeisung'] - row['Netzbezug']

    # Bedingung für netzdienliche Ladung des Speichers
    if leistungsbilanz > 0:
        # Berechnung der verfügbaren Ladeleistung
        ladeleistung = min(leistungsbilanz, speicher_kapazitaet * (1 - max_ladezustand))

        # Berechnung des aktuellen Ladezustands
        ladezustand = (speicher_kapazitaet * row['Ladezustand']) / 100

        # Bedingung für das Laden des Speichers
        if ladezustand < speicher_kapazitaet * min_ladezustand:
            # Laden des Speichers
            ladezustand += ladeleistung

            # Bedingung für maximalen Ladezustand
            if ladezustand > speicher_kapazitaet * max_ladezustand:
                # Suche nach den maximalen Werten der Einspeisung
                maximalwerte = data.loc[index:, 'Netzeinspeisung'].nlargest(int(speicher_kapazitaet * max_ladezustand))

                # Berechnung der verfügbaren Ladeleistung basierend auf den maximalen Werten
                ladeleistung = min(maximalwerte.sum(), speicher_kapazitaet * (1 - max_ladezustand))

                # Laden des Speichers mit der verfügbaren Ladeleistung
                ladezustand += ladeleistung

                # Aktualisierung der DataFrame-Zeile mit dem neuen Ladezustand
                data.loc[index, 'Ladezustand'] = (ladezustand / speicher_kapazitaet) * 100

                # Überspringen der nächsten Iterationen mit der for-Schleife
                continue

        # Aktualisierung der DataFrame-Zeile mit dem neuen Ladezustand
        data.loc[index, 'Ladezustand'] = (ladezustand / speicher_kapazitaet) * 100

# Speichern der Daten in einer CSV-Datei
data.to_csv('netzbezug_netzeinspeisung_speicher.csv', index=False)

import pandas as pd
import numpy as np
import datetime

# Definition der Speicherkapazität
speicher_kapazitaet = 12  # kWh

# Definition der Grenzen für den Ladezustand des Speichers
min_ladezustand = 0.1
max_ladezustand = 0.9

# Definition des Zeitintervalls in Minuten
zeitintervall = 1

# Definition des Datumsbereichs
start_datum = datetime.datetime(2023, 1, 1)
end_datum = datetime.datetime(2023, 12, 31)

# Erstellung eines leeren DataFrames für die Ergebnisse
ergebnisse = pd.DataFrame(columns=['Datum', 'Uhrzeit', 'Netzbezug', 'Netzeinspeisung', 'Ladezustand'])

# Iteration über die Tage im Datumsbereich
for datum in pd.date_range(start_datum, end_datum):
    # Erstellung eines DataFrames für den aktuellen Tag
    tag = pd.DataFrame(columns=['Datum', 'Uhrzeit', 'Netzbezug', 'Netzeinspeisung', 'Ladezustand'])

    # Iteration über die Minuten des aktuellen Tages
    for minute in pd.date_range(datum, datum + pd.Timedelta('1 day'), freq=f'{zeitintervall}T'):
        # Erstellung eines neuen DataFrames für die aktuelle Minute
        minute_df = pd.DataFrame(
            {'Datum': [minute.date()], 'Uhrzeit': [minute.time()], 'Netzbezug': [np.random.uniform(-1, 1)],
             'Netzeinspeisung': [np.random.uniform(-1, 1)], 'Ladezustand': [np.random.uniform(0, 1)]})

        # Hinzufügen des neuen DataFrames zur Tag DataFrame
        tag = pd.concat([tag, minute_df], ignore_index=True)

    # Initialisierung des SoC und der verbleibenden Kapazität für den aktuellen Tag
    tag_soc = tag.loc[0, 'Ladezustand']
    tag_verbleibende_kapazitaet = speicher_kapazitaet * tag_soc

    # Iteration über die Minuten des aktuellen Tages
    for index, row in tag.iterrows():
        # Berechnung der aktuellen Leistungsbilanz
        leistungsbilanz = row['Netzeinspeisung'] - row['Netzbezug']

        # Bedingung für netzdienliche Ladung des Speichers
        if leistungsbilanz > 0:
            # Berechnung der verfügbaren Ladeleistung
            ladeleistung = min(leistungsbilanz, tag_verbleibende_kapazitaet * (1 - max_ladezustand))

            # Bedingung für das Laden des Speichers
            if tag_soc < max_ladezustand:
                # Laden des Speichers
                tag_soc += ladeleistung / speicher_kapazitaet

                # Bedingung für maximalen L
