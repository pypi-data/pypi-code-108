# Copyright (c) 2021 Thomas Schanzer.
# Distributed under the terms of the BSD 3-Clause License.
"""Thermodynamic calculations for parcel theory.

This module implements various atmospheric thermodynamics calculations,
both original and from literature.
"""

# pylint: disable=invalid-name, too-many-locals, too-many-arguments

import numpy as np

import metpy.calc as mpcalc
import metpy.constants as const
from metpy.units import units

from scipy.special import lambertw


# ---------- Basic thermodynamic calculations ----------

def moist_lapse_dj(
        pressure, initial_temperature, reference_pressure=None, improve=True):
    """
    Compute temperature from pressure along pseudoadiabats.

    Follows the method of Davies-Jones (2008).

    Args:
        pressure: Array of pressures for which the temperature is to
            be found.
        initial_temperature: Initial parcel temperature.
        reference_pressure: The pressure corresponding to
            initial_temperature. Optional, defaults to pressure[0].
        improve: Whether or not to apply an iteration of Newton's
            method (only relevant for method == 'fast').

    Returns:
        Array of final temperatures.

    References:
        DAVIES-JONES, R 2008, ‘An Efficient and Accurate Method for
        Computing the Wet-Bulb Temperature along Pseudoadiabats’,
        Monthly weather review, vol. 136, no. 7, pp. 2764–2785.
    """
    if reference_pressure is None:
        reference_pressure = pressure[0]
    # parcel assumed to be saturated at all times
    q_initial = saturation_specific_humidity(
        reference_pressure, initial_temperature)
    # find initial theta-e (equal to final theta-e)
    theta_e = equivalent_potential_temperature(
        reference_pressure, initial_temperature, q_initial)
    # final temperature is equal to final wet bulb temperature
    # because parcel is saturated
    return wetbulb(pressure, theta_e, improve)


def temperature_change(delta_q):
    """
    Calculate the temperature change due to evaporation of water.

    Neglects the heat capacity of components other than dry air.

    Args:
        delta_q: Specific humidity increase due to evaporation.

    Returns:
        The resulting change in temperature.
    """
    delta_T = (- const.water_heat_vaporization
               * delta_q / const.dry_air_spec_heat_press)
    return delta_T.to(units.delta_degC)


def saturation_specific_humidity(pressure, temperature):
    """Calculate saturation specific humidity."""
    q_star = mpcalc.specific_humidity_from_mixing_ratio(
        mpcalc.saturation_mixing_ratio(pressure, temperature))
    if not hasattr(pressure, 'size') and not hasattr(temperature, 'size'):
        return q_star.item()
    return q_star


