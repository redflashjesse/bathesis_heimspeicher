import dash
import dash_bootstrap_components as dbc
from dash import html
from pandas.io.formats.style import coloring_args
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd
from main import *

# speichergroessen = main.speichergroessen
# print(f'{speichergroessen}')

speichergroesse = 12000 # speichergroessen[0]

# Load data
df = pd.read_pickle(
    f'C:/Users/EE/Documents/Petau/bathesis_heimspeicher/documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl')
# Leistungswerte von Wmin in Wh umrechnen
factor = 1  # or 60

#--- for speichergroesse in speichergroessen:

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

# values of stock
schwellenwert = 500  # 2/3 * df['GridPowerOut[Wh]'].max()
sum_pv_gen = (df['PowerGeneratedPV[Wh]'].sum() / 1000).round(2)
sum_einspeisung = (df['GridPowerOut[Wh]'].sum() / 1000).round(2)
pvdiketnutzung_kwh = sum_pv_gen - sum_einspeisung
sum_netzbezug = (df['GridPowerIn[Wh]'].sum() / 1000).round(2)
sum_netzleistung = sum_netzbezug + sum_einspeisung
autakie_ohne = (pvdiketnutzung_kwh / (df['GridPowerIn[Wh]'].sum() / 1000 + pvdiketnutzung_kwh)).round(3) * 100
anzahl_min_grenze_bestand = len(df[df['GridPowerOut[Wh]'] <= -schwellenwert])
# anzahl_min_einspeiseleistung_betand = len(df[df['GridPowerOut[Wh]'] <= -0])

summe_netzbezug_kWh = [f"Summe Netzbezug",
                       (f"{(sum_netzbezug)}kWh"),
                       "für das Jahr 2021"
                       ]
summe_netzeinspeisung_kWh = [f"Summe Netzeinspeisung", f"{(sum_einspeisung)}kWh", "für das Jahr 2021"]
summe_netzleistung_kWh_bestand = [f"Nettosumme der Leistung zum Netz ", f"{sum_netzleistung}kWh", "für das Jahr 2021"]
summe_pvertrag_kWh = [f"Summe PV Ertrag", f"{(sum_pv_gen)}kWh", "für das Jahr 2021"]
summe_pvdirketnutzung_kWh = [f"Summe PV Direktnutzung", f"{pvdiketnutzung_kwh}kWh", "für das Jahr 2021"]
autaktie_bestand = [f"Autaktie", f"{(autakie_ohne)} %", "für das Jahr 2021"]
spitzeneinspeisung_bestand = [
    f"Anzahl der Minuten zu denen eine Spitzenleistung über {schwellenwert} Wh einspeist wird",
    f"{(anzahl_min_grenze_bestand)}", "für das Jahr 2021"]

