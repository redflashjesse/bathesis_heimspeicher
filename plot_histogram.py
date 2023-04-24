# Imports
import math
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_histogram_sns(df, startday, endday, size, binsize=25):
    # set dpi globally

    sns.set(rc={'figure.figsize': (15, 10)})
    sns.set(rc={'savefig.dpi': 500})
    sns.set(rc={'font.size': 20})


    assert startday < endday
    # This line sets the date to the start day of the data frame in the format of year-month-day
    date = df.index[startday * 1440].strftime('%Y-%m-%d')

    start_idx = startday * 1440
    end_idx = endday * 1440  # These lines set the start and end indices for the data to be plotted.

    netzbezug_pure = df[f'GridPowerIn'][start_idx:end_idx]
    einspeisung_pure = df[f'GridPowerOut'][start_idx:end_idx]

    netzbezug_eigen = df[f'p_netzbezug_{size}Wh_eigenverbrauch'][start_idx:end_idx]
    einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'][start_idx:end_idx]

    netzbezug_netz = df[f'p_netzbezug_{size}Wh_netzdienlich'][start_idx:end_idx]
    einspeisung_netz = df[f'p_netzeinspeisung_{size}Wh_netzdienlich'][start_idx:end_idx]

    leistung_pure = einspeisung_pure.mul(-1) + netzbezug_pure
    leistung_eigenverbrauch = einspeisung_eigen.mul(-1) + netzbezug_eigen
    leistung_netz = einspeisung_netz.mul(-1) + netzbezug_netz


    # Make a multiple-histogram of data-sets with different length.
    # x_multi = [leistung_pure, leistung_eigenverbrauch, leistung_netz]
    # colors = ['green', 'blue', 'orange']
    labels = ['ohne Speicher', 'Speicher eigenverbrauch', 'Soeicher netzdiehnlich']

    sns.set_style('whitegrid')
    ax = sns.displot(data=pd.DataFrame({labels[0]: leistung_pure,
                                   labels[1]: leistung_eigenverbrauch,
                                   labels[2]: leistung_netz}),
                kde=True,
                rug=True,
                legend=True,
                element="step",
                fill=False)
    sns.move_legend(ax, "upper right", bbox_to_anchor=(1.2, .8),  frameon=False)
# Increase tick label size
    plt.tick_params(axis='both', labelsize=20)
    plt.title(f'Verteilung von Leistungen am {date}')
    plt.xlabel('Leistung in Wh', fontsize=16)
    plt.ylabel('Häufigkeit', fontsize=16)
    plt.tight_layout()
    plt.savefig(f'graphs/Histogramm_{date}.png', bbox_inches='tight')
    # Add legend outside the plot
    # plt.legend(loc='upper right')
    plt.show()
    # Save the Plot as png
    # fig.savefig(f'graphs/Histogramm_{date}.png')


def plot_histogram(df, startday, endday, size, binsize=25):
    """
It first defines the start and end dates for the data to be plotted, and sets the plotting style
to "fivethirtyeight". It then reads in the power consumption data for a grid connection,
and also for two scenarios where a storage system is used: one optimized for self-consumption,
and one optimized for grid services. The difference between power consumption and
power production (feed-in) is calculated for each scenario.

The script then determines the bin sizes for the histogram based on the maximum power consumption
and feed-in values. It then plots three histograms, one for each scenario, with the x-axis representing
the difference between power consumption and feed-in (i.e., net power flow), and the y-axis representing
the frequency of occurrence of each value. The three histograms are colored blue, red, and yellow
and labeled "without storage", "self-consumption optimized storage", and "grid service optimized storage".
A red vertical line is plotted at the zero net power flow value, and a legend is displayed.

	:param df: dataframe which contains all data, own consumption, grid friendly and without a battery
	:param startday: contains a number from 1 to 365, which stand for a day in a year
	:param endday: number one higher than the startday
	:param size: batterysize in Wh
	:param binsize: size of value which are group together
	"""
    assert startday < endday

	# This line sets the date to the start day of the data frame in the format of year-month-day
    date = df.index[startday * 1440].strftime('%Y-%m-%d')

    density = False  # This line sets the density of the histogram to be false.
    plt.style.use('fivethirtyeight')
    start_idx = startday * 1440
    end_idx = endday * 1440  # These lines set the start and end indices for the data to be plotted.
    fig, ax = plt.subplots()
    plt.rcParams.update({'font.size': 20})  # increase label size

    # The following three blocks of code read in and store the power data for different scenarios:
    # one without a storage system (netzbezug_pure and einspeisung_pure),
    # one with a storage system optimized for self-consumption (netzbezug_eigen and einspeisung_eigen),
    # and one with a storage system optimized for grid services (netzbezug_netz and einspeisung_netz).
    netzbezug_pure = df[f'GridPowerIn'][start_idx:end_idx]
    einspeisung_pure = df[f'GridPowerOut'][start_idx:end_idx]

    netzbezug_eigen = df[f'p_netzbezug_{size}Wh_eigenverbrauch'][start_idx:end_idx]
    einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'][start_idx:end_idx]

    netzbezug_netz = df[f'p_netzbezug_{size}Wh_netzdienlich'][start_idx:end_idx]
    einspeisung_netz = df[f'p_netzeinspeisung_{size}Wh_netzdienlich'][start_idx:end_idx]

    leistung_pure = einspeisung_pure.mul(-1) + netzbezug_pure
    leistung_eigenverbrauch = einspeisung_eigen.mul(-1) + netzbezug_eigen
    leistung_netz = einspeisung_netz.mul(-1) + netzbezug_netz

    # calculate the minimum output power and number of output power bins
    min_out = einspeisung_pure.max()
    bins_out = math.ceil(min_out / binsize)

    # calculate the maximum input power and number of input power bins
    max_in = netzbezug_pure.max()
    bins_in = math.ceil(max_in / binsize)

    # calculates the total number of power bins to be used in the histogram
    num_bin = bins_in + bins_out

    bar_width = 10  # set the width of each bar

    # Make a multiple-histogram of data-sets with different length.
    x_multi = [leistung_pure, leistung_eigenverbrauch, leistung_netz]
    colors = ['green', 'blue', 'orange']
    labels = ['ohne Speicher', 'Speicher Eigenverbrauch', 'Speicher netzdienlich']
    # n, bins, patches =\
    ax.hist(x_multi, num_bin,
            histtype='stepfilled',
            color=colors,
            label=labels,
            # width=bar_width,
            density=density,
            alpha=0.1)

    # plt.axvline(0, color='red', alpha=0.2, label='Nulllinie')  # creates a vertical line at the zero PowerPoint
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    # he next three lines create histograms for each power scenario and plot them on the same graph.

    # We can also normalize our inputs by the total number of counts
    # axs[1].hist(dist1, bins=n_bins, density=True)

    # Now we format the y-axis to display percentage
    # axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))

    # Increase tick label size
    plt.tick_params(axis='both', labelsize=20)
    plt.title(f'Verteilung von Leistungen am {date}')
    plt.xlabel('Leistung in Wh', fontsize=16)
    plt.ylabel('Häufigkeit', fontsize=16)
    plt.tight_layout()
    plt.show()

    # Save the Plot as png
    fig.savefig(f'graphs/Histogramm_{date}.png')
