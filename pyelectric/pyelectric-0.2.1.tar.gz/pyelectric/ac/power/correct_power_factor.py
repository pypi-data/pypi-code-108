import math

from pyelectric.ac.power import Power


def reactance(voltage: float, power: Power, new_factor: float) -> float:
    new_reactive_power = math.tan(math.acos(new_factor)) * power.active
    Q = power.reactive - new_reactive_power
    return voltage**2 / Q


def capacitance(reactance: float, frequency: float) -> float:
    return 1/(2*math.pi*frequency*reactance)
