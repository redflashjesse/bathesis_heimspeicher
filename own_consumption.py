# Imports
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import math


def cal_battery_own_consumption(netz_pv, soc_max,
                                soc_min, zeit,
                                speichergroessen, c_out, c_in,
                                min_flow_threshold,
                                eta, soc_start=None
                                ):
	"""
		Rechnung um den Speicher zu simulieren, die Leistungswerte und den neuen
		State of Charge in einer Liste wiederzugeben.
		Je nach Varianten kann so eine mögliche Leistung aufgezeigt werden.
		Parameter und Daten zu einem Speicher sind hier hinterlegt.
		Dieser kann durch die Speichergroesse angepasst werden.
		Dies ist die Grundlage für eine Berechnung der möglichen Emissionen, bei gleicher Leistung.
		 :rtype: Dataframe
		 :param: Dataframe
		 :return: Dataframe
		 """

	for speichergroesse in speichergroessen:
		p_ges = speichergroesse / zeit  # [W] / [minute]
		p_max_out = p_ges * c_out
		p_min_out = p_max_out * min_flow_threshold
		p_max_in = p_ges * c_in
		p_min_in = p_max_in * min_flow_threshold

		# Efficiency included in the borderline cases, set new limits
		p_max_out *= eta
		p_min_out *= eta
		p_max_in = p_max_in * (1 + (1 - eta))
		p_min_in = p_min_in * (1 + (1 - eta))

		soc = []  # minute-wise soc
		p_delta = []  # the difference in power per minute
		soc_deltas = []  # the difference in state of charge
		netzbezug = []  # result amuont of power form the grid
		netzeinspeisung = []  # result amuont of power to the grid
		netzleistung = []  # grid power

		if soc_start:
			soc_akt = soc_start  # This represents an opportunity to specify a defined state of charge.
		else:
			soc_akt = soc_max / 2  # assumption: 45% charged at startup

		for index, row in netz_pv.iterrows():
			# Default: no change, no in, no out, p_soll = 0
			soc_ist = soc_akt
			soc_delta = 0
			p_ist = 0
			# Show network interface whether import or withdrawal takes place
			p_soll = float(row['GridPowerIn']) - float(row['GridPowerOut'])

			if p_soll > 0:  # check for positive
				# p_supply = p_soll * (1 + (1 - eta))  # factor in losses
				p_ist = min(p_max_out, p_soll)  # Threshold for upper bound

				if p_ist >= p_min_out:  # Threshold for lower bound
					soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
					soc_akt = soc_ist - soc_delta
				else:
					p_ist = 0
					soc_akt = 0

				# Capacity check, prevent depletion
				if soc_akt < soc_min:
					soc_akt = soc_ist
					p_ist = 0
					soc_delta = 0

			if p_soll < 0:  # Query whether storage can be carried out with excess current # case p_soll negative
				p_supply = abs(p_soll)
				p_ist = min(p_max_in, p_supply)

				if p_ist >= p_min_in:
					p_ist = -p_ist  # invert value to reflect incoming p
					soc_delta = ((p_ist * eta) / (speichergroesse / 100)) / 100
					soc_akt = soc_ist - soc_delta
				else:
					p_ist = 0
					soc_akt = 0

				# Capacity check, prevent overcharge
				if soc_akt > soc_max:
					soc_akt = soc_ist
					p_ist = 0
					soc_delta = 0

			# calculation of the grid power by intergration of a battery

			if p_ist > 0:
				p_netzbezug = row['GridPowerIn'] - max(p_ist, 0)
			if p_ist < 0:
				p_netzeinspeisung = row['GridPowerOut'] + min(p_ist, 0)
			else:  # p_ist==0:
				p_netzbezug = row['GridPowerIn']
				p_netzeinspeisung = row['GridPowerOut']

			p_netz = p_netzbezug - p_netzeinspeisung

			soc.append(soc_ist)
			p_delta.append(p_ist)
			soc_deltas.append(soc_delta)
			netzbezug.append(p_netzbezug)
			netzeinspeisung.append(p_netzeinspeisung)
			netzleistung.append(p_netz)

		netz_pv[f'p_delta_{speichergroesse}Wh_eigenverbrauch'] = p_delta
		netz_pv[f'current_soc_{speichergroesse}Wh_eigenverbrauch'] = soc
		netz_pv[f'soc_delta_{speichergroesse}Wh_eigenverbrauch'] = soc_deltas
		netz_pv[f'p_netzbezug_{speichergroesse}Wh_eigenverbrauch'] = netzbezug
		netz_pv[f'p_netzeinspeisung_{speichergroesse}Wh_eigenverbrauch'] = netzeinspeisung

	return netz_pv  # Leistungen_Speicher_eigenverbrauch
