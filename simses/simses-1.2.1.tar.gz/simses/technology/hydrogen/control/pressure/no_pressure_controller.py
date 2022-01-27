from simses.technology.hydrogen.control.pressure.pressure_controller import \
    PressureController


class NoPressureController(PressureController):

    def __init__(self):
        super().__init__()

    def calculate_n_h2_out(self, pressure_cathode: float, n_h2_prod: float, timestep: float, pressure_factor: float) -> float:
        return n_h2_prod

    def calculate_n_o2_out(self, pressure_anode: float, n_o2_prod: float, timestep: float) -> float:
        return n_o2_prod

    def calculate_n_h2_in(self, pressure_anode: float, n_h2_used: float) -> float:
        return n_h2_used

    def calculate_n_o2_in(self, pressure_cathode: float, n_o2_used: float) -> float:
        return n_o2_used
