# Imports
import math
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random as rd
import glob
from matplotlib.ticker import AutoLocator
from matplotlib.lines import Line2D
import matplotlib.lines as mlines

# set dpi globally
plt.rcParams['savefig.dpi'] = 500


def main():
    """
    Responsible for running everything sequentially, main has also the option to jump over some calculation and get
    some csv data, by setting values to false or true
    """
    read_original_data = False  # set up if data csv are availabel, which been calculated before or the calculation
    # runs with the basis data
    reduction_through_pv_sale = True  # set up if the calculation runs with co2_reduction_through_pv_sale or not
    only_plot = False # true - readin allready calculated and save datas from pre. runs and plot thoose data,
    # false - runs through all funktions
    plot_without_bars = True # switsh off bar in all plots
    simulate_new_sizes = True # if there are new setups at the sizes of batteries
    print(f'{simulate_new_sizes=}')
    speichergroessen = list(range(500,  # start
                                  10_000 + 1,  # end
                                  500))  # step  # in Wh
    soc_start = None

    if not only_plot:
        print("--- Program Start ---")
        print("--- Reading Inputs ---")

        if read_original_data:
            # Read OG Data
            print("--- Reading netz_pv ---")
            netz_pv = read_pv_netz_combined()
            print("--- Save ReadIns ---")
            netz_pv.to_csv(f'documents/netz_pv.csv')

        if not read_original_data:
            # Read saved Data instead of OG
            netz_pv = pd.read_csv(f'documents/netz_pv.csv')
            # print(len(netz_pv))
            # drops all identical timestamps, can lead to missing timestamps in the end
            netz_pv.drop_duplicates(subset='Timestamp',
                                    keep='first',
                                    inplace=True,
                                    ignore_index=False)
            # print(len(netz_pv))
            # set timestamp as index
            netz_pv.set_index('Timestamp', inplace=True)

            # Dropping last n rows using drop (new borders for the time shift, had to cut the first and last hour)
            netz_pv.drop(netz_pv.tail(88).index,
                         inplace=True)

        # Read OG Data
        if read_original_data:
            print("--- Reading Strommix ---")
            mix_de = read_modbus_strommix()

            print("--- Save ReadIns ---")
            mix_de.to_csv(f'documents/mix_de.csv')

        print("--- Reading Input Strommix ---")
        mix_de = pd.read_csv(f'documents/mix_de.csv')
        # set timestamp as index
        mix_de.set_index('Timestamp', inplace=True)
        mix_de = mix_de.iloc[60:, :]
        # print(mix.head(1))
        # print(mix.tail(1))
        # print(len(mix))

        print("--- Reading CO2-Index ---")
        co2_index = read_co2_index()

        read_original_data = True

        print("--- Calculation Strommix CO2 ---")
        if read_original_data:
            solution_quartier_strommix = cal_co2_grid(df=netz_pv,
                                                      strommix=mix_de,
                                                      co2_werte=co2_index)
            print("--- Save Calculation Strommix CO2  ---")
            solution_quartier_strommix.to_csv(f'documents/calculation_quartier_strommix.csv')

        # colums of calculation_quartier_strommix: Timestamp,PowerGeneratedPV,PowerOutputPV,GridPowerIn,GridPowerOut,
        # co2_emission_per_kwh,co2_emission_grid,em_reduction_through_sell

        if not read_original_data:
            solution_quartier_strommix = pd.read_csv(f'documents/calculation_quartier_strommix.csv')
            # set timestamp as index
            solution_quartier_strommix.set_index('Timestamp', inplace=True)

            # print(solution_df.head(1))

        if read_original_data:
            print("--- Calculation PV Eigennutzung ---")
            calculation_eigennutzung = cal_co2_pv_eigennutzung(netz_pv=solution_quartier_strommix,
                                                               co2_werte=co2_index,
                                                               reduction_through_pv_sale=reduction_through_pv_sale)

            # columns of calculation_eigennutzung: Timestamp,PowerGeneratedPV,PowerOutputPV,GridPowerIn,GridPowerOut,
            # co2_emission_per_kwh,co2_emission_grid,em_reduction_through_sell,co2_emission_internal,emission_total

            print("--- Save Calculation PV Eigennutzung  ---")
            calculation_eigennutzung.to_csv(f'documents/calculation_eigennutzung.csv')

        if not read_original_data:
            solution_df = pd.read_csv(f'documents/calculation_eigennutzung.csv')

        print(f'{simulate_new_sizes=}')

        if simulate_new_sizes:
            print("--- Simulation Batterie ---")
            calculation_eigennutzung = pd.read_csv(f'documents/calculation_eigennutzung.csv')
            # set timestamp as index
            calculation_eigennutzung.set_index('Timestamp', inplace=True)

            for size in speichergroessen:
                print(f"--- Simulation Batterie mit {size} Wh---")
                batterypower_df = cal_battery(netz_pv=calculation_eigennutzung,
                                              soc_start=soc_start,
                                              speichergroesse=size)

            print(f"--- Save Results for {speichergroessen} as battery sizes---")
            batterypower_df.to_csv(f'documents/simulated_power_for_storagesize.csv')

        if not simulate_new_sizes:
            print("--- Read the calculation of the reduction of emissions and network performance ---")
            batterypower_df = pd.read_csv(f'documents/simulated_power_for_storagesize.csv')
            # set timestamp as index
            batterypower_df.set_index('Timestamp', inplace=True)

        if simulate_new_sizes:
            print("--- Simulated CO2 for all sizes ---")
            # variant with emission for the storage calculated by cycles
            emission_df = cal_emission_for_each_battery_variant(df=batterypower_df,
                                                                speichergroessen=speichergroessen,
                                                                co2_werte=co2_index,
                                                                reduction_through_pv_sale=reduction_through_pv_sale)
            print("--- Save Simulated CO2 for all sizes ---")
            emission_df.to_csv(f'documents/simulated_storage_emission.csv')
            print(emission_df.columns.values.tolist())

        if not simulate_new_sizes:
            print("--- Read In Simulated CO2 for all sizes ---")
            emission_df = pd.read_csv(f'documents/simulated_storage_emission.csv')
            emission_df.set_index('Timestamp', inplace=True)

        assert len(emission_df) > 0

    only_plot = True
    if only_plot:
        print("--- Read In Simulated CO2 for all sizes ---")
        emission_df = pd.read_csv(f'documents/simulated_storage_emission.csv')
        emission_df.set_index('Timestamp', inplace=True)
        # print("--- Plot: Emission by variant ---")
        # plot_emission_per_minute(df=emission_df,
        #                          speichergroessen=speichergroessen)

        print("--- Plot: Compare emissions by battery size ---")
        plot_compare_emission_reduction_btw_batt_size(df=emission_df,
                                                      plot_without_bars=plot_without_bars,
                                                      speichergroessen=speichergroessen)

        print("--- Plot: Savings by Battery size ---")
        plot_potential_co2_savings(df=emission_df,
                                   plot_without_bars=plot_without_bars,
                                   speichergroessen=speichergroessen)
        print("--- Plot: Ratio ---")
        plot_potential_co2_savings_ratio(df=emission_df,
                                         plot_without_bars=plot_without_bars,
                                         speichergroessen=speichergroessen)