def equivalent_potential_temperature(p, Tk, q, prime=False):
    """
    Calculate equivalent potential temperature.

    Uses the approximation of theta-e given in eq. 39 of Bolton (1980).
    Variable names follow the notation of Bolton.

    Args:
        p: Pressure.
        Tk: Temperature.
        q: Specific humidity.
        prime: Whether or not to also return the derivative of
            theta-e with respect to temperature at the given temperature
            and pressure (optional, defaults to False).

    Returns:
        The equivalent potential temperature (and its derivative
        w.r.t. temperature if prime=True).

    References:
        Bolton, D 1980, ‘The Computation of Equivalent Potential
        Temperature’, Monthly weather review, vol. 108, no. 7,
        pp. 1046–1053.
    """
    # ensure correct units
    Tk = Tk.to(units.kelvin)

    # constants
    a = 17.67*units.dimensionless
    b = 243.5*units.kelvin
    C = 273.15*units.kelvin
    e0 = 6.112*units.mbar  # saturation vapour pressure at 0C (mbar)
    epsilon = const.epsilon
    kappa = const.kappa

    # other variables
    es = e0*np.exp(a*(Tk - C)/(Tk - C + b))  # sat. vapour pressure
    U = q/(1 - q)*(p - es)/(epsilon*es)  # relative humidity
    e = U*es  # vapour pressure
    Td = b*np.log(U*es/e0)/(a - np.log(U*es/e0)) + C  # dew point
    r = q/(1 - q)  # mixing ratio

    # LCL temperature
    Tl = (1/(1/(Td - 56*units.kelvin) + np.log(Tk/Td)/(800*units.kelvin))
          + 56*units.kelvin)
    # LCL potential temperature
    thetadl = Tk*(1000*units.mbar/(p - e))**kappa*(Tk/Tl)**(0.28*r)
    # equivalent potential temperature
    thetae = thetadl*np.exp((3036*units.kelvin/Tl - 1.78)*r*(1 + 0.448*r))

    if prime is False:
        if not (hasattr(p, 'size') or hasattr(Tk, 'size')
                or hasattr(q, 'size')):
            return thetae.item()
        return thetae

    # derivative of sat. vapour pressure w.r.t. temperature
    dloges_dTk = a*b/(Tk - C + b)**2
    # derivative of dew point w.r.t. temperature
    dTd_dTk = a*b/(a - np.log(U*es/e0))**2 * dloges_dTk
    # derivative of LCL temperature w.r.t. temperature
    dTl_dTk = (
        - (1/(Td - 56*units.kelvin) + np.log(Tk/Td)/(800*units.kelvin))**(-2)
        * (-1/(Td - 56*units.kelvin)**2*dTd_dTk
           + (1/Tk - 1/Td*dTd_dTk)/(800*units.kelvin))
    )
    # derivative of log(LCL potential temperature) w.r.t. temperature
    dlogthetadl_dTk = (1 + 0.28*r)/Tk - 0.28*r/Tl*dTl_dTk
    # derivative of log(equivalent potential temperature) w.r.t. temperature
    dlogthetae_dTk = (dlogthetadl_dTk
                      - 3036*units.kelvin/Tl**2 * r*(1 + 0.448*r)*dTl_dTk)

    if not (hasattr(p, 'size') or hasattr(Tk, 'size')
            or hasattr(q, 'size')):
        return thetae.item(), (thetae*dlogthetae_dTk).item()
    return thetae, thetae*dlogthetae_dTk


def saturation_equivalent_potential_temperature(p, Tk, prime=False):
    """
    Calculate saturation equivalent potential temperature.

    Uses the approximation of theta-e given in eq. 39 of Bolton (1980).
    Variable names follow the notation of Bolton.

    Args:
        p: Pressure.
        Tk: Temperature.
        prime: Whether or not to also return the derivative of
            theta-e with respect to temperature at the given temperature
            and pressure (optional, defaults to False).

    Returns:
        The saturation equivalent potential temperature (and its
        derivative w.r.t. temperature if prime=True).

    References:
        Bolton, D 1980, ‘The Computation of Equivalent Potential
        Temperature’, Monthly weather review, vol. 108, no. 7,
        pp. 1046–1053.
    """
    # ensure correct units
    Tk = Tk.to(units.kelvin)

    # constants
    a = 17.67*units.dimensionless
    b = 243.5*units.kelvin
    C = 273.15*units.kelvin
    e0 = 6.112*units.mbar  # saturation vapour pressure at 0C (mbar)
    epsilon = const.epsilon
    kappa = const.kappa

    # other variables
    es = e0*np.exp(a*(Tk - C)/(Tk - C + b))  # sat. vapour pressure
    rs = epsilon*es/(p - es)  # sat. mixing ratio

    # potential temperature of dry air
    thetadl = Tk*(1000*units.mbar/(p - es))**kappa
    # equivalent potential temperature
    thetae = thetadl*np.exp((3036*units.kelvin/Tk - 1.78)*rs*(1 + 0.448*rs))

    if prime is False:
        if not (hasattr(p, 'size') or hasattr(Tk, 'size')):
            return thetae.item()
        return thetae

    # derivative of sat. vapour pressure w.r.t. temperature
    des_dTk = a*b*es/(Tk - C + b)**2
    # derivative of sat. mixing ratio w.r.t. temperature
    drs_dTk = epsilon*p*des_dTk/(p - es)**2
    # derivative of log(potential temperature of dry air)
    dlogthetadl_dTk = 1/Tk + kappa*des_dTk/(p - es)
    # derivative of log(theta-e) w.r.t. temperature
    dlogthetae_dTk = (
        dlogthetadl_dTk
        - 3036*units.kelvin*rs*(1 + 0.448*rs)/Tk**2
        + (3036*units.kelvin/Tk - 1.78)*drs_dTk*(1 + 2*0.448*rs)
    )

    if not (hasattr(p, 'size') or hasattr(Tk, 'size')):
        return thetae.item(), (thetae*dlogthetae_dTk).item()
    return thetae, thetae*dlogthetae_dTk


