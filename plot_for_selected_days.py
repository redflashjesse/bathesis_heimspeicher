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
	batterypower_df.read
	for day in list_of_days:

		startday = day
		endday = startday + 1

		if use_data_for_plot:
			for size in speichergroessen:
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
				plot_histogram(df=batterypower_df, startday=startday, endday=endday,
				                     size=size
				                     )

