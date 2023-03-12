# Imports
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import math

def plot_histogram(df, startday, endday, size, binsize=100):
	assert startday < endday
	bins = 25
	date = df.index[startday * 1440]
	date = date.strftime('%Y-%m-%d')
	density = False
	plt.style.use('fivethirtyeight')
	fig, ax = plt.subplots()
	# Betrachtung der Leistungen am Netzpunkt ohne Quartierspeicher
	netzbezug_pure = df[f'GridPowerIn'][startday * 1440:endday * 1440]
	einspeisung_pure = df[f'GridPowerOut'][startday * 1440:endday * 1440]

	min_out = einspeisung_pure.max()
	print(f'{df.keys()=}')
	print(f'{einspeisung_pure=}')
	print(f'{min_out=}')
	bins_out = math.ceil(min_out / binsize)
	max_in = netzbezug_pure.max()
	bins_in = math.ceil(max_in / binsize)
	Leistung_pure = einspeisung_pure.mul(-1) + netzbezug_pure

	# Betrachtung der Leistungen am Netzpunkt mit Quartierspeicher nach Eigenverbrauchoptimiert
	netzbezug_eigen = df[f'p_netzbezug_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	min_out = einspeisung_eigen.max()
	bins_out = math.ceil(min_out / binsize)
	max_in = netzbezug_eigen.max()
	bins_in = math.ceil(max_in / binsize)
	Leistung_eigenverbrauch = einspeisung_eigen.mul(-1) + netzbezug_eigen

	# Betrachtung der Leistungen am Netzpunkt mit Quartierspeicher nach Netzdienlichoptimiert
	netzbezug_netz = df[f'p_netzbezug_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	einspeisung_netz = df[f'p_netzeinspeisung_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	min_out = einspeisung_netz.max()
	bins_out = math.ceil(min_out / binsize)
	max_in = netzbezug_netz.max()
	bins_in = math.ceil(max_in / binsize)
	Leistung_netz = einspeisung_netz.mul(-1) + netzbezug_netz

	print(min_out, max_in)
	print(type(round(min_out)), round(min_out))
	bins_einspeisung = list(range(int(round(min_out)), 0, int(round(min_out) / 10)))
	bins_netzbezug = list(range(int(round(max_in)), 0, int(round(min_out) / 10)))
	# plt.hist(netzbezug, bins=bins_in, density= True, edgecolor='black')
	plt.hist([Leistung_pure], bins=bins,  # [bins_out, bins_in],
	         color=['blue'  # , 'orange'
	                ], density=density, edgecolor='black', label='ohne Speicher',
	         alpha=0.6, zorder=1
	         )  # , log=True, linewidth=1)
	plt.hist([Leistung_eigenverbrauch], bins=bins,  # [bins_out, bins_in],
	         color=['red'  # , 'orange'
	                ], density=density, edgecolor='black', label='Speicher eigenverbrauch',
	         alpha=0.2, zorder=2
	         )  # , log=True, linewidth=1)
	plt.hist([Leistung_netz], bins=bins,  # [bins_out, bins_in],
	         color=['yellow'  # , 'orange'
	                ], density=density, edgecolor='black', label='Speicher netzdienlich',
	         alpha=0.5, zorder=3
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
	fig.savefig(f'graphs/Histogramm_{date}.png')


# plt.savefig(f'graphs/Histogramm_{date}.png'
# , dpi='figure', format=None, metadata=None,
# bbox_inches=None, pad_inches=0.1,
# facecolor='auto', edgecolor='auto',
# backend=None
# )