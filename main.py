# Imports
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta

# import of all needed funktion form other py-skripts
from gridfriendly import cal_grid_friendly
from own_consumption import cal_battery_own_consumption
from plot_for_selected_days import plot_for_selected_days
from read_in_all_data import read_in_all_data

# Global battery params
eta = 0.9  # Efficiency factor
soc_max = 0.9  # [range: 0-1 ]
soc_min = 0.1  # [range: 0-1 ]
zeit = 60  # [minute]
c_out = 1  # Coulombe Factor, depends on battery rating
c_in = 0.5  # Coulombe factor
min_flow_threshold = 0.1  # threshold for minimal flow for action to be taken [range: 0-1] in %

# set dpi globally
plt.rcParams['savefig.dpi'] = 800
plt.rcParams["figure.figsize"] = (25, 10)

# Global params for setting up the simulation
# variables to decide which data to use, in case of True, the data is read from csv, else from pickle, which been created by previous run

# TODO: decide if the data should be read from csv or the pickle, than run the main to simulate the battery usecase for houses or quarters

orginal_read = False
use_data_for_plot = False  # False-> pickle
plot_by_days = False
set_pickle_by_orginal = False  # True= read all csv data or False = read pickle for data
# speichergroessen gives the range and the size of the battery in Wh
speichergroessen = list(range(6_000, # start
                              30_000 + 1, # end
                              2_000)) # step # in Wh
# speichergroessen = [12_000] # simulate only one size or more by adding more values
# soc_start is use to set the start value of the battery, if None, the value is set to soc_max/2
soc_start = None  # input as float between 0.1,0,9; default = 0.45
# selection_days_start is used by plotting funktion to plot only a few days of interest
# selection_days_start = list(range(4, # start
#                                365, # end
#                               20)) # step # in days for the year
# this option is jump into the middle of the year
startday = 150
endday = startday + 1
# daysteps gives the option for plotting regularly spaced days
daysteps = 15
# filename for pickle, which is used to save the data of the simulation
filename = f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl'

# set the start day for the comparison, to get the data out of the simulation process, to check how does the way of optimization works
comparison_day = 140

def main():
    """
    Responsible for running everything sequentially,
    main has also the option to jump over some calculation and get
    some csv data, by setting values to false or true
    """

    # main function, which contains funktion and called them in a right order

    if set_pickle_by_orginal:
        # run all funktion to read in the data, calculate the battery flow and save the data as pickle
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
        pkl_filename_eigen = f'documents/speichersimulation_optimiert_eigenverbrauch.pkl'
        own_consumption.to_pickle(pkl_filename_eigen)
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
                                          min_flow_threshold=min_flow_threshold,
                                          comparison_day=comparison_day
                                          )

        print(f'--- Save Optimized Netzdienlich als pickle ---')
        pkl_filename = f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl'
        grid_friendly.to_pickle(pkl_filename)
        grid_friendly.to_csv(f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.csv')

        print('Save comparison df')
        # save_comparison_df(grid_friendly, speichergroessen, day=180)

    else:
        pkl_filename = f'documents/speichersimulation_optimiert_eigenverbrauch_netzdienlich.pkl'
        grid_friendly = pd.read_pickle(pkl_filename)

    print(grid_friendly.columns)
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
    print(f'--- Finish ---')

# Makes the method main
if __name__ == "__main__":
    main()
