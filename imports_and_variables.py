
def main():
    # Imports
    from datetime import timedelta
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import glob
    import math

    # Global Battery Params

    eta = 0.9  # Efficiency factor
    soc_max = 0.9  # [range: 0-1 ]
    soc_min = 0.1  # [range: 0-1 ]
    zeit = 60  # [minute]

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

    # Return everything
    return eta, soc_max, soc_min, zeit, plt, pd, np, glob, math, \
        orginal_read, use_data_for_plot, plot_by_days, speichergroessen, \
        soc_start, startday, endday, daysteps


# Makes the method main
if __name__ == "__main__":
	main()