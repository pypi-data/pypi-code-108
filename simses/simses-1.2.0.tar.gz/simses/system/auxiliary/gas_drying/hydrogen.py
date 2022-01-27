from simses.system.auxiliary.gas_drying.gas_dryer import GasDrying


class HydrogenGasDrying(GasDrying):

    def __init__(self):
        super().__init__()

        self.__spec_drying_energy = 139.62 * 10 ** 3  #  J/mol h2o  from: Life cycle assessment of hydrogen from proton exchange membrane water electrolysis in future energy systems
        self.__gas_drying_power = 0  #  W
        self.x_dry = 5 / 1000000  # 5 ppm

    def calculate_gas_drying_power(self, pressure_cathode, h2_outflow) -> None:
        x_h2o_after_condens = 0.07981 * pressure_cathode ** (-1.04)  # after condensation at 40°C after curve of: PEM-Elektrolyse-Systeme zur Anwendung in Power-to-Gas Anlagen
        n_h2o_drying = (x_h2o_after_condens - self.x_dry) * h2_outflow  # mol/s
        self.__gas_drying_power = self.__spec_drying_energy * n_h2o_drying  # W

    def get_gas_drying_power(self) -> float:
        return self.__gas_drying_power
