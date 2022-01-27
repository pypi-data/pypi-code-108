"""
    This script uses relationships proposed in:

    "New multi-physics approach for modelling and design of alkaline
    electrolysers" by M. Hammoudi et al.

    "Simulation tool based on a physics model and an electrical analogy for an alkaline electrolyser" by C. Henao et al.

    to generate the polarization curve of an alkaline elektrolyser, depending on:
    - temperature
    - pressure
    - electrolyte concentration
    as well as other parameters of the chosen specific electrolyser (In this case the Stuart HRI Electrolyser example was used)

    The resulting curves for current density and power are saved in .csv files, to later be imported by the alkaline
    electrolyser stack model for usage in SimSES.
"""

import glob
import math as m

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Parameters TODO more general approach for other Electrolysers (here: HRI)
koh_weight_concentration = 30                           # %
anode_surface = 0.03                                    # m^2
cathode_surface = 0.03                                  # m^2
anode_thickness = 0.002                                 # m
cathode_thickness = 0.002                               # m
anode_membrane_gap = 0.00125                            # m
cathode_membrane_gap = 0.00125                          # m
membrane_surface_area = 0.03                            # m^2
limiting_current_density = 300000                       # A/m^2
standard_temperature = 25                               # °C (Room Temperature)
standard_temperature = standard_temperature + 273.15    # K

# Input Variables
temperatures = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0]  # °C
pressures = np.linspace(1, 50, 30)                # bar
currents = np.linspace(0, 150, 300)

lookup_table_activation_overpotential = pd.read_csv('activation_overpotential_lookup_alkaline.csv', compression='gzip')

__IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
__FARADAY_CONST: float = 96485.3321  # As/mol

fitting_parameters = None

def calculate_cell_voltage(current: float, temperature: float, pressure: float) -> float:
    v_cell = 0

    # Convert temperature from °C to K
    temperature = (temperature + 273.15)

    # Get theoretical cell voltage
    v_theoretical = calculate_theoretical_voltage(temperature, pressure)
    v_cell += v_theoretical

    if current >= 0:
        # Get electrode activation overvoltages
        v_act_a = calculate_activation_overvoltage_anode(current, temperature)
        v_act_c = calculate_activation_overvoltage_cathode(current, temperature)
        v_activation_total = v_act_a + v_act_c
        v_cell += v_activation_total
        # Calculate ohmic resistances
        # Electrolyte
        v_electrolyte_resistance = calculate_electrolyte_overvoltage(current, temperature)
        v_cell += v_electrolyte_resistance
        # Electrodes
        v_electrode_resistances = calculate_electrode_overvoltage(current, temperature)
        v_cell += v_electrode_resistances
        # Membrane
        v_membrane_resistance = calculate_membrane_overvoltage(current, temperature)
        v_cell += v_membrane_resistance

    return v_cell


def calculate_theoretical_voltage(temperature: float, pressure: float) -> float:
    # Thermodynamic approximation of the reversible voltage at standard conditions
    v_reversible_standard_conditions = 1.50342 - 9.956 * 10 ** (-4) * temperature + 2.5 * 10 ** (-7) * temperature ** 2

    molarity = calculate_molarity(temperature)

    # Calculate vapour pressure of pure water pw* and pressure of gaseous KOH solution pw
    # (From: "The Thermodynamics of Aqueous Water Electrolysis" by LeRoy)
    pure_water_vapour_pressure = (temperature ** -3.4159) * np.exp(37.043 - (6275.7 / temperature))
    koh_solution_pressure = (temperature ** -3.498) * np.exp(37.93 - (6426.32 / temperature)) * np.exp(0.016214 - 0.13802 * molarity + 0.19330 * molarity**0.5)
    # Calculate water electrolysis theoretical voltage
    v_theoretical = v_reversible_standard_conditions + (
                (__IDEAL_GAS_CONST * temperature) / (2 * __FARADAY_CONST)) * np.log(
        (pressure - koh_solution_pressure) ** (3 / 2) * (pure_water_vapour_pressure / koh_solution_pressure))

    # Correction terms for the consideration of real gas instead of ideal gas
    v_correction1 = (pressure - koh_solution_pressure) * (21.661 * 10 ** (-6) - (5.471 * 10 ** (-3)) / temperature)
    v_theoretical += v_correction1
    v_correction2 = (pressure - koh_solution_pressure) ** 2 * (
                -1 * ((6.289 * 10 ** -6) / temperature) + ((0.135 * 10 ** -3) / temperature ** 1.5)
                + ((2.547 * 10 ** -3) / temperature ** 2) - (0.4825 / temperature ** 3))
    v_theoretical += v_correction2

    return v_theoretical


