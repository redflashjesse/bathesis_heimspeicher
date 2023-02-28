# Imports
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import glob
import math

# set dpi globally
plt.rcParams['savefig.dpi'] = 500
plt.rcParams["figure.figsize"] = (15, 10)

# Global Battery Params

eta = 0.9  # Efficiency factor
soc_max = 0.9  # [range: 0-1 ]
soc_min = 0.1  # [range: 0-1 ]
zeit = 60  # [minute]


def main():
	"""
	Responsible for running everything sequentially, main has also the option to jump over some calculation and get
	some csv data, by setting values to false or true
	"""
	orginal_read = False
	use_data_for_plot = True  # or pickle
	plot_by_days = False
	speichergroessen = [12_000]
	# list(range(500,  # start
	#      10_000 + 1,  # end
	#      500))  # step  # in Wh
	soc_start = None  # input as float between 0.1,0,9; default = 0.45
	# selection_days_start = list(range(4, # start
	#                                365, # end
	#                               20)) # step # in days for the year
	startday = 150
	endday = startday + 1
	daysteps = 15

	if orginal_read:
		print(f"--- Read in Smartmeter Daten ---")
		base_data = read_pv_netz_combined()
		print(f"--- Pickle Daten ---")
		base_data.to_pickle(f'documents/base_data.pkl')

	else:
		print(f"--- Read in Smartmeter Daten aus Pickle ---")
		base_data = pd.read_pickle(f'documents/base_data.pkl')

	# print(len(base_data))
	if plot_by_days:
		plot_for_selected_days(daystep=daysteps, speichergroessen=speichergroessen,
		                       base_data=base_data, soc_start=soc_start,
		                       use_data_for_plot=use_data_for_plot
		                       )
	else:
		if use_data_for_plot:
			for size in speichergroessen:
				print(f"--- Simulation Batterie nach Eigenverbrauch mit {size} Wh---")
				batterypower_df, p_max_in, p_max_out, p_min_in, p_min_out = cal_battery_own_consumption(
						netz_pv=base_data,
						soc_start=soc_start,
						speichergroesse=size
				)

				print(f'--- Save Netz PV Speicher Eigenverbrauch als pickle ---')
				batterypower_df.to_pickle(f'documents/netz_pv_mit_speichersimulation_eigenverbrauch.pkl')

				print(f"--- Simulation Batterie nach netzdienlich mit {size} Wh---")

				cal_gridfriendly(df=batterypower_df,
				                 soc_start=soc_start,
				                 speichergroesse=size,
				                 p_max_in=p_max_in,
				                 p_max_out=p_max_out,
				                 p_min_in=p_min_in,
				                 p_min_out=p_min_out
				                 )

				print(f'--- Save Netz PV Speicher netzdienlich als pickle ---')
				batterypower_df.to_pickle(f'documents/netz_pv_mit_speichersimulation_netzdienlich.pkl')
		else:
			print(f'--- use pickle for data ---')
			batterypower_df = pd.read_pickle(f'documents/netz_pv_mit_speichersimulation_netzdienlich.pkl')

		print(f'--- Plot: Leistungsverlauf ---')
		# print(batterypower_df.keys())
		# for day in selection_days_start:
		#   startday = day
		for size in speichergroessen:
			plot_power(df=batterypower_df,
			           startday=startday,
			           endday=endday,
			           size=size
			           )
			plot_power_freq_dist(df=batterypower_df,
			                     startday=startday,
			                     endday=endday,
			                     size=size
			                     )