def read_modbus_pv(filename):
    """
    Daten aus dem Ordner PV-Anlage an df übergeben und den Timestamp als Index setzen.
    Die relevanten Daten (Active power +&-) werden an ein df übergeben, übrige Daten werden nicht weiter berücksichtigt.
    :rtype: object
    :param filename: Name of the file that serves as input. Format : .csv
    :return: Dataframe
    """
# TODO einlesen der Leistungswerte, die Umrechnung auf eine Wh ist noch nicht erfolgt, jeden Wert mit 1/60 multiplizieren
    df = pd.read_csv(f'{filename}', header=1, sep=';')  # read in
    df = df.iloc[1:]  # delete caption
    df = df.reset_index(drop=True)  # index starts with 0
    # transforming unix timestamp to Pandas Timestamp
    df['Timestamp'] = pd.to_datetime(df['UNIX-Timestamp'], unit='s',
                                     origin='unix').round('min') + timedelta(hours=2)
    # select only 'Timestamp', 'Active power+ PV', 'Active power- PV'
    df = df[['Timestamp', 'Active power+', 'Active power-']]
    # set timestamp as index
    df.set_index('Timestamp', inplace=True)
    # rename columns PV
    df.columns = ['PowerGeneratedPV', 'PowerOutputPV']
    # set the format form str to float
    df['PowerGeneratedPV'] = 1/60 * df['PowerGeneratedPV'].astype(float) # set the unit Wh instead of Wmin
    df['PowerOutputPV'] = 1/60 * df['PowerOutputPV'].astype(float)   # set the unit Wh instead of Wmin
    return df


def read_modbus_netz(filename):
    """
    Daten aus dem Ordner Netzanschluss an df übergeben und Timestamp als Index einführen.
    Die Spalten Active power +&- werden unter neuer Bezeichnung zurückgeben.
      :rtype: object
      :param filename: Name of the file that serves as input. Format : .csv
      :return: Dataframe
      """
    # TODO einlesen der Leistungswerte, die Umrechnung auf eine Wh ist noch nicht erfolgt, jeden Wert mit 1/60 multiplizieren
    df = pd.read_csv(f'{filename}',
                     header=1,
                     sep=';')  # read in
    df = df.iloc[1:]  # delete caption
    df = df.reset_index(drop=True)  # index starts with 0
    # unix timestamp to Pandas Timestamp
    df['Timestamp'] = pd.to_datetime(df['UNIX-Timestamp'], unit='s',
                                     origin='unix').round('min') + timedelta(hours=2)

    df = df[['Timestamp', 'Active power+', 'Active power-']]
    # select only 'Timestamp', 'Active power+ PV', 'Active power- PV'
    df.set_index('Timestamp', inplace=True)  # set timestamp as index
    # rename colums
    df.columns = ['GridPowerIn', 'GridPowerOut']  # GridPowerIn = Netzbezug; GriPowerOut = Überschussstrom
    # set the format form str to float
    df['GridPowerIn'] = 1/60 * df['GridPowerIn'].astype(float)  # set the unit Wh instead of Wmin
    df['GridPowerOut'] = 1/60 * df['GridPowerOut'].astype(float)  # set the unit Wh instead of Wmin
    return df


def read_modbus_strommix(filename='Realisierte_Erzeugung_202101010000_202112312359.csv'):
    """
    Daten aus dem Ordner Strommix_Erzeugung an df übergeben und einen Index (Timestamp) eingeführt.
    Der Timestamp wird aus Datum und Uhrzeit generiert, damit einheitliche Timestamps vorliegen.
    Mit einer for Schleif wird die Datenreihe so erweitert, dass jede Minute vorhanden ist. Die ursprünglichen
    Daten besitzen eine viertel Stundentaktung.
    :rtype: object
    :param filename: Name of the file that serves as input. Format : .csv
    :return: Dataframe
    :fileversion: Realisierte_Erzeugung_202104010000_202104052359.csv, Realisierte_Erzeugung_202101010000_202112312359.csv
    """

    df = pd.read_csv(f'data/Strommix_Erzeugung/{filename}',
                     header=0, sep=';',
                     thousands='.',
                     parse_dates=[['Datum', 'Uhrzeit']],
                     dayfirst=True)  # read in
    # rename columsname
    df.columns = ['Timestamp', 'Biomasse', 'Wasserkraft', 'WindOffshore', 'WindOnshore',
                  'Photovoltaik', 'SonstigeErneuerbare', 'Kernenergie', 'Braunkohle',
                  'Steinkohle', 'Erdgas', 'Pumpspeicher', 'SonstigeKonventionelle']
    # for each element at timestamp, add 14 times value series with writen in 0
    for index, elem in enumerate(df['Timestamp']):
        # DEBUG
        # print(index)

        biomasse = df.at[index, 'Biomasse']
        wasserkraft = df.at[index, 'Wasserkraft']
        windoffshore = df.at[index, 'WindOffshore']
        windonshore = df.at[index, 'WindOnshore']
        photovoltaik = df.at[index, 'Photovoltaik']
        sonstigeerneuerbare = df.at[index, 'SonstigeErneuerbare']
        kernenergie = df.at[index, 'Kernenergie']
        braunkohle = df.at[index, 'Braunkohle']
        steinkohle = df.at[index, 'Steinkohle']
        erdgas = df.at[index, 'Erdgas']
        pumpspeicher = df.at[index, 'Pumpspeicher']
        sonstigekonventionelle = df.at[index, 'SonstigeKonventionelle']
        # Here the CO2 emission values of Smard, which are recorded every quarter of an hour,
        # extended to every single minute of an hour
        # (given the first minute and then appending the same value 14 times, so 15 minutes are filled)
        for x in range(14):
            new_time = elem + timedelta(minutes=x + 1)
            df_insert = pd.DataFrame([[new_time, biomasse, wasserkraft, windoffshore, windonshore,
                                       photovoltaik, sonstigeerneuerbare, kernenergie, braunkohle, steinkohle,
                                       erdgas, pumpspeicher, sonstigekonventionelle]], columns=df.columns)
            df = pd.concat([df, df_insert])
    df = df.sort_values(by='Timestamp')
    # set timestamp as index
    df.set_index('Timestamp', inplace=True)
    # df = df.reset_index(drop=True)

    # new column, which contains the sum of each minute
    df['Total'] = df.loc[:, :].sum(1)
    return df


