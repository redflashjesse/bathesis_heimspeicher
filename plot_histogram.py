# Imports
import math
import matplotlib.pyplot as plt


def plot_histogram(df, startday, endday, size, binsize=100):
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
	:param endday: number one higher then the startday
	:param size: batterysize in Wh
	:param binsize: size of value which are group together
	"""
	assert startday < endday


	date = df.index[startday * 1440].strftime('%Y-%m-%d') #  This line sets the date to the start day of the data frame in the format of year-month-day
	density = False # This line sets the density of the histogram to be false.
	plt.style.use('fivethirtyeight')
	start_idx = startday * 1440
	end_idx = endday * 1440 # These lines set the start and end indices for the data to be plotted.
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

	Leistung_pure = einspeisung_pure.mul(-1) + netzbezug_pure
	Leistung_eigenverbrauch = einspeisung_eigen.mul(-1) + netzbezug_eigen
	Leistung_netz = einspeisung_netz.mul(-1) + netzbezug_netz

	# calculate the minimum output power and number of output power bins
	min_out = einspeisung_pure.max()
	bins_out = math.ceil(min_out / binsize)

	# calculate the maximum input power and number of input power bins
	max_in = netzbezug_pure.max()
	bins_in = math.ceil(max_in / binsize)

	# calculates the total number of power bins to be used in the histogram
	bins = bins_in + bins_out
	#bins = 25

	bar_width = 1 / 3  # set the width of each bar

	# The next three lines create histograms for each power scenario and plot them on the same graph.
	plt.hist([Leistung_pure],
			 bins=bins,
			 color=['green'],
			 density=density,
			 edgecolor='black',
			 label='ohne Speicher',
			 alpha=0.2,
			 zorder=2,
			 width=bar_width-1
			 )

	plt.hist([Leistung_eigenverbrauch],
			 bins=bins,
			 color=['blue'],
			 density=density,
			 edgecolor='black',
			 label='Speicher eigenverbrauch',
			 alpha=0.3,
			 zorder=2,
			 width=bar_width
			 )

	plt.hist([Leistung_netz],
			 bins=bins,
			 color=['orange'],
			 density=density,
			 edgecolor='black',
			 label='Speicher netzdienlich',
			 alpha=0.5,
			 zorder=2,
			 width=bar_width+1
			 )  # , log=True, linewidth=1)

	plt.axvline(0, color='red')  # creates a vertical line at the zero power point
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


"""
	
	         """
