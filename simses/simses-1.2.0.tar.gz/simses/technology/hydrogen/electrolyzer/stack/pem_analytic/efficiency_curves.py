import numpy as np
import pandas as pd

from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.electrical_model import \
    PemElectricalModel
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.fluid_model import \
    PemFluidModel
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.membrane_model import \
    PemMembraneModel
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.pressure_model import \
    PemPressureModel


class PemElectrolyzerEfficiencyCurves:

    def __init__(self, electrical_model: PemElectricalModel, membrane_model: PemMembraneModel, pressure_model: PemPressureModel, fluid_modell: PemFluidModel):
        self.__electrical_model = electrical_model
        self.__membrane_model = membrane_model
        self.__pressure_model = pressure_model
        self.__fluid_model = fluid_modell

    def calculate_efficiency_curves(self, hydrogen_state: ElectrolyzerState, start=0.01, stop=3.01, step=0.01):
        # stack_temperature = hydrogen_state.temperature_el  # °C
        # p_anode = hydrogen_state.pressure_anode_el  # barg
        # p_cathode = hydrogen_state.pressure_cathode_el  # barg
        # resistance_increase = hydrogen_state.resistance_increase_el  # p.u.
        # exchange_current_decrease = hydrogen_state.exchange_current_decrease_el  # p.u.
        current_dens_series = pd.Series(np.arange(start, stop, step))
        current_cell_series = current_dens_series.multiply(self.__membrane_model.get_geometric_area_cell())  # cells are connected serial -> stack current = cell current
        voltage_cell_series = current_dens_series.apply(lambda x: self.__electrical_model.get_cell_voltage(x,
                                                                                            hydrogen_state))
        # voltage_stack_series = voltage_cell_series.apply(lambda x: x * self.__number_cells)
        rev_voltage = self.__electrical_model.get_rev_voltage(hydrogen_state.temperature)

        # calculation of partial pressures of hydrogen and oxygen and saturation pressure of water
        h2o_sat_pressure = self.__pressure_model.get_sat_pressure_h2o(hydrogen_state.temperature)
        part_pressure_h2_series = current_dens_series.apply(lambda x: self.__pressure_model.get_partial_pressure_h2(
                                                            hydrogen_state, x))
        part_pressure_o2_series = current_dens_series.apply(lambda x: self.__pressure_model.get_partial_pressure_o2(
                                                            hydrogen_state, x))

        # generation and use of water, hydrogen and oxygen
        h2_gen_cell_series = current_cell_series.apply(self.__fluid_model.get_h2_generation_cell)
        o2_gen_cell_series = current_cell_series.apply(self.__fluid_model.get_o2_generation_cell)
        h2o_use_cell_series = current_cell_series.apply(self.__fluid_model.get_h2o_use_cell)

        # permeation of hydrogen, oxygen and water through membrane
        # def clac_h2_perm_df(df):
        #     return self.calculate_h2_permeation_cell(df[0], df[1])
        # df_part_pressures = pd.DataFrame({'part pressure h2': part_pressure_h2_series,
        #                                   'part pressure o2': part_pressure_o2_series})
        # h2_perm_cell_series = df_part_pressures.apply(clac_h2_perm_df, axis=1)
        # o2_perm_cell_series = part_pressure_o2_series.apply(self.calculate_o2_permeation_cell)
        # h2o_perm_cell_series = current_cell_series.apply(self.calculate_h2o_permeation_cell)

        h2_perm_series = current_cell_series.apply(lambda x: self.__membrane_model.get_h2_permeation_for_cell(hydrogen_state, x))
        o2_perm_series = current_cell_series.apply(lambda x: self.__membrane_model.get_o2_permeation_for_cell(hydrogen_state, x))
        h2o_perm_series = current_cell_series.apply(self.__membrane_model.get_h2o_permeation_for_cell)

        # use of water, production of hydrogen and oxygen at cell level
        # def calc_h2_net_cat_df(df):
        #     return self.calculate_h2_net_cathode(df[0], df[1], df[2])
        # df_net_h2_cathode = pd.DataFrame({'h2 gen': h2_gen_cell_series, 'h2 perm': h2_perm_cell_series,
        #                                   'o2 perm': o2_perm_cell_series})
        h2_net_cathode_series = current_cell_series.apply(lambda x: self.__fluid_model.get_h2_net_cathode(hydrogen_state, x))
        h2_net_cathode_series[h2_net_cathode_series < 0] = np.nan  # replace negative values by nan, so that is not calculated in the faraday efficiency

        # efficiency curve
        voltage_efficiency_series = voltage_cell_series.apply(lambda x: rev_voltage / x)
        faraday_efficiency_series = h2_net_cathode_series.divide(h2_gen_cell_series)
        cell_efficiency_series = voltage_efficiency_series.multiply(faraday_efficiency_series)

        return pd.DataFrame({'current density': current_dens_series, 'cell efficiency': cell_efficiency_series,
                             'voltage efficiency': voltage_efficiency_series, 'faraday efficiency': faraday_efficiency_series})

