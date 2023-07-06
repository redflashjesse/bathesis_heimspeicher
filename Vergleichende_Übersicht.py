import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table
import pandas as pd
import main
from pprint import pprint
import os

speichergroessen = main.speichergroessen
#                   list(range(6_000, # start
#                               30_000, # end
#                               2_000)) # step # in Wh

# size = speichergroessen[10]
schwellenwert = 930/2

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

    return df


df = factorize_df(df)


# method for creating single cards
def create_card(list, color):
    card = dbc.Card(
        dbc.CardBody([
            html.H4(list[0], className="card-title", style={'font-size': '22px'}),
            html.Br(),
            html.H2(list[1], className="card-subtitle", style={'font-size': '26px'}),
            html.Br(),
            html.P(list[2], className="card-text", style={'font-size': '16px'}),
            html.Br(),
        ]),
        color=color,
        inverse=True,
        style={'width': '300px', 'height': '260px'}
    )
    return card


def calc_base(df):
    base_values = []
    # calc base values
    sum_pv_gen = (df['PowerGeneratedPV[Wh]'].sum() / 1000).round(2)
    sum_einspeisung = (df[df['GridPowerOut[Wh]'] <= -.1]['GridPowerOut[Wh]'].sum() / 1000).round(2)
    pvdirektnutzung_kwh_bestand = -(sum_einspeisung-sum_pv_gen).round(2)
    sum_netzbezug = (df['GridPowerIn[Wh]'].sum() / 1000).round(2)
    sum_netzleistung = sum_netzbezug + sum_einspeisung
    autarkie_ohne = (pvdirektnutzung_kwh_bestand / (sum_netzbezug+ pvdirektnutzung_kwh_bestand)).round(4) * 100
    anzahl_min_grenze_bestand = len(df[df['GridPowerOut[Wh]'] <= -schwellenwert])
    anzahl_min_einspeisung_bestand = len(df[df['GridPowerOut[Wh]'] <= -.1])
    durchnittliche_einspeisung_bestand = (df[df['GridPowerOut[Wh]'] <= -.1]['GridPowerOut[Wh]'].sum()
                                          / anzahl_min_einspeisung_bestand).round(2)
    sum_speicherleistung = f'---'
    # search for einspeisung aprox above schwellenwert
    durchnittliche_einspeisung_spitzen_bestand = (df[df['GridPowerOut[Wh]'] <= -schwellenwert]['GridPowerOut[Wh]'].sum() / anzahl_min_grenze_bestand).round(2)
    base_values = [sum_einspeisung, pvdirektnutzung_kwh_bestand, sum_netzbezug,
                   sum_netzleistung, sum_speicherleistung, autarkie_ohne,
                   anzahl_min_grenze_bestand, anzahl_min_einspeisung_bestand,
                   durchnittliche_einspeisung_bestand, durchnittliche_einspeisung_spitzen_bestand]

    # create cards for base values
    summe_netzbezug_kWh = [f"Summe Netzbezug",
                           (f"{(sum_netzbezug)}kWh"),
                           "für das Jahr 2021"]
    summe_netzeinspeisung_kWh = [f"Summe Netzeinspeisung", f"{(sum_einspeisung)}kWh", "für das Jahr 2021"]
    summe_netzleistung_kWh_bestand = [f"Nettosumme der Leistung zum Netz ", f"{sum_netzleistung}kWh",
                                      "für das Jahr 2021"]
    summe_pvertrag_kWh = [f"Summe PV Ertrag", f"{(sum_pv_gen)}kWh", "für das Jahr 2021"]
    summe_pvdirektnutzung_kWh = [f"Summe PV Direktnutzung", f"{pvdirektnutzung_kwh_bestand}kWh", "für das Jahr 2021"]
    autarkie_bestand = [f"Autarkie", f"{(autarkie_ohne)} %", "für das Jahr 2021"]
    spitzeneinspeisung_bestand = [
        f"Anzahl der Minuten zu denen eine Spitzenleistung über {schwellenwert} Wh einspeist wird",
        f"{(anzahl_min_grenze_bestand)}", "für das Jahr 2021"]

    card01 = create_card(summe_netzbezug_kWh, base_color)
    card02 = create_card(summe_netzeinspeisung_kWh, base_color)
    card03 = create_card(summe_netzleistung_kWh_bestand, base_color)
    card04 = create_card(summe_pvertrag_kWh, base_color)
    card05 = create_card(summe_pvdirektnutzung_kWh, base_color)
    card06 = create_card(autarkie_bestand, base_color)
    card07 = create_card(spitzeneinspeisung_bestand, base_color)
    return card01, card02, card03, card04, card05, card06, card07, base_values


