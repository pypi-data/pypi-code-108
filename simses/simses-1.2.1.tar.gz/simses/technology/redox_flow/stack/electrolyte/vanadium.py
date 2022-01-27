import scipy.interpolate

from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem


class VanadiumSystem(ElectrolyteSystem):
    """The parameters of VanadiumSystem are based on experimental data of an electrolyte consisting of 1.6 M Vanadium in
    aqueous sulphuric acid (2 M H2SO4) from GfE (Gesellschaft für Elektrometallurgie mbH)."""

    MAX_ELECTROLYTE_TEMPERATURE = 40 + 273.15  # K
    MIN_ELECTROLYTE_TEMPERATURE = 10 + 273.15  # K

    def __init__(self, capacity: float, redox_flow_config: RedoxFlowConfig):
        super().__init__(capacity)
        self.__max_soc = redox_flow_config.max_soc
        self.__concentration_v = 1600  # mol/m^3
        self.__density_electrolyte = 1334  # kg/m^3 mean value from Lisa Hoffmann master theses (2018)
        self.__capacity_density = self.FARADAY * self.__concentration_v / 2
        soc_arr_vis = [0.15, 0.5, 0.85]
        temp_arr_vis = [288.15, 298.15, 308.15]
        visc_arr_an = [[0.00602, 0.00444, 0.00348],
                       [0.00576, 0.00418, 0.00321],
                       [0.00529, 0.00372, 0.00275]]
        self.__visc_interp_an = scipy.interpolate.interp2d(soc_arr_vis, temp_arr_vis, visc_arr_an, kind='linear')
        soc_arr_vis = [0.15, 0.5, 0.85]
        temp_arr_vis = [288.15, 298.15, 308.15]
        visc_arr_ca = [[0.00532, 0.00398, 0.00315],
                       [0.00513, 0.00379, 0.00296],
                       [0.00468, 0.00335, 0.00252]]
        self.__visc_interp_ca = scipy.interpolate.interp2d(soc_arr_vis, temp_arr_vis, visc_arr_ca, kind='linear')
        self.__max_temperature = self.MAX_ELECTROLYTE_TEMPERATURE
        self.__min_temperature = self.MIN_ELECTROLYTE_TEMPERATURE
        self.__min_viscosity = float(self.__visc_interp_ca(self.__max_soc, self.get_min_temperature()))
        self.__max_viscosity = float(self.__visc_interp_an(0.0, self.get_max_temperature()))

    def get_viscosity_anolyte(self, redox_flow_state: RedoxFlowState) -> float:
        """
        The parameter for the viscosity are based on experimental measurements performed at ZAE Bayern by Lisa Hoffmann.
        Literature source: Hoffmann, Lisa. Physical properties of a VRFB-electrolyte and their impact on the
        cell-performance. master theses. RWTH Aachen, 2018.
        The temperature dependency at SOC 50 % was extrapolated to the other SOC values.
        """
        soc = redox_flow_state.soc
        temp = redox_flow_state.temperature
        viscosity = self.__visc_interp_an(soc, temp)
        return float(viscosity)

    def get_viscosity_catholyte(self, redox_flow_state: RedoxFlowState) -> float:
        """
        The parameter for the viscosity are based on experimental measurements performed at ZAE Bayern by Lisa Hoffmann.
        Literature source: Hoffmann, Lisa. Physical properties of a VRFB-electrolyte and their impact on the
        cell-performance. master theses. RWTH Aachen, 2018.
        The temperature dependency at SOC 50 % was extrapolated to the other SOC values.
        """
        soc = redox_flow_state.soc
        temp = redox_flow_state.temperature
        viscosity = self.__visc_interp_ca(soc, temp)
        return float(viscosity)

    def get_min_viscosity(self):
        return self.__min_viscosity

    def get_max_viscosity(self):
        return self.__max_viscosity

    def get_max_temperature(self) -> float:
        return self.__max_temperature

    def get_min_temperature(self) -> float:
        return self.__min_temperature

    def get_vanadium_concentration(self) -> float:
        return self.__concentration_v  # mol/m^3

    def get_capacity_density(self) -> float:
        return self.__capacity_density  # As/m^3

    def get_electrolyte_density(self) -> float:
        return self.__density_electrolyte

    def close(self):
        super().close()
