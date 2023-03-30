# Imports
from datetime import timedelta

import numpy as np


def cal_grid_friendly(df, soc_max, soc_min, zeit, speichergroessen, eta, c_out, c_in, min_flow_threshold,
                      soc_start=None
                      ):
	"""
	Daten im df GridPowerIn, GridPowerOut,
 (speichergrößen abhänig) p_delta, soc_delta,
 current_soc (Betrachtung zu Beginn der Minute),
 p_netzeinspeisung, p_netzbezug
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

		for day in unique_days:

			following_day = day + timedelta(days=1)
			df_day = df.loc[(df.index.date >= day)
			                & (df.index.date < following_day)].copy()
			# set for each day the variable
			soc_reached_limit = False

			socs = []  # minute-wise soc
			p_deltas = []  # the difference in power per minute
			soc_deltas = []  # the difference in state of charge
			netzbezug = []  # result amuont of power form the grid
			netzeinspeisung = []  # result amuont of power to the grid
			netzleistung = []  # grid power

			# hier soll einmal das df durch gerechnet werden
			for index, row in df_day.iterrows():
				soc_ist = soc_akt

				# Show network interface whether import or withdrawal takes place
				p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])  # Bezug - Einspeisung

				if p_soll > 0:  # Discharging battery # TODO check soc abgleich
					p_ist = min(p_max_out, max(p_min_out, p_soll * (1 + (1 - eta))))
					soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
					soc_akt = max(soc_min, soc_ist - soc_delta) if soc_akt < soc_min else soc_ist - soc_delta
					if soc_akt < soc_min: # case battery has reached the lower limit
						soc_akt = soc_ist
						p_ist = 0
						soc_delta = 0

					'''if soc_akt > soc_max:  # todo prüfen ob die bedinnung stimmt
						soc_reached_limit = True
						soc_akt = soc_ist
						p_ist = 0
						soc_delta = 0'''
				else:  # charging the battery
					p_supply = abs(p_soll)
					p_ist = -min(p_max_in, max(p_min_in, p_supply))
					soc_delta = ((p_ist * eta) / (speichergroesse / 100)) / 100
					soc_akt = min(soc_max, soc_ist - soc_delta) if soc_akt > soc_max else soc_ist + soc_delta
					if soc_akt > soc_max: # case battery has reached the upper limit
						soc_reached_limit = True
						soc_akt = soc_ist
						p_ist = 0
						p_delta = 0

					'''if soc_akt < soc_min:  # todo prüfen ob die bedinnung stimmt
						soc_akt = soc_ist
						p_ist = 0
						soc_delta = 0'''

				if p_ist > 0:
					p_netzbezug = row['GridPowerIn'] - max(p_ist, 0)
					p_netzeinspeisung = 0
				elif p_ist < 0:
					p_netzeinspeisung = row['GridPowerOut'] + min(p_ist, 0)
					p_netzbezug = 0
				else:  # p_ist==0:
					p_netzbezug = row['GridPowerIn']
					p_netzeinspeisung = row['GridPowerOut']

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
				df.loc[(df.index.date >= day)
				       & (df.index.date < following_day)] = df_day
				#print(f'No optimization needed in {day}')

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
					#print(f'{first_minute_of_day=}')
					#print(f'{minute_before=}')
					soc_akt = df.loc[minute_before, f'current_soc_{speichergroesse}Wh_netzdienlich']
				# Find index of first non-zero value in 'Netzeinspeisung'
				index_first_non_zero = df_day[df_day[f'GridPowerOut'] > 0].index[0]

				# Find corresponding value of 'current_soc'
				current_soc = df_day.loc[index_first_non_zero, f'current_soc_{speichergroesse}Wh_netzdienlich']

				# Calculate number of steps to get from 'current_soc' to 'soc_max'
				optimization_steps_estimate = int(round((soc_max - current_soc) / soc_delta_max))

				#print(f'{optimization_steps_estimate=}')

				# Index der x höchsten Werte finden
				optimizable_indices = df_day[f'GridPowerOut'].nlargest(optimization_steps_estimate).index.tolist()

				# start gridfriendly
				df_day_opt = optimize_one_day(df_day, p_max_out, p_min_out,
				                              p_max_in, p_min_in,
				                              soc_akt, eta, soc_min, soc_max, speichergroesse,
				                              optimizable_indices, day
				                              )

				# save each day after cal into a df for the hole year
				df.loc[(df.index.date >= day)
				       & (df.index.date < following_day)] = df_day_opt

	return df


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
	for index, row in df_day.iterrows():
		# checken was gemacht werden muss für die Zeile ob laden oder entladen
		# entladen ist gleich geblieben
		# beim laden muss neben dem soc zuerst der index in der liste optimizable_indices
		# gefunden werden damit geladenwerden kann

		p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])  # Bezug - Einspeisung

		if p_soll > 0:  # Battery discharging
			if min(p_max_out, p_soll) > p_min_out and soc_akt > soc_min:
				p_ist = max(p_min_out, min(p_max_out, p_soll))
				soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
				soc_ist = soc_akt - soc_delta
			else:  # p_soll out of the possible range and index is not in the list optimizable_indices
				p_ist = p_soll
				soc_delta = 0
				soc_ist = soc_akt

		else:  # Battery charging possible
			# check if optimizable index is present
			if index not in optimizable_indices:
				p_ist = p_soll
				soc_delta = 0
				soc_ist = soc_akt
			# TODO
			# charging should be deferred
			# pass # if index größer als der letze optimizable_indices dann laden wenn soc kleiner als soc_max ist
			else:
				# battery charging should go through
				p_soll = abs(p_soll)
				if min(p_max_in, p_soll) > p_min_in:
					p_ist = max(p_min_in, min(p_max_in, p_soll))
					soc_delta = ((p_ist * (eta)) / (speichergroesse / 100)) / 100
					soc_ist = soc_akt + soc_delta
					p_ist = - p_ist
			# TODO

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

			# fill the list with values for each minute
			df_day.at[index, f'current_soc_{speichergroesse}Wh_netzdienlich'] = soc_ist
			df_day.at[index, f'soc_delta_{speichergroesse}Wh_netzdienlich'] = soc_delta
			df_day.at[index, f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = p_netzbezug_opt
			df_day.at[index, f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = p_netzeinspeisung_opt
			df_day.at[index, f'p_netzleistung_{speichergroesse}Wh_netzdienlich'] = p_netzleistung_opt
			df_day.at[index, f'p_delta_{speichergroesse}Wh_netzdienlich'] = p_ist

	# endfor
	#print(f'finished optimizing {day}')

	return df_day