# values of own consumtion
sum_netzbezug_12000Wh_eigen = ((df['p_netzbezug_12000Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_netzeinspeisung_12000Wh_eigen = ((df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_netzleistung_12000Wh_eigen = ((df['p_netzleistung_12000Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_speicherleistung_12000Wh_eigen = ((df[df[f'p_delta_{speichergroesse}Wh_eigenverbrauch[Wh]'] > 0][
                                           f'p_delta_{speichergroesse}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_pvleistung_nutzung_12000Wh_eigen = (sum_netzbezug - sum_netzbezug_12000Wh_eigen) + pvdiketnutzung_kwh
autakie_12000Wh_eigen = (sum_pvleistung_nutzung_12000Wh_eigen / (df[
                                                                     f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch[Wh]'].sum() / 1000 + sum_pvleistung_nutzung_12000Wh_eigen)).round(
    5) * 100
anzahl_min_grenze_eigen = len(df[df['p_netzeinspeisung_12000Wh_eigenverbrauch[Wh]'] <= -schwellenwert])
# anzahl_min_einspeiseleistung_eigen = len(df[df[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch[Wh]'] <= -0,1])

summe_netzbezug_kWh_speichergroesse_Wh_eigenverbrauch = [f"Summe Netzbezug mit Speicher {speichergroesse}Wh",
                                                         f"{sum_netzbezug_12000Wh_eigen}kWh",
                                                         "eigenverbrauchsoptimiert"]
summe_netzeinspeisung_kWh_speichergroesse_Wh_eigenverbrauch = [
    f"Summe Netzeinspeisung mit Speicher {speichergroesse}Wh", f"{sum_netzeinspeisung_12000Wh_eigen}kWh",
    "eigenverbrauchsoptimiert"]
summe_netzleistung_kWh_speichergroesse_Wh_eigenverbrauch = [
    f"Nettosumme der Leistung zum Netz mit Speicher {speichergroesse}Wh", f"{sum_netzleistung_12000Wh_eigen}kWh",
    "eigenverbrauchsoptimiert"]
summe_nutzung_pv_mit_speichergroesse_Wh_eigenverbrauch = [
    f"Summe an eigengenutzter PV_Leistung mit Speicher {speichergroesse}Wh",
    f"{sum_pvleistung_nutzung_12000Wh_eigen.round(2)}kWh", "eigenverbrauchsoptimiert"]
summe_speicherleistung_kWh_speichergroesse_Wh_eigenverbrauch = [
    f"Summe Speicherleistung mit Speicher {speichergroesse}Wh", f"{sum_speicherleistung_12000Wh_eigen}kWh",
    "eigenverbrauchsoptimiert"]
autaktie_speichergroesse_Wh_eigenverbrauch = [f"Autaktiegrad mit Speicher {speichergroesse}Wh",
                                              f"{autakie_12000Wh_eigen} %", "eigenverbrauchsoptimiert"]
spitzeneinspeisung_eigenverbrauch = [
    f"Anzahl der Minuten zu denen eine Spitzenleistung über {schwellenwert} Wh einspeist wird mit Speicher",
    f"{(anzahl_min_grenze_eigen)}", "eigenverbrauchsoptimiert"]

# values of grid friendly
sum_netzbezug_12000Wh_netz = ((df['p_netzbezug_12000Wh_netzdienlich[Wh]'].sum() / 1000).round(2))
sum_netzeinspeisung_12000Wh_netz = ((df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]'].sum() / 1000).round(2))
sum_netzleistung_12000Wh_netz = ((df['p_netzleistung_12000Wh_netzdienlich[Wh]'].sum() / 1000).round(2))
sum_speicherleistung_12000Wh_netz = ((df[df[f'p_delta_{speichergroesse}Wh_netzdienlich[Wh]'] > 0][
                                          f'p_delta_{speichergroesse}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2))
sum_pvleistung_nutzung_12000Wh_netz = (sum_netzbezug - sum_netzbezug_12000Wh_netz) + pvdiketnutzung_kwh
autakie_12000Wh_netz = (sum_pvleistung_nutzung_12000Wh_netz / (df[
                                                                   f'p_netzbezug_{speichergroesse}Wh_netzdienlich[Wh]'].sum() / 1000 + sum_pvleistung_nutzung_12000Wh_netz)).round(
    5) * 100
anzahl_min_grenze_netz = len(df[df['p_netzeinspeisung_12000Wh_netzdienlich[Wh]'] <= -schwellenwert])
# anzahl_min_einspeiseleistung_netz = len(df[df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich[Wh]'] <= -0,1])

summe_netzbezug_kWh_speichergroesse_Wh_netzdienlich = [f"Summe Netzbezug mit Speicher {speichergroesse}Wh",
                                                       f"{sum_netzbezug_12000Wh_netz}kWh", "netzdienlich optimiert"]
summe_netzeinspeisung_kWh_speichergroesse_Wh_netzdienlich = [f"Summe Netzeinspeisung mit Speicher {speichergroesse}Wh",
                                                             f"{sum_netzeinspeisung_12000Wh_netz}kWh",
                                                             "netzdienlich optimiert"]
summe_netzleistung_kWh_speichergroesse_Wh_netzdienlich = [
    f"Nettosumme der Leistung zum Netz mit Speicher {speichergroesse}Wh", f"{sum_netzleistung_12000Wh_netz}kWh",
    "netzdienlich optimiert"]
# summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich = [f"Summe Speicherleistung mit Speicher {speichergroesse}Wh", f"{((df[df[f'p_delta_{speichergroesse}Wh_netzdienlich[Wh]'] > 0][f'p_delta_{speichergroesse}Wh_netzdienlich[Wh]'].sum()/1000).round(2))}kWh", "netzdienlich optimiert"]
summe_nutzung_pv_mit_speichergroesse_Wh_netzdienlich = [
    f"Summe an eigengenutzter PV_Leistung mit Speicher {speichergroesse}Wh",
    f"{sum_pvleistung_nutzung_12000Wh_netz}kWh", "netzdienlich optimiert"]
summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich = [
    f"Summe Speicherleistung mit Speicher {speichergroesse}Wh", f"{sum_speicherleistung_12000Wh_netz}kWh",
    "netzdienlich optimiert"]
autaktie_speichergroesse_Wh_netzdienlich = [f"Autaktiegrad mit Speicher {speichergroesse}Wh",
                                            f"{autakie_12000Wh_netz} %", "netzdienlich optimiert"]
spitzeneinspeisung_netzdienlich = [
    f"Anzahl der Minuten zu denen eine Spitzenleistung über {schwellenwert} Wh einspeist wird mit Speicher",
    f"{(anzahl_min_grenze_netz)}",
    f"netzdienlich optimiert"]  # bei {anzahl_min_einspeiseleistung_netz} Gesamtminuten Einspeisung"]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def create_card(title, content, text, color):
    card = dbc.Card(
        dbc.CardBody([html.H4(title, className="card-title"),
                html.Br(),
                html.H2(content, className="card-subtitle"),
                html.Br(),
                html.P(text, className="card-text"),
                html.Br(),]),
        color=color,  # "primary", "secondary", "success", "warning", "danger", "info", "light" und "dark".
        inverse=True
    )
    return card


card01 = create_card(summe_netzbezug_kWh[0],
                     summe_netzbezug_kWh[1],
                     summe_netzbezug_kWh[2],
                     "info")
card02 = create_card(summe_netzeinspeisung_kWh[0],
                     summe_netzeinspeisung_kWh[1],
                     summe_netzeinspeisung_kWh[2],
                     "info")
card03 = create_card(summe_netzleistung_kWh_bestand[0],
                     summe_netzleistung_kWh_bestand[1],
                     summe_netzleistung_kWh_bestand[2],
                     "info")
card04 = create_card(summe_pvertrag_kWh[0],
                     summe_pvertrag_kWh[1],
                     summe_pvertrag_kWh[2],
                     "info")
card05 = create_card(summe_pvdirketnutzung_kWh[0],
                     summe_pvdirketnutzung_kWh[1],
                     summe_pvdirketnutzung_kWh[2],
                     "info")
card06 = create_card(autaktie_bestand[0],
                     autaktie_bestand[1],
                     autaktie_bestand[2],
                     "info")
card07 = create_card(spitzeneinspeisung_bestand[0],
                     spitzeneinspeisung_bestand[1],
                     spitzeneinspeisung_bestand[2],
                     "info")

card11 = create_card(summe_netzbezug_kWh_speichergroesse_Wh_eigenverbrauch[0],
                     summe_netzbezug_kWh_speichergroesse_Wh_eigenverbrauch[1],
                     summe_netzbezug_kWh_speichergroesse_Wh_eigenverbrauch[2],
                     "primary")
card12 = create_card(summe_netzeinspeisung_kWh_speichergroesse_Wh_eigenverbrauch[0],
                     summe_netzeinspeisung_kWh_speichergroesse_Wh_eigenverbrauch[1],
                     summe_netzeinspeisung_kWh_speichergroesse_Wh_eigenverbrauch[2],
                     "primary")
card13 = create_card(summe_netzleistung_kWh_speichergroesse_Wh_eigenverbrauch[0],
                     summe_netzleistung_kWh_speichergroesse_Wh_eigenverbrauch[1],
                     summe_netzleistung_kWh_speichergroesse_Wh_eigenverbrauch[2],
                     "primary")
card14 = create_card(summe_speicherleistung_kWh_speichergroesse_Wh_eigenverbrauch[0],
                     summe_speicherleistung_kWh_speichergroesse_Wh_eigenverbrauch[1],
                     summe_speicherleistung_kWh_speichergroesse_Wh_eigenverbrauch[2],
                     "primary")
card15 = create_card(summe_nutzung_pv_mit_speichergroesse_Wh_eigenverbrauch[0],
                     summe_nutzung_pv_mit_speichergroesse_Wh_eigenverbrauch[1],
                     summe_nutzung_pv_mit_speichergroesse_Wh_eigenverbrauch[2],
                     "primary")
card16 = create_card(autaktie_speichergroesse_Wh_eigenverbrauch[0],
                     autaktie_speichergroesse_Wh_eigenverbrauch[1],
                     autaktie_speichergroesse_Wh_eigenverbrauch[2],
                     "primary")
card17 = create_card(spitzeneinspeisung_eigenverbrauch[0],
                     spitzeneinspeisung_eigenverbrauch[1],
                     spitzeneinspeisung_eigenverbrauch[2],
                     "primary")

card21 = create_card(summe_netzbezug_kWh_speichergroesse_Wh_netzdienlich[0],
                     summe_netzbezug_kWh_speichergroesse_Wh_netzdienlich[1],
                     summe_netzbezug_kWh_speichergroesse_Wh_netzdienlich[2],
                     "secondary")
card22 = create_card(summe_netzeinspeisung_kWh_speichergroesse_Wh_netzdienlich[0],
                     summe_netzeinspeisung_kWh_speichergroesse_Wh_netzdienlich[1],
                     summe_netzeinspeisung_kWh_speichergroesse_Wh_netzdienlich[2],
                     "secondary")
card23 = create_card(summe_netzleistung_kWh_speichergroesse_Wh_netzdienlich[0],
                     summe_netzleistung_kWh_speichergroesse_Wh_netzdienlich[1],
                     summe_netzleistung_kWh_speichergroesse_Wh_netzdienlich[2],
                     "secondary")
card24 = create_card(summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich[0],
                     summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich[1],
                     summe_speicherleistung_kWh_speichergroesse_Wh_netzdienlich[2],
                     "secondary")
card25 = create_card(summe_nutzung_pv_mit_speichergroesse_Wh_netzdienlich[0],
                     summe_nutzung_pv_mit_speichergroesse_Wh_netzdienlich[1],
                     summe_nutzung_pv_mit_speichergroesse_Wh_netzdienlich[2],
                     "secondary")
card26 = create_card(autaktie_speichergroesse_Wh_netzdienlich[0],
                     autaktie_speichergroesse_Wh_netzdienlich[1],
                     autaktie_speichergroesse_Wh_netzdienlich[2],
                     "secondary")
card27 = create_card(spitzeneinspeisung_netzdienlich[0],
                     spitzeneinspeisung_netzdienlich[1],
                     spitzeneinspeisung_netzdienlich[2],
                     "secondary")

width = 1, 5

app.layout = html.Div([
    dbc.Row([
        dbc.Col(card01, width=width),
        dbc.Col(card02, width=width),
        dbc.Col(card03, width=width),
        dbc.Col(card04, width=width),
        dbc.Col(card05, width=width),
        dbc.Col(card06, width=width),
        dbc.Col(card07, width=width),
    ]),
    dbc.Row([
        dbc.Col(card11, width=width),
        dbc.Col(card12, width=width),
        dbc.Col(card13, width=width),
        dbc.Col(card14, width=width),
        dbc.Col(card15, width=width),
        dbc.Col(card16, width=width),
        dbc.Col(card17, width=width),
    ]),
    dbc.Row([
        dbc.Col(card21, width=width),
        dbc.Col(card22, width=width),
        dbc.Col(card23, width=width),
        dbc.Col(card24, width=width),
        dbc.Col(card25, width=width),
        dbc.Col(card26, width=width),
        dbc.Col(card27, width=width),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)