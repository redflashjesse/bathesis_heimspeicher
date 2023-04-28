# Imports
from datetime import timedelta
import numpy as np
import pandas as pd


def cal_grid_friendly(df, soc_max, soc_min, zeit,
                      speichergroessen, eta, c_out, c_in, min_flow_threshold,
                      soc_start=None
                      ):
    """
    Daten im df GridPowerIn, GridPowerOut,
 (speichergrößen abhänig) p_delta, soc_delta,
 current_soc (Betrachtung zu Beginn der Minute),
 p_netzeinspeisung, p_netzbezug
        :param min_flow_threshold:
        :param c_in: battery parameter
        :param c_out: battery parameter
        :param eta: efficient
        :param df: base of the data
        :param soc_max: battery parameter
        :param soc_min: battery parameter
        :param zeit: is a parameter of time for charging and discharging
        :param speichergroessen: size of battery
        :param soc_start: where soc starts
        :return: df with data of grid friendly charging
        """
    for speichergroesse in speichergroessen:
        # specification for each size
        p_ges = speichergroesse / zeit  # [W] / [minute]
        p_max_out = p_ges * c_out
        p_min_out = p_max_out * min_flow_threshold
        p_max_in = p_ges * c_in
        p_min_in = p_max_in * min_flow_threshold

        # Efficiency included in the borderline cases, set new limits
        p_max_out *= eta
        p_min_out *= eta
        p_max_in = p_max_in * (1 + (1 - eta))
        p_min_in = p_min_in * (1 + (1 - eta))

        # set the maximum of soc_delta in case for charging
        soc_delta_max = (p_max_in / (speichergroesse / 100)) / 100

        # Insert new empty columns, we initialize the new columns here and fill them later
        df[f'p_delta_{speichergroesse}Wh_netzdienlich'] = np.nan
        df[f'current_soc_{speichergroesse}Wh_netzdienlich'] = np.nan
        df[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = np.nan
        df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = np.nan
        df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = np.nan
        df[f'p_netzleistung_{speichergroesse}Wh_netzdienlich'] = np.nan

        if soc_start:
            soc_akt = soc_start  # This represents an opportunity to specify a defined state of charge.
        else:
            soc_akt = soc_max / 2  # assumption: 45% charged at startup
        # Default: no change, no in, no out, p_soll = 0
        soc_delta = 0
        p_ist = 0

        # Schleife durch jeden Tag im Jahr gehen
        unique_days = df.index.date.tolist()
        unique_days = list(dict.fromkeys(unique_days))
        first_day = unique_days[0]
        list_of_days_optimization = []
        df_list_opt = pd.DataFrame()

        for day in unique_days:

            following_day = day + timedelta(days=1)
            df_day = df.loc[(df.index.date >= day)
                            & (df.index.date < following_day)].copy()
            # set for each day the variable
            soc_reached_limit = False
            soc_ist = soc_akt

            socs = []  # minute-wise soc
            p_deltas = []  # the difference in power per minute
            soc_deltas = []  # the difference in state of charge
            netzbezug = []  # result amuont of power form the grid
            netzeinspeisung = []  # result amuont of power to the grid
            netzleistung = []  # grid power

            # Here, the dataframe for the year is being processed like own consumtion
            # add by the case if one day reached soc_max the day will cal in an other way
            for index, row in df_day.iterrows():
                soc_ist = soc_akt

                # Show network interface whether import or withdrawal takes place
                # Calculate target power
                p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])

                # Discharging the battery
                if p_soll > 0:
                    p_ist = min(p_max_out, p_soll)  # Threshold for upper bound

                    if p_ist >= p_min_out:  # Threshold for lower bound
                        soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
                        soc_akt = soc_ist - soc_delta
                    else:
                        p_ist, soc_delta, soc_akt = 0, 0, soc_ist

                    # Capacity check, prevent depletion
                    if soc_akt <= soc_min:
                        soc_akt, p_ist, soc_delta = soc_ist, 0, 0

                    # calculation of the grid power by intergration of a battery
                    p_netzbezug = row['GridPowerIn'] - max(p_ist, 0)
                    p_netzeinspeisung = 0

                # Charging the battery
                elif p_soll < 0:
                    p_supply = abs(p_soll)
                    p_ist = min(p_max_in, p_supply)

                    if p_ist >= p_min_in:
                        p_ist = -p_ist  # invert value to reflect incoming p
                        soc_delta = ((p_ist * eta) / (speichergroesse / 100)) / 100
                        soc_akt = soc_ist - soc_delta

                    else:
                        p_ist, soc_delta, soc_akt = 0, 0, soc_ist

                    # Capacity check, prevent overcharge
                    if soc_akt > soc_max:
                        soc_akt, p_ist, soc_delta, soc_reached_limit = soc_ist, 0, 0, True

                    # calculation of the grid power by intergration of a battery
                    p_netzeinspeisung = row['GridPowerOut'] + min(p_ist, 0)
                    p_netzbezug = 0

                # No power exchange # p_soll==0:
                else:
                    p_netzbezug, p_netzeinspeisung = row['GridPowerIn'], row['GridPowerOut']
                    soc_akt, p_ist, soc_delta = soc_ist, 0, 0

                p_netz = p_netzbezug - p_netzeinspeisung

                socs.append(soc_ist)
                p_deltas.append(p_ist)
                soc_deltas.append(soc_delta)
                netzbezug.append(p_netzbezug)
                netzeinspeisung.append(p_netzeinspeisung)
                netzleistung.append(p_netz)

            df_day[f'p_delta_{speichergroesse}Wh_netzdienlich'] = p_deltas
            df_day[f'current_soc_{speichergroesse}Wh_netzdienlich'] = socs
            df_day[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = soc_deltas
            df_day[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = netzbezug
            df_day[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = netzeinspeisung
            df_day[f'p_netzleistung_{speichergroesse}Wh_netzdienlich'] = netzleistung

            if not soc_reached_limit:
                # save df_day in df
                df.loc[(df.index.date >= day)
                       & (df.index.date < following_day)] = df_day
            # print(f'No optimization needed in {day}')

            else:
                # case reached soc limit
                if day == first_day:  # check if the first day needs optimization
                    print('reached Battery Max on first day')
                    if soc_start:
                        soc_akt = soc_start  # This represents an opportunity to specify a defined state of charge.
                    else:
                        soc_akt = soc_max / 2  # assumption: 45% charged at startup
                else:
                    print(f'Optimization needed in {day}')
                    first_minute_of_day = df_day.first_valid_index()
                    minute_before = first_minute_of_day - timedelta(minutes=1)
                    # print(f'{first_minute_of_day=}')
                    # print(f'{minute_before=}')
                    soc_akt = df.loc[minute_before, f'current_soc_{speichergroesse}Wh_netzdienlich']

                # Find index of first non-zero value in 'Netzeinspeisung'
                index_first_non_zero = df_day[df_day[f'GridPowerOut'] > p_min_in].index[0]

                # Find corresponding value of 'current_soc'
                current_soc = df_day.loc[index_first_non_zero, f'current_soc_{speichergroesse}Wh_netzdienlich']

                optimizable_indices_list = df_day['GridPowerOut'].sort_values(ascending=False).index.tolist()
                assert len(df_day['GridPowerOut']) == len(optimizable_indices_list)

                # length of each day
                desired_length = len(df_day['GridPowerOut'])

                # fill the length up 1440 values
                # optimizable_indices_list = np.pad(optimizable_indices_list, (0, desired_length - len(optimizable_indices_list)),
                #                     mode='constant', constant_values=np.nan)
                df_list_opt[f'GridPowerOut_{day}_{speichergroesse}Wh'] = df_day['GridPowerOut']
                print(f'{len(optimizable_indices_list)=}')
                print(f'{desired_length=}')

                # Fülle fehlende Werte mit NaN auf
                optimizable_indices_list_len = np.pad(optimizable_indices_list, (0, desired_length - len(optimizable_indices_list)),
                                                 mode='constant', constant_values=np.nan)
                print(f'{len(optimizable_indices_list_len)=}, {day=}')


                df_list_opt[f'optimizable_indices_list_{day}_{speichergroesse}Wh'] = optimizable_indices_list_len

                optimization_steps_estimate = 0

                for idx in optimizable_indices_list:
                    p_supply_index = df_day.loc[idx, 'GridPowerOut']
                    p_ist_index = min(p_max_in, p_supply_index)  # Wert aus GridPowerOut begrenzt auf p_max_in

                    if p_ist_index >= p_min_in:
                        soc_delta_indices = ((p_ist_index * eta) / (speichergroesse / 100)) / 100
                        soc_akt_indices = current_soc + soc_delta_indices
                        current_soc = soc_akt_indices
                        optimization_steps_estimate += 1
                        if soc_akt_indices >= soc_max:
                            break  # Schleife wird beendet, sobald soc_akt >= soc_max ist

                # Calculate number of steps to get from 'current_soc' to 'soc_max'
                # optimization_steps_estimate = int(round((soc_max-soc_min)/soc_delta_max))
                # #int(round((soc_max - current_soc) / soc_delta_max))

                assert optimization_steps_estimate <= len(df_day['GridPowerOut'])
                assert optimization_steps_estimate >= 0

                # Index der x höchsten Werte finden
                optimizable_indices = df_day[f'GridPowerOut'].nlargest(optimization_steps_estimate).index.tolist()

                # Bestimme die gewünschte Länge der Spalte optimizable_indices
                desired_length = len(df_day['GridPowerOut'])

                # Fülle fehlende Werte mit NaN auf
                optimizable_indices_len = np.pad(optimizable_indices, (0, desired_length - len(optimizable_indices)),
                                             mode='constant', constant_values=np.nan)

                df_list_opt[f'optimizable_indices_{day}_{speichergroesse}Wh'] = optimizable_indices_len

                # start gridfriendly
                df_day_opt = optimize_one_day(df_day, p_max_out, p_min_out,
                                              p_max_in, p_min_in,
                                              soc_akt, eta, soc_min, soc_max, speichergroesse,
                                              optimizable_indices, day
                                              )

                # save each day after cal into a df for the hole year
                df.loc[(df.index.date >= day)
                       & (df.index.date < following_day)] = df_day_opt

    return df, df_list_opt


def optimize_one_day(df_day, p_max_out, p_min_out,
                     p_max_in, p_min_in,
                     soc_akt, eta, soc_min, soc_max, speichergroesse,
                     optimizable_indices, day
                     ):
    """
            The tool charge the battery only if the index of the possible charging minute in the optimizable_indices list.
            discharging is possible any time if the soc above soc_min
        :param df_day: dataframe of the day
        :param p_max_out: parameter of the battery depending of size
        :param p_min_out: parameter of the battery depending of size
        :param p_max_in: parameter of the battery depending of size
        :param p_min_in: parameter of the battery depending of size
        :param soc_akt: soc of previous day at the last minute
        :param eta: efficiency
        :param soc_min: limit of soc
        :param soc_max: limit of soc
        :param speichergroesse: the size of the battery
        :param optimizable_indices: minute of charging in a list
        :param day: value of date
        :return: df_day for insert part of the df
    """
    socs_opt = []  # minute-wise soc
    p_deltas_opt = []  # the difference in power per minute
    soc_deltas_opt = []  # the difference in state of charge
    netzbezug_opt = []  # result amuont of power form the grid
    netzeinspeisung_opt = []  # result amuont of power to the grid
    netzleistung_opt = []  # grid power
    soc_ist = soc_akt
    for index, row in df_day.iterrows():
        p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])  # Bezug - Einspeisung
        soc_akt = soc_ist
        if p_soll > 0:  # Battery discharging
            if min(p_max_out, p_soll) > p_min_out and soc_akt > soc_min:
                p_ist = max(p_min_out, min(p_max_out, p_soll))
                soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
                soc_ist = soc_akt - soc_delta
            else:  # p_soll out of the possible range and index is not in the list optimizable_indices
                p_ist = 0
                soc_delta = 0
                soc_ist = soc_akt

        else:  # Battery charging possible
            # check if optimizable index is present
            if index not in optimizable_indices:
                p_ist = 0
                soc_delta = 0
                soc_ist = soc_akt
            # charging should be deferred
            # pass # todo wäre noch ne möglichkeit: if index größer als der letze optimizable_indices dann laden wenn soc kleiner als soc_max ist
            else:
                # battery charging should go through
                p_soll = abs(p_soll)
                if min(p_max_in, p_soll) > p_min_in:
                    p_ist = max(p_min_in, min(p_max_in, p_soll))
                    soc_delta = ((p_ist * (eta)) / (speichergroesse / 100)) / 100
                    soc_ist = soc_akt + soc_delta
                    p_ist = - p_ist
                    if soc_ist > soc_max:
                        p_ist, soc_delta, soc_ist = 0, 0, soc_akt
                else:
                    p_ist, soc_delta, soc_ist = 0, 0, soc_akt

        if p_ist > 0:
            p_netzbezug_opt = row['GridPowerIn'] - max(p_ist, 0)
            p_netzeinspeisung_opt = 0
        elif p_ist < 0:
            p_netzeinspeisung_opt = row['GridPowerOut'] + min(p_ist, 0)
            p_netzbezug_opt = 0
        else:  # p_ist==0:
            p_netzbezug_opt = row['GridPowerIn']
            p_netzeinspeisung_opt = row['GridPowerOut']
        p_netzleistung_opt = p_netzbezug_opt - p_netzeinspeisung_opt
        socs_opt.append(soc_ist)
        p_deltas_opt.append(p_ist)
        soc_deltas_opt.append(soc_delta)
        netzbezug_opt.append(p_netzbezug_opt)
        netzeinspeisung_opt.append(p_netzeinspeisung_opt)
        netzleistung_opt.append(p_netzleistung_opt)

    df_day[f'p_delta_{speichergroesse}Wh_netzdienlich'] = p_deltas_opt
    df_day[f'current_soc_{speichergroesse}Wh_netzdienlich'] = socs_opt
    df_day[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = soc_deltas_opt
    df_day[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = netzbezug_opt
    df_day[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = netzeinspeisung_opt
    df_day[f'p_netzleistung_{speichergroesse}Wh_netzdienlich'] = netzleistung_opt

    return df_day

    # endfor
    # print(f'finished optimizing {day}')
