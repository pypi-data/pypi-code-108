# Copyright (c) 2021 Thomas Schanzer.
# Distributed under the terms of the BSD 3-Clause License.
"""Tools for specifying environmental profiles in dparcel.

The Environment class allows the user to supply real atmospheric
sounding data to use for parcel calculations. Alternatively, the
idealised_sounding function can be used to generate an Environment
instance using an idealised sounding.
"""

import numpy as np

import metpy.calc as mpcalc
from metpy.units import units, concatenate
import metpy.constants as const

from scipy.interpolate import interp1d
from scipy.integrate import solve_ivp, simps
from scipy.optimize import minimize_scalar

from .thermo import equivalent_potential_temperature, wetbulb


class Environment:
    """Class for atmospheric sounding data."""

    def __init__(
            self, pressure, height, temperature, dewpoint, liquid_ratio=None,
            info='', name=''):
        """
        Instantiate an Environment.

        Args:
            pressure: Pressure array in the sounding.
            height: Height array in the sounding.
            temperature: Temperature array in the sounding.
            dewpoint: Dewpoint array in the sounding.
            liquid_ratio: Array of liquid water partial density to
                total density in the sounding (optional, defaults to
                all zero).
            info: Information to store with the sounding, e.g. date
                (optional)
            name: Short name for the sounding, e.g. 'Sydney' (optional).
        """
        # record input data as attributes for use by methods
        self._pressure_raw = pressure.m_as(units.mbar)
        self._height_raw = height.m_as(units.meter)
        self._height_raw -= np.min(self._height_raw)  # set z = 0 at surface
        self._temperature_raw = temperature.m_as(units.celsius)
        self._dewpoint_raw = dewpoint.m_as(units.celsius)

        # if no liquid ratio profile is given, assume it is zero
        if liquid_ratio is None:
            self._liquid_ratio_raw = np.zeros(pressure.size)
        elif hasattr(liquid_ratio, 'units'):
            self._liquid_ratio_raw = liquid_ratio.m_as(units.dimensionless)

        self.info = info
        self.name = name

        # functions to interpolate input data, so variables are known
        # at any height

        self._pressure_to_temperature_interp = interp1d(
            self._pressure_raw, self._temperature_raw,
            fill_value='extrapolate')
        self._height_to_temperature_interp = interp1d(
            self._height_raw, self._temperature_raw, fill_value='extrapolate')

        self._pressure_to_dewpoint_interp = interp1d(
            self._pressure_raw, self._dewpoint_raw, fill_value='extrapolate')
        self._height_to_dewpoint_interp = interp1d(
            self._height_raw, self._dewpoint_raw, fill_value='extrapolate')

        self._pressure_to_liquid_ratio_interp = interp1d(
            self._pressure_raw, self._liquid_ratio_raw,
            fill_value='extrapolate')
        self._height_to_liquid_ratio_interp = interp1d(
            self._height_raw, self._liquid_ratio_raw, fill_value='extrapolate')

        self._pressure_to_height_interp = interp1d(
            self._pressure_raw, self._height_raw, fill_value='extrapolate')
        self._height_to_pressure_interp = interp1d(
            self._height_raw, self._pressure_raw, fill_value='extrapolate')

    def temperature_from_pressure(self, pressure):
        """Find the environmental temperature at a given pressure."""
        temperature = self._pressure_to_temperature_interp(
            pressure.m_as(units.mbar))
        if temperature.size == 1:
            temperature = temperature.item()
        return temperature*units.celsius

    def dewpoint_from_pressure(self, pressure):
        """Find the environmental dew point at a given pressure."""
        dewpoint = self._pressure_to_dewpoint_interp(pressure.m_as(units.mbar))
        if dewpoint.size == 1:
            dewpoint = dewpoint.item()
        return dewpoint*units.celsius

    def liquid_ratio_from_pressure(self, pressure):
        """Find the environmental liquid ratio at a given pressure."""
        liquid_ratio = self._pressure_to_liquid_ratio_interp(
            pressure.m_as(units.mbar))
        if liquid_ratio.size == 1:
            liquid_ratio = liquid_ratio.item()
        return liquid_ratio*units.dimensionless

    def pressure(self, height):
        """Find the environmental pressure at a given height."""
        pressure = self._height_to_pressure_interp(height.m_as(units.meter))
        if pressure.size == 1:
            pressure = pressure.item()
        return pressure*units.mbar

    def height(self, pressure):
        """Find the height at a given environmental pressure."""
        height = self._pressure_to_height_interp(pressure.m_as(units.mbar))
        if height.size == 1:
            height = height.item()
        return height*units.meter

    def temperature(self, height):
        """Find the environmental temperature at a given height."""
        temperature = self._height_to_temperature_interp(
            height.m_as(units.meter))
        if temperature.size == 1:
            temperature = temperature.item()
        return temperature*units.celsius

    def dewpoint(self, height):
        """Find the environmental dew point at a given height."""
        dewpoint = self._height_to_dewpoint_interp(
            height.m_as(units.meter))
        if dewpoint.size == 1:
            dewpoint = dewpoint.item()
        return dewpoint*units.celsius

    def liquid_ratio(self, height):
        """Find the environmental liquid ratio at a given height."""
        liquid_ratio = self._height_to_liquid_ratio_interp(
            height.m_as(units.meter))
        if liquid_ratio.size == 1:
            liquid_ratio = liquid_ratio.item()
        return liquid_ratio*units.dimensionless

    def wetbulb_temperature(self, height):
        """
        Find the environmental wet-bulb temperature at a given height.

        Uses the approximation of eq. (39) in Bolton (1980) for
        equivalent potential temperature, and the approximation of
        Davies-Jones (2008) to find the wet bulb temperature.

        References:
            DAVIES-JONES, R 2008, ‘An Efficient and Accurate Method for
            Computing the Wet-Bulb Temperature along Pseudoadiabats’,
            Monthly weather review, vol. 136, no. 7, pp. 2764–2785.

            Bolton, D 1980, ‘The Computation of Equivalent Potential
            Temperature’, Monthly weather review, vol. 108, no. 7,
            pp. 1046–1053.
        """
        pressure = self.pressure(height)
        theta_e = self.equivalent_potential_temperature(height)
        return wetbulb(pressure, theta_e, improve=True)

    def specific_humidity(self, height):
        """Find the environmental specific humidity at a given height."""
        pressure = self.pressure(height)
        dewpoint = self.dewpoint(height)
        q = mpcalc.specific_humidity_from_dewpoint(
            pressure, dewpoint)
        if not hasattr(height, 'size'):
            return q.item()
        return q

    def density(self, height):
        """Find the environmental density at a given height."""
        pressure = self.pressure(height)
        temperature = self.temperature(height)
        mixing_ratio = mpcalc.mixing_ratio_from_specific_humidity(
            self.specific_humidity(height))
        return mpcalc.density(pressure, temperature, mixing_ratio)

    def equivalent_potential_temperature(self, height):
        """
        Find the environmental equivalent potential temperature.

        Uses the approximation of eq. (39) in Bolton (1980).

        References:
            Bolton, D 1980, ‘The Computation of Equivalent Potential
            Temperature’, Monthly weather review, vol. 108, no. 7,
            pp. 1046–1053.
        """
        pressure = self.pressure(height)
        temperature = self.temperature(height)
        specific_humidity = self.specific_humidity(height)
        theta_e = equivalent_potential_temperature(
            pressure, temperature, specific_humidity)
        return theta_e

    def potential_temperature(self, height):
        """Find the environmental potential temperature at a given height."""
        pressure = self.pressure(height)
        temperature = self.temperature(height)
        return mpcalc.potential_temperature(pressure, temperature)

    def virtual_temperature(self, height):
        """Find the environmental virtual temperature at a given height."""
        temperature = self.temperature(height)
        mixing_ratio = mpcalc.mixing_ratio_from_specific_humidity(
            self.specific_humidity(height))
        return mpcalc.virtual_temperature(temperature, mixing_ratio)

    def dry_static_energy(self, height):
        """Find the environmental dry static energy at a given height."""
        return mpcalc.dry_static_energy(height, self.temperature(height))

    def moist_static_energy(self, height):
        """Find the environmental moist static energy at a given height."""
        temperature = self.temperature(height)
        specific_humidity = self.specific_humidity(height)
        return mpcalc.moist_static_energy(
            height, temperature, specific_humidity)

    def mixing_ratio(self, height):
        """Find the environmental mixing ratio at a given height."""
        return mpcalc.mixing_ratio_from_specific_humidity(
            self.specific_humidity(height))

    def relative_humidity(self, height):
        """Find the environmental relative humidity at a given height."""
        temperature = self.temperature(height)
        dewpoint = self.dewpoint(height)
        rh = mpcalc.relative_humidity_from_dewpoint(temperature, dewpoint)
        if not hasattr(height, 'size'):
            return rh.item()
        return rh

    def dcape_dcin(self, samples=10000):
        """
        Compute DCAPE and DCIN according to Market et. al. (2017).

        Args:
            samples: Number of samples to use for integration (optional).

        Returns:
            DCAPE and DCIN for the sounding.

        References:
            Market, PS, Rochette, SM, Shewchuk, J, Difani, R, Kastman, JS,
            Henson, CB & Fox, NI 2017, ‘Evaluating elevated convection
            with the downdraft convective inhibition’, Atmospheric
            science letters, vol. 18, no. 2, pp. 76–81.
        """
        # find minimum wet bulb temperature in lowest 6 km
        def env_wetbulb(z):
            return self.wetbulb_temperature(z*units.meter).m_as(units.kelvin)
        sol = minimize_scalar(env_wetbulb, bounds=(0, 6000), method='bounded')
        z_initial = sol.x
        p_initial = self.pressure(z_initial*units.meter)
        t_initial = sol.fun*units.kelvin

        def integrand(z_final):
            # find the virtual temperature after moist pseudoadiabatic
            # descent to the final level
            z_final = z_final*units.meter
            p_final = self.pressure(z_final)
            t_final = mpcalc.moist_lapse(p_final, t_initial, p_initial)
            w_final = mpcalc.saturation_mixing_ratio(p_final, t_final)
            tv_final = mpcalc.virtual_temperature(t_final, w_final)

            # find the environmental virtual temperature at that level
            t_env = self.temperature(z_final)
            w_env = mpcalc.mixing_ratio_from_specific_humidity(
                self.specific_humidity(z_final))
            tv_env = mpcalc.virtual_temperature(t_env, w_env)

            return 1 - tv_final.m_as(units.kelvin)/tv_env.m_as(units.kelvin)

        # DCAPE: integrate from surface to level of minimum wet bulb
        # temperature, taking positive area only.
        # passing the integrand function to scipy.integrate.quad is very
        # slow so we compute many samples and use Simpson's method.
        z_sample = np.linspace(0, z_initial, samples)
        dcape = simps(
            np.maximum(integrand(z_sample), 0), z_sample)*units.meter*const.g
        # DCIN: integrate from surface to level of minimum wet bulb
        # temperature, taking negative area only
        dcin = simps(
            np.minimum(integrand(z_sample), 0), z_sample)*units.meter*const.g

        return dcape.item(), dcin.item()