def calculate_activation_overvoltage_anode(current: float, temperature: float) -> float:
    # Calculate bubble rate coverage of electrodes (assumed to be identical for both electrodes)
    bubble_rate_coverage = calculate_bubble_rate_coverage(current, temperature)
    # Calculate nominal electrode surfaces
    anode_surface_nom = anode_surface * (1 - bubble_rate_coverage)
    current_density = current / (anode_surface_nom * 10000.0) # A/cm2
    # Calculate transfer coefficient for anode and cathode for HRI Electrolyser TODO more general approach?
    alpha_a = 0.0675 + 0.00095 * temperature
    # Calculate tafel slope for anode and cathode
    tafel_slope = (__IDEAL_GAS_CONST * temperature) / (2*__FARADAY_CONST * alpha_a)
    # Calculate exchange current densities for anode and cathode for HRI Electrolyser (Ni Electrodes) TODO more general approach?
    exchange_current_density = 30.4 - 0.206 * temperature + 0.00035 * temperature ** 2  # mA/cm2 ?
    # Calculate activation overvoltages of the electrodes:
    v_activation_anode = tafel_slope * m.asinh(current_density / (2*exchange_current_density / 1000.0))

    return v_activation_anode


def calculate_activation_overvoltage_cathode(current: float, temperature: float) -> float:
    # Calculate bubble rate coverage of electrodes (assumed to be identical for both electrodes)
    bubble_rate_coverage = calculate_bubble_rate_coverage(current, temperature)
    # Calculate nominal electrode surfaces
    cathode_surface_nom = cathode_surface * (1 - bubble_rate_coverage)
    current_density = current / (cathode_surface_nom * 10000.0)
    # Calculate transfer coefficient for anode and cathode for HRI Electrolyser TODO more general approach?
    alpha_c = 0.1175 + 0.00095 * temperature
    # Calculate tafel slope for anode and cathode
    tafel_slope = (__IDEAL_GAS_CONST * temperature) / (2*__FARADAY_CONST * alpha_c)
    # Calculate exchange current densities for anode and cathode for HRI Electrolyser (Ni Electrodes) TODO more general approach?
    exchange_current_density = 13.72491 - 0.09055 * temperature + 0.09055 * temperature ** 2  # mA/cm2 ?
    # Calculate activation overvoltages of the electrodes:
    v_activation_cathode = tafel_slope * m.asinh(current_density / (2*exchange_current_density / 1000.0))

    return v_activation_cathode


def calculate_activation_overvoltage_lookup(current: float, temperature: float) -> float:
    bubble_rate_coverage = calculate_bubble_rate_coverage(current, temperature)
    electrode_surface_nom = anode_surface * (1 - bubble_rate_coverage)
    current_density = current / (electrode_surface_nom * 10000.0)

    temperature = temperature - 273.15  # °C
    temperature_idx = abs(lookup_table_activation_overpotential['temperature in °C'] - temperature).idxmin()
    filter_temperature = lookup_table_activation_overpotential.iloc[temperature_idx, 0]  # °C
    filtered_table = lookup_table_activation_overpotential[lookup_table_activation_overpotential['temperature in °C'] == filter_temperature]
    filtered_table.reset_index(drop=True, inplace=True)

    current_idx = abs(filtered_table['current density in A/cm2'] - current_density).idxmin()
    activation_overvoltage = filtered_table.iloc[current_idx, 2] + filtered_table.iloc[current_idx, 3]

    return activation_overvoltage


def calculate_electrode_overvoltage(current: float, temperature: float) -> float:
    # Calculate electrical conductivity of Ni TODO more general approach?
    conductivity_nickel = 14.3 * 10**6  # S/m generic value for Nickel at room temperature TODO find good source
    conductivity_nickel = conductivity_nickel / 100   # S/cm
    # Calculate electrode resistances
    resistance_anode = (1 / conductivity_nickel) * ((anode_thickness * 100) / (anode_surface * 10000))
    resistance_cathode = (1 / conductivity_nickel) * ((cathode_thickness * 100) / (cathode_surface * 10000))
    v_electrode_resistances = (resistance_anode + resistance_cathode) * current

    return v_electrode_resistances


