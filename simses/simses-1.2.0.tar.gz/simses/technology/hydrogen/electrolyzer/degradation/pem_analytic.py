from simses.commons.config.simulation.electrolyzer import ElectrolyzerConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.degradation.calendar.pem_analytic import \
    CalendarDegradationPemElMultiDimAnalyitic
from simses.technology.hydrogen.electrolyzer.degradation.cyclic.pem_analytic import \
    CyclicDegradationPemElMultiDimAnalytic
from simses.technology.hydrogen.electrolyzer.degradation.degradation_model import \
    DegradationModel
from simses.technology.hydrogen.electrolyzer.stack.stack_model import ElectrolyzerStackModel


class PemElMultiDimAnalyticDegradationModel(DegradationModel):

    def __init__(self, electrolyzer: ElectrolyzerStackModel, config: ElectrolyzerConfig,
                 general_config: GeneralSimulationConfig):
        super().__init__(CyclicDegradationPemElMultiDimAnalytic(),
                         CalendarDegradationPemElMultiDimAnalyitic(general_config))

        self.__end_of_life = config.eol
        self.__rev_voltage_bol = electrolyzer.get_reference_voltage_eol(0.0, 1.0)
        self.__voltage_increase_eol = 0.27  # V
        self.__soh = 1.0  # p.u.

    def calculate_soh(self, state: ElectrolyzerState) -> None:
        self.__soh = 1.0 - 0.2 * (state.reference_voltage - self.__rev_voltage_bol) / self.__voltage_increase_eol

    def get_soh_el(self):
        return self.__soh