def plot_for_selected_days(daystep, speichergroessen, base_data, soc_start, use_data_for_plot):
	"""
		Auswahl bestimmter Tag aus dem Jahresdatensatz, Auswahl erste Möglichkeit einzelne Tage auszuwählen
		zum Beisspiel zwei Tage im Monat, Daten für die NetzLeistung und PVleistung werden in
		geleichen Tagen ausgeswählt
		 :rtype: object
		 :param: Name of the file that serves as input. Format : .csv
		 :return: list of filename
		"""
	list_of_days = list(range(1, 365, daystep))
	for day in list_of_days:

		startday = day
		endday = startday + 1

		if use_data_for_plot:
			for size in speichergroessen:
				print(f"--- Simulation Batterie nach Eigenverbrauch mit {size} Wh---")
				batterypower_df, p_max_in, p_max_out, p_min_in, p_min_out = cal_battery_own_consumption(
						netz_pv=base_data,
						soc_start=soc_start,
						speichergroesse=size
				)

				print(f'--- Save Netz PV Speicher Eigenverbrauch als pickle ---')
				batterypower_df.to_pickle(f'documents/netz_pv_mit_speichersimulation_eigenverbrauch.pkl')

				print(f"--- Simulation Batterie nach netzdienlich mit {size} Wh---")
				batterypower_df = cal_battery_gridfriendly(df=batterypower_df,
				                                           soc_start=soc_start,
				                                           speichergroesse=size,
				                                           p_max_in=p_max_in,
				                                           p_max_out=p_max_out,
				                                           p_min_out=p_min_out,
				                                           p_min_in=p_min_in
				                                           )

				print(f'--- Save Netz PV Speicher netzdienlich als pickle ---')
				batterypower_df.to_pickle(f'documents/netz_pv_mit_speichersimulation_netzdienlich.pkl')
		else:
			print(f'--- use pickle for data ---')
			batterypower_df = pd.read_pickle(f'documents/netz_pv_mit_speichersimulation_netzdienlich.pkl')

			print(f'--- Plot: Leistungsverlauf ---')
			print(batterypower_df.keys())
			# for day in selection_days_start:
			#   startday = day
			for size in speichergroessen:
				plot_power(df=batterypower_df, startday=startday, endday=endday,
				           size=size
				           )
				plot_power_freq_dist(df=batterypower_df, startday=startday, endday=endday,
				                     size=size
				                     )


def read_modbus_pv(filename):
	"""
	Daten aus dem Ordner PV-Anlage an df übergeben und den Timestamp als Index setzen.
	Die relevanten Daten (Active power +&-) werden an ein df übergeben, übrige Daten werden nicht weiter berücksichtigt.
	:rtype: object
	:param filename: Name of the file that serves as input. Format : .csv
	:return: Dataframe
	"""
	df = pd.read_csv(f'{filename}', header=1, sep=';')  # read in
	df = df.iloc[1:]  # delete caption
	df = df.reset_index(drop=True)  # index starts with 0
	# transforming unix timestamp to Pandas Timestamp
	df['Timestamp'] = pd.to_datetime(df['UNIX-Timestamp'], unit='s',
	                                 origin='unix'
	                                 ).round('min') + timedelta(hours=1)
	# select only 'Timestamp', 'Active power+ PV', 'Active power- PV'
	df = df[['Timestamp', 'Active power+', 'Active power-']]
	# set timestamp as index
	df.set_index('Timestamp', inplace=True)
	# rename columns PV
	df.columns = ['PowerGeneratedPV', 'PowerOutputPV']
	# set the format form str to float
	df['PowerGeneratedPV'] = 1 / 60 * df['PowerGeneratedPV'].astype(float)  # set the unit Wh instead of Wmin
	df['PowerOutputPV'] = 1 / 60 * df['PowerOutputPV'].astype(float)  # set the unit Wh instead of Wmin
	return df


def read_modbus_netz(filename):
	"""
	Daten aus dem Ordner Netzanschluss an df übergeben und Timestamp als Index einführen.
	Die Spalten Active power +&- werden unter neuer Bezeichnung zurückgeben.
	  :rtype: object
	  :param filename: Name of the file that serves as input. Format : .csv
	  :return: Dataframe
	  """
	df = pd.read_csv(f'{filename}',
	                 header=1,
	                 sep=';'
	                 )  # read in
	df = df.iloc[1:]  # delete caption
	df = df.reset_index(drop=True)  # index starts with 0
	# unix timestamp to Pandas Timestamp
	df['Timestamp'] = pd.to_datetime(df['UNIX-Timestamp'], unit='s',
	                                 origin='unix'
	                                 ).round('min') + timedelta(hours=1)

	df = df[['Timestamp', 'Active power+', 'Active power-']]
	# select only 'Timestamp', 'Active power+ PV', 'Active power- PV'
	df.set_index('Timestamp', inplace=True)  # set timestamp as index
	# rename colums
	df.columns = ['GridPowerIn', 'GridPowerOut']  # GridPowerIn = Netzbezug; GriPowerOut = Überschussstrom
	# set the format form str to float
	df['GridPowerIn'] = 1 / 60 * df['GridPowerIn'].astype(float)  # set the unit Wh instead of Wmin
	df['GridPowerOut'] = 1 / 60 * df['GridPowerOut'].astype(float)  # set the unit Wh instead of Wmin
	return df


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
	df_add = df_add.groupby(df_add.index).sum()
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
	df = pv_df.merge(netz_df, left_on='Timestamp', right_on='Timestamp', how='outer')
	df.fillna(0.0)
	df = df.iloc[::]
	# df = np.nan_to_num(df)
	return df