def calculate_electrolyte_overvoltage(current: float, temperature: float) -> float:
    molarity = calculate_molarity(temperature)
    bubble_rate_coverage = calculate_bubble_rate_coverage(current, temperature)

    # Calculate ionic conductivity of KOH in S/cm
    conductivity_koh_free = -2.041 * molarity - 0.0028 * molarity**2 + 0.005332 * molarity * temperature + 207.2 * (
                molarity / temperature) \
                     + 0.001043 * molarity**3 - 0.0000003 * molarity**2 * temperature**2
    # Calculate free resistance of electrolyte
    resistance_electrolyte_free = (1 / conductivity_koh_free) * ((anode_membrane_gap / anode_surface + cathode_membrane_gap / cathode_surface) / 100)
    # Incorporate bubble rate into resistance
    resistance_electrolyte_from_bubble_rate = resistance_electrolyte_free * ((1 / ((1 - (2 / 3) * bubble_rate_coverage) ** (3 / 2))) - 1)
    resistance_electrolyte_total = resistance_electrolyte_free + resistance_electrolyte_from_bubble_rate
    v_electrolyte_resistance = resistance_electrolyte_total * current

    return v_electrolyte_resistance


def calculate_membrane_overvoltage(current: float, temperature: float) -> float:
    # Calculate Membrane resistance (HRI Electrolyser: 0.5mm Zirfon) TODO more general approach?
    # resistance_membrane = (0.060 + 80 * m.exp(temperature / 50)) / (10000 * membrane_surface_area * 10000)

    # Generic values from "VERMEIREN, P. (1998). Evaluation of the ZirfonS separator for use in alkaline water electrolysis and Ni-H2 batteries.
    # International Journal of Hydrogen Energy, 23(5), 321–324. doi:10.1016/s0360-3199(97)00069-4" (Regression from graph)
    resistance_membrane_per_area = fitting_parameters.zirfon1 * temperature ** 2 + fitting_parameters.zirfon2 * temperature + fitting_parameters.zirfon3
    resistance_membrane = resistance_membrane_per_area / (membrane_surface_area * 10000)
    v_membrane_resistance = resistance_membrane * current

    return v_membrane_resistance


def calculate_molarity(temperature: float) -> float:
    # Calculate molarity of KOH electrolyte
    # From "New multi-physics approach for modelling and design of alkaline electrolysers" by M. Hammoudi et al.
    molarity = (koh_weight_concentration * (
            183.1221 - 0.56845 * temperature + 984.5679 * m.exp(koh_weight_concentration / 115.96277))) / (
                       100 * 56.105)

    return molarity


def calculate_bubble_rate_coverage(current: float, temperature: float) -> float:
    bubble_rate_coverage = (-97.25 + 182 * (temperature / standard_temperature) - 84 * (temperature / standard_temperature) ** 2) * (
            (current / cathode_surface) / limiting_current_density) ** 0.3

    return bubble_rate_coverage


def generate_polarisation_lookup():
    lookup_voltages = []
    lookup_temperatures = []
    lookup_pressures = []
    lookup_currents = []

    for i in range(len(temperatures)):
        for p in range(len(pressures)):
            for j in range(len(currents)):
                # lookup_voltages.append(calculate_cell_voltage(currents[j], temperatures[i], pressures[p]))
                xdata = np.array([[temperatures[i]], [pressures[p]], [currents[j]]])
                lookup_voltages.append(cell_voltage_fit_model_function(xdata, fitting_parameters.ac, fitting_parameters.bc, fitting_parameters.cc,
                                                        fitting_parameters.aa, fitting_parameters.ba, fitting_parameters.ca,
                                                        fitting_parameters.r1, fitting_parameters.r2, fitting_parameters.r3,
                                                        fitting_parameters.a1, fitting_parameters.a2)[0])
                lookup_temperatures.append(temperatures[i])
                lookup_pressures.append(pressures[p])
                lookup_currents.append(currents[j])

    lookup_currents = np.array(lookup_currents)
    lookup_temperatures = np.array(lookup_temperatures)
    lookup_pressures = np.array(lookup_pressures)
    lookup_voltages = np.array(lookup_voltages)

    # Create lookup table for alkaline electrolyser cell voltage from current
    dict1 = {'temperature in °C' : lookup_temperatures, 'P bar' : lookup_pressures,
             'current in A' : lookup_currents, 'cell voltage in V' : lookup_voltages}
    df1 = pd.DataFrame(dict1)
    df1.to_csv('cell_voltage_lookup_alkaline.csv', index=False)

    # Create lookup table for alkaline electrolyser cell current from power
    lookup_power = lookup_voltages * lookup_currents
    dict2 = {'temperature in °C': lookup_temperatures, 'P bar': lookup_pressures,
             'power in W': lookup_power, 'current in A': lookup_currents}
    df2 = pd.DataFrame(dict2)
    df2.to_csv('cell_current_lookup_alkaline.csv', index=False)