def lcl_romps(p, T, q):
    """
    Analytic solution for the LCL (adapted from Romps 2017).

    This code is adapted from Romps (2017):
    https://romps.berkeley.edu/papers/pubdata/2016/lcl/lcl.py

    Args:
        p: Pressure.
        T: Temperature.
        q: Specific humidity.

    Returns:
        (pressure, temperature) at the LCL.

    References:
        Romps, DM 2017, ‘Exact Expression for the Lifting Condensation
        Level’, Journal of the atmospheric sciences, vol. 74,
        no. 12, pp. 3891–3900.
    """
    # unit conversions
    rhl = mpcalc.relative_humidity_from_specific_humidity(p, T, q).m
    p = p.m_as(units.pascal)
    T = T.m_as(units.kelvin)

    # Parameters
    Ttrip = 273.16  # K
    ptrip = 611.65  # Pa
    E0v = 2.3740e6  # J/kg
    rgasa = 287.04  # J/kg/K
    rgasv = 461  # J/kg/K
    cva = 719  # J/kg/K
    cvv = 1418  # J/kg/K
    cvl = 4119  # J/kg/K
    cpa = cva + rgasa
    cpv = cvv + rgasv

    def pvstarl(T):
        """Calculate the saturation vapor pressure over liquid water."""
        return (ptrip * (T/Ttrip)**((cpv-cvl)/rgasv)
                * np.exp((E0v - (cvv-cvl)*Ttrip) / rgasv * (1/Ttrip - 1/T)))

    pv = rhl * pvstarl(T)
    qv = rgasa*pv / (rgasv*p + (rgasa-rgasv)*pv)
    rgasm = (1-qv)*rgasa + qv*rgasv
    cpm = (1-qv)*cpa + qv*cpv
    aL = -(cpv-cvl)/rgasv + cpm/rgasm
    bL = -(E0v-(cvv-cvl)*Ttrip)/(rgasv*T)
    cL = rhl*np.exp(bL)
    T_lcl = bL/(aL*lambertw(bL/aL*cL**(1/aL), -1).real)*T
    p_lcl = p*(T_lcl/T)**(cpm/rgasm)

    if not (hasattr(p, 'size') or hasattr(T, 'size')
            or hasattr(q, 'size')):
        return (p_lcl/1e2*units.mbar).item(), (T_lcl*units.kelvin).item()
    return p_lcl/1e2*units.mbar, T_lcl*units.kelvin


def wetbulb_romps(pressure, temperature, specific_humidity):
    """
    Calculate wet bulb temperature using Normand's rule and Romps (2017).

    Args:
        p: Pressure.
        T: Temperature.
        q: Specific humidity.

    Returns:
        Wet bulb temperature.

    References:
        Romps, DM 2017, ‘Exact Expression for the Lifting Condensation
        Level’, Journal of the atmospheric sciences, vol. 74,
        no. 12, pp. 3891–3900.
    """
    lcl_pressure, lcl_temperature = lcl_romps(
        pressure, temperature, specific_humidity)
    # descend moist adiabatically from the LCL to the starting level
    return mpcalc.moist_lapse(pressure, lcl_temperature, lcl_pressure).item()


# ---------- Calculations from Davies-Jones 2008 ----------

def wetbulb_potential_temperature(theta_e):
    """
    Calculate theta-w from theta-e using Eq. 3.8 of Davies-Jones 2008.

    Variable names follow the notation of Davies-Jones.

    Args:
        theta_e: Equivalent potential temperature.

    Returns:
        Wet bulb potential temperature.

    References:
        DAVIES-JONES, R 2008, ‘An Efficient and Accurate Method for
        Computing the Wet-Bulb Temperature along Pseudoadiabats’,
        Monthly weather review, vol. 136, no. 7, pp. 2764–2785.
    """
    theta_e = theta_e.m_as(units.kelvin)

    C = 273.15
    X = theta_e/C

    # coefficients
    a0 = 7.101574
    a1 = -20.68208
    a2 = 16.11182
    a3 = 2.574631
    a4 = -5.205688
    b1 = -3.552497
    b2 = 3.781782
    b3 = -0.6899655
    b4 = -0.5929340

    theta_w = (
        theta_e - C
        - np.exp((a0 + a1*X + a2*X**2 + a3*X**3 + a4*X**4)
                 / (1 + b1*X + b2*X**2 + b3*X**3 + b4*X**4))
        * (theta_e >= 173.15)
    )

    if not hasattr(theta_e, 'size'):
        return (theta_w*units.celsius).item()
    return theta_w*units.celsius


