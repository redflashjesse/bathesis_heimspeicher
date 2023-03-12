
def cal_gridfriendly(df, speichergroesse, p_max_in, p_max_out, p_min_in, p_min_out, startday, endday, soc_start=None, ):
    """
# battery parameter by the size
    :param df:
    :param speichergroesse:
    :param p_max_in:
    :param p_max_out:
    :param p_min_in:
    :param p_min_out:
    :param soc_start:
    :return:
    """

    for day in list(range(startday, endday, 1)):  # now limited to 1 day
        start_idx = startday * 1440
        end_idx = endday * 1440
        print(f'{start_idx=}')
        print(f'{end_idx=}')
        assert start_idx < end_idx

        batt_reached_peak = False

        soc = []  # minute-wise soc
        p_delta = []  # the difference in power per minute
        soc_deltas = []  # the difference in state of charge
        netzbezug = []  # result amuont of power form the grid
        netzeinspeisung = []  # result amuont of power to the grid
        netzleistung = []  # grid power
        if soc_start and day == 0:
            soc_akt = soc_start  # This represents an opportunity to specify a defined state of charge.
        elif day == 0:
            soc_akt = soc_max / 2  # assumption: 45% charged at startup
        else:
            soc_akt = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'].iloc[start_idx - 1] # TODO

        df_day = df.iloc[start_idx:end_idx].copy(deep=True)

        # for each day start here
        for index, row in df_day.iterrows():
            soc_ist = soc_akt
            soc_delta = 0
            p_ist = 0

            # Show network interface whether import or withdrawal takes place
            p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])

            if p_soll >= 0:  # check for positive
                # p_supply = p_soll * (1 + (1 - eta))  # factor in losses
                p_ist = min(p_max_out, p_soll)  # Threshold for upper bound

                if p_ist >= p_min_out:  # Threshold for lower bound
                    soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
                    soc_delta = -soc_delta
                    soc_akt = soc_ist + soc_delta

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
                    batt_reached_peak = True
                    soc_akt = soc_ist
                    p_ist = 0
                    soc_delta = 0

            if p_ist > 0:
                p_netzbezug = row['GridPowerIn'] - max(p_ist, 0)
            if p_ist < 0:
                p_netzeinspeisung = row['GridPowerOut'] + min(p_ist, 0)
            else:  # p_ist==0:
                p_netzbezug = row['GridPowerIn']
                p_netzeinspeisung = row['GridPowerOut']

            # save data from the normal run
            p_netz = p_netzbezug - p_netzeinspeisung

            soc.append(soc_ist)
            p_delta.append(p_ist)
            soc_deltas.append(soc_delta)
            netzbezug.append(p_netzbezug)
            netzeinspeisung.append(p_netzeinspeisung)
            netzleistung.append(p_netz)

        df_day[f'p_netzbezug_ohne_speicher'] = df[f'GridPowerIn']
        df_day[f'p_einspeisung_ohne_speicher'] = df[f'GridPowerOut']
        df_day[f'p_delta_{speichergroesse}Wh_netzdienlich'] = p_delta
        df_day[f'current_soc_{speichergroesse}Wh_netzdienlich'] = soc
        df_day[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = soc_deltas
        df_day[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = netzbezug
        df_day[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = netzeinspeisung

        # calculation done
        # check if optimization is needed
        if batt_reached_peak:
            df_day, last_soc = charge_gridfriendly(df=df_day,
                                                   speichergroesse=speichergroesse,
                                                   p_max_in=p_max_in,
                                                   p_max_out=p_max_out,
                                                   p_min_in=p_min_in,
                                                   p_min_out=p_min_out
                                                   )

        # df.append(df_day)  # TODO correct merging
        df = pd.concat([df, df_day], axis=1)
    return df, df_day


def charge_gridfriendly(df, speichergroesse, p_max_in, p_max_out, p_min_in, p_min_out):
    print("--- Executing charge_gridfriendly ---")

    grid_feed_start = df[df[f'GridPowerOut'] > 0].index[0]  # .index[0] choose the first value
    minute_before_feed = grid_feed_start - timedelta(minutes=1)

    grid_feed_end = df[df[f'GridPowerOut'] > 0].index[-1]
    df_daylight_pool = df[grid_feed_start:grid_feed_end].copy(deep=True)

    # erster soc Wert für die berechnung
    soc_akt = df[f'current_soc_{speichergroesse}Wh_netzdienlich'][minute_before_feed]

    # cal of how many min are need estimated for charging for rise the soc from sunset
    size_in_kwh = speichergroesse / 100
    soc_delta_max = ((p_max_in * eta) / size_in_kwh) / 100
    initial_soc = df[f'current_soc_{speichergroesse}Wh_netzdienlich'][minute_before_feed]
    times_charge = round((soc_max - initial_soc) / soc_delta_max)

    optimized_soc_list = []
    optimized_indices = []
    for x in range(times_charge):
        netzeinspeisung_max = max(df_daylight_pool[f'GridPowerOut'])
        index = df_daylight_pool[f'GridPowerOut'].idxmax()

        # check max
        charging_performance = min(p_max_in, netzeinspeisung_max)
        # check min
        if charging_performance < p_min_in:
            charging_performance = 0
        # just take old values that are in df, no optimization possible

        if charging_performance > 0:  # optimization possible
            surplus = netzeinspeisung_max - charging_performance
            df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'][index] = surplus

            df[f'p_delta_{speichergroesse}Wh_netzdienlich'][index] = charging_performance
            # calc addition to battery
            soc_delta = ((charging_performance * eta) / (speichergroesse / 100)) / 100

            df[f'soc_delta_{speichergroesse}Wh_netzdienlich'][index] = soc_delta
            optimized_soc_list.append(soc_delta)
            optimized_indices.append(index)

        df_daylight_pool = df_daylight_pool.drop(labels=index)

    # look for the minute start feed soc
    max_soc_reached = df[f'current_soc_{speichergroesse}Wh_netzdienlich'].loc[grid_feed_start]
    assert max_soc_reached < soc_max

    soc = []  # minute-wise soc
    p_deltas = []  # the difference in power per minute
    soc_deltas = []  # the difference in state of charge
    netzbezug = []  # result amuont of power form the grid
    netzeinspeisung = []  # result amuont of power to the grid
    netzleistung = []  # grid power

    # valus at feed start
    soc_akt = df[f'current_soc_{speichergroesse}Wh_netzdienlich'][0]
    p_delta = df[f'p_delta_{speichergroesse}Wh_netzdienlich'][0]
    soc_delta = df[f'soc_delta_{speichergroesse}Wh_netzdienlich'][0]
    p_netzbezug = df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'][0]
    p_netzeinspeisung = df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'][0]

    for index, row in df.iterrows():
        row_optimized = True if index in optimized_indices else False
        soc_ist = soc_akt

        if not row_optimized:
            if row[f'soc_delta_{speichergroesse}Wh_netzdienlich'] < 0:  # check for negativ soc_delta
                p_ist = min(p_max_out, float(row['GridPowerIn']))  # Threshold for upper bound

                if p_ist >= p_min_out:  # Threshold for lower bound
                    soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
                    soc_akt = soc_ist - soc_delta
                else:
                    soc_akt = soc_ist
                    p_ist = 0
                    soc_delta = 0

                # Capacity check, prevent depletion
                if soc_akt < soc_min:
                    soc_akt = soc_ist
                    p_ist = 0
                    soc_delta = 0
            else:
                soc_akt = soc_ist
                p_ist = 0
                soc_delta = 0

        else:  # if row_optimized:
            soc_delta = df[f'soc_delta_{speichergroesse}Wh_netzdienlich'][index]
            p_delta = df[f'p_delta_{speichergroesse}Wh_netzdienlich'][index]
            p_netzeinspeisung = df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'][index]

            if row[f'GridPowerOut'] - p_delta < 0:
                # änderung von wert p_delta
                p_delta = row[f'GridPowerOut']
                if p_delta < p_min_in:
                    p_delta = 0
                    soc_delta = 0
                p_ist = row[f'GridPowerOut'] - p_delta
            else:
                p_ist = row[f'GridPowerOut'] - p_delta
                soc_akt = soc_ist + soc_delta

            # Capacity check, prevent overcharge
            if soc_akt > soc_max:
                soc_akt = soc_ist
                p_ist = 0
                soc_delta = 0

        if p_ist > 0:
            p_netzbezug = row['GridPowerIn'] - max(p_ist, 0)
        if p_ist < 0:
            p_netzeinspeisung = row['GridPowerOut'] + min(p_ist, 0)
        else:  # p_ist==0:
            p_netzbezug = row['GridPowerIn']
            p_netzeinspeisung = row['GridPowerOut']

        p_netz = p_netzbezug - p_netzeinspeisung

        soc.append(soc_ist)
        p_deltas.append(p_ist)
        soc_deltas.append(soc_delta)
        netzbezug.append(p_netzbezug)
        netzeinspeisung.append(p_netzeinspeisung)
        netzleistung.append(p_netz)

    df[f'p_delta_{speichergroesse}Wh_netzdienlich'] = p_deltas
    df[f'current_soc_{speichergroesse}Wh_netzdienlich'] = soc
    df[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = soc_deltas
    df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = netzbezug
    df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = netzeinspeisung
    last_soc = soc_ist

    return df, last_soc