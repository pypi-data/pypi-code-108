from numpy import sqrt


class RampinelliFit:

    """
    Inverter Equation based on:
    G.A. Rampinelli, A. Krenzinger, and F. Chenlo Romero.
    "Mathematical models for efficiency of inverters used in grid connected photovoltaic systems".
    In: Renewable and Sustainable Energy Reviews 34 (June 2014), pp. 578–587.
    doi: 10.1016/j.rser.2014.03.047.

    efficiency = p / (p + k0 + k1*p k2*p^2), where p = p_ac / p_max.
    """

    def __init__(self, max_power: float, charge_coefficients: tuple, discharge_coefficients: tuple = None):
        self.__max_power: float = max_power
        if discharge_coefficients is None:
            discharge_coefficients = charge_coefficients
        self.__k0_charge, self.__k1_charge, self.__k2_charge = charge_coefficients
        self.__k0_discharge, self.__k1_discharge, self.__k2_discharge = discharge_coefficients

    def get_efficiency_to_ac_reverse(self, dc_power: float) -> float:
        p = (self.__max_power + self.__k1_discharge * self.__max_power) / self.__k2_discharge
        q = (self.__max_power ** 2 * self.__k0_discharge - abs(dc_power) * self.__max_power) / self.__k2_discharge
        return min(0.0, -(-p / 2 + sqrt((p / 2) ** 2 - q)))

    def get_efficiency_to_dc_reverse(self, dc_power: float) -> float:
        p = (abs(dc_power) * self.__max_power * (1 + self.__k1_charge)) / (self.__k2_charge * abs(dc_power) - self.__max_power)
        q = (abs(dc_power) * self.__k0_charge * self.__max_power ** 2) / (self.__k2_charge * abs(dc_power) - self.__max_power)
        return max(0.0, -p / 2 + sqrt((p / 2) ** 2 - q))

    def get_efficiency_to_ac(self, power: float) -> float:
        power_ratio = abs(power) / self.__max_power
        if power_ratio < 0.0 or power_ratio > 1.0:
            raise Exception('Power ratio is not possible: ' + str(power_ratio))
        return power_ratio / (power_ratio + self.__k0_discharge + self.__k1_discharge * power_ratio +
                              self.__k2_discharge * power_ratio ** 2)

    def get_efficiency_to_dc(self, power: float) -> float:
        power_ratio = abs(power) / self.__max_power
        if power_ratio < 0.0 or power_ratio > 1.0:
            raise Exception('Power ratio is not possible: ' + str(power_ratio))
        return power_ratio / (power_ratio + self.__k0_charge + self.__k1_charge * power_ratio +
                              self.__k2_charge * power_ratio ** 2)