def _daviesjones_f(Tw, pi, Q=None, kind='pseudo'):
    """
    Evaluate the function f defined in eq. 2.3 of Davies-Jones 2008.

    Variable names follow the notation of Davies-Jones.

    Args:
        Tw: Wet-bulb temperature in KELVIN.
        pi: Nondimensional pressure.
        Q: total mixing ratio of all phases of water (only needed for
            reversible adiabats).
        kind: 'pseudo' for pseudoadiabats and 'reversible' for
            reversible adiabats.

    Returns:
        The value of f(Tw, pi).

    References:
        DAVIES-JONES, R 2008, ‘An Efficient and Accurate Method for
        Computing the Wet-Bulb Temperature along Pseudoadiabats’,
        Monthly weather review, vol. 136, no. 7, pp. 2764–2785.
    """
    cp = const.dry_air_spec_heat_press.m
    R = const.dry_air_gas_constant.m
    lambda_ = cp/R
    pressure = 1000.0 * pi**lambda_  # in mbar

    # coefficients
    C = 273.15
    if kind == 'pseudo':
        k0 = 3036
        k1 = 1.78
        k2 = 0.448
        nu = 0.2854  # poisson constant for dry air
    elif kind == 'reversible':
        if Q is None:
            raise ValueError(
                'Total water mixing ratio Q must be supplied for '
                'reversible adiabats.')
        L0 = 2.501e6
        L1 = 2.37e3
        cpd = const.dry_air_spec_heat_press.m
        cw = const.water_specific_heat.m*1e3
        k0 = (L0 + L1*C)/(cpd + cw*Q)
        k1 = L1/(cpd + cw*Q)
        k2 = 0
        nu = const.dry_air_gas_constant.m/(cpd + cw*Q)
    else:
        raise ValueError("kind must be 'pseudo' or 'reversible'.")

    # saturation mixing ratio and vapour pressure calculated using
    # eq. 10 of Bolton 1980
    rs = mpcalc.saturation_mixing_ratio(
        pressure*units.mbar, Tw*units.kelvin).m_as(units.dimensionless)
    es = mpcalc.saturation_vapor_pressure(Tw*units.kelvin).m_as(units.mbar)

    G = (k0/Tw - k1)*(rs + k2*rs**2)
    f = (C/Tw)**lambda_ * (1 - es/pressure)**(lambda_*nu) * np.exp(-lambda_*G)
    return f


