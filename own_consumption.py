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
		The cal_battery_own_consumption() function is used to simulate a battery storage system
		and output the power values and new State of Charge (SOC) in a list. It takes several parameters,
		including the net power (pv power minus power from the grid), the maximum and minimum SOC values,
		the time, storage sizes, charging and discharging coefficients, minimum flow threshold, efficiency,
		and starting SOC (which is optional). The function calculates the maximum input and output power for
		the battery based on its storage size, and takes into account the efficiency factor in the borderline cases.

		The function then iterates over each minute in the netz_pv dataframe, which contains the power
		values from the grid and PV, and determines whether the battery should charge or discharge
		based on the net power value. If the net power is positive, the battery will discharge,
		and if it is negative, the battery will charge. The function then calculates the actual
		power to be supplied to or from the battery, based on the maximum input/output power
		and the minimum flow threshold, and checks if the battery is not overcharged or depleted.
		The function also calculates the grid power by integrating the battery and records the SOC,
		power delta, SOC delta, net power from the grid, power to the grid, and grid power in each
		iteration. Finally, the function returns a dataframe with all these values.

		 :param netz_pv: a pandas DataFrame containing the power input from the grid and the power output from photovoltaic cells
		 :param soc_max: the maximum state of charge of the battery (expressed as a percentage)
		 :param soc_min: the minimum state of charge of the battery (expressed as a percentage)
		 :param zeit: the duration of the simulation (expressed in minutes)
		 :param speichergroessen: a list of possible battery storage capacities (expressed in watt-minutes)
		 :param c_out: the discharge rate of the battery (expressed as a fraction of the storage capacity per minute)
		 :param c_in: the charge rate of the battery (expressed as a fraction of the storage capacity per minute)
		 :param min_flow_threshold: the minimum power flow rate (expressed as a fraction of the maximum power flow rate)
		 :param eta: the efficiency of the battery (expressed as a fraction)
		 :param soc_start: the initial state of charge of the battery (expressed as a percentage), optional, default is soc_max / 2.
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

			if p_soll > 0:  # check for positive (Netzbezug)
				# p_supply = p_soll * (1 + (1 - eta))  # factor in losses
				p_ist = min(p_max_out, p_soll)  # Threshold for upper bound

				if p_ist >= p_min_out:  # Threshold for lower bound
					soc_delta = ((p_ist * (1 + (1 - eta))) / (speichergroesse / 100)) / 100
					soc_akt = soc_ist - soc_delta
				else:
					p_ist = 0
					soc_delta = 0
					soc_akt = soc_ist

				# Capacity check, prevent depletion
				if soc_akt < soc_min:
					soc_akt = soc_ist
					p_ist = 0
					soc_delta = 0

			if p_soll < 0:  # Query whether storage can be carried out with excess current
				# case p_soll negative
				p_supply = abs(p_soll)
				p_ist = min(p_max_in, p_supply)

				if p_ist >= p_min_in:
					p_ist = -p_ist  # invert value to reflect incoming p
					soc_delta = ((p_ist * eta) / (speichergroesse / 100)) / 100
					soc_akt = soc_ist - soc_delta
				else:
					p_ist = 0
					soc_delta = 0
					soc_akt = soc_ist

				# Capacity check, prevent overcharge
				if soc_akt > soc_max:
					soc_akt = soc_ist
					p_ist = 0
					soc_delta = 0

			# calculation of the grid power by intergration of a battery
			if p_ist > 0:
				p_netzbezug = row['GridPowerIn'] - max(p_ist, 0)
				p_netzeinspeisung = 0
			elif p_ist < 0:
				p_netzeinspeisung = row['GridPowerOut'] + min(p_ist, 0)
				p_netzbezug = 0
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
		netz_pv[f'p_netzleistung_{speichergroesse}Wh_eigenverbrauch'] = netzleistung # TODO wird noch nicht im gesamten df aufgeführt

	return netz_pv  # Leistungen_Speicher_eigenverbrauch