def cal_pv_eigennutzung(netz_pv):
	"""
   Innerhalb dieser Funktion werden die Emission berechnet,
   die durch den selbstgenutzten Strom der Photovoltaik entstehen.

	  :param: Name of the file that serves as input. Format : .csv
	  :return: Dataframe
	  """

	eigenverbrauch = []
	for _, row in netz_pv.iterrows():
		# convert W to kW
		internally_used_power = float(row.PowerGeneratedPV - row.GridPowerOut) / 1000
		eigenverbrauch.append(internally_used_power)
	netz_pv['PV-Eigennutzung'] = eigenverbrauch
	return netz_pv


def cal_battery_own_consumption(netz_pv, speichergroesse, soc_start=None):
	"""
		Rechnung um den Speicher zu simulieren, die Leistungswerte und den neuen
		State of Charge in einer Liste wiederzugeben.
		Je nach Varianten kann so eine mögliche Leistung aufgezeigt werden.
		Parameter und Daten zu einem Speicher sind hier hinterlegt.
		Dieser kann durch die Speichergroesse angepasst werden.
		Dies ist die Grundlage für eine Berechnung der möglichen Emissionen, bei gleicher Leistung.
		 :rtype: Dataframe
		 :param: Dataframe
		 :return: Dataframe
		 """

	p_ges = speichergroesse / zeit  # [W] / [minute]
	c_out = 1  # Coulombe Factor, depends on battery rating
	c_in = 0.5  # Coulombe factor
	min_flow_threshold = 0.1  # threshold for minimal flow for action to be taken [range: 0-1] in %

	p_max_out = p_ges * c_out
	p_min_out = p_max_out * min_flow_threshold
	p_max_in = p_ges * c_in
	p_min_in = p_max_in * min_flow_threshold

	# Efficiency included in the borderline cases, set new limits
	p_max_out *= eta
	p_min_out *= eta
	p_max_in = p_max_in * (1 + (1 - eta))
	p_min_in = p_min_in * (1 + (1 - eta))

	soc = []  # minute-wise soc
	p_delta = []  # the difference in power per minute
	soc_deltas = []  # the difference in state of charge
	netzbezug = []  # result amuont of power form the grid
	netzeinspeisung = []  # result amuont of power to the grid
	netzleistung = []  # grid power

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

		# calculation of the grid power by intergration of a battery

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
		netzleistung.append(p_netz)

	netz_pv[f'p_delta_{speichergroesse}Wh_eigenverbrauch'] = p_delta
	netz_pv[f'current_soc_{speichergroesse}Wh_eigenverbrauch'] = soc
	netz_pv[f'soc_delta_{speichergroesse}Wh_eigenverbrauch'] = soc_deltas
	netz_pv[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch'] = netzbezug
	netz_pv[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'] = netzeinspeisung

	return netz_pv, p_max_in, p_max_out, p_min_in, p_min_out  # Leistungen_Speicher_eigenverbrauch


def cal_battery_gridfriendly(df, speichergroesse,
                             p_max_in, p_max_out, p_min_in, p_min_out,
                             soc_start=None
                             ):
	max_soc_reached = max(df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'])
	print(max_soc_reached)
	netzeinspeisung_max = max(df[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'])
	print(netzeinspeisung_max)

	# Check if there is even enough overproduction
	if (netzeinspeisung_max < p_max_in):
		df[f'p_delta_{speichergroesse}Wh_netzdienlich'] = df[f'p_delta_{speichergroesse}Wh_eigenverbrauch']
		df[f'current_soc_{speichergroesse}Wh_netzdienlich'] = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch']
		df[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = df[f'soc_delta_{speichergroesse}Wh_eigenverbrauch']
		df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = df[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch']
		df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = df[
			f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch']
		return df  # Leistungen_Speicher_eigenverbrauch

	df[f'p_delta_{speichergroesse}Wh_netzdienlich'] = df[f'p_delta_{speichergroesse}Wh_eigenverbrauch']
	df[f'current_soc_{speichergroesse}Wh_netzdienlich'] = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch']
	df[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = df[f'soc_delta_{speichergroesse}Wh_eigenverbrauch']
	df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = df[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch']
	df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = df[
		f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch']

	df_pool = df

	while (max_soc_reached <= soc_max + 0.01):  # End Condition TODO: Cheat rausnehmen

		netzeinspeisung_max = max(df_pool[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'])
		surplus = netzeinspeisung_max - p_max_in
		# where is the max?
		index = df_pool[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'].idxmax()

		df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'][index] = surplus

		df[f'p_delta_{speichergroesse}Wh_netzdienlich'][index] = p_max_in
		# calc addition to battery
		soc_delta = ((p_max_in * eta) / (speichergroesse / 100)) / 100

		df[f'soc_delta_{speichergroesse}Wh_netzdienlich'][index] = soc_delta

		df[f'current_soc_{speichergroesse}Wh_netzdienlich'][index] += soc_delta
		# adapt new soc
		max_soc_reached = df[f'current_soc_{speichergroesse}Wh_netzdienlich'][index]

		# print(f'Changed a Minute @ {index}')
		# print(df.loc[[index]].transpose())
		df_pool = df_pool.drop(labels=index)

	return df


def cal_gridfriendly(df, speichergroesse,
                     p_max_in, p_max_out, p_min_in, p_min_out,  # battery parameter by the size
                     soc_start=None
                     ):
	list_of_days = list(range(0, 365, 1))
	for day in list_of_days:
		startday = day
		endday = startday + 1
		batt_reached_peak = False
		start_idx = startday * 1440
		end_idx = endday * 1440
		print(f'{start_idx=}')
		print(f'{end_idx=}')
		assert start_idx < end_idx

		soc = []  # minute-wise soc
		p_delta = []  # the difference in power per minute
		soc_deltas = []  # the difference in state of charge
		netzbezug = []  # result amuont of power form the grid
		netzeinspeisung = []  # result amuont of power to the grid
		netzleistung = []  # grid power

		if soc_start:
			soc_akt = soc_start  # This represents an opportunity to specify a defined state of charge.
		else:
			soc_akt = soc_max / 2  # assumption: 45% charged at startup

		df_day = df.iloc[start_idx:end_idx]
		print(len(df_day))

		# for each day start here
		for index, row in df_day.iterrows():
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
					# call if it is the first time then go to while, otherwise go ahead the while:
					# where this happens: switch for this day, back to the first infeed minute be the index
					# until soc > soc_max
					if batt_reached_peak:
						soc_akt = soc_ist
						p_ist = 0
						soc_delta = 0
					else:  # shuffle output for netzfreundlichkeit
						batt_reached_peak = True

			# calculation of the grid power by intergration of a battery
			# TODO Bedinnungen anpassen dies gilt nur wenn der für den Bereich außerhalb der While Betrachtung

			if p_ist > 0:
				p_netzbezug = row['GridPowerIn'] - max(p_ist, 0)
			if p_ist < 0:
				p_netzeinspeisung = row['GridPowerOut'] + min(p_ist, 0)
			else:  # p_ist==0:
				p_netzbezug = row['GridPowerIn']
				p_netzeinspeisung = row['GridPowerOut']

			#TODO
			# abspeichern der daten aus dem normalen durchlauf
		#df = charge_gridfriendly(df= df_day)

	return df


def charge_gridfriendly(df, speichergroesse,
                        p_max_in, p_max_out,
                        p_min_in, p_min_out
                        ):
	print("Executing charge_gridfriendly")

	# TODO Idee die Schleife in eigene Funktion zu überführen
	grid_feed_start = df[df[f'GridPowerOut'] > 0].index[0]

	minute_before_feed = grid_feed_start - timedelta(minutes=1)

	grid_feed_end = df[df[f'GridPowerOut'] > 0].index[-1]

	print(df[f'GridPowerOut'][grid_feed_end])


	# Todo Ausrechnen der möglichen Ausspeise minuten bei tages licht
	max_soc_reached = df[f'current_soc_{speichergroesse}Wh_netzdienlich'].loc[grid_feed_start]

	print(f'{max_soc_reached=}')
	# start bis ende bei allen bezugsleistungen einen negativien soc delta schreiben
	# dann mit der while schleife den max einspeise wertfinden und zelle soc delta ändern
	while max_soc_reached <= soc_max:  # End Condition

		print(f'{max_soc_reached=}')
		netzeinspeisung_max = max(df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'])
		index = df[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'].idxmax()
		print(f'{netzeinspeisung_max=}')
		print(f'{index=}')
		surplus = netzeinspeisung_max - p_max_in
		# where is the max?


		# nach jeder schleife jede row durchlaufen und checken wie sich soc beentwickelt
		# bei soc < 0.9 weiter max einspeisung suchen
		# bei soc > 0.9 am tag die daten bis zum Index wo soc>0.9 erreicht worden ist fest schreiben
		# und zurückgeben an den normalen verlauf
		df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'][index] = surplus

		df[f'p_delta_{speichergroesse}Wh_netzdienlich'][index] = p_max_in
		# calc addition to battery
		soc_delta = ((p_max_in * eta) / (speichergroesse / 100)) / 100

		df[f'soc_delta_{speichergroesse}Wh_netzdienlich'][index] = soc_delta

		df[f'current_soc_{speichergroesse}Wh_netzdienlich'][index] += soc_delta
		# adapt new soc
		max_soc_reached = df[f'current_soc_{speichergroesse}Wh_netzdienlich'][index]

		# print(f'Changed a Minute @ {index}')
		# print(df.loc[[index]].transpose())
		df_pool = df_pool.drop(labels=index)

	return df


# starts of plots
def plot_power(df, startday, endday, size):
	assert startday < endday
	date = df.index[startday * 1440 + 200]
	date = date.strftime('%Y-%m-%d')
	fig, ax = plt.subplots()

	# Leistungsverlauf ohne Quartierspeicher
	netzbezug_pure = df[f'GridPowerIn'][startday * 1440:endday * 1440]
	einspeisung_pure = df[f'GridPowerOut'][startday * 1440:endday * 1440]
	einspeisung_pure = einspeisung_pure.mul(-1)
	plt.plot(netzbezug_pure, label='Netzbezug ohne Speicher', alpha=0.4, zorder=1)
	plt.plot(einspeisung_pure, label='Einspeisung ohne Speicher', alpha=0.4, zorder=1)

	# Leistungsverlauf mit Quatierspeicher nach eigenverbrauch
	netzbezug_eigen = df[f'p_netzbezug_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	einspeisung_eigen = einspeisung_eigen.mul(-1)
	plt.plot(netzbezug_eigen, label='Speicher Eigenverbrauch', alpha=0.4, zorder=2)
	plt.plot(einspeisung_eigen, label='Speicher Eigenverbrauch', alpha=0.4, zorder=2)

	# Leistungsverlauf mit Quatierspeicher nach netzdienlich
	netzbezug_eigen = df[f'p_netzbezug_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	einspeisung_eigen = einspeisung_eigen.mul(-1)
	# Ladeleistung = df[f'p_ladeleistung_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]

	plt.plot(netzbezug_eigen, label='Speicher netzdienlich', alpha=0.4, zorder=3)
	plt.plot(einspeisung_eigen, label='Speicher netzdienlich', alpha=0.4, zorder=3)
	# plt.fill_between(Ladeleistung, y2= 0, label='Ladeleistung des Speichers', alpha=0.4, zorder=3)

	plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
	ax.xaxis.set_ticks_position('bottom')  # the rest is the same
	# plt.ylim(1000, )
	ax.grid(True)
	plt.xticks(rotation='vertical')  # range(len(labels)), labels,
	# plt.gcf().set_size_inches(15, 5)
	plt.title(f'Leistungsverlauf')
	plt.suptitle(f'für {date}')
	plt.xlabel('Zeit in h')
	plt.ylabel('Leistung in Wh')
	plt.tight_layout()
	plt.show()
	fig.savefig(f'graphs/Leistungsverlauf_{date}.png')


def plot_power_freq_dist(df, startday, endday, size, binsize=100):
	assert startday < endday
	bins = 25
	date = df.index[startday * 1440 + 200]
	date = date.strftime('%Y-%m-%d')
	density = False
	plt.style.use('fivethirtyeight')
	fig, ax = plt.subplots()
	# Betrachtung der Leistungen am Netzpunkt ohne Quartierspeicher
	netzbezug_pure = df[f'GridPowerIn'][startday * 1440:endday * 1440]
	einspeisung_pure = df[f'GridPowerOut'][startday * 1440:endday * 1440]
	min_out = einspeisung_pure.max()
	bins_out = math.ceil(min_out / binsize)
	max_in = netzbezug_pure.max()
	bins_in = math.ceil(max_in / binsize)
	Leistung_pure = einspeisung_pure.mul(-1) + netzbezug_pure

	# Betrachtung der Leistungen am Netzpunkt mit Quartierspeicher nach Eigenverbrauchoptimiert
	netzbezug_eigen = df[f'p_netzbezug_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	min_out = einspeisung_eigen.max()
	bins_out = math.ceil(min_out / binsize)
	max_in = netzbezug_eigen.max()
	bins_in = math.ceil(max_in / binsize)
	Leistung_eigenverbrauch = einspeisung_eigen.mul(-1) + netzbezug_eigen

	# Betrachtung der Leistungen am Netzpunkt mit Quartierspeicher nach Netzdienlichoptimiert
	netzbezug_netz = df[f'p_netzbezug_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	einspeisung_netz = df[f'p_netzeinspeisung_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	min_out = einspeisung_netz.max()
	bins_out = math.ceil(min_out / binsize)
	max_in = netzbezug_netz.max()
	bins_in = math.ceil(max_in / binsize)
	Leistung_netz = einspeisung_netz.mul(-1) + netzbezug_netz

	print(min_out, max_in)
	print(type(round(min_out)), round(min_out))
	bins_einspeisung = list(range(int(round(min_out)), 0, int(round(min_out) / 10)))
	bins_netzbezug = list(range(int(round(max_in)), 0, int(round(min_out) / 10)))
	# plt.hist(netzbezug, bins=bins_in, density= True, edgecolor='black')
	plt.hist([Leistung_pure], bins=bins,  # [bins_out, bins_in],
	         color=['blue'  # , 'orange'
	                ], density=density, edgecolor='black', label='ohne Speicher',
	         alpha=0.6, zorder=1
	         )  # , log=True, linewidth=1)
	plt.hist([Leistung_eigenverbrauch], bins=bins,  # [bins_out, bins_in],
	         color=['red'  # , 'orange'
	                ], density=density, edgecolor='black', label='Speicher eigenverbrauch',
	         alpha=0.2, zorder=2
	         )  # , log=True, linewidth=1)
	plt.hist([Leistung_netz], bins=bins,  # [bins_out, bins_in],
	         color=['yellow'  # , 'orange'
	                ], density=density, edgecolor='black', label='Speicher netzdienlich',
	         alpha=0.5, zorder=3
	         )  # , log=True, linewidth=1)
	plt.axvline(0, color='red')
	plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
	# We can also normalize our inputs by the total number of counts
	# axs[1].hist(dist1, bins=n_bins, density=True)
	# Now we format the y-axis to display percentage
	# axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))
	plt.title(f'Verteilung von Leistungen am {date}')
	plt.xlabel('Leistung in Wh')
	plt.ylabel('Häufigkeit')
	plt.tight_layout()
	plt.show()
	fig.savefig(f'graphs/Histogramm_{date}.png')


# plt.savefig(f'graphs/Histogramm_{date}.png'
# , dpi='figure', format=None, metadata=None,
# bbox_inches=None, pad_inches=0.1,
# facecolor='auto', edgecolor='auto',
# backend=None
# )


# Makes the method main
if __name__ == "__main__":
	main()