def _daviesjones_fprime(tau, pi, Q=None, kind='pseudo'):
    """
    Evaluate df/dtau (pi fixed) defined in eqs. A.1-A.5 of Davies-Jones 2008.

    Variable names follow the notation of Davies-Jones.

    Args:
        tau: Temperature in KELVIN.
        pi: Nondimensional pressure.
        Q: total mixing ratio of all phases of water (only needed for
            reversible adiabats).
        kind: 'pseudo' for pseudoadiabats and 'reversible' for
            reversible adiabats.

    Returns:
        The value of f'(Tau, pi) for fixed pi.

    References:
        DAVIES-JONES, R 2008, ‘An Efficient and Accurate Method for
        Computing the Wet-Bulb Temperature along Pseudoadiabats’,
        Monthly weather review, vol. 136, no. 7, pp. 2764–2785.
    """
    cp = const.dry_air_spec_heat_press.m
    R = const.dry_air_gas_constant.m
    lambda_ = cp/R
    pressure = 1000.0 * pi**lambda_  # in mbar

    # coefficients
    C = 273.15
    epsilon = 0.6220
    if kind == 'pseudo':
        k0 = 3036
        k1 = 1.78
        k2 = 0.448
        nu = 0.2854  # poisson constant for dry air
    elif kind == 'reversible':
        if Q is None:
            raise ValueError(
                'Total water mixing ratio Q must be supplied for '
                'reversible adiabats.')
        L0 = 2.501e6
        L1 = 2.37e3
        cpd = const.dry_air_spec_heat_press.m
        # cw = 4190.  # specific heat of liquid water
        cw = const.water_specific_heat.m*1e3
        k0 = (L0 + L1*C)/(cpd + cw*Q)
        k1 = L1/(cpd + cw*Q)
        k2 = 0
        nu = const.dry_air_gas_constant.m/(cpd + cw*Q)
    else:
        raise ValueError("kind must be 'pseudo' or 'reversible'.")

    # saturation mixing ratio and vapour pressure calculated using
    # eq. 10 of Bolton 1980
    rs = mpcalc.saturation_mixing_ratio(
        pressure*units.mbar, tau*units.kelvin).m_as(units.dimensionless)
    es = mpcalc.saturation_vapor_pressure(tau*units.kelvin).m_as(units.mbar)

    des_dtau = es*17.67*243.5/(tau - C + 243.5)**2  # eq. A.5
    drs_dtau = epsilon*pressure/(pressure - es)**2 * des_dtau  # eq. A.4
    dG_dtau = (-k0/tau**2 * (rs + k2*rs**2)
               + (k0/tau - k1)*(1 + 2*k2*rs)*drs_dtau)  # eq. A.3
    dlogf_dtau = -lambda_*(1/tau + nu/(pressure - es)*des_dtau
                           + dG_dtau)  # eq. A.2
    df_dtau = _daviesjones_f(tau, pi) * dlogf_dtau  # eq. A.1
    return df_dtau


def wetbulb(pressure, theta_e, improve=True):
    """
    Calculate wet bulb temperature using the method in Davies-Jones 2008.

    Variable names follow the notation of Davies-Jones.

    Args:
        pressure: Pressure.
        theta_e: Equivalent potential temperature.
        improve: Whether or not to perform a single iteration of
            Newton's method to improve accuracy (defaults to False).

    Returns:
        Wet bulb temperature.

    References:
        DAVIES-JONES, R 2008, ‘An Efficient and Accurate Method for
        Computing the Wet-Bulb Temperature along Pseudoadiabats’,
        Monthly weather review, vol. 136, no. 7, pp. 2764–2785.
    """
    # constants
    cp = const.dry_air_spec_heat_press.m
    R = const.dry_air_gas_constant.m
    lambda_ = cp/R
    C = 273.15

    # convert inputs to the correct form for the method
    pressure = np.atleast_1d(pressure.m_as(units.mbar))
    theta_e = np.atleast_1d(theta_e.m_as(units.kelvin))
    pi = (pressure/1000.0)**(1./lambda_)
    Teq = theta_e*pi

    # slope and intercept for guesses - eq. 4.3, 4.4
    k1 = -38.5*pi**2 + 137.81*pi - 53.737
    k2 = -4.392*pi**2 + 56.831*pi - 0.384

    # transition point between approximation schemes - eq. 4.7
    D = 1/(0.1859*pressure/1000 + 0.6512)

    # initial guess
    X = (C/Teq)**lambda_
    Tw = np.zeros(Teq.size)

    case1 = X > D
    A = 2675.0
    # saturation mixing ratio calculated via vapour pressure using
    # eq. 10 of Bolton 1980
    rs = mpcalc.saturation_mixing_ratio(
        pressure[case1]*units.mbar, Teq[case1]*units.kelvin).m
    # d(log(e_s))/dT calculated also from eq. 10, Bolton 1980
    d_log_es_dt = 17.67*243.5/(Teq[case1] + 243.5)**2
    Tw[case1] = Teq[case1] - C - A*rs/(1 + A*rs*d_log_es_dt)  # eq. 4.8

    case2 = (X >= 1) & (X <= D)
    Tw[case2] = k1[case2] - k2[case2]*X[case2]  # eq. 4.9

    case3 = (X >= 0.4) & (X < 1)
    Tw[case3] = (k1[case3] - 1.21) - (k2[case3] - 1.21)*X[case3]  # eq. 4.10

    case4 = X < 0.4
    Tw[case4] = ((k1[case4] - 2.66) - (k2[case4] - 1.21)*X[case4]
                 + 0.58/X[case4])  # eq. 4.11

    if improve is True:
        improve = 1
    elif improve is False:
        improve = 0
    for _ in range(improve):
        # execute iterations of Newton's method (eq. 2.6)
        slope = _daviesjones_fprime(Tw + C, pi)
        fvalue = _daviesjones_f(Tw + C, pi)
        Tw = Tw - (fvalue - X)/slope

    return (Tw if pressure.size > 1 else Tw.item())*units.celsius


