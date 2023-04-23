# Imports
import pandas as pd

from plot_trend_of_power import plot_power
from plot_histogram import plot_histogram
from plot_histogram import plot_histogram_sns


def plot_for_selected_days(df, daystep, speichergroessen, use_data_for_plot, filename):
	"""
The function plot_for_selected_days is used to select specific days from a yearly dataset
and plot the power values for the selected days. The function expects a large dataframe (df)
containing the data for the entire year, an integer value daystep indicating the interval
between selected days, a list of speichergroessen (storage sizes) for which to plot the power values,
a boolean value use_data_for_plot indicating whether to use pre-processed data or not, and a filename
to read the input data from.

If use_data_for_plot is True, the function reads the pre-processed data from the specified file
and prints the keys of the dataframe. If it is False, the function attempts to read
the input data from the specified file. For each day in the list of days, the function calls
the plot_power function and plot_histogram function to generate power plots for the specified storage sizes.

The function does not return anything, but generates and saves plot images for each selected day
and storage size combination.
		 :param daystep: is a value of the distanz of which days are choosed for plotting
		 :param speichergroessen: a list which size the battery could be
		 :param use_data_for_plot: If use_data_for_plot is True, the function reads the pre-processed data from the specified file
				and prints the keys of the dataframe.
		 :param filename: location where the pickle is found
		 :type df: expects a large df with the whole year
		 :return: list of filename
		"""
	list_of_days = list(range(1, 365, daystep))

	if use_data_for_plot:
		print(f'--- use pickle for data ---')
		df = pd.read_pickle(filename) # (f'documents/speichersimulation_optimiert_netzdienlich.pkl')

		print(f'--- Plot: Leistungsverlauf ---')


	if not use_data_for_plot:
		if filename:
			try:
				df = pd.read_pickle(filename)
			except Exception as e:
				print('Es hat was mit dem Daten aus Pickle auslesen nicht geklappt', e)

	for day in list_of_days:

		startday = day
		endday = startday + 1

		for size in speichergroessen:
			#plot_power(df=df,
			 #          startday=startday,
			  #         endday=endday,
			   #        size=size
			    #       )

			plot_histogram_sns(df=df,
			               startday=startday,
			               endday=endday,
			               size=size
			               )