def display_example_curve(temperature: float, pressure: float, compareUI: bool):
    voltages = []
    current_densities = []
    for j in range(len(currents)):
        voltages.append(calculate_cell_voltage(currents[j], temperature, pressure))
        current_densities.append(currents[j] / (anode_surface * 10000))

    fig = plt.figure()

    if compareUI:
        # Compare different electrolyzers
        legend = []
        legend.append('Cell Polarization Curve ' + str(temperature) + '°C at ' + str(pressure) + 'bar')
        ax1 = fig.add_subplot(211)
        ax1.title.set_text('Comparison of different alkaline electrolyzers')
        plt.plot(current_densities, voltages, color='red', linewidth=4)
        plt.ylabel('Cell Voltage in V')
        plt.xlabel('Cell Current Density in A/cm2')
        plt.grid(True)

        u_i_curve_path = '../ui_curves/general_alkaline\\'
        u_i_files = glob.glob(u_i_curve_path + '*.csv')
        styleindex = 0
        for curve in u_i_files:
            styleindex = styleindex + 1
            excelfile = pd.read_csv(curve)
            file_current_densities = excelfile.iloc[:, 0]
            file_cell_voltages = excelfile.iloc[:, 1]
            if styleindex < 11:
                plt.plot(file_current_densities.values, file_cell_voltages.values, linewidth=2)
            else:
                plt.plot(file_current_densities.values, file_cell_voltages.values, linewidth=2, linestyle='dashed')

            legend.append(curve[len(u_i_curve_path):len(curve)-4])

        plt.legend(legend)

        # Compare curves for Stuart HRI Electrolyzer
        legend2 = []
        legend2.append('Cell Polarization Curve ' + str(temperature) + '°C at ' + str(pressure) + 'bar')
        ax2 = fig.add_subplot(212)
        ax2.title.set_text('Comparison of different Stuart HRI Curves at 1 bar')
        plt.plot(current_densities, voltages, color='red', linewidth=4)
        plt.ylabel('Cell Voltage in V')
        plt.xlabel('Cell Current Density in A/cm2')
        plt.grid(True)

        u_i_curve_path = '../ui_curves/stuart_hri\\'
        u_i_files = glob.glob(u_i_curve_path + '*.csv')
        for curve in u_i_files:
            excelfile = pd.read_csv(curve)
            file_current_densities = excelfile.iloc[:, 0]
            file_cell_voltages = excelfile.iloc[:, 1]
            plt.plot(file_current_densities.values, file_cell_voltages.values, linewidth=2)
            legend2.append(curve[len(u_i_curve_path):len(curve) - 4])

        plt.legend(legend2)
    else:
        ax1 = fig.add_subplot(111)
        ax1.title.set_text('Cell Polarisation Curve')
        plt.plot(current_densities, voltages, color='red', linewidth=4)
        plt.ylabel('Cell Voltage in V')
        plt.xlabel('Cell Current Density in A/cm2')
        plt.grid(True)

    plt.show()