def reversible_lapse_daviesjones(
        pressure, initial_temperature, initial_liquid_ratio,
        reference_pressure=None, improve=2):
    """
    Compute temperature along reversible adiabats.

    Uses the method of Davies-Jones (2008). Variable names follow the
    notation of Davies-Jones.

    Errors were found in Equations (5.1) and (5.3). They have been
    corrected here after consultation with the author.

    Args:
        pressure: Array of pressures for which the temperature is to
            be found.
        initial_temperature: Initial parcel temperature.
        q_initial: Initial specific humidity.
        initial_liquid_ratio: Initial ratio of liquid mass to total.
        reference_pressure: The pressure corresponding to
            initial_temperature. Optional, defaults to pressure[0].
        improve: Number of iterations of Newton's method to execute.

    Returns:
        Array of final temperatures.

    References:
        DAVIES-JONES, R 2008, ‘An Efficient and Accurate Method for
        Computing the Wet-Bulb Temperature along Pseudoadiabats’,
        Monthly weather review, vol. 136, no. 7, pp. 2764–2785.
    """
    pressure = np.atleast_1d(pressure).m_as(units.mbar)
    if reference_pressure is None:
        reference_pressure = pressure[0]
    else:
        reference_pressure = reference_pressure.m_as(units.mbar)

    cp = const.dry_air_spec_heat_press.m
    R = const.dry_air_gas_constant.m
    lambda_ = cp/R
    reference_pi = (reference_pressure/1000.0)**(1./lambda_)
    C = 273.15

    # initial specific humidity is saturated specific humidity
    q_initial = saturation_specific_humidity(
        reference_pressure*units.mbar, initial_temperature).m

    # total mixing ratio (liquid + vapour)
    Q = ((q_initial + initial_liquid_ratio)
         / (1 - q_initial - initial_liquid_ratio))
    if hasattr(Q, 'units'):
        Q = Q.m_as(units.dimensionless)  # make sure Q is a number

    cpd = const.dry_air_spec_heat_press.m
    cw = const.water_specific_heat.m*1e3
    nu = const.dry_air_gas_constant.m/(cpd + cw*Q)

    # see eq. 5.3 of Davies-Jones 2008
    f_initial = _daviesjones_f(
        initial_temperature.m_as(units.kelvin), reference_pi, Q=Q,
        kind='reversible')
    A1 = f_initial**(-1/lambda_)*C/reference_pi**(lambda_*nu)  # correction

    # initial guess using pseudoadiabat
    temperature = moist_lapse_dj(
        pressure*units.mbar, initial_temperature,
        reference_pressure*units.mbar, improve=False).m_as(units.celsius)

    pi = (pressure/1000.0)**(1./lambda_)
    X = (C/(A1*pi**(lambda_*nu)))**lambda_  # correction
    for _ in range(improve):
        # apply iterations of Newton's method (eq. 2.6)
        slope = _daviesjones_fprime(
            temperature + C, pi, Q=Q, kind='reversible')
        fvalue = _daviesjones_f(
            temperature + C, pi, Q=Q, kind='reversible')
        temperature = temperature - (fvalue - X)/slope

    temperature *= units.celsius
    return temperature if pressure.size > 1 else temperature.item()