def read_co2_index():
    """
    Liest die Datei ein, in der nach Kraftwerkstypen spezifizierten co2 Werte ausgewiesen werden, diese sind aus
    einer Internetrecherche zusammengetragen. Sie bilden die Grundlage für die Umrechnung der genutzten
    kilowattstunden  in Emissionen.
    :rtype: object
    :return: Dataframe
    """
    co2_index = pd.read_csv('data/Kraftwerksemissionsschluessel.csv', header=0, sep=',')
    # delete the first colum
    del co2_index['Masseinheit']

    co2_index.columns = ['Biomasse', 'Wasserkraft', 'WindOffshore', 'WindOnshore',
                         'Photovoltaik', 'SonstigeErneuerbare', 'Kernenergie', 'Braunkohle',
                         'Steinkohle', 'Erdgas', 'Pumpspeicher', 'SonstigeKonventionelle']
    return co2_index


def readall_pv():
    """
    Daten aus dem Ordner PV-Anlage sollen eingebunden werden.
    Die einzeln df werden miteinander verbunden.
    Es sind zwei Smartmeter für das Quatier verbaut,
    sie werden hier zu einem Wert addiert und als df wieder ausgegeben.
     :rtype: object
     :param: Name of the file that serves as input. Format : .csv
     :return: Dataframe
    """
    # getting csv files from the folder PV_Anlage
    path1 = "data/PV-Anlage/Smartdaten_für_2021/Smart1/"
    path2 = "data/PV-Anlage/Smartdaten_für_2021/Smart2/"
    # path1 = "data/PV-Anlage/April/Smart1/"
    # path2 = "data/PV-Anlage/April/Smart2/"

    # read all the files with extension .csv
    filenames1 = glob.glob(path1 + "*.csv")
    filenames2 = glob.glob(path2 + "*.csv")
    'data/PV-Anlage/Smart1/SN73144693-EM-PV-OW-2021-04-01.csv'
    # for loop to iterate each folder and concat to one df for a folder

    dfone = pd.DataFrame
    dftwo = pd.DataFrame

    for index, file in enumerate(filenames1):
        df = read_modbus_pv(f'{file}')
        if index == 0:
            dfone = df
        else:
            dfone = pd.concat([dfone, df])

    for index, file in enumerate(filenames2):
        df = read_modbus_pv(f'{file}')
        if index == 0:
            dftwo = df
        else:
            dftwo = pd.concat([dftwo, df])
    # sort by timestamp as index
    # dfone = dfone.sort_values(dfone, by='Timestamp')
    # dftwo = dftwo.sort_values(dftwo, by='Timestamp')
    # combine both smartmeter to one dataframe

    assert not dfone.empty
    assert not dftwo.empty

    df_add = dfone.add(dftwo, fill_value=0)
    return df_add


def readall_netz():
    """
   Daten aus dem Ordner Netzanschluss werden in eine Liste geschrieben,
   welche die Namen der CSV-Dateien beinhaltet. Die einzeln Dateien werden eingelesen und
   miteinander verkünpft. Hier werden die zwei Smartzähler des Quatieres zu einem Wert addiert.
   Das bildet die Grundlage für die Berechnungen.
   :rtype: object
      :param: Name of the file that serves as input. Format : .csv
      :return: Dataframe
      """
    # getting csv files from the folder Netzanschluss
    path1 = "data/Netzanschluss/Smartdaten_für_2021/Smart1/"
    path2 = "data/Netzanschluss/Smartdaten_für_2021/Smart2/"
    # path1 = "data/Netzanschluss/April/Smart1/"
    # path2 = "data/Netzanschluss/April/Smart2/"
    # todo Netz/smart1 Datei vom 2021-03-29 hat einen Fehler bei der formatierung des Unix Timestamp

    # read all the files with extension .csv
    filenames1 = glob.glob(path1 + "*.csv")
    filenames2 = glob.glob(path2 + "*.csv")

    # for loop to iterate each folder and concat to one df for a folder
    dfone = pd.DataFrame
    dftwo = pd.DataFrame

    for index, file in enumerate(filenames1):
        df = read_modbus_netz(f'{file}')
        if index == 0:
            dfone = df
        else:
            dfone = pd.concat([dfone, df])

    for index, file in enumerate(filenames2):
        df = read_modbus_netz(f'{file}')
        if index == 0:
            dftwo = df
        else:
            dftwo = pd.concat([dftwo, df])

    # sort by timestamp as index
    dfone = dfone.sort_values(by='Timestamp')
    dftwo = dftwo.sort_values(by='Timestamp')

    # combine both smartmeter to one dataframe
    df_add = dfone.add(dftwo, fill_value=0)
    return df_add


def read_pv_netz_combined():
    """
    Ruft die pv und netz Funktionen auf und schreibt die in ein df.
         :return: Dataframe
         """
    pv_df = readall_pv()
    netz_df = readall_netz()
    # df = pd.concat([pv_df, netz_df], axis=1) # Todo
    print(pv_df.head())
    print(len(pv_df))
    print(netz_df.head())
    print(len(netz_df))
    df = pv_df.merge(netz_df, left_on='Timestamp', right_on='Timestamp', how='outer')
    df.fillna(0.0)
    print(df.head())
    print(len(df))

    return df


