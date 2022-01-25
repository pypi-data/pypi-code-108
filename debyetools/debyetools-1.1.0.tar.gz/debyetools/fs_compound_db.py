
import numpy as np
from scipy.optimize import curve_fit

Cp2fit = lambda T, P0, P1, P2, P3, P4, P5: P0*T**0 + P1*T**1 + P2*T**(-2) + P3*T**2 + P4*T**(-.5) + P5*T**(-3)
alpha2fit = lambda T, Q0, Q1, Q2, Q3: Q0*T**0 + Q1*T**1 + Q2*T**(-1) + Q3*T**(-2)
Ksinv2fit = lambda T, R0, R1, R2, R3: R0*T**0 + R1*T**1 + R2*T**2 + R3*T**3
Ksp2fit = lambda T, S0, S1: S0 + S1*(T-298.15)*np.log(T/298.15)

def fit_FS(tprops, T_from, T_to):
    """
    Procedure for the fitting of FS compound database parametes to thermodynamic properties.

    :param dict tprops: Dictionary with the thermodynamic properties.
    :params float T_from: Initial temperature.
    :params float T_to: Final temperature.

    :return dict: Dictionary with the optimal parameters.
    """

    from_ix = np.where(np.round(tprops['T'],2) == np.round(T_from,2))[0][0]
    to_ix = np.where(np.round(tprops['T'],2) == np.round(T_to,2))[0][0]

    fs_params_Cp, c = curve_fit(Cp2fit, tprops['T'][from_ix:to_ix+1], tprops['Cp'][from_ix:to_ix+1])
    fs_params_alpha, c = curve_fit(alpha2fit, tprops['T'][from_ix:to_ix+1], tprops['a'][from_ix:to_ix+1])
    fs_params_Ksinv, c = curve_fit(Ksinv2fit, tprops['T'][from_ix:to_ix+1], [1/ksi for ksi in tprops['Ks'][from_ix:to_ix+1]])
    fs_params_Ksp, c = curve_fit(Ksp2fit, tprops['T'][from_ix:to_ix+1], tprops['Ksp'][from_ix:to_ix+1])


    return {'Cp': fs_params_Cp, 'a':fs_params_alpha, '1/Ks': fs_params_Ksinv, 'Ksp':fs_params_Ksp}
