
class HysteresisController:

    def __init__(self):
        self.__hvac_thermal_power = 0
        self.__outlet_thermal_power = 0
        self.__outlet_open = False

    def compute(self) -> None:
        # Computation logic here to assign thermal power values
        pass

    @property
    def hvac_thermal_power(self) -> float:
        return self.__hvac_thermal_power

    @property
    def outlet_open(self) -> bool:
        return self.__outlet_open

    @property
    def outlet_thermal_power(self) -> float:
        return self.__outlet_thermal_power