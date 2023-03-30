# Imports
import math
import matplotlib.pyplot as plt


def plot_histogram(df, startday, endday, size, binsize=100):
	assert startday < endday

	date = df.index[startday * 1440].strftime('%Y-%m-%d')
	density = False
	plt.style.use('fivethirtyeight')
	start_idx = startday * 1440
	end_idx = endday * 1440
	fig, ax = plt.subplots()

	# Einlesen
	# Betrachtung der Leistungen am Netzpunkt ohne Quartierspeicher
	netzbezug_pure = df[f'GridPowerIn'][start_idx:end_idx]
	einspeisung_pure = df[f'GridPowerOut'][start_idx:end_idx]

	# Betrachtung der Leistungen am Netzpunkt mit Quartierspeicher nach Eigenverbrauchoptimiert
	netzbezug_eigen = df[f'p_netzbezug_{size}Wh_eigenverbrauch'][start_idx:end_idx]
	einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'][start_idx:end_idx]

	# Betrachtung der Leistungen am Netzpunkt mit Quartierspeicher nach Netzdienlichoptimiert
	netzbezug_netz = df[f'p_netzbezug_{size}Wh_netzdienlich'][start_idx:end_idx]
	einspeisung_netz = df[f'p_netzeinspeisung_{size}Wh_netzdienlich'][start_idx:end_idx]

	Leistung_pure = einspeisung_pure.mul(-1) + netzbezug_pure
	Leistung_eigenverbrauch = einspeisung_eigen.mul(-1) + netzbezug_eigen
	Leistung_netz = einspeisung_netz.mul(-1) + netzbezug_netz

	min_out = einspeisung_pure.max()
	bins_out = math.ceil(min_out / binsize)

	max_in = netzbezug_pure.max()
	bins_in = math.ceil(max_in / binsize)

	bins = bins_in + bins_out
	#bins = 25

	plt.hist([Leistung_pure],
	         bins=bins,
	         color=['blue'],
	         density=density,
	         edgecolor='black',
	         label='ohne Speicher',
	         alpha=0.6,
	         zorder=1
	         )

	plt.hist([Leistung_eigenverbrauch],
	         bins=bins,
	         color=['red'],
	         density=density,
	         edgecolor='black',
	         label='Speicher eigenverbrauch',
	         alpha=0.2,
	         zorder=2
	         )

	plt.hist([Leistung_netz],
	         bins=bins,
	         color=['yellow'],
	         density=density,
	         edgecolor='black',
	         label='Speicher netzdienlich',
	         alpha=0.5,
	         zorder=3
	         )  # , log=True, linewidth=1)

	plt.axvline(0, color='red')
	plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

	# We can also normalize our inputs by the total number of counts
	# axs[1].hist(dist1, bins=n_bins, density=True)

	# Now we format the y-axis to display percentage
	# axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))

	plt.title(f'Verteilung von Leistungen am {date}')
	plt.xlabel('Leistung in Wh')
	plt.ylabel('Häufigkeit')
	plt.tight_layout()
	plt.show()

	# Save the Plot as png
	fig.savefig(f'graphs/Histogramm_{date}.png')
