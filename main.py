# Imports
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import math

# Importieren aller benötigten Funktionen aus den Dateien

from gridfriendly import cal_grid_friendly
from own_consumption import cal_battery_own_consumption
from plot_histogram import plot_histogram
from plot_trend_of_power import plot_power
from read_in_all_data import read_in_all_data
from plot_for_selected_days import plot_for_selected_days

# Global Battery Params
eta = 0.9  # Efficiency factor
soc_max = 0.9  # [range: 0-1 ]
soc_min = 0.1  # [range: 0-1 ]
zeit = 60  # [minute]
c_out = 1  # Coulombe Factor, depends on battery rating
c_in = 0.5  # Coulombe factor
min_flow_threshold = 0.1  # threshold for minimal flow for action to be taken [range: 0-1] in %

# todo felht noch die Liste der zu betrachtenden Tage und der Speichergrößen

# set dpi globally
plt.rcParams['savefig.dpi'] = 500
plt.rcParams["figure.figsize"] = (15, 10)

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


def main():
	"""
	Responsible for running everything sequentially,
	main has also the option to jump over some calculation and get
	some csv data, by setting values to false or true
	"""

	# Hauptfunktion, die alle Funktionen aufruft

	# Alle Funktionen ausführen
	data = read_in_all_data()
	own_consumption = cal_battery_own_consumption(netz_pv=data,
	                                              speichergroessen=speichergroessen,
	                                              eta=eta,
	                                              soc_max=soc_max,
	                                              soc_min=soc_min,
	                                              zeit=zeit,
	                                              soc_start=soc_start,
	                                              c_out=c_out,
	                                              c_in=c_in,
	                                              min_flow_threshold=min_flow_threshold
	                                              )

	grid_friendly = cal_grid_friendly(df=data,
	                                  speichergroessen=speichergroessen,
	                                  eta=eta,
	                                  soc_max=soc_max,
	                                  soc_min=soc_min,
	                                  zeit=zeit,
	                                  soc_start=soc_start,
	                                  c_out=c_out,
	                                  c_in=c_in,
	                                  min_flow_threshold=min_flow_threshold
	                                  )

	plot_for_selected_days(daystep=daysteps,
	                       speichergroessen=speichergroessen,
	                       base_data=data,
	                       soc_start=soc_start,
	                       use_data_for_plot=use_data_for_plot
	                       )

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

				batterypower_df, df_day = cal_grid_friendly(df=batterypower_df, soc_max=soc_max, soc_min=soc_min, zeit=zeit,
				                                            speichergroessen=speichergroessen, soc_start=soc_start)

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