card01, card02, card03, card04, card05, card06, card07, base_values = calc_base(df)


def calc_cards(df, speichergroessen, base_values):
    calc_eigen = {}
    columns = ['Kenngrößen','Bestand (ohne Speicher)',]
    for size in speichergroessen:
        columns += f'{size/1000}kWh_eigenverbrauch', f'{size/1000}kWh_netzdienlich'
    table_df = pd.DataFrame(columns= columns)
    table_df['Kenngrößen'] = ['Summe Netzeinspeisung [kWh]', 'Summe selbstgenutzer PV-Leistung [kWh]', 'Summe Netzbezug [kWh]',
                            'Summe Netzleistung [kWh]', 'Summe Speicherleistung [kWh]', 'Erreichte Autarkie [%]',
                            'Anzahl min Einspeisung < Schwellenwert', 'Anzahl min Einspeisung',
                            'durchschnittliche Leistung pro Minute bei Einspeisung [Wh]', 'durchschnittliche Leistung pro Minute bei Einspeisung > Schwellenwert [Wh]'
                            ]

    table_df['Bestand (ohne Speicher)'] = base_values

    # calculation of values for speichergroessen
    for size in speichergroessen:
        values = {}
        sum_netzbezug = (df['GridPowerIn[Wh]'].sum() / 1000).round(2)
        sum_pv_gen = (df['PowerGeneratedPV[Wh]'].sum() / 1000).round(2)
        sum_einspeisung = (df['GridPowerOut[Wh]'].sum() / 1000).round(2)
        pvdirektnutzung_kwh_bestand = -(sum_einspeisung - sum_pv_gen).round(2)

        sum_einspeisung_eigen = (df[df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'] < -.1]
                                 [f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2)

        pvdirektnutzung_kwh_eigen = (pvdirektnutzung_kwh_bestand+(-sum_einspeisung + sum_einspeisung_eigen)).round(2)

        sum_netzbezug_eigen = ((df[f'p_netzbezug_{size}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2)).round(2)
        sum_netzeinspeisung_eigen = (
            (df[df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'] <-.1][f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'].sum() / 1000)).round(2)
        sum_netzleistung_eigen = ((df[f'p_netzleistung_{size}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2)).round(2)
        sum_speicherleistung_eigen = ((df[df[f'p_delta_{size}Wh_eigenverbrauch[Wh]'] > 0][
                                           f'p_delta_{size}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2)).round(2)
        sum_pvleistung_nutzung_eigen = ((sum_netzbezug - sum_netzbezug_eigen) + pvdirektnutzung_kwh_eigen).round(2)
        autarkie_eigen = ((sum_pvleistung_nutzung_eigen /
                           (sum_netzbezug_eigen + sum_pvleistung_nutzung_eigen)) * 100).round(2)
        anzahl_min_grenze_eigen = len(df[df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'] <= -schwellenwert])
        anzahl_min_einspeisung_eigen = len(df[df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'] < -.1])
        durchschnitt_einspeisung_eigen = (df[df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'] < -.1][f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'].sum()
                                          /anzahl_min_einspeisung_eigen).round(2)
        # search for einspeisung approx above schwellenwert
        durchschnitt_einspeisung_spitzen_eigen = (df[df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]']
                                                     <= -schwellenwert][f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'].sum()
                                                     /anzahl_min_grenze_eigen).round(2)

        table_df[f'{size/1000}kWh_eigenverbrauch'] = [sum_netzeinspeisung_eigen, pvdirektnutzung_kwh_eigen, sum_netzbezug_eigen,
                                                      sum_netzleistung_eigen, sum_speicherleistung_eigen, autarkie_eigen,
                                                      anzahl_min_grenze_eigen, anzahl_min_einspeisung_eigen,
                                                      durchschnitt_einspeisung_eigen, durchschnitt_einspeisung_spitzen_eigen
                                                      ]

        summe_netzbezug_kWh_Wh_eigenverbrauch = [f"Summe Netzbezug",  # mit Speicher {size}Wh",
                                                 f"{sum_netzbezug_eigen}kWh",
                                                 "eigenverbrauchsoptimiert"]
        values['summe_netzbezug_kWh_Wh_eigenverbrauch'] = summe_netzbezug_kWh_Wh_eigenverbrauch
        summe_netzeinspeisung_kWh_Wh_eigenverbrauch = [
            f"Summe Netzeinspeisung",  # mit Speicher {size}Wh",
            f"{sum_netzeinspeisung_eigen}kWh",
            "eigenverbrauchs optimiert"]
        values['summe_netzeinspeisung_kWh_Wh_eigenverbrauch'] = summe_netzeinspeisung_kWh_Wh_eigenverbrauch

        summe_netzleistung_kWh_Wh_eigenverbrauch = [
            f"Nettosumme der Leistung zum Netz",  # mit Speicher {size}Wh",
            f"{sum_netzleistung_eigen}kWh",
            "eigenverbrauchs optimiert"]
        values['summe_netzleistung_kWh_Wh_eigenverbrauch'] = summe_netzleistung_kWh_Wh_eigenverbrauch

        summe_nutzung_pv_mit_Wh_eigenverbrauch = [
            f"Summe an eigengenutzter PV_Leistung",  # mit Speicher {size}Wh",
            f"{sum_pvleistung_nutzung_eigen.round(2)}kWh", "eigenverbrauchs optimiert"]
        values['summe_nutzung_pv_mit_Wh_eigenverbrauch'] = summe_nutzung_pv_mit_Wh_eigenverbrauch

        summe_speicherleistung_kWh_Wh_eigenverbrauch = [
            f"Summe Speicherleistung",  # mit Speicher {size}Wh",
            f"{sum_speicherleistung_eigen}kWh",
            "eigenverbrauchs optimiert"]
        values['summe_speicherleistung_kWh_Wh_eigenverbrauch'] = summe_speicherleistung_kWh_Wh_eigenverbrauch

        autarkie_eigenverbrauch = [f"Autarkiegrad",  # mit Speicher {size}Wh",
                                   f"{autarkie_eigen} %", "eigenverbrauchs optimiert"]
        values['autarkie_Wh_eigenverbrauch'] = autarkie_eigenverbrauch
        spitzeneinspeisung_eigenverbrauch = [
            f"Anzahl der Minuten, zu denen eine Spitzenleistung über {schwellenwert} Wh einspeist wird mit Speicher",
            f"{anzahl_min_grenze_eigen}", "eigenverbrauchs optimiert"]
        values['spitzeneinspeisung_eigenverbrauch'] = spitzeneinspeisung_eigenverbrauch
        calc_eigen[f'{size}_Wh_Eigenverbrauch'] = values

    calc_netz = {}
    for size in speichergroessen:
        # values of grid friendly
        values = {}
        # sum of netzdienlich
        sum_netzbezug_netz = (df[f'p_netzbezug_{size}Wh_netzdienlich[Wh]'].sum() / 1000).round(2)
        sum_netzeinspeisung_netz = (df[df[f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'] < .1]
                                     [f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'].sum() / 1000).round(2)
        sum_netzleistung_netz = (df[f'p_netzleistung_{size}Wh_netzdienlich[Wh]'].sum() / 1000).round(2)
        sum_speicherleistung_netz = ((df[df[f'p_delta_{size}Wh_netzdienlich[Wh]'] > 0][
                                          f'p_delta_{size}Wh_netzdienlich[Wh]'].sum() / 1000)).round(2)
        #         pvdirektnutzung_kwh_bestand = -(sum_einspeisung - sum_pv_gen).round(2)
        #
        #         sum_einspeisung_eigen = (df[df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'] < -.1]
        #                                  [f'p_netzeinspeisung_{size}Wh_eigenverbrauch[Wh]'].sum() / 1000).round(2)
        #
        #         pvdirektnutzung_kwh_eigen = (pvdirektnutzung_kwh_bestand+(-sum_einspeisung + sum_einspeisung_eigen)).round(2)
        pvdirektnutzung_kwh_netz = (pvdirektnutzung_kwh_bestand+(-sum_einspeisung+sum_netzeinspeisung_netz)).round(2)

        sum_pvleistung_nutzung_netz = ((sum_netzbezug - sum_netzbezug_netz) + pvdirektnutzung_kwh_netz).round(2)
        autarkie_netz = ((sum_pvleistung_nutzung_netz / (sum_netzbezug_netz + sum_pvleistung_nutzung_netz)) * 100).round(2)
        anzahl_min_grenze_netz = len(df[df[f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'] <= -schwellenwert])
        anzahl_min_einspeisung_netz = len(df[df[f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'] < -.1])
        durchschnitt_einspeisung_netz = (df[df[f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'] <= -0.1][f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'].sum()
                                         / anzahl_min_einspeisung_netz).round(2)
        # search for the einspeisung values above the schwellenwert
        durchschnitt_einspeisung_spiten_netz = (df[df[f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'] <= -schwellenwert]
                                                [f'p_netzeinspeisung_{size}Wh_netzdienlich[Wh]'].sum() / anzahl_min_grenze_netz).round(2)

        table_df[f'{size/1000}kWh_netzdienlich'] = [sum_netzeinspeisung_netz, pvdirektnutzung_kwh_netz, sum_netzbezug_netz,
                                                    sum_netzleistung_netz, sum_speicherleistung_netz,
                                                    autarkie_netz, anzahl_min_grenze_netz, anzahl_min_einspeisung_netz,
                                                    durchschnitt_einspeisung_netz, durchschnitt_einspeisung_spiten_netz,
                                                    ]
        # valuecards of grid friendly
        summe_netzbezug_kWh_Wh_netzdienlich = [f"Summe Netzbezug",  # mit Speicher {size}Wh",
                                               f"{sum_netzbezug_netz}kWh", "netzdienlich optimiert"]
        values[f'summe_netzbezug_kWh_Wh_netzdienlich'] = summe_netzbezug_kWh_Wh_netzdienlich
        summe_netzeinspeisung_kWh_Wh_netzdienlich = [
            f"Summe Netzeinspeisung",  # mit Speicher {size}Wh",
            f"{sum_netzeinspeisung_netz}kWh",
            "netzdienlich optimiert"]
        values[f'summe_netzeinspeisung_kWh_Wh_netzdienlich'] = summe_netzeinspeisung_kWh_Wh_netzdienlich
        summe_netzleistung_kWh_Wh_netzdienlich = [
            f"Nettosumme der Leistung zum Netz",  # mit Speicher {size}Wh",
            f"{sum_netzleistung_netz}kWh",
            "netzdienlich optimiert"]
        values['summe_netzleistung_kWh_Wh_netzdienlich'] = summe_netzleistung_kWh_Wh_netzdienlich

        summe_nutzung_pv_Wh_netzdienlich = [
            f"Summe an eigengenutzter PV_Leistung",  # mit Speicher {size}Wh",
            f"{sum_pvleistung_nutzung_netz}kWh", "netzdienlich optimiert"]
        values['summe_nutzung_pv_Wh_netzdienlich'] = summe_nutzung_pv_Wh_netzdienlich

        summe_speicherleistung_kWh_Wh_netzdienlich = [
            f"Summe Speicherleistung",  # mit Speicher {size}Wh",
            f"{sum_speicherleistung_netz}kWh",
            "netzdienlich optimiert"]
        values['summe_speicherleistung_kWh_Wh_netzdienlich'] = summe_speicherleistung_kWh_Wh_netzdienlich

        autarkie_Wh_netzdienlich = [f"Autarkiegrad mit Speicher {size}Wh",
                                    f"{autarkie_netz} %", "netzdienlich optimiert"]
        values['autarkie_Wh_netzdienlich'] = autarkie_Wh_netzdienlich

        spitzeneinspeisung_netzdienlich = [
            f"Anzahl der Minuten zu denen eine Spitzenleistung über {schwellenwert} Wh einspeist wird mit Speicher",
            f"{anzahl_min_grenze_netz}",
            f"netzdienlich optimiert"]

        values['spitzeneinspeisung_netzdienlich'] = spitzeneinspeisung_netzdienlich
        # add values to dict
        calc_netz[f'{size}_Wh_Netzdienlich'] = values

    return calc_eigen, calc_netz, table_df


calc_eigen, calc_netz, table_df = calc_cards(df, speichergroessen, base_values)

# table_df to html  and save as html file
save_path = 'Kenngrößen_Tabelle.html'
table_df.to_html(save_path, index=False, classes='table table-striped table-hover', justify='center',)
def save_table_as_html(table_df):
    # Pfad zum Ordner "grafische_Ergebnisse"
    folder_path = "grafische_Ergebnisse"

    # Sicherstellen, dass der Ordner vorhanden ist
    os.makedirs(folder_path, exist_ok=True)

    # Pfad zur HTML-Datei innerhalb des Ordners
    save_path = os.path.join(folder_path, "Kenngrößen_Tabelle.html")
    css = """
    <style>
        .table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background-color: #f2f2f2;  /* Hintergrundfarbe der Überschriften */
            font-weight: bold;
        }

        td:first-child {
            font-weight: bold;  /* Abhebung der ersten Spalte */
        }
    </style>
    """

    html_content = css + table_df.to_html(index=False, classes='table table-striped table-hover', justify='center', )

    with open(save_path, 'w') as f:
        f.write(html_content)
    return html_content
save_table_as_html(table_df)

table_html = html.Div([
        html.H2('Vergleich der Kenngrößen der unterschiedlichen Speicher'),
        html.Div([html.Table([html.Tr([html.Th(col) for col in table_df.columns])] +
                             [html.Tr([html.Td(table_df.iloc[i][col]) for col in table_df.columns])
                              for i in range(len(table_df))])],
                 style={'overflowX': 'scroll'})
    ])
# create dashboards
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

width = 0.2, 1

# name of the app
app.title = "bathesis-heimspeicher"

# define the dash title
title = html.Div(html.H1("Vergleich von simulierten Speichern für ein Quartier"),
                 style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30})

# define the dash content
base = html.Div([
    dbc.Row([
        dbc.Col(card01, width=width),
        dbc.Col(card02, width=width),
        dbc.Col(card03, width=width),
        dbc.Col(card04, width=width),
        dbc.Col(card05, width=width),
        dbc.Col(card06, width=width),
        dbc.Col(card07, width=width),
    ]),
])

# subtabs = dcc.Tabs([
#   dcc.Tab(label='Eigenverbrauch', children=eigen),
#  dcc.Tab(label='Netzdienlich', children=netzdienlich),
# ])

subtabs = []
sub_eigen = []
sub_netz = []
#liste_pos = [0, 3, 6, 9, 12]
#speichergroessen = [speichergroessen[pos] for pos in liste_pos]
for size in speichergroessen:
    # calc_eigen[f'{size}_Wh_Eigenverbrauch'] = calc_eigen
    # calc_netz[f'{size}_Wh_Netzdienlich'] = calc_netz
    card11 = create_card(calc_eigen[f'{size}_Wh_Eigenverbrauch']['summe_netzbezug_kWh_Wh_eigenverbrauch'], eigen_color)
    card12 = create_card(calc_eigen[f'{size}_Wh_Eigenverbrauch']['summe_netzeinspeisung_kWh_Wh_eigenverbrauch'],
                         eigen_color)
    card13 = create_card(calc_eigen[f'{size}_Wh_Eigenverbrauch']['summe_netzleistung_kWh_Wh_eigenverbrauch'],
                         eigen_color)
    card14 = create_card(calc_eigen[f'{size}_Wh_Eigenverbrauch']['summe_speicherleistung_kWh_Wh_eigenverbrauch'],
                         eigen_color)
    card15 = create_card(calc_eigen[f'{size}_Wh_Eigenverbrauch']['summe_nutzung_pv_mit_Wh_eigenverbrauch'], eigen_color)
    card16 = create_card(calc_eigen[f'{size}_Wh_Eigenverbrauch']['autarkie_Wh_eigenverbrauch'], eigen_color)
    card17 = create_card(calc_eigen[f'{size}_Wh_Eigenverbrauch']['spitzeneinspeisung_eigenverbrauch'], eigen_color)

    card21 = create_card(calc_netz[f'{size}_Wh_Netzdienlich']['summe_netzbezug_kWh_Wh_netzdienlich'], netz_color)
    card22 = create_card(calc_netz[f'{size}_Wh_Netzdienlich']['summe_netzeinspeisung_kWh_Wh_netzdienlich'], netz_color)
    card23 = create_card(calc_netz[f'{size}_Wh_Netzdienlich']['summe_netzleistung_kWh_Wh_netzdienlich'], netz_color)
    card24 = create_card(calc_netz[f'{size}_Wh_Netzdienlich']['summe_speicherleistung_kWh_Wh_netzdienlich'], netz_color)
    card25 = create_card(calc_netz[f'{size}_Wh_Netzdienlich']['summe_nutzung_pv_Wh_netzdienlich'], netz_color)
    card26 = create_card(calc_netz[f'{size}_Wh_Netzdienlich']['autarkie_Wh_netzdienlich'], netz_color)
    card27 = create_card(calc_netz[f'{size}_Wh_Netzdienlich']['spitzeneinspeisung_netzdienlich'], netz_color)

    eigen = html.Div([
        dbc.Row([
            dbc.Col(card11, width=width),
            dbc.Col(card12, width=width),
            dbc.Col(card13, width=width),
            dbc.Col(card14, width=width),
            dbc.Col(card15, width=width),
            dbc.Col(card16, width=width),
            dbc.Col(card17, width=width),
        ]),
    ])

    netzdienlich = html.Div([
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
    sub_eigen=(dcc.Tab(label='Eigenverbrauch', children=eigen))
    sub_netz=(dcc.Tab(label='Netzdienlich', children=netzdienlich))
    subtabs.append(dcc.Tab(label=f'Speicher mit {size/1000} kWh',
                           children=[dcc.Tabs([
                                        #html.Br(),
                                        #html.H1(f'Kenngrößen mit einem {size/1000}kWh Speicher'),
                                        dcc.Tab(label='Eigenverbrauch', children=eigen),
                                        dcc.Tab(label='Netzdienlich', children=netzdienlich),
                                     ])
                                    ]
    ))

print(f'{len(speichergroessen)=}')
# table_df transponieren
# table_df = table_df.transpose()
# erstelle eine Tabelle mit den Kenngrößen
kenngroessen_table = html.Div([
    html.H1('Kenngrößen aller Speichergrößen'),
    html.Div([html.Table([html.Tr([html.Th(col) for col in table_df.columns])] +
                             [html.Tr([html.Td(table_df.iloc[i][col]) for col in table_df.columns])
                              for i in range(len(table_df))])],
                 style={'overflowX': 'scroll'})
    ])

tabs = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Vergleich ohne Speicher', children=base),
        dcc.Tab(label='Übersicht Tabelle', children=kenngroessen_table),
        *subtabs,
    ])
])
app.layout = html.Div([
    title,
    tabs,
    #kenngroessen_table
])

app.run_server(debug=True)
