import numpy as np


def calc_cv_cu_nist(T):
    # Temperature range: 4-300 K
    density = 8960  # No value in NIST database, so most trustworthy value

    coeff = [-0.3797, 3.54322, -12.7328, 21.9661, -18.996, 8.61013, -0.15973, -1.91844]
    log_T = np.log10(T)
    poly = np.polyval(coeff, log_T)

    return density * np.power(10, poly)


def calc_cv_nb3sn_nist(T, B, Tc0=17.8, Bc20=27.012):
    if not isinstance(T, np.ndarray):
        T = np.array([T])

    density = 8950
    cp = density * (234.89 + 0.0425 * T)
    coeff = [0.1662252, -0.6827738, -6.3977, 57.48133, -186.90995, 305.01434, -247.44839, 79.78547]

    log_T = np.log10(T)
    cp[(T > 20) & (T < 400)] = density * np.power(10, np.polyval(coeff, log_T[(T > 20) & (T < 400)]))

    Tc = 0
    if B <= Bc20:
        Tc = Tc0 * np.power(1 - B / Bc20, 0.59)

    beta = 1.241e-3
    gamma = 0.138

    cp[T <= Tc] = density * (
                (beta + 3 * gamma / np.power(Tc0, 2)) * np.power(T[T <= Tc], 3) + gamma * B / Bc20 * T[T <= Tc])

    cp[(T > Tc) & (T < 20)] = density * (beta * np.power(T[(T > Tc) & (T < 20)], 3) + gamma * T[(T > Tc) & (T < 20)])

    return cp
