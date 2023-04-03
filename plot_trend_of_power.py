from matplotlib import pyplot as plt


# starts of plots
def plot_power(df, startday, endday, size):
	"""
The function plot_power plots the power profile of a power supply system operated with a district storage.
The function takes as input a DataFrame (df) with power data, a start day (startday) and an end day (endday),
and the size of the district storage (size). The function first checks if the start day is less than
the end day to ensure that the data is correct. Then, the start day's date is converted
and saved in the "YYYY-MM-DD" format.

Three power profiles are plotted. First, the grid power purchase (GridPowerIn) and the feed-in (GridPowerOut)
without a district storage are displayed. Then, the power profiles with the district storage after
self-consumption and grid-supportive operation are displayed. For each power profile,
the data is selected from the DataFrame according to the start and end days,
and the corresponding plots are created. The charging power of the district storage is not plotted in this case.

The plots are created using the matplotlib package and displayed in a window.
Additionally, an image file of the plot in PNG format is saved in the "graphs" folder.
The axis labels and the plot title are automatically generated.
	:param df: dataframe which contains all data, own consumption, grid friendly and without a battery
	:param startday: contains a number from 1 to 365, which stand for a day in a year
	:param endday: number one higher then the startday
	:param size: batterysize in Wh
	"""
	assert startday < endday
	date = df.index[startday * 1440 + 200]
	date = date.strftime('%Y-%m-%d')
	fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
	plt.rcParams.update({'font.size': 20})  # increase label size

	# Power profile without storage
	netzbezug_pure = df[f'GridPowerIn'][startday * 1440:endday * 1440]
	einspeisung_pure = df[f'GridPowerOut'][startday * 1440:endday * 1440]
	einspeisung_pure = einspeisung_pure.mul(-1)
	ax1.plot(netzbezug_pure, label='Netzbezug ohne Speicher', color='limegreen', alpha=0.4, zorder=3)
	ax1.plot(einspeisung_pure, label='Einspeisung ohne Speicher', color='seagreen', alpha=0.3, zorder=3)

	# Power profile with a storage, runs after own consumtion
	netzbezug_eigen = df[f'p_netzbezug_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	einspeisung_eigen = einspeisung_eigen.mul(-1)
	ax1.plot(netzbezug_eigen, label='Netzbezug Eigenverbrauch', color='mediumblue', alpha=0.4, zorder=2)
	ax1.plot(einspeisung_eigen, label='Einspeisung Eigenverbrauch', color='cornflowerblue', alpha=0.4, zorder=2)

	# Power profile with a storage, runs after grid friendly
	netzbezug_netzdienlich = df[f'p_netzbezug_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	einspeisung_netzdienlich = df[f'p_netzeinspeisung_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	einspeisung_netzdienlich = einspeisung_netzdienlich.mul(-1)
	# Ladeleistung = df[f'p_ladeleistung_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]

	ax1.plot(netzbezug_netzdienlich, label='Netzbezug netzdienlich', color='orangered', alpha=0.4, zorder=1)
	ax1.plot(einspeisung_netzdienlich, label='Einspeisung netzdienlich', color='tomato', alpha=0.4, zorder=1)
	# plt.fill_between(Ladeleistung, y2= 0, label='Ladeleistung des Speichers', alpha=0.4, zorder=3)

	# Add SOC data on the secondary y-axis
	#ax2 = ax1.twinx()
	ax2.plot(df[f'current_soc_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440],
			 color='blue',
			 label='SOC eigenverbrauch',
			 alpha=1, linewidth=0.5)
	ax2.plot(df[f'current_soc_{size}Wh_netzdienlich'][startday * 1440:endday * 1440],
			 color='orange',
			 label='SOC netzdienlich',
			 alpha=1, linewidth=0.5)  # SOC plot
	ax2.set_ylabel('SOC in %')
	ax2.set_ylim([0, 1])
	ax2.grid(True)

	# call legend() twice to create separate legends for each axis
	lines, labels = ax1.get_legend_handles_labels()
	lines2, labels2 = ax2.get_legend_handles_labels()
	ax1.legend(lines + lines2, labels + labels2, bbox_to_anchor=(1.05, 1.0), loc='upper left')

	#plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
	#ax2.legend(bbox_to_anchor=(1.05, 0.85), loc='upper left')  # add legend for the SOC plot
	ax1.xaxis.set_ticks_position('bottom')  # the rest is the same
	# plt.ylim(1000, )
	ax1.grid(True)
	ax1.tick_params(axis='x', labelrotation=90)
	ax2.tick_params(axis='x', labelrotation=90)
	# Increase tick label size
	plt.tick_params(axis='both', labelsize=16)

	# plt.gcf().set_size_inches(15, 5)
	fig.suptitle(f'Leistungsverlauf für {date} mit {size} Wh')
	ax2.set_title('SOC Verlauf')
	ax1.set_title('Netzleistung')
	#plt.suptitle(f'für {date}')
	fig.supxlabel('Zeit in h')
	ax1.set_ylabel('Leistung in Wh')
	#plt.ylabel('Leistung in Wh')
	plt.tight_layout()
	plt.show()
	fig.savefig(f'graphs/Leistungsverlauf_{date}_{size}Wh.png')
# # Remove vertical space between axes
# fig.subplots_adjust(hspace=0)