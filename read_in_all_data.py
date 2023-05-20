# Imports
import glob
from datetime import timedelta
import pandas as pd


def read_in_all_data(original_read=True):
	"""
	starts the funktion read_pv_netz_combined

	:param original_read: Boolean. If True, reads from the original source and saves the data as a pickle file.
						If False, reads from the pickle file. Default is True.
	:return: Dataframe containing all data
	"""
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
	open all csv data for the time of intresst and choose the importent data from pv
	modification to the data and the timestamp
	:param filename: Name of the file that serves as input. Format: .csv
	:return: Dataframe containing relevant data (Active power + & -) with the timestamp set as the index
	"""
	# Read the data from the file and pass it to a dataframe
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
	:param filename: Name of the file that serves as input. Format: .csv
	:return: Dataframe containing relevant data (Active power + & -) with the timestamp set as the index and new column names
	"""
	# Read the data from the file and pass it to a dataframe
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
	To analyze the PV system, the data from the corresponding folder must be imported into the program. Initially,
	the individual dataframes are merged to obtain an overall overview. Additionally, two smart meters are installed
	where the PV system is installed, measuring the electricity consumption. To determine the total power
	consumption of the unit, the values of both smart meters are added and output as a new dataframe.
	In this way, the data from the PV system and the neighborhood power consumption can be merged and analyzed together.
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
   The program starts by writing the names of CSV files in the "Netzanschluss" folder to a list.
   Then, each file is read and merged together. The program adds the values of the two smart meters
   installed in the unit to create a single value. This value serves as the basis for further calculations.
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
	The function read_pv_netz_combined() calls the functions readall_pv() and readall_netz()
	to read the data from the PV and Netz folders, respectively. The two dataframes are merged
	based on their timestamps using the merge() function, and the resulting dataframe is
	stored in the df variable. Any missing values in the dataframe are then filled with 0
	using the fillna() method. Finally, the iloc() method is used to select all rows and
	columns of the dataframe, and the resulting dataframe is returned.
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
  	This function calculates the emissions resulting from the self-consumption of electricity generated by
  	the photovoltaic system. It takes as input the name of a .csv file and returns a dataframe.
  	The function iterates over the rows of the input dataframe and calculates the internally used
  	power in kilowatts by subtracting the power generated by the photovoltaic system from the power
  	fed into the grid. The resulting values are appended to a list called "eigenverbrauch". Finally,
  	a new column called "PV-Eigennutzung" is added to the input dataframe containing the values from
  	the "eigenverbrauch" list, and the updated dataframe is returned.

	  :param: Name of the file that serves as input. Format : .csv
	  :return: Dataframe
	  """

	eigenverbrauch = []
	for _, row in netz_pv.iterrows():
		# in W
		internally_used_power = float(row.PowerGeneratedPV - row.GridPowerOut)
		eigenverbrauch.append(internally_used_power)
	netz_pv['PV-Eigennutzung'] = eigenverbrauch
	return netz_pv
