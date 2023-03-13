# Imports
import pandas as pd
from datetime import datetime, timedelta


def cal_grid_friendly(df, p_max_in, p_max_out, p_min_in, p_min_out, speichergroesse):
	"""
	Daten im df GridPowerIn, GridPowerOut,
 (speichergrößen abhänig) p_delta, soc_delta,
 current_soc (Betrachtung zu Beginn der Minute),
 p_netzeinspeisung, p_netzbezug
		:param speichergroesse:
		:param p_max_in:
		:param p_max_out:
		:param p_min_in:
		:param p_min_out:
		:return:
		"""
	# Schleife durch jeden Tag im Jahr gehen
	unique_days = df.index.date.tolist()
	unique_days = list(dict.fromkeys(unique_days))

	for day in unique_days:
		following_day = day + timedelta(days=1)

		df_day = df.loc[(df.index.date >= day)
		                & (df.index.date < following_day)]

		print(f'{len(df_day)}')

		print("Datum:", day)
		'''
		# Schleife durch jede Minute des Tages gehen
		for _, row in df.loc[df['Timestamp'].datetime.date == day].iterrows():
			print("Minute:", row['Timestamp'].time())
			print("GridPowerIn:", row['GridPowerIn'])
			print("GridPowerOut:", row['GridPowerOut'])

		# Wenn es 1440 Werte für den Tag gibt, Timestamp auf Mitternacht setzen
		if len(df.loc[df['Timestamp'].datetime.date == day]) == 1440:
			df.loc[df['Timestamp'].datetime.date == day, 'Timestamp'] = df.loc[
				df['Timestamp'].datetime.date == day, 'Timestamp'].datetime.floor('D')

	# Die ersten fünf Zeilen des modifizierten DataFrames anzeigen
	print(df.head())
	'''

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
	return  # df
