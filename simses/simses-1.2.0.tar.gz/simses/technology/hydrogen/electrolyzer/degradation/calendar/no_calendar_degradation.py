from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel


class NoCalendarDegradationModel(CalendarDegradationModel):

    def __init__(self):
        super().__init__()

    def calculate_resistance_increase(self, state: ElectrolyzerState) -> None:
        pass

    def calculate_exchange_current_dens_decrease(self, state: ElectrolyzerState):
        pass

    def get_resistance_increase(self) -> float:
        return 0

    def get_exchange_current_dens_decrease(self) -> float:
        return 0

    def reset(self, state: ElectrolyzerState) -> None:
        pass

    def close(self) -> None:
        pass