def cal_co2_grid(df, strommix, co2_werte):
    """
     Rechnet die CO2 Emissionen für den aus dem Netz bezogenen Strom aus.
     Hier wird nur der Zustand ohne Speicher betrachtet.
     :rtype: object
     :param: Dataframe
     :return: Dataframe
     :Formel: CO2-Äquivalent=Summe(P_Kraftwerkstyp*CO2_Wert)/Summe(P_Kraftwerkstyp)
                Emissionen pro Min = 'AktivePower+Netz * CO2-Äquivalent
    Summe Emissionen = Summe(Emissionen über den gesamten Zeitraum)
    """
    co2_emission = []
    emissions_per_kwh = []
    saving_em_through_sell = []

    for index, row in strommix.iterrows():
        # check for missing indices in df
        if index not in df.index:
            pass
        else:
            # if index % 1000 == 0:
            #   print(index)
            # Calculate the co2 emissions from the electricity purchased from the grid
            emission_per_min = math.fsum([row.Biomasse * int(co2_werte.at[1, 'Biomasse']),
                                          row.Wasserkraft * int(co2_werte.at[1, 'Wasserkraft']),
                                          row.WindOffshore * int(co2_werte.at[1, 'WindOffshore']),
                                          row.WindOnshore * int(co2_werte.at[1, 'WindOnshore']),
                                          row.Photovoltaik * int(co2_werte.at[1, 'Photovoltaik']),
                                          row.SonstigeErneuerbare * int(co2_werte.at[1, 'SonstigeErneuerbare']),
                                          row.Kernenergie * int(co2_werte.at[1, 'Kernenergie']),
                                          row.Braunkohle * int(co2_werte.at[1, 'Braunkohle']),
                                          row.Steinkohle * int(co2_werte.at[1, 'Steinkohle']),
                                          row.Erdgas * int(co2_werte.at[1, 'Erdgas']),
                                          row.Pumpspeicher * int(co2_werte.at[1, 'Pumpspeicher']),
                                          row.SonstigeKonventionelle * int(co2_werte.at[1, 'SonstigeKonventionelle'])
                                          ])
            # factor of current emission per kwh
            #print(type(emission_per_min))
            #print(type(row.Total))
            emission_per_kwh = emission_per_min / row.Total

            # convert W into kW, that we got  [g/kWh]*[kWh]= [g] CO2-Emissionen

            power_grid_in = float(df.loc[index, 'GridPowerIn'])
            co2_equi_per_min = power_grid_in * float(emission_per_kwh)
            co2_equi_per_min /= 1000
#--- Save ReadIns ---
#--- Reading Strommix ---
#--- Save ReadIns ---
#--- Reading CO2-Index ---
#--- Calculation Strommix CO2 ---
#Traceback (most recent call last):
#  File "C:\Users\Petau\Desktop\Speicher-CO2-Bewertung\input_leistungsdaten_as_df.py", line 1105, in <module>
#    main()
#  File "C:\Users\Petau\Desktop\Speicher-CO2-Bewertung\input_leistungsdaten_as_df.py", line 87, in main
#    solution_quartier_strommix = cal_co2_grid(df=netz_pv,
#  File "C:\Users\Petau\Desktop\Speicher-CO2-Bewertung\input_leistungsdaten_as_df.py", line 470, in cal_co2_grid
#    co2_equi_per_min = float(df.loc[index, 'GridPowerIn']) * float(emission_per_kwh)
#  File "C:\Users\Petau\AppData\Local\Programs\Python\Python39\lib\site-packages\pandas\core\series.py", line 191, in wrapper
#    raise TypeError(f"cannot convert the series to {converter}")
# TypeError: cannot convert the series to <class 'float'>
# Process finished with exit code 1

            # write down a list with values for every minutes
            co2_emission.append(co2_equi_per_min)
            emissions_per_kwh.append(emission_per_kwh)

            # emission credite througt selling power to the grid
            saving_emission_per_kwh = emission_per_kwh - float(co2_werte.at[1, 'Photovoltaik'])
            amount_saving_emission_with_gridpowerout = saving_emission_per_kwh * float(
                df.loc[index, 'GridPowerOut'] / 1000)
            saving_em_through_sell.append(max(0, amount_saving_emission_with_gridpowerout))

    # for loop done
    # add the list as a colum to df
    df['co2_emission_per_kwh'] = emissions_per_kwh
    # calculation the emission by using grid power with simulate storages
    df['co2_emission_grid'] = co2_emission  # result at [g]
    df['em_reduction_through_sell'] = saving_em_through_sell
    # here are the amount of saved emission by selling Power to the grid
    return df


def cal_co2_pv_eigennutzung(netz_pv, co2_werte, reduction_through_pv_sale):
    """
   Innerhalb dieser Funktion werden die Emission berechnet,
   die durch den selbstgenutzten Strom der Photovoltaik entstehen.

      :param: Name of the file that serves as input. Format : .csv
      :return: Dataframe
      """

    tot_emission = []
    co2_factor = float(co2_werte.at[1, 'Photovoltaik'])
    for _, row in netz_pv.iterrows():
        # Calculates the CO₂ emissions for self-used PV energy
        # convert W to kW
        internally_used_power = float(row.PowerGeneratedPV - row.GridPowerOut) / 1000
        emission_per_min = internally_used_power * co2_factor
        # if we want to exclude negative values
        tot_emission.append(emission_per_min)
        # tot_emission.append(max(emission_per_min, 0))
        # Rechnung ist (GenPV-Überschuss)/1000 * co2_Photovolatik, in welchem Fall kommen negative werte
        # if we dont
        # tot_emission.append(emission_per_min)
    netz_pv['co2_emission_internal'] = tot_emission

    if reduction_through_pv_sale:
        netz_pv['emission_total'] = netz_pv.co2_emission_grid + netz_pv.co2_emission_internal \
                                    - netz_pv.em_reduction_through_sell
    if not reduction_through_pv_sale:
        netz_pv['emission_total'] = netz_pv.co2_emission_grid + netz_pv.co2_emission_internal

    return netz_pv


# Up to here the data is read in, linked together and the emissions are determined for the existing system
# From here on, battery characteristics are used to determine emission reduction potentials,
# which may result from the use of a backup battery.

