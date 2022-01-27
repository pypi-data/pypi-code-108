import numpy as np


class Hydrogen:

    FARADAY_CONST: float = 96485.3321  # As/mol
    IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
    REAL_GAS_FACTOR = 1.0006  # from: "Wasserstoff in der Fahrzeugtechnik" under normal conditions: p = 1 bar, T = 0°C
    ISENTROP_EXPONENT = 1.4098  # # from: "Wasserstoff in der Fahrzeugtechnik" under normal conditions: p = 1 bar, T = 0°C
    MOLAR_MASS_HYDROGEN = 1.00794 * 10 ** (-3) # kg/mol
    MOLAR_MASS_WATER: float = 0.018015  # kg/mol
    MOLAR_MASS_OXYGEN = 15.999 * 10 ** (-3)  # kg/mol
    HEAT_CAPACITY_WATER: float = 4184  # J/(kg K)
    HEAT_CAPACITY_HYDROGEN = 14304  # J/(kg K)
    HEAT_CAPACITY_OXYGEN = 920  # J/(kg K)
    NORM_QUBIC_M = 11.1235  # Nm³/kg
    DENSITY_WATER = 1000  # kg/m³
    EPS = np.finfo(float).eps
    LOWER_HEATING_VALUE = 33.327  # kWh/kg lower heating value H2
    VAN_D_WAALS_COEF_A = 0.02452065  # van der Waals coefficient A of H2 (J*m³)/mol²
    VAN_D_WAALS_COEF_B = 2.65e-5  # van der Waals coefficient B of H2  m³/mol
    BOLTZ_CONST = 1.38e-23  # J/K

    @staticmethod
    def realgas_factor(p_1, p_2):
        """ calculates real gas factor for hydrogen based on grafig out of "Wasserstoff in der Fahrzeugtechnik" p. 49
        for T = 300 K """
        slope = 8.5 * 10 ** (-4)
        return 1/2 * (2 + slope * (p_1 + p_2))

    @staticmethod
    def isentropic_exponent(p_1, p_2):
        """ calculates mean isentropic exponent for hydrogen for compression from pressure p_1 to pressure p_2 in bar
        based on diagram in Thermodynamic of Pressurized Gas Strorage in Hydrogen Science and Engineering (2016)
        valid for T = 50 °C """
        slope = 9.047 * 10 ** (-4)
        return 1/2 * (2 * 1.404 + slope * (p_1 + p_2))
