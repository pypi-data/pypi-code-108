import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
from datetime import datetime


def bsm_d1(K, F, sigma, r, T, q):
    d1 = (np.log(F/K) + (r - q + sigma**2/2) * T)/(sigma * T**0.5)
    return d1


def bsm(K, F, sigma, r, T, q, direction):
    # 欧式 BSM
    d1 = bsm_d1(K, F, sigma, r, T, q)
    d2 = d1 - sigma * (T**0.5)
    if direction.lower() == 'call':
        c = np.exp(-q * T) * F * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)
        return c
    elif direction.lower() == 'put':
        p = np.exp(-r * T) * K * norm.cdf(-d2) - np.exp(-q * T) * F * norm.cdf(-d1)
        return p
    elif direction.lower() == 'binary call':
        bc = np.exp(-r * T) * norm.cdf(d2)
        return bc
    elif direction.lower() == 'binary put':
        bp = np.exp(-r * T) * norm.cdf(-d2)
        return bp
    else:
        raise ValueError("Parameter direction Error")


def bsm_delta(K, F, sigma, r, T, q, direction):
    # 欧式 delta
    d1 = bsm_d1(K, F, sigma, r, T, q)
    d2 = d1 - sigma * (T ** 0.5)
    if direction.lower() == 'call':
        return np.exp(-q * T) * norm.cdf(d1)
    elif direction.lower() == 'put':
        return np.exp(-q * T) * (norm.cdf(d1) - 1)
    elif direction.lower() == 'binary call':
        return np.exp(-r * T) * norm.pdf(d2) / (sigma * F * T**0.5)
    elif direction.lower() == 'binary put':
        return -np.exp(-r * T) * norm.pdf(d2) / (sigma * F * T**0.5)
    else:
        raise ValueError("parameter direction should either be 'call' or 'put'")


def bsm_gamma(K, F, sigma, r, T, q):
    d1 = bsm_d1(K, F, sigma, r, T, q)
    gamma = norm.pdf(d1) * np.exp(-q * T) / (F * sigma * T**0.5)
    return gamma


def bsm_theta(K, F, sigma, r, T, q, direction):
    d1 = bsm_d1(K, F, sigma, r, T, q)
    d2 = d1 - sigma * (T ** 0.5)
    if direction.lower() == 'call':
        theta = -F * norm.pdf(d1) * sigma * np.exp(-q * T) / (2 * T**0.5) \
                + q * F * norm.cdf(d1) * np.exp(-q * T) - r * K * np.exp(-r * T) * norm.cdf(d2)
        return theta
    elif direction.lower() == 'put':
        theta = -F * norm.pdf(d1) * sigma * np.exp(-q * T) / (2 * T ** 0.5) \
                - q * F * norm.cdf(-d1) * np.exp(-q * T) + r * K * np.exp(-r * T) * norm.cdf(-d2)
        return theta
    else:
        raise ValueError("parameter direction should either be 'call' or 'put'")


def bsm_vega(K, F, sigma, r, T, q):
    d1 = bsm_d1(K, F, sigma, r, T, q)
    vega = F * T**0.5 * norm.pdf(d1) * np.exp(-q * T)
    return vega


def kv(K, F, sigma, r, T, q, direction):
    # 亚式看涨 KV
    q = q + sigma ** 2 / 6
    sigma = sigma / np.sqrt(3)
    d1 = bsm_d1(K, F, sigma, r, T, q)
    d2 = d1 - sigma * (T**0.5)
    if direction.lower() == 'call':
        c = np.exp(-q * T) * F * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)
        return c
    elif direction.lower() == 'put':
        p = np.exp(-r * T) * K * norm.cdf(-d2) - np.exp(-q * T) * F * norm.cdf(-d1)
        return p
    else:
        raise ValueError("parameter direction should either be 'call' or 'put'")


