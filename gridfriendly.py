# Imports
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def cal_grid_friendly(df, soc_max, soc_min, zeit, speichergroessen, eta, c_out, c_in, min_flow_threshold,
                      soc_start=None
                      ):
	"""
	Daten im df GridPowerIn, GridPowerOut,
 (speichergrößen abhänig) p_delta, soc_delta,
 current_soc (Betrachtung zu Beginn der Minute),
 p_netzeinspeisung, p_netzbezug
		:param soc_max:
		:param soc_min:
		:param zeit:
		:param speichergroessen:
		:param soc_start:
		:return:
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

		for day in unique_days:
			following_day = day + timedelta(days=1)
			df_day = df.loc[(df.index.date >= day)
			                & (df.index.date < following_day)].copy()
			# set for each day the variable
			soc_reached_limit = False

			soc = []  # minute-wise soc
			p_delta = []  # the difference in power per minute
			soc_deltas = []  # the difference in state of charge
			netzbezug = []  # result amuont of power form the grid
			netzeinspeisung = []  # result amuont of power to the grid
			netzleistung = []  # grid power

			# hier soll einmal das df durch gerechnet werden
			for index, row in df_day.iterrows():
				soc_ist = soc_akt
				# Show network interface whether import or withdrawal takes place
				p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])  # Bezug - Einspeisung
				if p_soll > 0:
					p_ist = min(p_max_out, max(p_min_out, p_soll * (1 + (1 - eta))))
					soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
					soc_akt = max(soc_min, soc_ist - soc_delta) if soc_akt < soc_min else soc_ist - soc_delta
					if soc_akt > soc_max:
						soc_reached_limit = True
						soc_akt = soc_ist
						p_ist = 0
						soc_delta = 0
				else:
					p_supply = abs(p_soll)
					p_ist = -min(p_max_in, max(p_min_in, p_supply))
					soc_delta = ((p_ist * eta) / (speichergroesse / 100)) / 100
					soc_akt = min(soc_max, soc_ist - soc_delta) if soc_akt > soc_max else soc_ist - soc_delta
					if soc_akt < soc_min:
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
				p_delta.append(p_ist)
				soc_deltas.append(soc_delta)
				netzbezug.append(p_netzbezug)
				netzeinspeisung.append(p_netzeinspeisung)
				netzleistung.append(p_netz)  # TODO spalte ins df eintragen?

			df_day[f'p_delta_{speichergroesse}Wh_netzdienlich'] = p_delta
			df_day[f'current_soc_{speichergroesse}Wh_netzdienlich'] = soc
			df_day[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = soc_deltas
			df_day[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = netzbezug
			df_day[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = netzeinspeisung

			if not soc_reached_limit:

				df.loc[(df.index.date >= day)
				       & (df.index.date < following_day)] = df_day
				print(f'No optimization needed in {day}')
			# TODO check if saving works

			else:  # case reached soc limit
				if day == first_day:
					print('reached Battery Max on first day')
					if soc_start:
						soc_akt = soc_start  # This represents an opportunity to specify a defined state of charge.
					else:
						soc_akt = soc_max / 2  # assumption: 45% charged at startup

				else:
					print(f'Optimization needed in {day}')
					first_minute_of_day = df_day.first_valid_index()
					minute_before = first_minute_of_day - timedelta(minutes=1)
					print(f'{first_minute_of_day=}')
					print(f'{minute_before=}')
					soc_akt = df.loc[minute_before, f'current_soc_{speichergroesse}Wh_netzdienlich']
				# Find index of first non-zero value in 'Netzeinspeisung'
				index_first_non_zero = df_day[df_day[f'GridPowerOut'] > 0].index[0]

				# Find corresponding value of 'current_soc'
				current_soc = df_day.loc[index_first_non_zero, f'current_soc_{speichergroesse}Wh_netzdienlich']

				# Calculate number of steps to get from 'current_soc' to 'soc_max'
				optimization_steps_estimate = int(round((soc_max - current_soc) / soc_delta_max))

				print(f'{optimization_steps_estimate=}')

				# Index der x höchsten Werte finden
				optimizable_indices = df_day[f'GridPowerOut'].nlargest(optimization_steps_estimate).index.tolist()
				print(f'{optimizable_indices=}')

				for index, row in df_day.iterrows():
					# cheken was gemacht werden muss für die Zeile ob laden oder entladen
					# entladen ist gleich geblieben
					# beim laden muss neben dem soc zuerst der index in der liste optimizable_indices
					# gefunden werden damit geladenwerden kann

					p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])  # Bezug - Einspeisung

					if p_soll > 0: # Battery discharging
						# TODO alle werte sollten normal ausgerechnet werden


					else: # Battery charging possible
						# check if optimizable index is present
						if index not in optimizable_indices:
							# TODO
							#charging should be deferred
							pass
						else:
							# battery charging should go through
							# TODO
							pass



				# hier einen neuen durchlauf machen und wenn einspeisung zu erstenmal erscheint dann max Werte in einliste schreiben mit abgleich vom derzeiten soc
				pass  # start gridfriendly

		# save each day in df_day

		# save each day after cal into a df for the hole year
		# fals kein voller soc erreicht wird, ablegen speichern und nächsten Tag anschauen

		# falls ja dann ab (vielleicht sonnenaufgang) ein charge gridfriendly aufrufen und das entstanden df über schreiben

		# grid charge friendly: schauen wieviele minuten muss geladen werden um die soc grenze zu ereichen die Liste mit den indexen ist ausreichend

		# schauen ob leistung benotigt wird aus speicher und bedinnungen überprüfen

		# schauen ob leistung aufgenommen wird uber indexliste und bedinnungen überprüfen

		# neue werde in spalten ablegen dies vlt concaten

		# ein gesamtes df erstellen
		# idee: aus spalte a im df_day die werte in eine liste schreiben  und dann die liste als neue dpalte für das ganze jahr in df einfügen

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