def display_example_curve_regression(temperature: float, pressure: float):
    voltages = []
    current_densities = []
    for j in range(len(currents)):
        xdata = np.array([[temperature], [pressure], [currents[j]]])
        voltages.append(cell_voltage_fit_model_function(xdata, fitting_parameters.ac, fitting_parameters.bc, fitting_parameters.cc,
                                                        fitting_parameters.aa, fitting_parameters.ba, fitting_parameters.ca,
                                                        fitting_parameters.r1, fitting_parameters.r2, fitting_parameters.r3,
                                                        fitting_parameters.a1, fitting_parameters.a2))
        current_densities.append(currents[j] / (anode_surface * 10000))

    fig = plt.figure()

    # Compare different electrolyzers
    legend = []
    legend.append('Cell Polarization Curve ' + str(temperature) + '°C at ' + str(pressure) + 'bar')
    ax1 = fig.add_subplot(211)
    ax1.title.set_text('Comparison of different alkaline electrolyzers')
    plt.plot(current_densities, voltages, color='red', linewidth=4)
    plt.ylabel('Cell Voltage in V')
    plt.xlabel('Cell Current Density in A/cm2')
    plt.grid(True)

    u_i_curve_path = '../ui_curves/general_alkaline\\'
    u_i_files = glob.glob(u_i_curve_path + '*.csv')
    styleindex = 0
    for curve in u_i_files:
        styleindex = styleindex + 1
        excelfile = pd.read_csv(curve)
        file_current_densities = excelfile.iloc[:, 0]
        file_cell_voltages = excelfile.iloc[:, 1]
        if styleindex < 11:
            plt.plot(file_current_densities.values, file_cell_voltages.values, linewidth=2)
        else:
            plt.plot(file_current_densities.values, file_cell_voltages.values, linewidth=2, linestyle='dashed')

        legend.append(curve[len(u_i_curve_path):len(curve) - 4])

    plt.legend(legend)

    # Compare curves for Stuart HRI Electrolyzer
    legend = []
    legend.append('Cell Polarization Curve ' + str(temperature) + '°C at ' + str(pressure) + 'bar')
    ax2 = fig.add_subplot(212)
    ax2.title.set_text('Comparison of different Stuart HRI Curves at 1 bar')
    plt.plot(current_densities, voltages, color='red', linewidth=4)
    plt.ylabel('Cell Voltage in V')
    plt.xlabel('Cell Current Density in A/cm2')
    plt.grid(True)

    u_i_curve_path = '../ui_curves/stuart_hri\\'
    u_i_files = glob.glob(u_i_curve_path + '*.csv')
    for curve in u_i_files:
        excelfile = pd.read_csv(curve)
        file_current_densities = excelfile.iloc[:, 0]
        file_cell_voltages = excelfile.iloc[:, 1]
        plt.plot(file_current_densities.values, file_cell_voltages.values, linewidth=2)
        legend.append(curve[len(u_i_curve_path):len(curve) - 4])

    plt.legend(legend)
    plt.show()


def display_activation_overpotential(temperature: float) -> float:
    temperature = temperature + 273.15
    current_densities = []
    v_asinh = []
    v_activation_lookup = []
    currents_activation = np.linspace(0, 100, 300)
    for j in range(len(currents_activation)):
        if currents_activation[j] > 0:
            current_densities.append(currents_activation[j] / (membrane_surface_area * 10000))
            v_act_a = calculate_activation_overvoltage_anode(currents_activation[j], temperature)
            v_act_c = calculate_activation_overvoltage_cathode(currents_activation[j], temperature)
            v_act_total = v_act_a + v_act_c

            v_act_total_lookup = calculate_activation_overvoltage_lookup(currents_activation[j], temperature)
            v_asinh.append(v_act_total)
            v_activation_lookup.append(v_act_total_lookup)
        else:
            current_densities.append(currents_activation[j] / (membrane_surface_area * 10000))
            v_asinh.append(0)
            v_activation_lookup.append(0)

    # Deviation Analysis
    absolute_error = np.array(v_asinh) - np.array(v_activation_lookup)
    mean_absolute_error = np.mean(abs(absolute_error))
    rms_error = np.sqrt(sum((absolute_error) ** 2) / len(absolute_error))

    # Plotting
    plt.subplot(111)
    plt.ylabel('Activation Voltage V')
    plt.xlabel('Cell Current Density in A/cm2')
    plt.grid(True)
    plt.title('Activation Overvoltage ' + str(temperature - 273.15) + '°C')
    plt.plot(current_densities, v_asinh)
    plt.plot(current_densities, v_activation_lookup)
    plt.legend(["v_act_asinh", "v_act_lookup (butler volmer)"])
    plt.show()

    return rms_error