def baw(K, F, sigma, r, T, q, direction, epsilon):
    n = 2 * (r - q) / (sigma**2)
    m = 2 * r / (sigma**2)
    k = 1 - np.exp(-r * T)
    q1 = (1 - n - np.sqrt((n - 1)**2 + 4 * m / k))/2
    q2 = (1 - n + np.sqrt((n - 1)**2 + 4 * m / k))/2

    dx = 0.01
    # epsilon = 0.00001
    i = 1
    imax = 50

    if direction.lower() == 'call':
        if q == 0:
            Call = bsm(K, F, sigma, r, T, q, 'call')
        else:
            S1 = K
            while i <= imax:
                c0 = bsm(K, S1, sigma, r, T, q, 'call')
                cu = bsm(K, S1 * (1 + dx), sigma, r, T, q, 'call')
                cd = bsm(K, S1 * (1 - dx), sigma, r, T, q, 'call')
                gap0 = S1 - K - c0 - (S1 / q2) * (1 - np.exp(-q * T) * norm.cdf(bsm_d1(K, S1, sigma, r, T, q)))
                gapu = S1 * (1 + dx) - K - cu - (S1 * (1 + dx) / q2) * (
                        1 - np.exp(-q * T) * norm.cdf(bsm_d1(K, S1 * (1 + dx), sigma, r, T, q)))
                gapd = S1 * (1 - dx) - K - cd - (S1 * (1 - dx) / q2) * (
                        1 - np.exp(-q * T) * norm.cdf(bsm_d1(K, S1 * (1 - dx), sigma, r, T, q)))
                dfx = (gapu - gapd)/(2 * dx * S1)

                if np.abs(gap0 / K) <= epsilon:
                    break
                else:
                    S1 -= gap0/dfx
                    i += 1
            if F >= S1:
                Call = F - K
            else:
                bsmc = bsm(K, F, sigma, r, T, q, 'call')
                Call = bsmc + (S1 / q2) * (
                        1 - np.exp(-q * T) * norm.cdf(bsm_d1(K, S1, sigma, r, T, q))
                ) * (F / S1)**q2
        return Call

    elif direction.lower() == 'put':
        S2 = K
        while i <= imax:
            p0 = bsm(K, S2, sigma, r, T, q, 'put')
            pu = bsm(K, S2 * (1 + dx), sigma, r, T, q, 'put')
            pd = bsm(K, S2 * (1 - dx), sigma, r, T, q, 'put')
            gap0 = K - S2 - p0 + (S2 / q1) * (1 - np.exp(-q * T) * norm.cdf(-bsm_d1(K, S2, sigma, r, T, q)))
            gapu = K - S2 * (1 + dx) - pu + (S2 * (1 + dx) / q1) * (
                    1 - np.exp(-q * T) * norm.cdf(-bsm_d1(K, S2 * (1 + dx), sigma, r, T, q)))
            gapd = K - S2 * (1 - dx) - pd + (S2 * (1 - dx) / q1) * (
                    1 - np.exp(-q * T) * norm.cdf(-bsm_d1(K, S2 * (1 - dx), sigma, r, T, q)))
            dfx = (gapu - gapd)/(2 * dx * S2)
            if np.abs(gap0) <= epsilon:
                break
            else:
                S2 -= gap0/dfx
                i += 1
        if F <= S2:
            Put = K - F
        else:
            bsmp = bsm(K, F, sigma, r, T, q, 'put')
            Put = bsmp - (S2 / q1) * (
                    1 - np.exp(-q * T) * norm.cdf(-bsm_d1(K, S2, sigma, r, T, q))
            ) * (F / S2)**q1
        return Put
    else:
        raise ValueError("parameter direction should either be 'call' or 'put'")


def bsm_imp_vol(K, F, sigma_guess, r, T, q, direction, opt):
    imax = 50
    i = 1
    epsilon = 0.00001
    while i <= imax:
        if np.abs(bsm(K, F, sigma_guess, r, T, q, direction) - opt) <= epsilon:
            break
        else:
            sigma_guess -= (
                                   bsm(K, F, sigma_guess, r, T, q, direction) - opt
                           ) / bsm_vega(K, F, sigma_guess, r, T, q)
            i += 1
    return sigma_guess


def baw_imp_vol(K, F, sigma_guess, r, T, q, direction, epsilon, opt):
    imax = 200
    i = 0
    # epsilon = 0.00001
    dx = 0.0001
    while i <= imax:
        if np.abs(baw(K, F, sigma_guess, r, T, q, direction, epsilon) - opt) <= epsilon:
            break
        else:
            dfx = (
                          baw(
                              K, F, sigma_guess * (1 + dx), r, T, q, direction, epsilon
                          ) - baw(
                      K, F, sigma_guess * (1 - dx), r, T, q, direction, epsilon
                  )
                  ) / (2 * sigma_guess * dx)
            sigma_guess -= (
                                   baw(K, F, sigma_guess, r, T, q, direction, epsilon) - opt
                           ) / dfx
            i += 1
    return sigma_guess


def crr_convertible_bond(K, F, sigma, T, steps, r=0.015, bond=100):
    delta_t = T / steps

    u = np.exp(sigma * np.sqrt(delta_t))
    d = 1 / u
    p = (np.exp(r * delta_t) - d) / (u - d)

    lattice = np.zeros((steps + 1, steps + 1))

    for i in range(steps + 1):
        spot_value = F * u ** (steps - i) * d ** i
        lattice[i, steps] = max(bond / K * spot_value, bond)

    discount_factor = np.exp(-r * delta_t)
    for j in range(steps - 1, -1, -1):
        for i in range(j + 1):
            fu = lattice[i, j + 1]
            fd = lattice[i, j + 1]
            discount_value = discount_factor * ((p * fu) + (1 - p) * fd)

            spot_value = F * u ** (j - i) * d ** i
            convert_value = bond / K * spot_value
            if convert_value > discount_value:
                a = 1
            lattice[i, j] = max(discount_value, convert_value)

    return lattice[0, 0]


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    ac = []
    ad = []
    ag = []
    x_axis = np.array(range(0, 100))
    for i in x_axis:
        print(i)
        # i = 80
        ac.append(
            bsm(
                K=50,
                F=i,
                sigma=0.5,
                T=1,
                q=0,
                r=0.015,
                direction='call'
            )
        )
        ad.append(
            bsm_delta(
                K=50,
                F=i,
                sigma=0.3,
                T=1,
                q=0,
                r=0.015,
                direction='call'
            )
        )
        ag.append(
            bsm_gamma(
                K=50,
                F=i,
                sigma=0.3,
                T=1,
                q=0,
                r=0.015,
            )
        )

    df = pd.DataFrame(
        {
            'spot': x_axis,
            'price': ac,
            'delta': ad,
            'gamma': ag
        }
    )
    df.to_excel('option_price.xlsx')

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(x_axis, ac)

    plt.show()






