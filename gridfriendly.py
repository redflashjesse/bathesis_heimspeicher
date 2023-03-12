import imports_and_variables

# DataFrame aus Pickle-Datei laden
data = pd.read_pickle('documents/netz_pv_mit_speichersimulation_eigenverbrauch.pkl')

# Daten im df GridPowerIn, GridPowerOut,
# (speichergrößen abhänig) p_delta, soc_delta,
# current_soc (Betrachtung zu beginn der Minute),
# p_netzeinspeisung, p_netzbezug

def cal_grid_friendly():

        # Schleife durch jeden Tag im Jahr gehen
    for day in data['Timestamp'].dt.date.unique('D'):
        print("Datum:", day)

        # Schleife durch jede Minute des Tages gehen
        for _, row in data.loc[data['Timestamp'].dt.date == day].iterrows():
            print("Minute:", row['Timestamp'].time())
            print("GridPowerIn:", row['GridPowerIn'])
            print("GridPowerOut:", row['GridPowerOut'])

        # Wenn es 1440 Werte für den Tag gibt, Timestamp auf Mitternacht setzen
        if len(data.loc[data['Timestamp'].dt.date == day]) == 1440:
            data.loc[data['Timestamp'].dt.date == day, 'Timestamp'] = data.loc[
                data['Timestamp'].dt.date == day, 'Timestamp'].dt.floor('D')

    # Die ersten fünf Zeilen des modifizierten DataFrames anzeigen
    print(data.head())

    """
            if not row_optimized: # Todo hier fällt rein löschen der Beladeleistungen und neues entladen bestimmen
    
                if row[f'soc_delta_{speichergroesse}Wh_netzdienlich'] < 0: # check for negativ soc_delta
                    if soc_ist <= soc_min: # if the battery soc to low --> no output
                        soc_akt = soc_ist
                        p_delta = 0
                        soc_delta = 0
                    else:
                        soc_akt = soc_ist + row[f'soc_delta_{speichergroesse}Wh_netzdienlich']
                        pass #TODO Werte von delta belassen nur neuen soc berechnen
                            # mit berücksichtigung der gerenzen und danach die Leistung bestimmen
                else:
                    pass #TODO soc nicht ändern und delta werte auf null setzen
    
            if row_optimized:
                # check the conditions and if it possible change the values
                # todo check if einspeisung > p_delta + p_min_in else soc_delta new cal
    
                potenzial_soc = soc_akt + soc_delta
                if potenzial_soc <= soc_max:
                    pass # TODO laden und alle werte neu berechnen
                    # change values
                else:
                    pass # TODO delta werte auf null und werte beibehalten
                    # values remain
                 """
    return # df