import math as m

import numpy as np

from simses.commons.constants import Hydrogen
from simses.technology.hydrogen.hydrogen_storage.hydrogen_storage import HydrogenStorage


class PressureTank(HydrogenStorage):

    __TEMPERATURE = 273.15 + 25  # K
    __WALL_THIKNESS = 1  # cm
    __WALL_DIFFUSION_COEF: float = 4.4 * 10.0 ** (-7) * m.exp(-0.555 / Hydrogen.BOLTZ_CONST / __TEMPERATURE)  # cm2/s  selfdischarge through wall

    def __init__(self, capacity: float, max_pressure: float, soc: float):
        super().__init__()
        self.__soc: float = soc  # p.u.
        self.__capacity: float = capacity  # Wh
        self.__max_pressure: float = max_pressure  # bar
        self.__max_amount_hydrogen: float = self.__get_max_amount_hydrogen()  # mol
        self.__volume: float = self.__get_volume() * (100.0 * 100.0 * 100.0)  # cm3
        self.__inner_radius: float = (3.0 * self.__volume / (4.0 * m.pi)) ** (1.0 / 3.0)  # cm
        self.__inner_surface: float = 4.0 * m.pi * self.__inner_radius ** 2  # cm2
        self.__tank_pressure: float = 0.0
        self.__calculate_tank_pressure()

    def __get_max_amount_hydrogen(self) -> float:
        """ returns max amount of hydrogen in mol that can be stored within the given pressuretank"""
        return self.__capacity / 1000.0 / (Hydrogen.LOWER_HEATING_VALUE * 2 * Hydrogen.MOLAR_MASS_HYDROGEN)

    def __get_volume(self) -> float:
        """ returns required volume in m³ of the tank that represents the desired capacity """
        pressure = self.__max_pressure * 10**5
        a = 1.0
        b = - (self.__max_amount_hydrogen * Hydrogen.VAN_D_WAALS_COEF_B + self.__max_amount_hydrogen * Hydrogen.IDEAL_GAS_CONST \
               * self.__TEMPERATURE / pressure)
        c = Hydrogen.VAN_D_WAALS_COEF_A * self.__max_amount_hydrogen ** 2 / pressure
        d = - Hydrogen.VAN_D_WAALS_COEF_B * Hydrogen.VAN_D_WAALS_COEF_A * self.__max_amount_hydrogen ** 3 / pressure
        coeff = [a, b, c, d]
        n = np.roots(coeff)
        return np.max(np.real(n))

    def __get_hydrogen_amount(self) -> float:
        """ returns the current amount of hydrogen within the tank for a given SOC """
        return self.__max_amount_hydrogen * self.__soc

    def __get_hydrogen_concentration(self) -> float:
        """ returns the current hydrogen concentration within the tank in mol/cm3 """
        return self.__get_hydrogen_amount() / self.__volume

    def __ideal_gas_law(self, act_mass, volume) -> float:
        """ returns current pressure of the tank in Pa
            volume in m3, temperature in K, act_mass in mol """
        return act_mass * Hydrogen.IDEAL_GAS_CONST * self.__TEMPERATURE / \
               (volume - act_mass * Hydrogen.VAN_D_WAALS_COEF_B) - Hydrogen.VAN_D_WAALS_COEF_A * \
               act_mass ** 2 / volume ** 2  # pressure in Pa

    def __diff_loss_wall(self) -> float:
        """ returns mass losses caused by diffusion through the wall in mol/s """
        return self.__WALL_DIFFUSION_COEF * self.__get_hydrogen_concentration() * self.__inner_surface / self.__WALL_THIKNESS

    def calculate_soc(self, time_difference, hydrogen_net_flow: float) -> None:
        self.__soc += (hydrogen_net_flow - self.__diff_loss_wall()) * (time_difference) / self.__max_amount_hydrogen
        self.__calculate_tank_pressure()

    def __calculate_tank_pressure(self) -> None:
        act_mass = self.__get_hydrogen_amount()
        volume = self.__volume / (100 * 100 * 100)  # cm³ -> m³
        self.__tank_pressure = self.__ideal_gas_law(act_mass, volume) / 10 ** 5  # pressure in bar

    def get_soc(self):
        return self.__soc

    def get_capacity(self):
        return self.__capacity

    def get_tank_pressure(self) -> float:
        return self.__tank_pressure

    def close(self) -> None:
        pass