def cal_battery(netz_pv, speichergroesse, soc_start=None):
    """
    Rechnung um den Speicher zu simulieren, die Leistungswerte und den neuen
    State of Charge in einer Liste wiederzugeben. Je nach Varianten kann so eine mögliche Leistung aufgezeigt werden.
    Parameter und Daten zu einem Speicher sind hier hinterlegt. Dieser kann durch die Speichergroesse angepasst werden.
    Dies ist die Grundlage für eine Berechnung der möglichen Emissionen, bei gleicher Leistung.

     :rtype: Dataframe
     :param: Dataframe
     :return: Dataframe
     """

    eta = 0.9  # Efficiency factor
    soc_max = 0.9  # [range: 0-1 ]
    soc_min = 0.1  # [range: 0-1 ]
    zeit = 90  # [minute]

    p_ges = speichergroesse / zeit  # [W] / [minute]
    c_out = 0.5  # Coulombe Factor, depends on battery rating
    c_in = 0.25  # Coulombe factor
    min_flow_threshold = 0.1  # threshold for minimal flow for action to be taken [range: 0-1] in %

    p_max_out = p_ges * c_out
    p_min_out = p_max_out * min_flow_threshold
    p_max_in = p_ges * c_in
    p_min_in = p_max_in * min_flow_threshold

    # Efficiency included in the borderline cases, set new limits
    # TODO überprüfen ob eta immer berücksichtigt wird
    p_max_out *= eta
    p_min_out *= eta
    p_max_in = p_max_in * (1 + (1 - eta))
    p_min_in = p_min_in * (1 + (1 - eta))

    soc = []  # minute-wise soc
    p_delta = []  # the difference in power per minute
    soc_deltas = []

    if soc_start:
        soc_akt = soc_start  # This represents an opportunity to specify a defined state of charge.
    else:
        soc_akt = soc_max / 2  # assumption: 45% charged at startup

    for index, row in netz_pv.iterrows():
        # Default: no change, no in, no out, p_soll = 0
        soc_ist = soc_akt
        soc_delta = 0
        p_ist = 0
        # Show network interface whether import or withdrawal takes place
        p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])

        if p_soll > 0:  # check for positive
            # p_supply = p_soll * (1 + (1 - eta))  # factor in losses
            p_ist = min(p_max_out, p_soll)  # Threshold for upper bound

            if p_ist >= p_min_out:  # Threshold for lower bound
                soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
                soc_akt = soc_ist - soc_delta

            # Capacity check, prevent depletion
            if soc_akt < soc_min:
                soc_akt = soc_ist
                p_ist = 0
                soc_delta = 0

        if p_soll < 0:  # Query whether storage can be carried out with excess current # case p_soll negative
            p_supply = abs(p_soll)
            p_ist = min(p_max_in, p_supply)

            if p_ist >= p_min_in:
                p_ist = -p_ist  # invert value to reflect incoming p
                soc_delta = ((p_ist * eta) / (speichergroesse / 100)) / 100
                soc_akt = soc_ist - soc_delta

            # Capacity check, prevent overcharge
            if soc_akt > soc_max:
                soc_akt = soc_ist
                p_ist = 0
                soc_delta = 0

        soc.append(soc_ist)
        p_delta.append(p_ist)
        soc_deltas.append(soc_delta)

    netz_pv[f'p_delta_{speichergroesse}Wh'] = p_delta
    netz_pv[f'current_soc_{speichergroesse}Wh'] = soc
    netz_pv[f'soc_delta_{speichergroesse}Wh'] = soc_deltas
    netz_pv.to_csv(f'documents/netz_pv_mit_speichersimulation.csv')
    return netz_pv