def idealised_sounding(relative_humidity):
    """
    Create an idealised sounding.

    The sounding has a 160 mbar thick boundary layer with a dry
    adiabatic temperature profile, a 10 mbar thick capping inversion
    and a moist adiabatic temperature profile above the boundary layer.
    The specific humidity is constant in the boundary layer, and the
    relative humidity is constant above the boundary layer.

    The sounding is assumed to be hydrostatic; the sounding is first
    defined in terms of pressure, then a nested function dzdp is
    defined and we numerically solve dzdp(p, z) = -1/(rho*g).

    Args:
        relative_humidity: Relative humidity above the boundary layer.

    Returns:
        Arrays of pressure, height, temperature and specific humidity
        in the sounding.
    """
    # generate discrete temperature profile
    pressure = np.arange(1013.25, 200, -5)*units.mbar
    t_boundary_layer = mpcalc.dry_lapse(
        np.arange(1013.25, 1013.25 - 161, -5)*units.mbar, 20*units.celsius)
    t_capping = t_boundary_layer[-1] + [1.5, 3.0]*units.delta_degC
    t_remaining = mpcalc.moist_lapse(
        np.arange(1013.25 - 175, 200, -5)*units.mbar, t_capping[-1],
        reference_pressure=(1013.25 - 170)*units.mbar)
    temperature = concatenate([
        t_boundary_layer, t_capping, t_remaining,
    ])

    # generate discrete dew point profile
    q_boundary_layer = mpcalc.specific_humidity_from_mixing_ratio(
        6e-3*units.dimensionless)
    dewpoint_boundary_layer = mpcalc.dewpoint_from_specific_humidity(
        np.arange(1013.25, 1013.25 - 161, -5)*units.mbar, t_boundary_layer,
        np.ones(t_boundary_layer.size)*q_boundary_layer)
    dewpoint_remaining = mpcalc.dewpoint_from_relative_humidity(
        t_remaining, np.ones(t_remaining.size)*relative_humidity)
    # ensure the dewpoint is continuous across the capping inversion
    dewpoint_capping_top = mpcalc.dewpoint_from_relative_humidity(
        t_capping[-1], relative_humidity)
    dewpoint_capping = concatenate([
        (dewpoint_boundary_layer[-1].to(units.kelvin)
         + dewpoint_capping_top.to(units.kelvin))/2,
        dewpoint_capping_top,
    ])
    dewpoint = concatenate([
        dewpoint_boundary_layer, dewpoint_capping, dewpoint_remaining,
    ])

    # interpolate discrete profiles to give variables at any pressure
    temperature_interp = interp1d(
        pressure.m_as(units.pascal), temperature.m_as(units.kelvin),
        fill_value='extrapolate')
    dewpoint_interp = interp1d(
        pressure.m_as(units.pascal), dewpoint.m_as(units.kelvin),
        fill_value='extrapolate')

    # now solve the hydrostatic equation so the variables can be
    # expressed as functions of height
    def dzdp(pressure, *_):
        """
        Calculate the rate of height change w.r.t. pressure, dz/dp.

        Args:
            pressure: The pressure at the point of interest, in Pa.

        Returns:
            The derivative dz/dp in m/Pa.
        """
        pressure = pressure*units.pascal
        temperature = temperature_interp(pressure.m)*units.kelvin
        dewpoint = dewpoint_interp(pressure.m)*units.kelvin

        specific_humidity = mpcalc.specific_humidity_from_dewpoint(
            pressure, dewpoint)
        mixing_ratio = mpcalc.mixing_ratio_from_specific_humidity(
            specific_humidity)
        density = mpcalc.density(pressure, temperature, mixing_ratio)
        return (-1/(density*const.g)).m_as(units.meter/units.pascal)

    height = solve_ivp(
        dzdp, (1013.25e2, np.min(pressure.m_as(units.pascal))),
        [0], t_eval=pressure.m_as(units.pascal)).y*units.meter

    return pressure, np.squeeze(height), temperature, dewpoint
