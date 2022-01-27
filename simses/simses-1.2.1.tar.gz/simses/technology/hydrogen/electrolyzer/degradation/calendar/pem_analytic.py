import math as m

from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel


class CalendarDegradationPemElMultiDimAnalyitic(CalendarDegradationModel):
    """
    Calendaric degradation model for PemElectrolyzerMultiDimAnalyitc
    decreases the exchange current density in dependency of the operation time
    """
    def __init__(self, general_config: GeneralSimulationConfig):
        super().__init__()
        self.__start_time = general_config.start  # s
        self.__exchange_current_decrease = 0  # p.u.
        self.__resistance_increase = 0  # p.u.
        self.__timestep = general_config.timestep

    # def calculate_resistance_increase(self, hydrogen_state: HydrogenState) -> None:
    #     relative_time_h = (hydrogen_state.time - self.__start_time) / 3600  # s -> h
    #     resistance_increase_over_total_lifetime = 0.12699  # Ohm cm²
    #     resistance_bol = 0.18416  # reference resistance at atmospheric pressure, i = 2 A/cm², T = 80°C
    #     rel_resistance_increase = resistance_increase_over_total_lifetime / resistance_bol
    #     lifetime = 80000  # h
    #     self.__resistance_increase = rel_resistance_increase / lifetime * relative_time_h

    def calculate_resistance_increase(self, state: ElectrolyzerState) -> None:
        current_dens = state.current_density
        timestep_h = self.__timestep / 3600  # s -> h
        resistance_increase_over_total_lifetime = 0.12699  # Ohm cm²
        resistance_bol = 0.18416  # reference resistance at atmospheric pressure, i = 2 A/cm², T = 80°C
        rel_resistance_increase = resistance_increase_over_total_lifetime / resistance_bol
        lifetime = 80000  # h
        if current_dens == 0:
            self.__resistance_increase += 0
        else:
            self.__resistance_increase += rel_resistance_increase / lifetime * timestep_h

    def calculate_exchange_current_dens_decrease(self, state: ElectrolyzerState):
        """
        Calculation of exchange current density decrease dependent on time the electrolyzer cell is in operation.
        based on paper: "Polymer electrolyte membrane water electrolysis: Restraining degradation in the presence
        of fluctuating power"  by Rakousky, Christoph
        year: 2017
        :param state:
        :return: none
        """
        relative_time_h = (state.time - self.__start_time) / 3600  # s -> h
        self.__exchange_current_decrease = 54.34 / 100 * m.exp(-0.007806 * relative_time_h) + 45.56 / 100

    def get_resistance_increase(self) -> float:
        return self.__resistance_increase

    def get_exchange_current_dens_decrease(self) -> float:
        return self.__exchange_current_decrease

    def reset(self, state: ElectrolyzerState) -> None:
        pass

    def close(self) -> None:
        pass