def cal_emission_for_each_battery_variant(df, speichergroessen, co2_werte, reduction_through_pv_sale):
    """
    Rechnung die Vergleichsemissionen der einzelnen Speichervarianten zum Ist Zustand zu vergleichen
    Zeigt die mögliche Leistungsverschiebung vom Netz zum Speicher auf. Durch die veränderten Leistungsbezug, werden
    neue Emissionswerte erforderlich diese können dann aus dem Dataframe ausgelesen werden.
     :rtype: Dataframe
     :param: Dataframe
     :return: Dataframe
    """

    co2_factor_pv = float(co2_werte.at[1, 'Photovoltaik']) # [g/kWh]
    bat_cycles = 5_000  # with assumed 5_000 times of sub-cycles
    battery_initial_emission = 140_000  # 140_000 g emission for each kWh of batterysize
    battery_runtime = 15 * 365 * 24 * 60  # 15 years, given in minutes
    capacity = 0.8 # 80 % of the batterycapacity is available
    co2_em_bat_prod_cycles = battery_initial_emission / bat_cycles # / capacity # 140kg emissions by production of one kWh battery
    co2_em_bat_prod_lifetime = battery_initial_emission / battery_runtime

    for size in speichergroessen:
        co2_em_cycles = []
        co2_em_lifetime = []
        bat_size_kwh = float(size / 1000)
        co2_em_speicher_lifetime = co2_em_bat_prod_lifetime * bat_size_kwh
        co2_em_speicher_cycles = co2_em_bat_prod_cycles * bat_size_kwh
        co2_emissions_reduce_by_delta_ps = []

        print(f'{size=}')  # Progress indication

        for index, row in df.iterrows():
            number_positive = True if row[f'p_delta_{size}Wh'] > 0 else False
            no_change = True if row[f'p_delta_{size}Wh'] == 0 else False

            p_delta_kwh = row[f'p_delta_{size}Wh']/1000  # unit changed from Wh to kWh

            # case True is when power is taken from storage and stored in the home network.
            # power output of the battery
            if number_positive:
                # cap to only positive values
                sim_grid_power_in = row.GridPowerIn - row[f'p_delta_{size}Wh']
                sim_grid_power_out = row.GridPowerOut
                sim_direct_use_pv = max(0, row.PowerGeneratedPV - row.GridPowerOut)
                co2_em_p_delta_lifetime = co2_em_speicher_lifetime
                co2_em_p_delta_cycles = p_delta_kwh * co2_em_speicher_cycles

            # case False is when power taken into the battery
            else:
                sim_grid_power_in = row.GridPowerIn
                # cap to only positive values
                sim_grid_power_out = row.GridPowerOut - row[f'p_delta_{size}Wh']
                sim_direct_use_pv = max(0, row.PowerGeneratedPV - row.GridPowerOut)

                co2_em_p_delta_lifetime = p_delta_kwh * co2_factor_pv + co2_em_speicher_lifetime
                co2_em_p_delta_cycles = p_delta_kwh * co2_factor_pv

            if no_change:
                sim_grid_power_in = row.GridPowerIn
                sim_grid_power_out = row.GridPowerOut
                sim_direct_use_pv = max(0, row.PowerGeneratedPV - row.GridPowerOut)
                co2_em_p_delta_lifetime = co2_em_speicher_lifetime
                co2_em_p_delta_cycles = 0

            sim_direct_use_pv_co2_em = (sim_direct_use_pv / 1000) * co2_factor_pv
            sim_co2_emission = (sim_grid_power_in / 1000) * row.co2_emission_per_kwh
            # row.GridPowerOut)
            sale_co2_em_pv = (sim_grid_power_out / 1000) * co2_factor_pv
            theoretical_co2_em_by_others = (sim_grid_power_out / 1000) * row.co2_emission_per_kwh
            co2_reduction_through_pv_sale = theoretical_co2_em_by_others - sale_co2_em_pv

            if reduction_through_pv_sale:
                co2_wert_lifetime = sim_co2_emission + sim_direct_use_pv_co2_em + co2_em_p_delta_lifetime \
                                    - co2_reduction_through_pv_sale
                co2_wert_cycles = sim_co2_emission + sim_direct_use_pv_co2_em + co2_em_p_delta_cycles \
                                  - co2_reduction_through_pv_sale

            if not reduction_through_pv_sale:
                co2_wert_lifetime = sim_co2_emission + sim_direct_use_pv_co2_em + co2_em_p_delta_lifetime \
                    # - co2_reduction_through_pv_sale
                co2_wert_cycles = sim_co2_emission + sim_direct_use_pv_co2_em + co2_em_p_delta_cycles \
                    # - co2_reduction_through_pv_sale

            co2_em_cycles.append(co2_wert_cycles)
            co2_em_lifetime.append(co2_wert_lifetime)

        assert len(co2_em_cycles) > 0
        assert len(co2_em_lifetime) > 0
        assert len(co2_em_cycles) == len(co2_em_lifetime)

        df[f'co2_em_cycles_at_{size}Wh'] = co2_em_cycles
        df[f'co2_em_lifetime_at_{size}Wh'] = co2_em_lifetime

        # Calculation of the difference in emissions with storage compared to the actual state of the exsinting system.
        co2_delta_cycles = df.emission_total - df[f'co2_em_cycles_at_{size}Wh']
        co2_delta_lifetime = df.emission_total - df[f'co2_em_lifetime_at_{size}Wh']

        df[f'co2_savings_cycles_at_{size}Wh'] = df.emission_total - df[
            f'co2_em_cycles_at_{size}Wh']
        df[f'co2_savings_lifetime_at_{size}Wh'] = df.emission_total - df[
            f'co2_em_lifetime_at_{size}Wh']

        # calculation of the emission bonus at the end of the period under review, storage as energy at the battery
        value_last_soc = float(df[f'current_soc_{size}Wh'].iat[-1])
        co2_em_bonus_after_runningtime = value_last_soc * bat_size_kwh * co2_factor_pv
        df[f'Gutschrift_für_restl_SoC_{size}Wh'] = co2_em_bonus_after_runningtime
    return df