def reversible_lapse_saunders(
        pressure, t_initial, l_initial, reference_pressure=None, improve=2):
    """
    Calculate temperature along reversible adiabats.

    Uses Eq. 3 of Saunders (1957). Variable names follow the notation
    of Saunders.

    Args:
        pressure: Pressure array.
        t_initial: Initial temperature.
        l_initial: Initial ratio of liquid mass to total
        reference_pressure: Pressure corresponding to t_inital.
        improve: Number of Newton's method iterations to use.

    Returns:
        Resultant temperature array.

    References:
        Saunders, PM 1957, ‘The thermodynamics of saturated air: A
        contribution to the classical theory’, Quarterly journal of
        the Royal Meteorological Society, vol. 83, no. 357,
        pp. 342–350.
    """
    pressure = np.atleast_1d(pressure).m_as(units.mbar)
    if reference_pressure is None:
        reference_pressure = pressure[0]
    else:
        reference_pressure = reference_pressure.m_as(units.mbar)

    t_initial = t_initial.m_as(units.kelvin)
    if hasattr(l_initial, 'units'):
        l_initial = l_initial.m_as(units.dimensionless)

    # constants
    cp = const.dry_air_spec_heat_press.m
    cw = const.water_specific_heat.m*1e3
    R = const.dry_air_gas_constant.m
    C = 273.15
    e0 = 6.112
    a = 17.67
    b = 243.5
    epsilon = const.epsilon.m
    L0 = 2.501e6
    L1 = 2.37e3

    # total vapour + liquid water mixing ratio (invariant)
    q_initial = saturation_specific_humidity(
        reference_pressure*units.mbar, t_initial*units.kelvin).m
    r = (q_initial + l_initial)/(1 - q_initial - l_initial)

    def saunders_function(p, t):
        """Evaluate the LHS of Eq. 3 and its derivative w.r.t. temperature."""
        # saturation vapour pressure and derivative
        es = e0*np.exp(a*(t - C)/(t - C + b))
        des_dt = a*b/(t - C + b)**2 * es

        # saturation (vapour) mixing ratio and derivative
        rw = epsilon*es/(p - es)
        drw_dt = epsilon*p*des_dt/(p - es)**2

        # latent heat of vapourisation of water and derivative
        Lv = L0 - L1*(t - C)
        dLv_dt = -L1

        # LHS of Eq. 3 and derivative
        fvalue = (cp + r*cw)*np.log(t) + rw*Lv/t - R*np.log(p - es)
        fprime = ((cp + r*cw)/t + (t*(drw_dt*Lv + rw*dLv_dt) - rw*Lv)/t**2
                  + R*des_dt/(p - es))
        return fvalue, fprime

    # RHS of Eq. 3
    A, _ = saunders_function(reference_pressure, t_initial)

    # initial guess: pseudoadiabatic values
    t_final = mpcalc.moist_lapse(
        pressure*units.mbar, t_initial*units.kelvin,
        reference_pressure*units.mbar).m_as(units.kelvin)

    # apply iterations of Newton's method
    for _ in range(improve):
        fvalue, fprime = saunders_function(pressure, t_final)
        t_final = t_final - (fvalue - A)/fprime
    t_final *= units.kelvin
    return t_final if t_final.size > 1 else t_final.item()


# ---------- adiabatic descent calculation ----------

