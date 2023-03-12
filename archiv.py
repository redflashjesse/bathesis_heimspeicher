

"""
def cal_battery_gridfriendly(df, speichergroesse,
                             p_max_in, p_max_out, p_min_in, p_min_out,
                             soc_start=None
                             ):
	max_soc_reached = max(df[f'current_soc_{speichergroesse}Wh_eigenverbrauch'])
	print(max_soc_reached)
	netzeinspeisung_max = max(df[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'])
	print(netzeinspeisung_max)

	# Check if there is even enough overproduction
	if (netzeinspeisung_max < p_max_in):
		df[f'p_delta_{speichergroesse}Wh_netzdienlich'] = df[f'p_delta_{speichergroesse}Wh_eigenverbrauch']
		df[f'current_soc_{speichergroesse}Wh_netzdienlich'] = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch']
		df[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = df[f'soc_delta_{speichergroesse}Wh_eigenverbrauch']
		df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = df[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch']
		df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = df[
			f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch']
		return df  # Leistungen_Speicher_eigenverbrauch

	df[f'p_delta_{speichergroesse}Wh_netzdienlich'] = df[f'p_delta_{speichergroesse}Wh_eigenverbrauch']
	df[f'current_soc_{speichergroesse}Wh_netzdienlich'] = df[f'current_soc_{speichergroesse}Wh_eigenverbrauch']
	df[f'soc_delta_{speichergroesse}Wh_netzdienlich'] = df[f'soc_delta_{speichergroesse}Wh_eigenverbrauch']
	df[f'p_netzbezug_{speichergroesse}Wh_netzdienlich'] = df[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch']
	df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'] = df[
		f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch']

	df_pool = df

	while (max_soc_reached <= soc_max + 0.01):  # End Condition TODO: Cheat rausnehmen
		netzeinspeisung_max = max(df_pool[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'])
		surplus = netzeinspeisung_max - p_max_in
		# where is the max?
		index = df_pool[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'].idxmax()
		df[f'p_netzeinspeisung_{speichergroesse}Wh_netzdienlich'][index] = surplus
		df[f'p_delta_{speichergroesse}Wh_netzdienlich'][index] = p_max_in
		# calc addition to battery
		soc_delta = ((p_max_in * eta) / (speichergroesse / 100)) / 100
		df[f'soc_delta_{speichergroesse}Wh_netzdienlich'][index] = soc_delta
		df[f'current_soc_{speichergroesse}Wh_netzdienlich'][index] += soc_delta
		# adapt new soc
		max_soc_reached = df[f'current_soc_{speichergroesse}Wh_netzdienlich'][index]
		df_pool = df_pool.drop(labels=index)
	return df
	"""
