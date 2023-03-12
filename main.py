# Importieren aller benötigten Funktionen aus den Dateien

from gridfriendly import cal_grid_friendly
from own_consumption import cal_battery_own_consumption
from plot_histogram import plot_histogram
from plot_trend_of_power import plot_power
from read_in_all_data import read_in_all_data
from plot_for_selected_days import plot_for_selected_days
import imports_and_variables


def main():
	"""
	Responsible for running everything sequentially,
	main has also the option to jump over some calculation and get
	some csv data, by setting values to false or true
	"""
	# Call main() and store the returned values in variables
	eta, soc_max, soc_min, zeit, plt, pd, np, glob, math, \
		orginal_read, use_data_for_plot, plot_by_days, speichergroessen, soc_start, \
		startday, endday, daysteps = imports_and_variables.main()

	# Hauptfunktion, die alle Funktionen aufruft

	# Alle Funktionen ausführen
	data = read_in_all_data()
	own_consumption = cal_battery_own_consumption(data)
	grid_friendly = cal_grid_friendly(data)
	plot_for_selected_days(daystep=daysteps, speichergroessen=speichergroessen,
		                       base_data=data, soc_start=soc_start,
		                       use_data_for_plot=use_data_for_plot)

	plot_histogram(grid_friendly, own_consumption)
	plot_power(data)

	# print(len(base_data))
	if plot_by_days:
		plot_for_selected_days(daystep=daysteps, speichergroessen=speichergroessen,
		                       base_data=data, soc_start=soc_start,
		                       use_data_for_plot=use_data_for_plot
		                       )
	else:
		if use_data_for_plot:
			for size in speichergroessen:
				print(f"--- Simulation Batterie nach Eigenverbrauch mit {size} Wh---")
				batterypower_df, p_max_in, p_max_out, p_min_in, p_min_out = cal_battery_own_consumption(
						netz_pv=data,
						soc_start=soc_start,
						speichergroesse=size
				)

				print(f'--- Save Netz PV Speicher Eigenverbrauch als pickle ---')
				batterypower_df.to_pickle(f'documents/netz_pv_mit_speichersimulation_eigenverbrauch.pkl')
				batterypower_df.to_csv(f'documents/netz_pv_mit_speichersimulation_eigeverbrauch.csv')

				print(f"--- Simulation Batterie nach netzdienlich mit {size} Wh---")

				batterypower_df, df_day = cal_grid_friendly(df=batterypower_df,
				                                   soc_start=soc_start,
				                                   speichergroesse=size,
				                                   p_max_in=p_max_in,
				                                   p_max_out=p_max_out,
				                                   p_min_in=p_min_in,
				                                   p_min_out=p_min_out,
				                                   startday=startday,
				                                   endday=endday
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
			plot_power(df=df_day,
			           startday=0,
			           endday=1,
			           size=size
			           )
			plot_histogram(df=df_day,
			                     startday=0,
			                     endday=1,
			                     size=size
			                     )




# Makes the method main
if __name__ == "__main__":
	main()
