import glob
import math as m

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

# Parameters TODO more general approach for other Electrolysers (here: Stuart HRI)
koh_weight_concentration = 30  # %
anode_surface = 0.03  # m^2
cathode_surface = 0.03  # m^2
anode_thickness = 0.002  # m
cathode_thickness = 0.002  # m
anode_membrane_gap = 0.00125  # m
cathode_membrane_gap = 0.00125  # m
membrane_surface_area = 0.03  # m^2
limiting_current_density = 300000  # A/m^2 (limiting current density)
standard_temperature = 25  # °C (Room Temperature)
standard_temperature = standard_temperature + 273.15  # K

__FARADAY_CONST: float = 96485.3321  # As/mol
__IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)


def calculate_bubble_rate_coverage(current: float, temperature: float) -> float:
    # TODO Check variation in Formula from Olivier Paper (2 instead of 0.3)
    bubble_rate_coverage = (-97.25 + 182 * (temperature / standard_temperature) - 84 * (
                temperature / standard_temperature) ** 2) * (
                                   (current / cathode_surface) / limiting_current_density) ** 0.3

    return bubble_rate_coverage


def calculate_anode_activation_current(activation_overvoltage: float, temperature: float) -> float:
    alpha_a = 0.0675 + 0.00095 * temperature
    exchange_current_density = 30.4 - 0.206 * temperature + 0.00035 * temperature ** 2  # ma/cm2 ?
    exchange_current_density = exchange_current_density / 1000.0  # A/cm2

    factor = (2 * __FARADAY_CONST * activation_overvoltage) / (
                __IDEAL_GAS_CONST * temperature)
    current_density_anode = exchange_current_density * (m.exp(alpha_a * factor) - m.exp(-(1 - alpha_a) * factor))

    return current_density_anode


def calculate_cathode_activation_current(activation_overvoltage: float, temperature: float) -> float:
    alpha_c = 0.1175 + 0.00095 * temperature
    exchange_current_density = 13.72491 - 0.09055 * temperature + 0.09055 * temperature ** 2
    exchange_current_density = exchange_current_density / 1000.0  # A/cm2

    factor = (2 * __FARADAY_CONST * activation_overvoltage) / (
                __IDEAL_GAS_CONST * temperature)
    current_density_cathode = exchange_current_density * (m.exp(alpha_c * factor) - m.exp(-(1 - alpha_c) * factor))

    return current_density_cathode


def generate_activation_overvoltage_lookup():
    # Input Variables
    # temperatures = [22.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0]  # °C
    temperatures = np.linspace(22.0, 160.0, 100)
    activation_overvoltages = np.linspace(0, 1, 5000)
    current_densities = np.linspace(0, 0.5, 1000)

    lookup_temperatures = []
    lookup_v_activation_anode = []
    lookup_v_activation_cathode = []
    lookup_current_densities = []

    for t in range(len(temperatures)):
        current_densities_cathode = []
        current_densities_anode = []

        temperature = temperatures[t]
        temperature = temperature + 273.15  # K

        for i in range(len(activation_overvoltages)):
            current_densities_anode.append(calculate_anode_activation_current(activation_overvoltages[i], temperature))
            current_densities_cathode.append(
                calculate_cathode_activation_current(activation_overvoltages[i], temperature))

        interpolation_cathode = interpolate.interp1d(current_densities_cathode, activation_overvoltages,
                                                     fill_value='extrapolate')
        interpolation_anode = interpolate.interp1d(current_densities_anode, activation_overvoltages,
                                                   fill_value='extrapolate')

        for j in range(len(current_densities)):
            v_activation_cathode = interpolation_cathode(current_densities[j])
            v_activation_anode = interpolation_anode(current_densities[j])
            lookup_v_activation_anode.append(v_activation_anode)
            lookup_v_activation_cathode.append(v_activation_cathode)
            lookup_temperatures.append(temperature - 273.15)
            lookup_current_densities.append(current_densities[j])

    lookup_v_activation_cathode = np.array(lookup_v_activation_cathode)
    lookup_v_activation_anode = np.array(lookup_v_activation_anode)
    lookup_temperatures = np.array(lookup_temperatures)
    lookup_current_densities = np.array(lookup_current_densities)

    # Create lookup table for alkaline electrolyser cell activation overpotential from current densitiy
    dict1 = {'temperature in °C': lookup_temperatures, 'current density in A/cm2': lookup_current_densities,
             'cathode activation voltage in V': lookup_v_activation_cathode,
             'anode activation voltage in V': lookup_v_activation_anode}
    df1 = pd.DataFrame(dict1)
    df1.to_csv('activation_overpotential_lookup_alkaline.csv', index=False)


def display_example(temperature: float, compare: bool):
    temperature = temperature + 273.15
    activation_overvoltages = np.linspace(0, 1, 10000)

    current_densities_cathode = []
    current_densities_anode = []

    for j in range(len(activation_overvoltages)):
        current_densities_anode.append(calculate_anode_activation_current(activation_overvoltages[j], temperature))
        current_densities_cathode.append(calculate_cathode_activation_current(activation_overvoltages[j], temperature))

    current_densities = np.linspace(0, 0.5, 1000)
    interpolation_cathode = interpolate.interp1d(current_densities_cathode, activation_overvoltages,
                                                 fill_value='extrapolate')
    interpolation_anode = interpolate.interp1d(current_densities_anode, activation_overvoltages,
                                               fill_value='extrapolate')

    v_activation_total = []
    for j1 in range(len(current_densities)):
        current = current_densities[j1] * anode_surface * 10000
        bubble_rate_coverage = calculate_bubble_rate_coverage(current, temperature)
        electrode_surface_nom = anode_surface * (1 - bubble_rate_coverage)
        current_density = current / (electrode_surface_nom * 10000)  # A/cm2
        v_activation_cathode = interpolation_cathode(current_density)
        v_activation_anode = interpolation_anode(current_density)
        v_activation_total.append(v_activation_cathode + v_activation_anode)

    plt.subplot(111)
    plt.ylabel('Activation overpotential in V')
    plt.xlabel('Current density in A/cm2')
    plt.title('Activation overpotential')
    plt.grid(True)
    plt.plot(current_densities, v_activation_total)
    if compare:
        # Compare activation overpotential curves from source paper
        legend = []
        legend.append('Calculated activation overpotential at ' + str(temperature - 273.15) + '°C')

        activation_curve_path = 'ui_curves/activation_overpotential_alkaline\\'
        u_i_files = glob.glob(activation_curve_path + '*.csv')
        for curve in u_i_files:
            excelfile = pd.read_csv(curve)
            file_current_densities = excelfile.iloc[:, 0]
            file_activation_voltages = excelfile.iloc[:, 1]
            plt.plot(file_current_densities.values, file_activation_voltages.values, linewidth=2)
            legend.append(curve[len(activation_curve_path):len(curve) - 4])

        plt.legend(legend)

    plt.show()


"""Command Section"""
# generate_activation_overvoltage_lookup()
# display_example(25, compare=True)