# Ab hier sind die Plotbefehle aufgeführt, diese stellen die Wertetabellen grafisch da.
def plot_compare_emission_reduction_btw_batt_size(df, plot_without_bars, speichergroessen):
    """
    Dieser Plot kann aus den Daten des df ein Balkendiagramm erstellen, welches die Summen
    der Emissionen über den betrachteten Zeitraum  darstellen. Pro Speichergröße werden zwei
    unterschiedliche Mengen an Emissionen ausgegeben, da zwei Berechnungsgrundlagen für die
    Emissionen pro kWh Speicher vorliegen:
    Lifetime - Emissionen werden auf jede Minute einer prognostizierten Betriebszeit umgelegt,
    fixer Betrag pro Minute unabhängig von der Benutzung
    Cycles - Emissionen werden auf die kWh umgelegt, die der Speicher an Leistungsabgabe
    dem Nutzer zur Verfügung stellt.
    :param df: data with power and emission for each variante
    :param speichergroessen: variante of battery size
    :return: plot, image as .png
    """
    fig, ax = plt.subplots()
    # Here, we get the current emission as a baseline @ first place
    emission_as_is = df[f'emission_total'].sum() / 1000  # df as g for the amount of kWh
    print(f'{emission_as_is=}')
    emission_sums_cycles = [emission_as_is, ]
    emission_sums_lifetime = [emission_as_is, ]
    number_of_bars = len(speichergroessen) + 1
    x_coords = np.arange(0, number_of_bars, 1)
    labels = [0]
    colors = ['red']
    colors2 = ['red']

    for size in speichergroessen:
        emissions_cycles = df[f'co2_em_cycles_at_{size}Wh']
        emissions_lifetime = df[f'co2_em_lifetime_at_{size}Wh']
        emission_sums_cycles.append(emissions_cycles.sum() / 1000 )
        emission_sums_lifetime.append(emissions_lifetime.sum() / 1000 )
        # consideration of the co2 credit for the rest amount of power at the end of observation period
        # emission_sums_cycles-= df[1, f'Gutschrift_für_restl._SoC_{size}kWh']
        # emission_sums_lifetime -= df[1, f'Gutschrift_für_restl._SoC_{size}kWh']
        labels.append(round(size/1000, 1))
        colors.append((rd.random(), rd.random(), rd.random()))
        colors2.append((rd.random(), rd.random(), rd.random()))
    emission_sums_cycles_rounded = [round(x, 2) for x in emission_sums_cycles]
    emission_sums_lifetime_rounded = [round(x, 2) for x in emission_sums_lifetime]

    print(f'{emission_sums_cycles_rounded=} in kg')
    print(f'{emission_sums_lifetime_rounded=} in kg')
    print(f'{labels=}')

    width = 0.1  # the width of the bars
    # This plots the bars with the random colors
    if not plot_without_bars:
        cycles_bar = ax.bar(x=x_coords - width,
                            height=emission_sums_cycles_rounded,
                            align='center',
                            # label=emission_sums_cycles_rounded,
                            color=colors,
                            width=width / 2)

        lifetime_bar = ax.bar(x=x_coords + width,
                              height=emission_sums_lifetime_rounded,
                              align='center',
                              # label=emission_sums_lifetime_rounded,
                              color=colors,
                              width=width / 2)
    # Set and plots the one color line and markers, with the random colors
    cycles_plot = plt.plot(emission_sums_cycles_rounded,
                           # marker='1',
                           color='tab:blue',
                           fillstyle='none',
                           linestyle='--',
                           label='Cycle')
    for index, elem in enumerate(emission_sums_cycles_rounded):
        plt.plot(index + width,
                 elem,
                 color=colors[index],
                 markersize=10,
                 marker='1'
                 # ,label='Cycles', f'{index}', f'{elem}'
                 )

    lifetime_plot = plt.plot(emission_sums_lifetime_rounded,
                             # marker='x',
                             color='tab:green',  # fillstyle='none',
                             linestyle=':',
                             label='Lifetime')
    for index, elem in enumerate(emission_sums_lifetime_rounded):
        plt.plot(index - width,
                 elem,
                 color=colors[index],
                 markersize=5,
                 marker='x'
                 # ,label='Cycles', f'{index}', f'{elem}'
                 )

    # adding to legend the explanation of the markers
    # plt.plot([], [], ' ', label="Extra label on the legend")
    plt.plot([], [],
             color='black',
             marker='1',
             linestyle='None',
             markersize=10,
             label='Cycle')

    plt.plot([], [],
             color='black',
             marker='x',
             linestyle='None',
             markersize=5,
             label='Lifetime')
    plt.plot([], [], ' ', marker= '$0$',
             color= 'black',
             label=f'{round(emission_as_is, 2)}')

    # set a number on each bar
    # ax.bar_label(cycles_bar, padding=5)
    # ax.bar_label(lifetime_bar, padding=5)

    y_min = min(min(emission_sums_lifetime), min(emission_sums_cycles))
    y_max = max(max(emission_sums_lifetime), max(emission_sums_cycles))
    padding = 500

    ax.set_ylim([y_min - padding, y_max + padding])
    ax.xaxis.set_ticks_position('bottom')  # the rest is the same
    # plt.ylim(1000, )
    ax.grid(True)
    plt.xticks(range(len(labels)), labels, rotation='vertical')
    plt.xlabel('Varianten in kWh')
    plt.ylabel('CO2 Emissionen in kg')
    plt.title('Übersicht Emissionsmengen mit Gutschrift durch Einspeisung')
    plt.legend(bbox_to_anchor=(1, 1), loc="upper left")
    # um die legende zu kürzen \n{round(total / 1000, 2)}\n{round(total / 1000, 2)}
    plt.tight_layout()
    plt.gcf().set_size_inches(15, 5)
    plt.show()
    fig.savefig(f'graphs/Vergleich_Ist_zu_verschiedenen_Speichergroessen.png')


def plot_potential_co2_savings(df,plot_without_bars, speichergroessen):
    """
    Dieser Plot zeigt, welche Mengen an CO2 Emissionen mit den unterschiedlichen Größen
    an Speichern eingespart werden kann, bei den Emissionen für die eigne Elektrizitätsversorgung
    :param df: data with power and emission for each variante
    :param speichergroessen: variante of batterysize
    :return: plot, image as .png
    """

    fig, ax = plt.subplots()
    # Here, we get the current emission as a baseline @ first place
    savings_as_is = 0
    savings_sums_cycles = [savings_as_is, ]
    savings_sums_lifetime = [savings_as_is, ]
    number_of_bars = len(speichergroessen) + 1
    x_coords = np.arange(0, number_of_bars, 1)
    labels = [0]
    colors = ['red']
    colors2 = ['red']

    for size in speichergroessen:
        savings_cycles = df[f'co2_savings_cycles_at_{size}Wh']
        savings_lifetime = df[f'co2_savings_lifetime_at_{size}Wh']
        # / df[f'co2_em_at_{int(size / 1000)}kWh']
        savings_sums_cycles.append(savings_cycles.sum() / 1000 )
        savings_sums_lifetime.append(savings_lifetime.sum() / 1000 )

        labels.append(round(size/1000, 1))
        colors.append((rd.random(), rd.random(), rd.random()))
        colors2.append((rd.random(), rd.random(), rd.random()))
    savings_sums_cycles_rounded = [round(x, 2) for x in savings_sums_cycles]
    savings_sums_lifetime_rounded = [round(x, 2) for x in savings_sums_lifetime]

    width = 0.1  # the width of the bars
    # This plots the bars with the random colors
    if not plot_without_bars:
        cycles_bar = ax.bar(x=x_coords - width,
                            height=savings_sums_cycles_rounded,
                            align='center',
                            # label=savings_sums_cycles_rounded,
                            color=colors,
                            width=width / 2)
        lifetime_bar = ax.bar(x=x_coords + width * 0.5,
                              height=savings_sums_lifetime_rounded,
                              align='center',
                              # label=savings_sums_lifetime_rounded,
                              color=colors,
                              width=width / 2)
    # Set and plots the one color line and markers, with the random colors
    cycles_plot = plt.plot(savings_sums_cycles_rounded,
                           # marker='1',
                           color='tab:blue',
                           fillstyle='none',
                           linestyle='--',
                           label='Cycle')
    for index, elem in enumerate(savings_sums_cycles_rounded):
        plt.plot(index + width,
                 elem,
                 color=colors[index],
                 markersize=10,
                 marker='1'
                 # ,label='Cycles', f'{index}', f'{elem}'
                 )

    lifetime_plot = plt.plot(savings_sums_lifetime_rounded,
                             # marker='x',
                             color='tab:green',
                             fillstyle='none',
                             linestyle=':',
                             label='Lifetime')

    for index, elem in enumerate(savings_sums_lifetime_rounded):
        plt.plot(index - width,
                 elem,
                 color=colors[index],
                 markersize=5,
                 marker='x'
                 # ,label='Cycles', f'{index}', f'{elem}'
                 )
    # adding to legend the explanation of the markers
    # plt.plot([], [], ' ', label="Extra label on the legend")
    plt.plot([], [],
             color='black',
             marker='1',
             linestyle='None',
             markersize=10,
             label='Cycle')

    plt.plot([], [],
             color='black',
             marker='x',
             linestyle='None',
             markersize=5,
             label='Lifetime')

    # set a number on each bar
    # ax.bar_label(cycles_bar, padding=5)
    # ax.bar_label(lifetime_bar, padding=5)

    ax.xaxis.set_ticks_position('bottom')  # the rest is the same
    ax.grid(True)
    plt.xticks(range(len(labels)), labels, rotation='vertical')
    plt.xlabel('Varianten in kWh')
    plt.ylabel('CO2 Einsparungen in kg')
    plt.title('Übersicht Einsparungen an CO2 mit Speicheroptionen')
    plt.legend(bbox_to_anchor=(1, 1), loc="upper left", title='Summe CO2 in kg')
    # to cut the lengend in total \n{round(total / 1000, 2)}\n{round(total / 1000, 2)}
    plt.tight_layout()
    plt.gcf().set_size_inches(15, 5)
    plt.show()
    fig.savefig(f'graphs/Vergleich_Einsparungen_CO2.png')


