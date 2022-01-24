import numpy as np


def calc_jc_nbti_bottura(T, B, Tc0=9.2, Bc20=14.5, Jc_ref=3.0e9, C0=27.04, alpha=0.57, beta=0.8477, gamma=2.23234):
    # Direction of the magnetic field is not important
    B = abs(B)

    # Calculate critical magnetic field
    Bc2 = Bc20 * (1 - np.power(T / Tc0, 1.7))

    # Fix too small values
    Bc2 = np.maximum(Bc2, 0.001)

    # Calculate critical current density
    return Jc_ref * C0 * np.power(B, alpha - 1) / np.power(Bc2, alpha) * np.power(1 - B / Bc2, beta) \
           * np.power(1 - np.power(T / Tc0, 1.7), gamma)


def calc_jc_nb3sn_bordini(T, B, Jc0=267845e6, Tc0=16.3, Bc20=26.45, alpha=1.0):
    # Direction of the magnetic field is not important
    B = abs(B)

    # Very small magnetic field causes numerical problems
    B = np.maximum(B, 0.001)

    # Ratio of temperature to critical temperature
    # Avoid values higher than 1
    f_T_T0 = np.minimum(T / Tc0, 1.0)

    # Calculate critical magnetic field
    Bc2 = Bc20 * (1 - np.power(f_T_T0, 1.52))

    # Ratio of magnetic field to critical magnetic field
    f_B_Bc2 = B / Bc2

    # Avoid values higher than 1
    f_B_Bc2 = np.minimum(f_B_Bc2, 1.0)

    C = Jc0 * np.power(1 - np.power(f_T_T0, 1.52), alpha) * np.power(1 - np.power(f_T_T0, 2.0), alpha)
    return C / B * np.power(f_B_Bc2, 0.5) * np.power(1 - f_B_Bc2, 2.0)  # A / m^2


def calc_jc_nb3sn_summers(T, B, Tc0=18.0, Bc20=28.0, Jc0=3.85e10):
    # Direction of the magnetic field is not important
    B = abs(B)

    # Very small magnetic field causes numerical problems
    B = np.maximum(B, 0.001)

    # Very small temperature causes numerical problems
    T = np.maximum(T, 0.001)

    # Avoid values higher than 1
    f_T_T0 = np.minimum(T / Tc0, 1.0)
    Bc2 = Bc20 * (1 - np.power(f_T_T0, 2)) * (1 - 0.31 * np.power(f_T_T0, 2) * (1 - 1.77 * np.log(f_T_T0)))
    f_B_Bc2 = B / Bc2

    # Avoid values higher than 1
    f_B_Bc2 = np.minimum(f_B_Bc2, 1.0)

    return Jc0 / np.sqrt(B) * np.power(1 - f_B_Bc2, 2) * np.power((1 - np.power(f_T_T0, 2)), 2)


def calc_jc_nb3sn_summers_orig(T, B, Tc0=18.0, Bc20=28.0, Jc0=3.85e10):
    # Direction of the magnetic field is not important
    B = abs(B)

    # Very small magnetic field causes numerical problems
    B = np.maximum(B, 0.001)

    # Very small temperature causes numerical problems
    T = np.maximum(T, 0.001)

    # Avoid values higher than 1
    f_T_T0 = np.minimum(T / Tc0, 1.0)
    Bc2 = Bc20 * (1 - np.power(f_T_T0, 2)) * (1 - 0.31 * np.power(f_T_T0, 2) * (1 - 1.77 * np.log(f_T_T0)))
    f_B_Bc2 = B / Bc2

    # Avoid values higher than 1
    f_B_Bc2 = np.minimum(f_B_Bc2, 1.0)

    return Jc0 / np.sqrt(B) * np.power(1 - f_B_Bc2, 2) * 1 / np.sqrt(f_B_Bc2) * np.power((1 - np.power(f_T_T0, 2)), 2)


