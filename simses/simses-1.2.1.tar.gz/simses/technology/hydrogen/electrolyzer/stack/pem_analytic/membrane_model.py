import numpy

from simses.commons.constants import Hydrogen
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.stack.pem_analytic.pressure_model import \
    PemPressureModel


class PemMembraneModel:

    # TODO Earnings per share?
    EPS = numpy.finfo(float).eps
    GEOM_AREA_CELL = 1225  # cm2  example from Siemens from: PEM-Elektrolyse-Systeme zur Anwendung in Power-to-Gas Anlagen
    DIFF_COEF_H2 = 4.65 * 10 ** (-11)  # mol/(cm s bar)
    DIFF_COEF_O2 = 2 * 10 ** (-11)  # mol/(cm s bar)
    DP_COEF_H2 = 2 * 10 ** (-11)  # mol/(cm s bar)
    WATER_DRAG_COEFF = 0.27  # molH20/ molH+

    def __init__(self, pressure_model: PemPressureModel, geom_area_cell: float = GEOM_AREA_CELL, thickness: float = 200 * 10 ** (-4),
                 humidification: float = 25.0):
        self.__thickness: float = thickness  # cm
        self.__LAMBDA: float = humidification  # degree of humidification
        self.__geom_area_cell: float = geom_area_cell  # cm2
        self.__pressure_model: PemPressureModel = pressure_model

    def get_geometric_area_cell(self) -> float:
        return self.__geom_area_cell

    def resistance(self, stack_temperature) -> float:
        conductivity_nafion = (0.005139 * self.__LAMBDA - 0.00326) * \
                              numpy.exp(1268 * (1 / (303) - 1 / (stack_temperature + 273.15)))  # S/cm
        return self.__thickness / conductivity_nafion

    def get_h2_permeation_for_cell(self, state: ElectrolyzerState, current_cell: float) -> float:
        """
        permeation of hydrogen through membrane due to diffusion because of differential partial pressures
        Parameters
        ----------
        part_pressure_h2 :
        part_pressure_o2 :

        Returns
        -------
        float:
            mol/s
        """
        current_dens_cell = current_cell / self.__geom_area_cell
        part_pressure_h2: float = self.__pressure_model.get_partial_pressure_h2(state, current_dens_cell)
        sat_pressure_h2o: float = self.__pressure_model.get_sat_pressure_h2o(state.temperature)
        part_pressure_o2: float = self.__pressure_model.get_partial_pressure_o2(state, current_dens_cell)
        if part_pressure_h2 + sat_pressure_h2o <= 1 + self.EPS:  # prevention of negatative pressures at cathode side
            return 0
        return self.DIFF_COEF_H2 * part_pressure_h2 / self.__thickness * self.__geom_area_cell + self.DP_COEF_H2 * \
               (part_pressure_h2 - part_pressure_o2) / self.__thickness * self.__geom_area_cell  # mol/s

    def get_o2_permeation_for_cell(self, state: ElectrolyzerState, current_cell: float) -> float:
        """
        permeation of oxygen through membrane due to diffusion because of differential partial pressures

        Parameters
        ----------
        part_pressure_o2 :

        Returns
        -------

        """
        current_dens_cell = current_cell / self.__geom_area_cell
        part_pressure_h2: float = self.__pressure_model.get_partial_pressure_h2(state, current_dens_cell)
        part_pressure_o2: float = self.__pressure_model.get_partial_pressure_o2(state, current_dens_cell)
        if part_pressure_h2 == 0 or current_cell == 0:  # prevention of negative pressures at anode side
            return 0
        return self.DIFF_COEF_O2 * part_pressure_o2 / self.__thickness * self.__geom_area_cell  # mol/s

    def get_h2o_permeation_for_cell(self, current_cell: float) -> float:
        return self.WATER_DRAG_COEFF * current_cell / Hydrogen.FARADAY_CONST