def plot_potential_co2_savings_ratio(df, plot_without_bars, speichergroessen):
    """
    Darstellung wie viele CO2 Emissionen pro verbauter kWh Speicher eingespart werden
    :param df: data with power and emission for each variante
    :param speichergroessen: variante of batterysize
    :return: plot
    """

    fig, ax = plt.subplots()
    # Here, we get the current emission as a baseline @ first place
    """ savings_as_is = 0
    savings_sums_cycles = [savings_as_is, ]
    savings_sums_lifetime = [savings_as_is, ]
    number_of_bars = len(speichergroessen) + 1
    x_coords = np.arange(0, number_of_bars, 1)
    labels = [0]
    colors = ['red']"""
    # Here, plot without the current emission as a baseline
    savings_sums_cycles = []
    savings_sums_lifetime = []
    number_of_bars = len(speichergroessen)
    x_coords = np.arange(0, number_of_bars, 1)
    labels = []
    colors = []

    for size in speichergroessen:
        savings_cycles = df[f'co2_savings_cycles_at_{size}Wh']
        savings_lifetime = df[f'co2_savings_lifetime_at_{size}Wh']
        savings_sums_cycles.append(savings_cycles.sum() / 1000 )
        savings_sums_lifetime.append(savings_lifetime.sum() / 1000 )

        labels.append(round(size/1000, 1))
        colors.append((rd.random(), rd.random(), rd.random()))

    benefit_ratios_cycles = np.empty_like(savings_sums_cycles)
    benefit_ratios_lifetime = np.empty_like(savings_sums_lifetime)
    np.divide(savings_sums_cycles, labels, benefit_ratios_cycles)
    np.divide(savings_sums_lifetime, labels, benefit_ratios_lifetime)

    benefit_ratios_cycles_rounded = [round(x, 3) for x in benefit_ratios_cycles]
    benefit_ratios_lifetime_rounded = [round(x, 3) for x in benefit_ratios_lifetime]

    width = 0.1  # the width of the bars
# This plots the bars with the random colors
    if not plot_without_bars:
        cycles_bar = ax.bar(x=x_coords - width,
                            height=benefit_ratios_cycles_rounded,
                            align='center',
                            # label=benefit_ratios_cycles_rounded,
                            color=colors,
                            # fillstyle='none',
                            width=width / 2)
        lifetime_bar = ax.bar(x=x_coords + width,
                              height=benefit_ratios_lifetime_rounded,
                              align='center',
                              # label=benefit_ratios_lifetime_rounded,
                              color=colors,
                              # fillstyle='none',
                              width=width / 2)
# Set and plots the one color line and markers, with the random colors
    cycles_plot = plt.plot(benefit_ratios_cycles_rounded,
                           # marker='1',
                           color='tab:blue',
                           fillstyle='none',
                           linestyle='--',
                           label='Cycle')
    for index, elem in enumerate(benefit_ratios_cycles_rounded):
        plt.plot(index - width,
                 elem,
                 color=colors[index],
                 markersize=10,
                 marker='1'
                 # ,label='Cycles', f'{index}', f'{elem}'
                 )

    lifetime_plot = plt.plot(benefit_ratios_lifetime_rounded,
                             # marker='x',
                             color='tab:green',
                             fillstyle='none',
                             linestyle=':',
                             label='Lifetime')

    for index, elem in enumerate(benefit_ratios_lifetime_rounded):
        plt.plot(index + width,
                 elem,
                 color=colors[index],
                 markersize=5,
                 marker='x'
                 # ,label='Savings/Lifetime'
                 )
# adding to legend the explanation of the markers
    plt.plot([], [],
             color='black',
             marker='1',
             linestyle='None',
             markersize=10,
             label='Cycle')

    plt.plot([], [],
             color='black',
             marker='x',
             linestyle='None',
             markersize=5,
             label='Lifetime')

    # set a number on each bar
    # ax.bar_label(cycles_bar, padding=5)
    # ax.bar_label(lifetime_bar, padding=5)


    plt.xticks(range(len(labels)), labels, rotation='vertical')
    ax.xaxis.set_ticks_position('bottom')  # the rest is the same
    ax.grid(True)
    plt.xlabel('Varianten in kWh')
    plt.ylabel('CO2 Einsparungen in kg/kWh')
    plt.title('Vergleich an Minderung pro kWh Speichergröße')
    plt.legend(bbox_to_anchor=(1, 1), loc="upper left", title='Einsparungen pro kWh')
    plt.tight_layout()
    plt.gcf().set_size_inches(15, 5)
    plt.show()
    fig.savefig(f'graphs/Vergleich_Einsparungen_pro_kWh.png', bbox_inches='tight')

    result_df = pd.DataFrame({'speichergroessen': labels,
                              'benefit_ratios_cycles_rounded': benefit_ratios_cycles_rounded,
                              'benefit_ratios_lifetime_rounded': benefit_ratios_lifetime_rounded,
                              })
    result_df.to_csv('documents/results_table.csv')


# Makes the method main
# __name__
if __name__ == "__main__":
    main()
