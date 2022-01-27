import math

import numpy as np
import pandas as pd

from simses.commons.config.data.electrolyzer import ElectrolyzerDataConfig
from simses.commons.constants import Hydrogen
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.stack.alkaline.fluid_model import \
    AlkalineFluidModel
from simses.technology.hydrogen.electrolyzer.stack.alkaline.pressure_model import \
    AlkalinePressureModel


class AlkalineElectricalModel:

    __POWER_HEADER = 'power in W'
    __TEMPERATURE_HEADER = 'temperature in °C'
    __PRESSURE_HEADER = 'P bar'
    __CURRENT_IDX = 3
    __TEMPERATURE_IDX = 0
    __PRESSURE_IDX = 1

    # Parameters TODO more general approach for other Electrolysers (here: HRI Stuart Electrolyser)
    __koh_weight_concentration = 30  # %
    __anode_surface = 0.03  # m^2
    __cathode_surface = 0.03  # m^2
    __anode_thickness = 0.002  # m
    __cathode_thickness = 0.002  # m
    __anode_membrane_gap = 0.00125  # m
    __cathode_membrane_gap = 0.00125  # m
    __membrane_surface_area = 0.03  # m^2
    __limiting_current_density = 300000  # A/m^2 (limiting current density)
    __standard_temperature = 25  # °C (Room Temperature)
    __standard_temperature = __standard_temperature + 273.15  # K

    def __init__(self, pressure_model: AlkalinePressureModel, fluid_model: AlkalineFluidModel, electrolyzer_data_config: ElectrolyzerDataConfig, parameters):
        self.__pressure_model = pressure_model
        self.__fluid_model = fluid_model
        self.__POWER_FILE = electrolyzer_data_config.alkaline_electrolyzer_multidim_lookup_currentdensity_file
        self.__power_curve = pd.read_csv(self.__POWER_FILE, compression='gzip')
        self.__parameters = parameters

    def get_cell_voltage(self, current: float, state: ElectrolyzerState):
        # Resistance correction factors
        r1 = self.__parameters.r1
        r2 = self.__parameters.r2
        r3 = self.__parameters.r3

        stack_temperature = state.temperature  # °C
        stack_temperature = stack_temperature + 273.15  # K

        v_cell = 0

        # Get theoretical cell voltage
        v_theoretical = self.__theoretical_voltage(state, current)
        v_cell += v_theoretical
        # Get activation overvoltages
        v_activation_anode = self.__activation_voltage_anode(state, current)
        v_activation_cathode = self.__activation_voltage_cathode(state, current)
        v_activation_total = v_activation_anode + v_activation_cathode
        v_cell += v_activation_total
        # Calculate ohmic overvoltages
        r_electrodes = self.__electrode_resistance()
        v_electrode_resistances = r_electrodes * current
        r_electrolyte = self.__electrolyte_resistance(current, stack_temperature)
        v_electrolyte_resistance = r_electrolyte * current
        r_membrane = self.__membrane_resistance(stack_temperature)
        v_membrane_resistance = r_membrane * current

        v_cell += v_electrolyte_resistance * r1
        v_cell += v_electrode_resistances * r2
        v_cell += v_membrane_resistance * r3

        return v_cell

    def get_current(self, power_cell: float, state: ElectrolyzerState):
        pressure = state.pressure_cathode     # bar (pressure assumed to be identical for cathode and anode) TODO Check Validity
        stack_temperature = state.temperature     # °C
        # Get current from lookuptable
        if power_cell <= 0:
            return 0
        else:
            temperature_idx = abs(self.__power_curve[self.__TEMPERATURE_HEADER] - stack_temperature).idxmin()
            filter_temperature = self.__power_curve.iloc[temperature_idx, self.__TEMPERATURE_IDX]   # °C
            powercurve = self.__power_curve[self.__power_curve[self.__TEMPERATURE_HEADER] == filter_temperature]
            powercurve.reset_index(drop=True, inplace=True)

            pressure_idx = abs(powercurve[self.__PRESSURE_HEADER] - pressure).idxmin()
            filter_pressure = powercurve.iloc[pressure_idx, self.__PRESSURE_IDX]  # Bar
            powercurve = powercurve[powercurve[self.__PRESSURE_HEADER] == filter_pressure]
            powercurve.reset_index(drop=True, inplace=True)

            power_idx = abs(powercurve[self.__POWER_HEADER] - power_cell).idxmin()
            current = powercurve.iloc[power_idx, 3]  # A
            return current


    def __reversible_voltage(self, stack_temperature) -> float:
        # Thermodynamic approximation of the reversible voltage at standard conditions
        return 1.50342 - 9.956 * 10 ** (-4) * stack_temperature + 2.5 * 10 ** (-7) * stack_temperature ** 2

    def __theoretical_voltage(self, state: ElectrolyzerState, current) -> float:
        stack_temperature = state.temperature           # °C
        stack_temperature = stack_temperature + 273.15  # K
        pressure = state.pressure_cathode  # bar (pressure assumed to be identical for cathode and anode) TODO Check Validity

        v_reversible_standard_conditions = self.get_rev_voltage(stack_temperature)

        molarity = self.__fluid_model.get_molarity(stack_temperature)
        # Calculate vapour pressure of pure water pw* and pressure of gaseous KOH solution pw
        # (From: "The Thermodynamics of Aqueous Water Electrolysis" by LeRoy)
        vapour_pressure_pure_water = self.__pressure_model.get_vapour_pressure_pure_water(stack_temperature)
        aqueous_vapour_pressure_koh = self.__pressure_model.get_aqueous_vapour_pressure_koh(molarity, stack_temperature)

        # Calculate water electrolysis theoretical voltage
        v_theoretical = v_reversible_standard_conditions + (
                (Hydrogen.IDEAL_GAS_CONST * stack_temperature) / (2 * Hydrogen.FARADAY_CONST)) * math.log(
            (pressure - aqueous_vapour_pressure_koh) ** (3 / 2) * (vapour_pressure_pure_water / aqueous_vapour_pressure_koh))

        # Correction terms for the consideration of real gas instead of ideal gas
        v_correction1 = (pressure - aqueous_vapour_pressure_koh) * (21.661 * 10 ** (-6) - (5.471 * 10 ** (-3)) / stack_temperature)
        v_theoretical += v_correction1
        v_correction2 = (pressure - aqueous_vapour_pressure_koh) ** 2 * (
                -1 * ((6.289 * 10 ** -6) / stack_temperature) + ((0.135 * 10 ** -3) / stack_temperature ** 1.5)
                + ((2.547 * 10 ** -3) / stack_temperature ** 2) - (0.4825 / stack_temperature ** 3))
        v_theoretical += v_correction2

        return v_theoretical

    def __activation_voltage_anode(self, state: ElectrolyzerState, current: float) -> float:
        # Anode correction factors
        aa = self.__parameters.aa
        ba = self.__parameters.ba
        ca = self.__parameters.ca

        # Transfer coefficient correction factor
        a1 = self.__parameters.a1

        stack_temperature = state.temperature  # °C
        stack_temperature = stack_temperature + 273.15  # K

        # Calculate bubble rate coverage of electrodes (assumed to be identical for both electrodes)
        bubble_rate_coverage = self.__bubble_rate_coverage(current, stack_temperature)
        # Calculate nominal electrode surfaces
        anode_surface_nom = self.__anode_surface * (1 - bubble_rate_coverage)
        current_density_anode = current / (anode_surface_nom * 10000.0)  # A/cm2
        # Calculate transfer coefficient for anode for HRI Electrolyser
        alpha_a = 0.0675 + 0.00095 * stack_temperature * a1
        # Calculate tafel slope for anode
        factor_anode = (Hydrogen.IDEAL_GAS_CONST * stack_temperature) / (
                2 * Hydrogen.FARADAY_CONST * alpha_a)
        # Calculate exchange current density for anode for HRI Electrolyser (Ni Electrode)
        exchange_current_density_anode = aa + ba * stack_temperature + ca * stack_temperature ** 2  # mA/cm2
        # Calculate activation overvoltage of the electrode:
        v_activation_anode = factor_anode * np.arcsinh(
            current_density_anode / (2 * exchange_current_density_anode / 1000.0))

        return v_activation_anode

    def __activation_voltage_cathode(self, state: ElectrolyzerState, current: float) -> float:
        # Cathode correction factors
        ac = self.__parameters.ac
        bc = self.__parameters.bc
        cc = self.__parameters.cc

        # Transfer coefficient correction factor
        a2 = self.__parameters.a2

        stack_temperature = state.temperature  # °C
        stack_temperature = stack_temperature + 273.15  # K

        # Calculate bubble rate coverage of electrodes (assumed to be identical for both electrodes)
        bubble_rate_coverage = self.__bubble_rate_coverage(current, stack_temperature)
        # Calculate nominal electrode surface
        cathode_surface_nom = self.__cathode_surface * (1 - bubble_rate_coverage)
        current_density_cathode = current / (cathode_surface_nom * 10000.0)
        # Calculate transfer coefficient for cathode for HRI Electrolyser
        alpha_c = 0.1175 + 0.00095 * stack_temperature * a2
        # Calculate tafel slope for cathode
        factor_cathode = (Hydrogen.IDEAL_GAS_CONST * stack_temperature) / (
                2 * Hydrogen.FARADAY_CONST * alpha_c)
        # Calculate exchange current density for cathode for HRI Electrolyser (Ni Electrode)
        exchange_current_density_cathode = ac + bc * stack_temperature + cc * stack_temperature ** 2  # mA/cm2
        # Calculate activation overvoltage of the electrode:
        v_activation_cathode = factor_cathode * np.arcsinh(
            current_density_cathode / (2 * exchange_current_density_cathode / 1000.0))

        return v_activation_cathode

    def __bubble_rate_coverage(self, current, stack_temperature) -> float:
        bubble_rate_coverage = (-97.25 + 182 * (stack_temperature / self.__standard_temperature) - 84 * (stack_temperature / self.__standard_temperature) ** 2) * (
                (current / self.__cathode_surface) / self.__limiting_current_density) ** 0.3

        return bubble_rate_coverage

    def get_rev_voltage(self, stack_temperature) -> float:
        """ Returns reversible Cell Voltage at standard pressure depending on stack temperature in K """
        return self.__reversible_voltage(stack_temperature)

    def calculate_bubble_rate_coverage(self, current, stack_temperature) -> float:
        return self.__bubble_rate_coverage(current, stack_temperature)

    def __electrode_resistance(self) -> float:
        # Calculate electrical conductivity of Ni TODO more general approach?
        conductivity_nickel = 14.3 * 10 ** 6  # S/m (generic value for nickel based electrode)
        conductivity_nickel = conductivity_nickel / 100  # S/cm
        # Calculate electrode resistances
        resistance_anode = (1 / conductivity_nickel) * ((self.__anode_thickness * 100) / (self.__anode_surface * 10000))
        resistance_cathode = (1 / conductivity_nickel) * ((self.__cathode_thickness * 100) / (self.__cathode_surface * 10000))

        return resistance_anode + resistance_cathode

    def __electrolyte_resistance(self, current, stack_temperature) -> float:
        molarity = self.__fluid_model.get_molarity(stack_temperature)
        bubble_rate_coverage = self.calculate_bubble_rate_coverage(current, stack_temperature)

        # Calculate ionic conductivity of KOH in S/cm
        conductivity_koh_free = -2.041 * molarity - 0.0028 * molarity ** 2 + 0.005332 * molarity * stack_temperature + 207.2 * (
                molarity / stack_temperature) \
                         + 0.001043 * molarity ** 3 - 0.0000003 * molarity ** 2 * stack_temperature ** 2
        # Calculate free resistance of electrolyte
        resistance_ele_free = (1 / conductivity_koh_free) * (
                    (self.__anode_membrane_gap / self.__anode_surface + self.__cathode_membrane_gap / self.__cathode_surface) / 100)
        # Incorporate bubble rate into resistance
        resistance_ele_epsilon = resistance_ele_free * ((1 / ((1 - (2 / 3) * bubble_rate_coverage) ** (3 / 2))) - 1)
        resistance_ele = resistance_ele_free + resistance_ele_epsilon

        return resistance_ele

    def __membrane_resistance(self, stack_temperature) -> float:
        # Generic values from "VERMEIREN, P. (1998). Evaluation of the ZirfonS separator for use in alkaline water electrolysis and Ni-H2 batteries.
        # International Journal of Hydrogen Energy, 23(5), 321–324. doi:10.1016/s0360-3199(97)00069-4" (FROM GRAPH!)
        resistance_membrane_per_area = self.__parameters.zirfon1 * stack_temperature ** 2 + self.__parameters.zirfon2 * stack_temperature + self.__parameters.zirfon3
        resistance_membrane_total = resistance_membrane_per_area / (self.__membrane_surface_area * 10000)

        return resistance_membrane_total

    def get_geometric_area_cell(self) -> float:
        return self.__membrane_surface_area