def descend(
        pressure, temperature, specific_humidity, liquid_ratio,
        reference_pressure, improve=2, improve_reversible=2, kind='pseudo'):
    """
    Calculate the temperature of a descending parcel.

    Uses conservation of equivalent potential temperature to determine
    the final temperature if the parcel switches from a moist to a dry
    adiabat.

    Args:
        pressure: Final pressure.
        temperature: Initial temperature.
        specific_humidity: Initial specific humidity.
        liquid_ratio: Initial liquid ratio.
        reference_pressure: Initial pressure.
        improve: Number of iterations to use if the parcel must switch
            from moist to dry adiabat (default: 1). Alternatively,
            specify False to skip iteration and take the moist
            adiabatic value, or 'exact' to iterate until convergence.
        improve_reversible: Number of iterations to use for reversible
            adiabat calculation.
        kind: 'pseudo' for pseudoadiabats, 'reversible' for reversible
            adiabats.

    Returns:
        Final temperature, specific humidity and liquid ratio.
    """
    # calculate dry adiabatic value outside if statement since it
    # is needed for the guess in case 2.2
    t_final_dry = mpcalc.dry_lapse(pressure, temperature, reference_pressure)

    if liquid_ratio <= 0:
        # case 1: dry adiabat only
        q_final = specific_humidity
        l_final = 0*units.dimensionless
        return t_final_dry, q_final, l_final

    # case 2: some moist descent
    if kind == 'pseudo':
        t_final_moist = mpcalc.moist_lapse(
            pressure, temperature, reference_pressure)
    elif kind == 'reversible':
        t_final_moist = reversible_lapse_saunders(
            pressure, temperature, liquid_ratio,
            reference_pressure, improve=improve_reversible)
    else:
        raise ValueError("kind must be 'pseudo' or 'reversible'.")
    q_final_moist = saturation_specific_humidity(pressure, t_final_moist)
    l_final_moist = specific_humidity + liquid_ratio - q_final_moist

    if l_final_moist >= 0 or improve is False:
        # case 2.1: moist adiabat only
        if not hasattr(pressure, 'size'):
            return (t_final_moist.item(), q_final_moist.item(),
                    l_final_moist.item())
        return t_final_moist, q_final_moist, l_final_moist

    # case 2.2: adiabat switching
    # use amount of liquid to place guess between dry and moist values
    t_final = (
        t_final_dry.to(units.kelvin)
        + liquid_ratio/(q_final_moist - specific_humidity).m
        * (t_final_moist.to(units.kelvin) - t_final_dry.to(units.kelvin)))
    q_final = specific_humidity + liquid_ratio
    l_final = 0*units.dimensionless

    # we seek the final temperature such that the final theta-e
    # is equal to the initial theta-e
    theta_e_initial = equivalent_potential_temperature(
        reference_pressure, temperature, specific_humidity)
    # apply iterations of Newton's method
    for _ in range(improve):
        value, slope = equivalent_potential_temperature(
            pressure, t_final, q_final, prime=True)
        t_final = t_final - (value - theta_e_initial)/slope

    if not hasattr(pressure, 'size'):
        return t_final.item(), q_final.item(), l_final.item()
    return t_final, q_final, l_final


# ---------- entrainment calculations ----------

def mix(parcel, environment, rate, dz):
    """
    Mix parcel and environment variables (for entrainment).

    Args:
        parcel: Parcel value.
        environment: Environment value.
        rate: Entrainment rate.
        dz: Distance descended.

    Returns:
        Mixed value of the variable.
    """
    return parcel + rate * (environment - parcel) * dz


def equilibrate(pressure, t_initial, q_initial, l_initial):
    """
    Find parcel properties after phase equilibration.

    Args:
        pressure: Pressure during the change (constant).
        t_initial: Initial temperature of the parcel.
        q_initial: Initial specific humidity of the parcel.
        l_initial: Initial ratio of liquid mass to parcel mass.

    Returns:
        A tuple containing the final parcel temperature, specific
            humidity and liquid ratio.
    """
    q_sat_initial = saturation_specific_humidity(pressure, t_initial)
    if ((q_initial <= q_sat_initial and l_initial <= 0)
            or q_initial == q_sat_initial):
        # parcel is already in equilibrium
        return t_initial, q_initial, np.maximum(l_initial, 0).item()

    # to find the initial temperature after evaporation,first assume
    # that the parcel becomes saturated and therefore attains its
    # wet bulb temperature
    t_final = wetbulb_romps(pressure, t_initial, q_initial)
    q_final = saturation_specific_humidity(pressure, t_final)
    l_final = q_initial + l_initial - q_final

    # check if the assumption was realistic
    if l_final < 0:
        # if the liquid content resulting from evaporation to the point
        # of saturation is negative, this indicates that l_initial is
        # not large enough to saturate the parcel. We find the actual
        # resulting temperature using the conservation of equivalent
        # potential temperature during the evaporation process:
        # we use Newton's method to seek the temperature such that
        # the final equivalent potential temperature is unchanged.
        # As an initial guess, assume the temperature change is -L*dq/c_p
        theta_e = equivalent_potential_temperature(
            pressure, t_initial, q_initial)
        t_final = t_initial - (const.water_heat_vaporization
                               * l_initial/const.dry_air_spec_heat_press)
        q_final = q_initial + l_initial
        l_final = 0*units.dimensionless
        for _ in range(3):
            value, slope = equivalent_potential_temperature(
                pressure, t_final, q_final, prime=True)
            t_final -= (value - theta_e)/slope

    return t_final.item(), q_final.item(), l_final.item()
