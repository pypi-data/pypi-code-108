import numpy as np


def calc_rho_cu_nist(T, B, RRR):

    if not isinstance(T, np.ndarray):
        T = np.array([T])

    p1 = 1.171e-17
    p2 = 4.49
    p3 = 3.841e10
    p4 = 1.14
    p5 = 50
    p6 = 6.428
    p7 = 0.4531

    B = abs(B)

    rho_0 = 1.553e-8 / RRR
    rho_i = p1 * np.power(T, p2) / (1 + p1 * p3 * np.power(T, p2 - p4)) * np.exp(-np.power(p5 / T, p6))
    rho_i0 = p7 * rho_i * rho_0 / (rho_i + rho_0)

    rho_n = rho_0 + rho_i + rho_i0

    if B > 0.01:
        a0 = -2.662
        a1 = 0.3168
        a2 = 0.6229
        a3 = -0.1839
        a4 = 0.01827

        x = 1.553e-8 * B / rho_n

        log_x = np.log10(x)
        f_exp = a0 + a1 * log_x + a2 * np.power(log_x, 2) + a3 * np.power(log_x, 3) + a4 * np.power(log_x, 4)
        corr = np.power(10, f_exp)
    else:
        corr = 0

    return rho_n * (1 + corr)
