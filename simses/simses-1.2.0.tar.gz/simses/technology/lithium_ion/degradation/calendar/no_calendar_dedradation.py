from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.degradation.calendar.calendar_degradation import \
    CalendarDegradationModel


class NoCalendarDegradationModel(CalendarDegradationModel):

    def __init__(self):
        super().__init__(None)

    def calculate_degradation(self, time: float, battery_state: LithiumIonState) -> None:
        pass

    def calculate_resistance_increase(self, time: float, battery_state: LithiumIonState) -> None:
        pass

    def get_degradation(self) -> float:
        return 0

    def get_resistance_increase(self) -> float:
        return 0

    def reset(self, battery_state: LithiumIonState) -> None:
        pass

    def close(self) -> None:
        pass
