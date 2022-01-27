from simses.commons.state.technology.electrolyzer import ElectrolyzerState
from simses.technology.hydrogen.electrolyzer.degradation.calendar.no_calendar_degradation import \
    NoCalendarDegradationModel
from simses.technology.hydrogen.electrolyzer.degradation.cyclic.no_cyclic_degradation import \
    NoCyclicDegradationModel
from simses.technology.hydrogen.electrolyzer.degradation.degradation_model import \
    DegradationModel


class NoDegradationModel(DegradationModel):

    def __init__(self):
        super().__init__(NoCyclicDegradationModel(), NoCalendarDegradationModel())

    def calculate_soh(self, state: ElectrolyzerState) -> None:
        pass

    def get_soh_el(self):
        return 1
