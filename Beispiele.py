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