# Three fitting parameters each for quadratic description of exchange current densities as f(T) (As aforementioned paper by Henao et al)
def cell_voltage_fit_model_function(x, ac, bc, cc, aa, ba, ca, r1, r2, r3, a1, a2):
    temperature = x[0, :]
    pressure = x[1, :]
    current = x[2, :]

    v_cell = 0

    # Convert temperature from °C to K
    temperature = (temperature + 273.15)

    # Get theoretical cell voltage
    v_theoretical = calculate_theoretical_voltage(temperature, pressure)
    v_cell += v_theoretical

    # Calculate bubble rate coverage of electrodes (assumed to be identical for both electrodes)
    bubble_rate_coverage = calculate_bubble_rate_coverage(current, temperature)
    # Calculate nominal electrode surfaces
    anode_surface_nom = anode_surface * (1 - bubble_rate_coverage)
    current_density_anode = current / (anode_surface_nom * 10000.0)  # A/cm2
    cathode_surface_nom = cathode_surface * (1 - bubble_rate_coverage)
    current_density_cathode = current / (cathode_surface_nom * 10000.0)
    # Calculate transfer coefficient for anode and cathode for HRI Electrolyser
    alpha_a = 0.0675 + 0.00095 * temperature*a1
    alpha_c = 0.1175 + 0.00095 * temperature*a2
    # Calculate tafel slopes for anode and cathode
    factor_anode = (__IDEAL_GAS_CONST * temperature) / (
                2 * __FARADAY_CONST * alpha_a)
    factor_cathode = (__IDEAL_GAS_CONST * temperature) / (
            2 * __FARADAY_CONST * alpha_c)
    # Calculate exchange current densities for anode and cathode for HRI Electrolyser (Ni Electrodes)
    exchange_current_density_anode = aa + ba * temperature + ca * temperature ** 2  # mA/cm2
    exchange_current_density_cathode = ac + bc * temperature + cc * temperature ** 2  # mA/cm2
    # Calculate activation overvoltages of the electrodes:
    v_activation_anode = factor_anode * np.arcsinh(current_density_anode / (2 * exchange_current_density_anode / 1000.0))
    v_activation_cathode = factor_cathode * np.arcsinh(current_density_cathode / (2 * exchange_current_density_cathode / 1000.0))
    v_activation_total = v_activation_anode + v_activation_cathode
    v_cell += v_activation_total
    # Calculate ohmic resistances
    # Electrolyte
    v_electrolyte_resistance = calculate_electrolyte_overvoltage(current, temperature)
    v_cell += v_electrolyte_resistance * r1
    # Electrodes
    v_electrode_resistances = calculate_electrode_overvoltage(current, temperature)
    v_cell += v_electrode_resistances * r2
    # Membrane
    v_membrane_resistance = calculate_membrane_overvoltage(current, temperature)
    v_cell += v_membrane_resistance * r3

    return v_cell


def get_fitting_data():
    u_i_curve_path = '../ui_curves/stuart_hri\\'
    u_i_files = glob.glob(u_i_curve_path + '*.csv')
    currents_fit = []
    cell_voltages_fit = []
    pressures_fit = []
    temperatures_fit = []
    for curve in u_i_files:
        excelfile = pd.read_csv(curve)
        file_current_densities = excelfile.iloc[:, 0]
        file_cell_voltages = excelfile.iloc[:, 1]
        file_temperatures = excelfile.iloc[:, 2]
        file_pressures = excelfile.iloc[:, 3]
        currents_fit = np.concatenate([currents_fit, file_current_densities * cathode_surface * 10000])
        cell_voltages_fit = np.concatenate([cell_voltages_fit, file_cell_voltages])
        temperatures_fit = np.concatenate([temperatures_fit, file_temperatures])
        pressures_fit = np.concatenate([pressures_fit, file_pressures])

    # Extra Curves for other alkaline electrolyzers
    # u_i_curve_path = 'UICurves\\GeneralAlkaline\\'
    # u_i_files = glob.glob(u_i_curve_path + '*.csv')
    # for curve in u_i_files:
    #     excelfile = pd.read_csv(curve)
    #     file_current_densities = excelfile.iloc[:, 0]
    #     file_cell_voltages = excelfile.iloc[:, 1]
    #     file_temperatures = excelfile.iloc[:, 2]
    #     file_pressures = excelfile.iloc[:, 3]
    #     currents_fit = np.concatenate([currents_fit, file_current_densities * cathode_surface * 10000])
    #     cell_voltages_fit = np.concatenate([cell_voltages_fit, file_cell_voltages])
    #     temperatures_fit = np.concatenate([temperatures_fit, file_temperatures])
    #     pressures_fit = np.concatenate([pressures_fit, file_pressures])

    xdata = np.array([temperatures_fit, pressures_fit, currents_fit])
    ydata = np.array(cell_voltages_fit)

    return xdata, ydata

