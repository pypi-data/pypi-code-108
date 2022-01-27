import math


class AlkalinePressureModel:    # TODO Check if assumption of equal pressures is correct/applicable

    def __init__(self):
        pass

    def get_sat_pressure_h2o(self, molarity: float, stack_temperature: float) -> float:
        # return self.__get_aqueous_vapour_pressure_koh(molarity, stack_temperature)
        pass

    def get_partial_pressure_h2(self, molarity: float, stack_temperature: float):
        return self.__get_aqueous_vapour_pressure_koh(molarity, stack_temperature)

    def get_partial_pressure_o2(self, molarity: float, stack_temperature: float):
        return self.__get_aqueous_vapour_pressure_koh(molarity, stack_temperature)

    def get_aqueous_vapour_pressure_koh(self, molarity: float, stack_temperature: float) -> float:
        return self.__get_aqueous_vapour_pressure_koh(molarity, stack_temperature)

    def __get_aqueous_vapour_pressure_koh(self, molarity: float, stack_temperature: float) -> float:
        return (stack_temperature ** -3.498) * math.exp(37.93 - (6426.32 / stack_temperature)) * \
               math.exp(0.016214 - 0.13802 * molarity + 0.19330 * molarity ** 0.5)

    def get_vapour_pressure_pure_water(self, stack_temperature: float) -> float:
        return self.__get_vapour_pressure_pure_water(stack_temperature)

    def __get_vapour_pressure_pure_water(self, stack_temperature: float) -> float:
        return (stack_temperature ** -3.4159) * math.exp(37.043 - (6275.7 / stack_temperature))
