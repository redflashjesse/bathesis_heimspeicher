# Imports
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import math


def main():
	original_read = True
	print("--- Funktion read_in_all_data ---")
	base_data = read_in_all_data()
	return base_data

def read_in_all_data():

	if original_read:
		print("--- Read in Smartmeter Daten ---")
		base_data = read_pv_netz_combined()
		print("--- Pickle Daten ---")
		base_data.to_pickle("documents/base_data.pkl")
	else:
		print("--- Read in Smartmeter Daten aus Pickle ---")
		base_data = pd.read_pickle("documents/base_data.pkl")
	return base_data


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


if __name__ == "__main__":
	main()