def polarisation_deviations():
    xdata_ref, voltages_ref = get_fitting_data()
    temperatures_ref = xdata_ref[0]
    pressures_ref = xdata_ref[1]
    currents_ref = xdata_ref[2]

    voltages_calculated = []
    for i in range(len(temperatures_ref)):
        xdata = np.array([[temperatures_ref[i]], [pressures_ref[i]], [currents_ref[i]]])
        voltages_calculated.append(cell_voltage_fit_model_function(xdata, fitting_parameters.ac, fitting_parameters.bc,
                                                        fitting_parameters.cc,
                                                        fitting_parameters.aa, fitting_parameters.ba,
                                                        fitting_parameters.ca,
                                                        fitting_parameters.r1, fitting_parameters.r2,
                                                        fitting_parameters.r3,
                                                        fitting_parameters.a1, fitting_parameters.a2))
    voltages_calculated = np.array(voltages_calculated)
    voltages_calculated = voltages_calculated.reshape(len(voltages_calculated),)
    #voltages_ref = voltages_ref.reshape(len(voltages_ref), 1)
    #currents_ref = currents_ref.reshape(len(currents_ref), 1)
    voltage_error_absolute = abs(voltages_calculated - voltages_ref)
    mean_abs_err = np.mean(voltage_error_absolute)
    max_abs_err = max(abs(voltage_error_absolute))
    RMS = np.sqrt(sum((voltage_error_absolute) ** 2) / len(voltage_error_absolute))
    print(RMS)

    fig = plt.figure()
    legend = []
    ax1 = fig.add_subplot(111)
    for temperature in np.unique(temperatures_ref):
        currents_selected = currents_ref[np.where(temperatures_ref == temperature)]
        voltage_error_selected = voltage_error_absolute[np.where(temperatures_ref == temperature)]
        plt.plot(currents_selected, voltage_error_selected, linewidth=2)
        # Export Error Data in Excel
        # dict1 = {'Current in A': currents_selected, 'Absolute Error in V': voltage_error_selected}
        # df1 = pd.DataFrame(dict1)
        # df1.to_csv(('Absolute_Error_' + str(temperature) + '.csv'), index=False)

    plt.ylabel('Absolute Voltage Error in V')
    plt.xlabel('Cell Current in A')
    plt.grid(True)
    plt.show()


# COMMAND SECTION

# xdata, ydata = get_fitting_data()
# lb = - np.inf
# ub = np.inf
# EPS = np.finfo(float).eps
# lower_bounds = (lb, lb, lb, lb, lb, lb, lb, lb, lb, lb, lb)
# upper_bounds = (ub, ub, ub, ub, ub, ub, ub, ub, ub, ub, ub)
# popt, pcov = curve_fit(cell_voltage_fit_model_function, xdata, ydata, absolute_sigma=False, p0=[1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1], maxfev=1000000,
#                        bounds=(lower_bounds,upper_bounds))
# dict = {'parameters': popt}
# df = pd.DataFrame(dict)
# df.to_csv('parameters_alkaline_overvoltage_fit.csv', index=False)

# display_example_curve_regression(53, 1)

# generate_polarisation_lookup()

# display_example_curve(23, 1, compareUI = True)

# rms_error = []
# for i in range(len(temperatures)):
#     rms_error.append(display_activation_overpotential(temperatures[i]))
#
#
# avg_rms_error = sum(rms_error) / len(rms_error)
# print(avg_rms_error)

polarisation_deviations()

