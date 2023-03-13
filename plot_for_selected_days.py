# Imports
import pandas as pd

from plot_trend_of_power import plot_power
from plot_histogram import plot_histogram


def plot_for_selected_days(df, daystep, speichergroessen, use_data_for_plot):
	"""
		Auswahl bestimmter Tag aus dem Jahresdatensatz, Auswahl erste Möglichkeit einzelne Tage auszuwählen
		zum Beisspiel zwei Tage im Monat, Daten für die NetzLeistung und PVleistung werden in
		geleichen Tagen ausgeswählt
		 :type df: expects a large df with the whole year
		 :rtype: object
		 :param: Name of the file that serves as input. Format : .csv
		 :return: list of filename
		"""
	list_of_days = list(range(1, 365, daystep))

	if use_data_for_plot:
		print(f'--- use pickle for data ---')
		batterypower_df = pd.read_pickle(f'documents/netz_pv_mit_speichersimulation_netzdienlich.pkl')

		print(f'--- Plot: Leistungsverlauf ---')
		print(batterypower_df.keys())

	if not use_data_for_plot:
		raise NotImplementedError()
		# TODO
		pass

	for day in list_of_days:

		startday = day
		endday = startday + 1

		for size in speichergroessen:
			plot_power(df=batterypower_df,
			           startday=startday,
			           endday=endday,
			           size=size
			           )
			plot_histogram(df=batterypower_df,
			               startday=startday,
			               endday=endday,
			               size=size
			               )
