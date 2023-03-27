from matplotlib import pyplot as plt

# starts of plots
def plot_power(df, startday, endday, size):
	assert startday < endday
	date = df.index[startday * 1440 + 200]
	date = date.strftime('%Y-%m-%d')
	fig, ax = plt.subplots()

	# Leistungsverlauf ohne Quartierspeicher
	netzbezug_pure = df[f'GridPowerIn'][startday * 1440:endday * 1440]
	einspeisung_pure = df[f'GridPowerOut'][startday * 1440:endday * 1440]
	einspeisung_pure = einspeisung_pure.mul(-1)
	plt.plot(netzbezug_pure, label='Netzbezug ohne Speicher', alpha=0.4, zorder=1)
	plt.plot(einspeisung_pure, label='Einspeisung ohne Speicher', alpha=0.4, zorder=1)

	# Leistungsverlauf mit Quatierspeicher nach eigenverbrauch
	netzbezug_eigen = df[f'p_netzbezug_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_eigenverbrauch'][startday * 1440:endday * 1440]
	einspeisung_eigen = einspeisung_eigen.mul(-1)
	plt.plot(netzbezug_eigen, label='Speicher Eigenverbrauch', alpha=0.4, zorder=2)
	plt.plot(einspeisung_eigen, label='Speicher Eigenverbrauch', alpha=0.4, zorder=2)

	# Leistungsverlauf mit Quartierspeicher nach netzdienlich

	netzbezug_eigen = df[f'p_netzbezug_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	einspeisung_eigen = df[f'p_netzeinspeisung_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]
	einspeisung_eigen = einspeisung_eigen.mul(-1)
	# Ladeleistung = df[f'p_ladeleistung_{size}Wh_netzdienlich'][startday * 1440:endday * 1440]

	plt.plot(netzbezug_eigen, label='Speicher netzdienlich', alpha=0.4, zorder=3)
	plt.plot(einspeisung_eigen, label='Speicher netzdienlich', alpha=0.4, zorder=3)
	# plt.fill_between(Ladeleistung, y2= 0, label='Ladeleistung des Speichers', alpha=0.4, zorder=3)

	plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
	ax.xaxis.set_ticks_position('bottom')  # the rest is the same
	# plt.ylim(1000, )
	ax.grid(True)
	plt.xticks(rotation='vertical')  # range(len(labels)), labels,
	# plt.gcf().set_size_inches(15, 5)
	plt.title(f'Leistungsverlauf')
	plt.suptitle(f'für {date}')
	plt.xlabel('Zeit in h')
	plt.ylabel('Leistung in Wh')
	plt.tight_layout()
	plt.show()
	fig.savefig(f'graphs/Leistungsverlauf_{date}.png')
