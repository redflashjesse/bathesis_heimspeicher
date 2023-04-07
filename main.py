# Imports
import matplotlib.pyplot as plt
import pandas as pd

# Importieren aller benötigten Funktionen aus den Dateien
from gridfriendly import cal_grid_friendly
from own_consumption import cal_battery_own_consumption
from plot_for_selected_days import plot_for_selected_days
from plot_histogram import plot_histogram
from plot_trend_of_power import plot_power
from read_in_all_data import read_in_all_data

# Global Battery Params
eta = 0.9  # Efficiency factor
soc_max = 0.9  # [range: 0-1 ]
soc_min = 0.1  # [range: 0-1 ]
zeit = 60  # [minute]
c_out = 1  # Coulombe Factor, depends on battery rating
c_in = 0.5  # Coulombe factor
min_flow_threshold = 0.1  # threshold for minimal flow for action to be taken [range: 0-1] in %

# set dpi globally
plt.rcParams['savefig.dpi'] = 500
plt.rcParams["figure.figsize"] = (15, 10)

orginal_read = False
use_data_for_plot = True  # or pickle
plot_by_days = False
set_pickle_by_orginal = False  # True= read all csv data or False = read pickle for data
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
filename = f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl'


def main():
    """
    Responsible for running everything sequentially,
    main has also the option to jump over some calculation and get
    some csv data, by setting values to false or true
    """

    # Hauptfunktion, die alle Funktionen aufruft

    if set_pickle_by_orginal:
        # Alle Funktionen ausführen
        data = read_in_all_data()
        print(f"--- Simulation Batterie nach Eigenverbrauch ---")
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
        print(f'--- Save Optimized Eigenverbrauchsopimiert als pickle ---')
        pkl_filename = f'documents/speichersimulation_optimiert_eigenverbrauch.pkl'
        own_consumption.to_pickle(pkl_filename)
        print(f"--- Simulation Batterie nach netzdienlich ---")
        grid_friendly = cal_grid_friendly(df=own_consumption,
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
        print(f'--- Save Optimized Netzdienlich als pickle ---')
        pkl_filename = f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl'
        grid_friendly.to_pickle(pkl_filename)
        grid_friendly.to_csv(f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.csv')
        print(grid_friendly.keys())

    else:
        pkl_filename = f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl'
        grid_friendly = pd.read_pickle(pkl_filename)

    print(f'--- Start plots ---')
    plot_for_selected_days(daystep=daysteps,
                           speichergroessen=speichergroessen,
                           df=grid_friendly,
                           use_data_for_plot=use_data_for_plot,
                           filename=pkl_filename
                           )

    """
    print(f'--- Plot: Leistungsverlauf ---')
    # print(batterypower_df.keys())
    # for day in selection_days_start:
    #   startday = day
    for size in speichergroessen:
        plot_power(df=grid_friendly,
                   startday=0,
                   endday=1,
                   size=size
                   )
        plot_histogram(df=grid_friendly,
                       startday=0,
                       endday=1,
                       size=size
                       )
    """


# Makes the method main
if __name__ == "__main__":
    main()
