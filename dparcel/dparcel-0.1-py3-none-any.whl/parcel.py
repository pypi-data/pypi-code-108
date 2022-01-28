# Copyright (c) 2021 Thomas Schanzer.
# Distributed under the terms of the BSD 3-Clause License.
"""Class for parcel theory calculations on real atmospheric soundings."""

import numpy as np

import metpy.calc as mpcalc
from metpy.units import units, concatenate
import metpy.constants as const

from scipy.interpolate import interp1d
from scipy.integrate import solve_ivp

from .thermo import (descend, equilibrate, equivalent_potential_temperature,
                     saturation_specific_humidity, moist_lapse_dj, mix,
                     saturation_equivalent_potential_temperature)
from .environment import Environment, idealised_sounding


class Parcel(Environment):
    """Class for parcel theory calculations with entrainment."""

    def _entrain_discrete(self, height, state, rate, step, kind='pseudo'):
        """
        Find parcel properties after descent/entrainment.

        Only valid for small steps.

        Args:
            height: Initial height.
            state: 3-tuple of initial temperature, specific humidity
                and liquid ratio.
            rate: Entrainment rate.
            step: Size of *downward* step, i.e. initial minus final height.
            kind: 'pseudo' for pseudoadiabats, 'reversible' for reversible
                adiabats.

        Returns:
            3-tuple of final temperature, specific humidity and liquid ratio.
        """
        t_parcel = state[0]
        q_parcel = state[1]
        l_parcel = state[2]
        p_initial = self.pressure(height)
        p_final = self.pressure(height - step)

        # step 1: mix parcel and environment
        t_mixed = mix(t_parcel, self.temperature(height), rate, step)
        q_mixed = mix(
            q_parcel, self.specific_humidity(height), rate,step)
        l_mixed = mix(l_parcel, self.liquid_ratio(height), rate, step)

        # step 2: ensure parcel is in phase equilibrium
        t_eq, q_eq, l_eq = equilibrate(p_initial, t_mixed, q_mixed, l_mixed)

        # step 3: dry or moist adiabatic descent
        t_final, q_final, l_final = descend(
            p_final, t_eq, q_eq, l_eq, p_initial, kind=kind)

        return (t_final, q_final, l_final)

    def profile(
            self, height, t_initial, q_initial, l_initial, rate,
            step=50*units.meter, reference_height=None, kind='pseudo'):
        """
        Calculate parcel properties for descent with entrainment.

        Valid for arbitrary steps.

        Args:
            height: Array of heights of interest.
            t_initial: Initial parcel temperature.
            q_initial: Initial parcel specific humidity.
            l_initial: Initial parcel liquid ratio.
            rate: Entrainment rate.
            step: Size of *downward* step for computing finite differences.
            kind: 'pseudo' for pseudoadiabats, 'reversible' for reversible
                adiabats.

        Returns:
            3-tuple containing the temperature, specific humidity and
                liquid ratio arrays for the given height array.
        """
        height = np.atleast_1d(height).m_as(units.meter)
        step = step.m_as(units.meter)

        if height.size > 1 and np.any(height[:-1] <= height[1:]):
            raise ValueError(
                'Height array must be monotonically decreasing.')
        if reference_height is not None:
            reference_height = reference_height.m_as(units.meter)
            if height.size == 1 and height.item() == reference_height:
                # no descent needed, return initial values
                return t_initial, q_initial, l_initial
            if np.any(height > reference_height):
                raise ValueError(
                    'All final heights must be below reference_height. '
                    'height = {} m, reference_height = {} m.'.format(
                        height, reference_height))

        # create height array with correct spacing
        if reference_height is None or reference_height == height[0]:
            all_heights = np.arange(height[0], height[-1], -step)
            all_heights = np.append(all_heights, height[-1])*units.meter
        else:
            all_heights = np.arange(reference_height, height[-1], -step)
            all_heights = np.append(all_heights, height[-1])*units.meter

        # calculate t, q and l one downward step at a time
        sol_states = [(t_initial, q_initial, l_initial)]
        for i in range(all_heights.size - 1):
            next_state = self._entrain_discrete(
                all_heights[i], sol_states[i], rate,
                all_heights[i] - all_heights[i+1], kind=kind)
            sol_states.append(next_state)

        if height.size == 1:
            return [var.item() for var in sol_states[-1]]

        t_sol = concatenate(
            [state[0] for state in sol_states]).m_as(units.celsius)
        q_sol = concatenate([state[1] for state in sol_states]).m
        l_sol = concatenate([state[2] for state in sol_states]).m

        # find the values of t, q and l at the originally specified heights
        t_interp = interp1d(all_heights.m, t_sol)
        t_out = t_interp(height)*units.celsius
        q_interp = interp1d(all_heights.m, q_sol)
        q_out = q_interp(height)*units.dimensionless
        l_interp = interp1d(all_heights.m, l_sol)
        l_out = l_interp(height)*units.dimensionless

        return t_out, q_out, l_out

    def parcel_density(
            self, height, initial_height, t_initial, q_initial, l_initial,
            rate, step=50*units.meter, kind='pseudo', liquid_correction=True):
        """
        Calculate parcel density as a function of height.

        Args:
            height: Height of the parcel.
            initial_height: Initial height.
            t_initial: Initial temperature.
            q_initial: Initial specific humidity.
            l_initial: Initial liquid ratio.
            rate: Entrainment rate.
            step: Step size for entrainment calculation.
            kind: 'pseudo' for pseudoadiabats, 'reversible' for reversible
                adiabats.
            liquid_correction: Whether or not to account for the mass
                of liquid water.

        Returns:
            The density of the parcel at <height>.
        """
        t_final, q_final, l_final = self.profile(
            height, t_initial, q_initial, l_initial, rate, step=step,
            reference_height=initial_height, kind=kind)
        r_final = mpcalc.mixing_ratio_from_specific_humidity(q_final)
        p_final = self.pressure(height)

        gas_density = mpcalc.density(p_final, t_final, r_final)
        return gas_density/(1 - l_final.m*liquid_correction)

    def buoyancy(
            self, height, initial_height, t_initial, q_initial, l_initial,
            rate, step=50*units.meter, kind='pseudo', liquid_correction=True):
        """
        Calculate parcel buoyancy as a function of height.

        Args:
            height: Height of the parcel.
            initial_height: Initial height.
            t_initial: Initial temperature.
            q_initial: Initial specific humidity.
            l_initial: Initial liquid ratio.
            rate: Entrainment rate.
            step: Step size for entrainment calculation.
            kind: 'pseudo' for pseudoadiabats, 'reversible' for reversible
                adiabats.
            liquid_correction: Whether or not to account for the mass
                of liquid water.

        Returns:
            The buoyancy of the parcel at <height>.
        """
        env_density = self.density(height)
        parcel_density = self.parcel_density(
            height, initial_height, t_initial, q_initial, l_initial, rate,
            step, kind=kind, liquid_correction=liquid_correction)

        return (env_density - parcel_density)/parcel_density*const.g

    def motion(
            self, time, initial_height, initial_velocity, t_initial,
            q_initial, l_initial, rate, step=50*units.meter,
            kind='pseudo', liquid_correction=True):
        """
        Solve the equation of motion for the parcel.

        Integration stops if the parcel reaches a minimum height or
        the surface.

        Args:
            time: Array of times for which the results will be reported.
            initial_height: Initial height.
            initial_velocity: Initial vertical velocity.
            t_initial: Initial temperature.
            q_initial: Initial specific humidity.
            l_initial: Initial liquid ratio.
            rate: Entrainment rate.
            step: Step size for entrainment calculation.
            kind: 'pseudo' for pseudoadiabats, 'reversible' for reversible
                adiabats.
            liquid_correction: Whether or not to account for the mass
                of liquid water.

        Returns:
            Bunch object with the folliwing fields defined --
                - **height** -- Array of parcel height at each time step.
                - **velocity** -- Array of parcel velocity at each time step.
                - **temperature** -- Array of parcel temperature at each time
                  step.
                - **specific_humidity** -- Array of parcel specific humidity
                  at each time step.
                - **liquid_ratio** -- Array of parcel liquid water mass ratio
                  at each time step.
                - **density** -- Array of parcel density at each time step.
                - **buoyancy** -- Array of parcel buoyancy at each time step.
                - **neutral_buoyancy_time** -- The time at which the parcel
                  reached its neutral buoyancy level (np.nan if this did
                  not occur because the parcel reached the ground before
                  becoming neutrally buoyant).
                - **hit_ground_time** -- The time at which the parcel reached
                  the surface (np.nan if this did not occur because the
                  parcel stopped at some minimum height above the surface).
                - **min_height_time** -- The time at which the parcel reached
                  its minimum height (np.nan if this did not occur because
                  it reached the surface).
                - **neutral_buoyancy_height** -- The height of the neutral
                  buoyancy level (np.nan if it does not exist because the
                  parcel reached the ground before becoming neutrally
                  buoyant).
                - **neutral_buoyancy_velocity** -- The parcel's velocity at its
                  neutral buoyancy level (np.nan if this does not exist
                  because the parcel reached the ground before becoming
                  neutrally buoyant).
                - **hit_ground_velocity** -- The parcel's velocity at the
                  surface (np.nan if the parcel did not reach the surface).
                - **min_height** -- The minimum height reached by the parcel
                  (np.nan if it reached the surface).
        """
        # pre-compute temperature as a function of height to avoid
        # redundant calculations at every time step
        sample_heights = np.arange(
            initial_height.m_as(units.meter), 0,
            -step.m_as(units.meter))*units.meter
        sample_t, sample_q, sample_l = self.profile(
            sample_heights, t_initial, q_initial, l_initial, rate, step,
            kind=kind)

        def motion_ode(_, state):
            """Define the parcel's equation of motion."""
            height = np.max([state[0], 0])*units.meter

            # find the index of the closest height at which the temperature
            # was pre-computed
            closest_index = (
                sample_heights.size - 1
                - np.searchsorted(np.flip(sample_heights), height))

            # solve_ivp may test height > initial_height
            if closest_index == -1:
                height = sample_heights[0]
                closest_index = 0

            # start from the pre-computed values and integrate the small
            # remaining distance to the desired level to find the buoyancy
            buoyancy = self.buoyancy(
                height, sample_heights[closest_index], sample_t[closest_index],
                sample_q[closest_index], sample_l[closest_index], rate, step,
                kind, liquid_correction)
            return [state[1], buoyancy.m]

        # event function for solve_ivp, zero when parcel reaches min height
        def min_height(_, state):
            return state[1]
        min_height.direction = 1  # find zero that goes from - to +
        min_height.terminal = True  # stop integration at minimum height

        # event function for solve_ivp, zero when parcel hits ground
        def hit_ground(_, state):
            return state[0]
        hit_ground.terminal = True  # stop integration at ground

        # event function for solve_ivp, zero when parcel is neutrally
        # buoyant
        def neutral_buoyancy(time, state):
            return motion_ode(time, state)[1]

        # solve the equation of motion
        initial_height = initial_height.m_as(units.meter)
        initial_velocity = initial_velocity.m_as(units.meter/units.second)
        time = time.to(units.second).m
        sol = solve_ivp(
            motion_ode,
            [np.min(time), np.max(time)],
            [initial_height, initial_velocity],
            t_eval=time,
            events=[neutral_buoyancy, hit_ground, min_height])

        # record height and velocity
        height = np.full(len(time), np.nan)
        velocity = np.full(len(time), np.nan)
        height[:len(sol.y[0, :])] = sol.y[0, :]
        velocity[:len(sol.y[1, :])] = sol.y[1, :]

        # record times of events
        # sol.t_events[i].size == 0 means the event did not occur
        neutral_buoyancy_time = (  # record only the first instance
            sol.t_events[0][0] if sol.t_events[0].size > 0 else np.nan)
        hit_ground_time = (
            sol.t_events[1][0] if sol.t_events[1].size > 0 else np.nan)
        min_height_time = (
            sol.t_events[2][0] if sol.t_events[2].size > 0 else np.nan)

        # record states at event times
        neutral_buoyancy_height = (  # record only the first instance
            sol.y_events[0][0, 0] if sol.y_events[0].size > 0 else np.nan)
        neutral_buoyancy_velocity = (  # record only the first instance
            sol.y_events[0][0, 1] if sol.y_events[0].size > 0 else np.nan)
        hit_ground_velocity = (
            sol.y_events[1][0, 1] if sol.y_events[1].size > 0 else np.nan)
        min_height_height = (
            sol.y_events[2][0, 0] if sol.y_events[2].size > 0 else np.nan)

        # compute parcel propterties for the solution
        temperature = np.full(len(time), np.nan)
        specific_humidity = np.full(len(time), np.nan)
        liquid_ratio = np.full(len(time), np.nan)
        density = np.full(len(time), np.nan)
        buoyancy = np.full(len(time), np.nan)

        t_profile, q_profile, l_profile = self.profile(
            sol.y[0, :]*units.meter, t_initial, q_initial, l_initial,
            rate, step, kind=kind)
        temperature[:len(sol.y[0, :])] = t_profile.m_as(units.celsius)
        specific_humidity[:len(sol.y[0, :])] = q_profile.m
        liquid_ratio[:len(sol.y[0, :])] = l_profile.m

        r_profile = mpcalc.mixing_ratio_from_specific_humidity(q_profile)
        p_profile = self.pressure(sol.y[0, :]*units.meter)
        gas_density = mpcalc.density(p_profile, t_profile, r_profile)
        density_profile = gas_density/(1 - l_profile.m*liquid_correction)
        density[:len(sol.y[0, :])] = (
            density_profile).m_as(units.kilogram/units.meter**3)

        env_density = self.density(sol.y[0, :]*units.meter)
        buoyancy[:len(sol.y[0, :])] = (
            (env_density - density_profile)/density_profile*const.g
        ).m_as(units.meter/units.second**2)

        # collect everything in a bunch object
        result = MotionResult()
        result.height = height*units.meter
        result.velocity = velocity*units.meter/units.second
        result.temperature = temperature*units.celsius
        result.specific_humidity = specific_humidity*units.dimensionless
        result.liquid_ratio = liquid_ratio*units.dimensionless
        result.density = density*units.kilogram/units.meter**3
        result.buoyancy = buoyancy*units.meter/units.second**2
        result.neutral_buoyancy_time = neutral_buoyancy_time*units.second
        result.hit_ground_time = hit_ground_time*units.second
        result.min_height_time = min_height_time*units.second
        result.neutral_buoyancy_height = neutral_buoyancy_height*units.meter
        result.neutral_buoyancy_velocity = (
            neutral_buoyancy_velocity*units.meter/units.second)
        result.hit_ground_velocity = (
            hit_ground_velocity*units.meter/units.second)
        result.min_height = min_height_height*units.meter
        return result


class IdealisedParcel(Parcel):
    """Parcel in an idealised sounding."""

    def __init__(self, relative_humidity):
        """
        Creates an instance of IdealisedParcel.

        Args:
            relative_humidity: Relative humidity above the boundary layer.

        Returns:
            An instance of IdealisedParcel.
        """
        pressure, height, temperature, dewpoint = idealised_sounding(
            relative_humidity)
        super().__init__(pressure, height, temperature, dewpoint)


class FastParcel(Environment):
    """Class for improved parcel theory calculations with entrainment."""

    def parcel_equivalent_potential_temperature(
            self, initial_height, initial_temperature,
            initial_specific_humidity, entrainment_rate):
        """
        Calculate equivalent potential temperature of an entraining parcel.

        Follows Eq. (6) of Sherwood et al. 2013.

        Args:
            initial_height: Initial parcel height.
            initial_temperature: Initial parcel temperature.
            initial_specific_humidity: Initial parcel specific humidity.
            entrainment_rate: Parcel entrainment rate (either a constant
                or a callable function of height).

        Returns:
            A function that returns the equivalent potential temperature of
            the parcel, given a height below the starting height.
        """
        # determine the initial condition for the ODE
        initial_pressure = self.pressure(initial_height)
        initial_theta_e = equivalent_potential_temperature(
            initial_pressure, initial_temperature, initial_specific_humidity)

        # if the entrainment rate is a function, ensure it has the right units.
        # if it is a constant, make it a constant function.
        if callable(entrainment_rate):
            rate = entrainment_rate
            def epsilon(height):
                return rate(height*units.meter).m_as(1/units.meter)
        else:
            rate = entrainment_rate.m_as(1/units.meter)
            def epsilon(_):
                return rate

        def dtheta_e_dz(height, theta_e):
            """Find the derivative of parcel theta-e w.r.t. height."""
            env_theta_e = self.equivalent_potential_temperature(
                height*units.meter
            ).m_as(units.kelvin)
            return epsilon(height)*(theta_e - env_theta_e)

        sol = solve_ivp(
            dtheta_e_dz,
            [initial_height.m_as(units.meter), 0],  # solution interval
            (initial_theta_e.m_as(units.kelvin),),  # initial condition
            method='LSODA', dense_output=True
        )

        def theta_e(height):
            """Find parcel theta-e at a given height."""
            # if the input was an array, output an array. otherwise output
            # a number.
            if hasattr(height, 'size') and height.size > 1:
                return np.squeeze(
                    sol.sol(height.m_as(units.meter))
                )*units.kelvin
            return sol.sol(height.m_as(units.meter)).item()*units.kelvin

        return theta_e

    def water_content(
            self, initial_height, initial_specific_humidity,
            initial_liquid_ratio, entrainment_rate):
        """
        Calculate total water content of an entraining parcel.

        Args:
            initial_height: Initial parcel height.
            initial_specific_humidity: Initial parcel specific humidity.
            initial_liquid_ratio: Initial parcel liquid water mass ratio.
            entrainment_rate: Parcel entrainment rate (either a constant
                or a callable function of height).

        Returns:
            A function that returns the total water content of
            the parcel, given a height below the starting height.
        """
        # determine the initial condition
        initial_water = initial_specific_humidity + initial_liquid_ratio

        # if the entrainment rate is a function, ensure it has the right units.
        # if it is a constant, make it a constant function.
        if callable(entrainment_rate):
            rate = entrainment_rate
            def epsilon(height):
                return rate(height*units.meter).m_as(1/units.meter)
        else:
            rate = entrainment_rate.m_as(1/units.meter)
            def epsilon(_):
                return rate

        def dQ_dz(height, parcel_water):
            """Find the derivative of parcel water content w.r.t. height."""
            env_water = (
                self.specific_humidity(height*units.meter)
                + self.liquid_ratio(height*units.meter)
            ).m_as(units.dimensionless)
            return epsilon(height)*(parcel_water - env_water)

        sol = solve_ivp(
            dQ_dz,
            [initial_height.m_as(units.meter), 0],  # solution interval
            (initial_water.m_as(units.dimensionless),),  # initial condition
            method='LSODA', dense_output=True
        )

        def water(height):
            """Find total parcel water content at a given height."""
            # if the input was an array, output an array. otherwise output
            # a number.
            if hasattr(height, 'size') and height.size > 1:
                return np.squeeze(
                    sol.sol(height.m_as(units.meter))
                )*units.dimensionless
            return sol.sol(
                height.m_as(units.meter)
            ).item()*units.dimensionless

        return water

    def _properties_moist(
            self, height, initial_height, initial_temperature,
            theta_e, total_water, improve=5):
        """
        Calculate the temperature of an entraining parcel (moist descent only).

        Args:
            height: Array of heights of interest.
            initial_height: Starting height of the parcel.
            initial_temperature: Initial temperature of the parcel.
            theta_e: Callable, giving parcel equivalent potential temperature
                as a function of height.
            total_water: Callable, giving total water content of the parcel
                as a function of height.
            improve: Number of Newton iterations to perform.

        Returns:
            Arrays of parcel temperatures, specific humidities and
            liquid ratios at the heights of interest.
        """
        # compute the final theta-e values
        theta_e_sol = theta_e(height)
        water = total_water(height)

        # obtain a first guess for temperature using Davies-Jones (2008)
        pressure = self.pressure(height)
        initial_pressure = self.pressure(initial_height)
        temperature = moist_lapse_dj(
            pressure, initial_temperature, initial_pressure, improve=False)

        # solve using Newton's method
        for _ in range(improve):
            value, slope = saturation_equivalent_potential_temperature(
                pressure, temperature, prime=True)
            temperature -= (value - theta_e_sol)/slope

        specific_humidity = saturation_specific_humidity(pressure, temperature)
        liquid_ratio = water - specific_humidity

        return temperature, specific_humidity, liquid_ratio

    def _properties_dry(
            self, height, initial_height, initial_temperature,
            theta_e, total_water, improve=5):
        """
        Calculate the temperature of an entraining parcel (dry descent only).

        Args:
            height: Array of heights of interest.
            initial_height: Starting height of the parcel.
            initial_temperature: Initial temperature of the parcel.
            theta_e: Callable, giving parcel equivalent potential temperature
                as a function of height.
            total_water: Callable, giving total water content of the parcel
                as a function of height.
            improve: Number of Newton iterations to perform.

        Returns:
            Arrays of parcel temperatures, specific humidities and
            liquid ratios at the heights of interest.
        """
        # compute the final theta-e values and specific humidities
        theta_e_sol = theta_e(height)
        q_sol = total_water(height)

        # use a dry adiabatic first guess for temperature
        pressure = self.pressure(height)
        initial_pressure = self.pressure(initial_height)
        temperature = mpcalc.dry_lapse(
            pressure, initial_temperature, initial_pressure)

        # solve using Newton's method
        for _ in range(improve):
            value, slope = equivalent_potential_temperature(
                pressure, temperature, q_sol, prime=True)
            temperature -= (value - theta_e_sol)/slope

        # liquid ratio is always zero, but the array should have the same
        # shape as the others
        if hasattr(height, 'size') and height.size > 1:
            liquid_ratio = np.zeros(height.size)*units.dimensionless
        else:
            liquid_ratio = 0*units.dimensionless

        return temperature, q_sol, liquid_ratio

    def _transition_point(
            self, initial_height, initial_temperature, initial_liquid_ratio,
            theta_e, total_water, improve=5):
        """
        Finds the transition point between moist and dry descent.

        Args:
            initial_height: Starting height of the parcel.
            initial_temperature: Initial temperature of the parcel.
            initial_liquid_ratio: Initial liquid water ratio of the parcel.
            theta_e: Callable, giving parcel equivalent potential temperature
                as a function of height.
            total_water: Callable, giving total water content of the parcel
                as a function of height.
            improve: Number of Newton iterations to perform.

        Returns:
            The height at which the liquid water ratio in the parcel
            becomes zero, and its temperature at that point.
        """
        if initial_liquid_ratio <= 0:
            # dry descent only
            return initial_height, initial_temperature

        height = np.arange(
            initial_height.m_as(units.meter), 0, -100
        )*units.meter
        height = concatenate([height, 0*units.meter])
        t_moist, _, l_moist = self._properties_moist(
            height, initial_height, initial_temperature,
            theta_e, total_water, improve)

        if l_moist[-1] > 0:
            # moist descent only
            return 0*units.meter, t_moist[-1].item()

        # now find the transition point where l == 0

        # choose a suitable bracketing interval for the transition point.
        # out of the heights that give positive l_moist, use the one
        # that gives the smallest l_moist as one end of the interval
        guess_above = height[
            np.nanargmin(np.where(l_moist < 0, np.nan, l_moist))
        ]
        # out of the heights that give negative l_moist, use the one
        # that gives the largest l_moist as the other end
        guess_below = height[
            np.nanargmax(np.where(l_moist > 0, np.nan, l_moist))
        ]

        # evaluate the parcel properties on a finely spaced array within
        # the bracketing interval and interpolate to find the point of
        # l_moist == 0
        height = np.linspace(
            guess_above.m_as(units.meter), guess_below.m_as(units.meter), 100)
        t_moist, _, l_moist = self._properties_moist(
            height*units.meter, initial_height, initial_temperature,
            theta_e, total_water, improve)
        z_switch = interp1d(l_moist.m, height)(0)
        t_switch = interp1d(height, t_moist.m_as(units.kelvin))(z_switch)

        return z_switch.item()*units.meter, t_switch.item()*units.kelvin

    def properties(
            self, height, initial_height, initial_temperature, z_switch,
            t_switch, theta_e, total_water, improve=5):
        """
        Calculate the properties of an entraining parcel.

        Args:
            height: Array of heights of interest.
            initial_height: Starting height of the parcel.
            initial_temperature: Initial temperature of the parcel.
            z_switch: Height at which the parcel's liquid completely
                evaporates.
            t_switch Parcel temperature at z_switch.
            theta_e: Callable, giving parcel equivalent potential temperature
                as a function of height.
            total_water: Callable, giving total water content of the parcel
                as a function of height.
            improve: Number of Newton iterations to perform.

        Returns:
            Arrays of parcel temperatures, specific humidities and
            liquid ratios at the heights of interest.
        """
        height = np.atleast_1d(height)
        t_final = np.zeros(height.size)*units.kelvin
        q_final = np.zeros(height.size)*units.dimensionless
        l_final = np.zeros(height.size)*units.dimensionless

        if np.any(height > z_switch):
            (t_final[height > z_switch],
             q_final[height > z_switch],
             l_final[height > z_switch]) = self._properties_moist(
                height[height > z_switch],
                initial_height, initial_temperature,
                theta_e, total_water, improve)

        if np.any(height <= z_switch):
            (t_final[height <= z_switch],
             q_final[height <= z_switch],
             l_final[height <= z_switch]) = self._properties_dry(
                height[height <= z_switch], z_switch, t_switch,
                theta_e, total_water, improve)

        if height.size == 1:
            return t_final.item(), q_final.item(), l_final.item()

        return t_final, q_final, l_final

    def buoyancy(
            self, height, initial_height, initial_temperature, z_switch,
            t_switch, theta_e, total_water, liquid_correction=True, improve=5):
        """
        Calculate the buoyancy of an entraining parcel.

        Args:
            height: Array of heights of interest.
            initial_height: Starting height of the parcel.
            initial_temperature: Initial temperature of the parcel.
            z_switch: Height at which the parcel's liquid completely
                evaporates.
            t_switch Parcel temperature at z_switch.
            theta_e: Callable, giving parcel equivalent potential temperature
                as a function of height.
            total_water: Callable, giving total water content of the parcel
                as a function of height.
            liquid_correction: Whether or not to account for the mass of
                liquid water in the parcel.
            improve: Number of Newton iterations to perform.

        Returns:
            Arrays of parcel buoyancies at the heights of interest.
        """
        t_parcel, q_parcel, l_parcel = self.properties(
            height, initial_height, initial_temperature, z_switch, t_switch,
            theta_e, total_water, improve)
        r_parcel = mpcalc.mixing_ratio_from_specific_humidity(q_parcel)
        tv_parcel = mpcalc.virtual_temperature(t_parcel, r_parcel)
        tv_env = self.virtual_temperature(height)
        # if liquid correction is off, set liquid ratio to 0
        l = l_parcel.m_as(units.dimensionless)*liquid_correction
        return ((1 - l)*tv_parcel - tv_env)/tv_env*const.g

    def motion(
            self, time, initial_height, initial_velocity, t_initial,
            q_initial, l_initial, rate, liquid_correction=True, improve=1):
        """
        Solve the equation of motion for the parcel.

        Integration stops if the parcel reaches a minimum height or
        the surface.

        Args:
            time: Array of times for which the results will be reported.
            initial_height: Initial height.
            initial_velocity: Initial vertical velocity.
            t_initial: Initial temperature.
            q_initial: Initial specific humidity.
            l_initial: Initial liquid ratio.
            rate: Entrainment rate.
            liquid_correction: Whether or not to account for the mass
                of liquid water.
            improve: Number of Newton iterations to use for calculating
                temperature values.

        Returns:
            Bunch object with the folliwing fields defined --
                - **height** -- Array of parcel height at each time step.
                - **velocity** -- Array of parcel velocity at each time step.
                - **temperature** -- Array of parcel temperature at each time
                  step.
                - **specific_humidity** -- Array of parcel specific humidity
                  at each time step.
                - **liquid_ratio** -- Array of parcel liquid water mass ratio
                  at each time step.
                - **density** -- Array of parcel density at each time step.
                - **buoyancy** -- Array of parcel buoyancy at each time step.
                - **neutral_buoyancy_time** -- The time at which the parcel
                  reached its neutral buoyancy level (np.nan if this did
                  not occur because the parcel reached the ground before
                  becoming neutrally buoyant).
                - **hit_ground_time** -- The time at which the parcel reached
                  the surface (np.nan if this did not occur because the
                  parcel stopped at some minimum height above the surface).
                - **min_height_time** -- The time at which the parcel reached
                  its minimum height (np.nan if this did not occur because
                  it reached the surface).
                - **neutral_buoyancy_height** -- The height of the neutral
                  buoyancy level (np.nan if it does not exist because the
                  parcel reached the ground before becoming neutrally
                  buoyant).
                - **neutral_buoyancy_velocity** -- The parcel's velocity at its
                  neutral buoyancy level (np.nan if this does not exist
                  because the parcel reached the ground before becoming
                  neutrally buoyant).
                - **hit_ground_velocity** -- The parcel's velocity at the
                  surface (np.nan if the parcel did not reach the surface).
                - **min_height** -- The minimum height reached by the parcel
                  (np.nan if it reached the surface).
        """
        # theta-e and total water as functions of height, and the
        # moist-to-dry transition point, need only be determined once
        theta_e = self.parcel_equivalent_potential_temperature(
            initial_height, t_initial, q_initial, rate)
        total_water = self.water_content(
            initial_height, q_initial, l_initial, rate)
        z_switch, t_switch = self._transition_point(
            initial_height, t_initial, l_initial,
            theta_e, total_water, improve=5)

        def motion_ode(_, state):
            """Define the parcel's equation of motion."""
            height = np.max([state[0], 0])*units.meter
            buoyancy = self.buoyancy(
                height, initial_height, t_initial, z_switch, t_switch,
                theta_e, total_water, improve=improve,
                liquid_correction=liquid_correction)
            return [state[1], buoyancy.m]

        # event function for solve_ivp, zero when parcel reaches min height
        def min_height(_, state):
            return state[1]
        min_height.direction = 1  # find zero that goes from - to +
        min_height.terminal = True  # stop integration at minimum height

        # event function for solve_ivp, zero when parcel hits ground
        def hit_ground(_, state):
            return state[0]
        hit_ground.terminal = True  # stop integration at ground

        # event function for solve_ivp, zero when parcel is neutrally
        # buoyant
        def neutral_buoyancy(time, state):
            return motion_ode(time, state)[1]

        # solve the equation of motion
        time = time.to(units.second).m
        sol = solve_ivp(
            motion_ode,
            [np.min(time), np.max(time)],
            [initial_height.m_as(units.meter),
             initial_velocity.m_as(units.meter/units.second)],
            t_eval=time,
            events=[neutral_buoyancy, hit_ground, min_height])

        # record height and velocity
        height = np.full(len(time), np.nan)
        velocity = np.full(len(time), np.nan)
        height[:len(sol.y[0, :])] = sol.y[0, :]
        velocity[:len(sol.y[1, :])] = sol.y[1, :]

        # record times of events
        # sol.t_events[i].size == 0 means the event did not occur
        neutral_buoyancy_time = (  # record only the first instance
            sol.t_events[0][0] if sol.t_events[0].size > 0 else np.nan)
        hit_ground_time = (
            sol.t_events[1][0] if sol.t_events[1].size > 0 else np.nan)
        min_height_time = (
            sol.t_events[2][0] if sol.t_events[2].size > 0 else np.nan)

        # record states at event times
        neutral_buoyancy_height = (  # record only the first instance
            sol.y_events[0][0, 0] if sol.y_events[0].size > 0 else np.nan)
        neutral_buoyancy_velocity = (  # record only the first instance
            sol.y_events[0][0, 1] if sol.y_events[0].size > 0 else np.nan)
        hit_ground_velocity = (
            sol.y_events[1][0, 1] if sol.y_events[1].size > 0 else np.nan)
        min_height_height = (
            sol.y_events[2][0, 0] if sol.y_events[2].size > 0 else np.nan)

        # compute parcel propterties for the solution
        temperature = np.full(len(time), np.nan)
        specific_humidity = np.full(len(time), np.nan)
        liquid_ratio = np.full(len(time), np.nan)
        density = np.full(len(time), np.nan)
        buoyancy = np.full(len(time), np.nan)

        t_profile, q_profile, l_profile = self.properties(
            sol.y[0, :]*units.meter, initial_height,
            t_initial, z_switch, t_switch, theta_e, total_water, improve)
        print(initial_height)
        temperature[:len(sol.y[0, :])] = t_profile.m_as(units.celsius)
        specific_humidity[:len(sol.y[0, :])] = q_profile.m
        liquid_ratio[:len(sol.y[0, :])] = l_profile.m

        r_profile = mpcalc.mixing_ratio_from_specific_humidity(q_profile)
        p_profile = self.pressure(sol.y[0, :]*units.meter)
        gas_density = mpcalc.density(p_profile, t_profile, r_profile)
        density_profile = gas_density/(1 - l_profile.m*liquid_correction)
        density[:len(sol.y[0, :])] = (
            density_profile).m_as(units.kilogram/units.meter**3)

        env_density = self.density(sol.y[0, :]*units.meter)
        buoyancy[:len(sol.y[0, :])] = (
            (env_density - density_profile)/density_profile*const.g
        ).m_as(units.meter/units.second**2)

        # collect everything in a bunch object
        result = MotionResult()
        result.height = height*units.meter
        result.velocity = velocity*units.meter/units.second
        result.temperature = temperature*units.celsius
        result.specific_humidity = specific_humidity*units.dimensionless
        result.liquid_ratio = liquid_ratio*units.dimensionless
        result.density = density*units.kilogram/units.meter**3
        result.buoyancy = buoyancy*units.meter/units.second**2
        result.neutral_buoyancy_time = neutral_buoyancy_time*units.second
        result.hit_ground_time = hit_ground_time*units.second
        result.min_height_time = min_height_time*units.second
        result.neutral_buoyancy_height = neutral_buoyancy_height*units.meter
        result.neutral_buoyancy_velocity = (
            neutral_buoyancy_velocity*units.meter/units.second)
        result.hit_ground_velocity = (
            hit_ground_velocity*units.meter/units.second)
        result.min_height = min_height_height*units.meter
        return result


class IdealisedFastParcel(FastParcel):
    """FastParcel in an idealised sounding."""

    def __init__(self, relative_humidity):
        """
        Creates an instance of IdealisedFastParcel.

        Args:
            relative_humidity: Relative humidity above the boundary layer.

        Returns:
            An instance of IdealisedFastParcel.
        """
        pressure, height, temperature, dewpoint = idealised_sounding(
            relative_humidity)
        super().__init__(pressure, height, temperature, dewpoint)


class MotionResult:
    """Container for calculation results."""

    def __init__(self):
        """Instantiates a MotionResult."""
        self.height = None
        self.velocity = None
        self.temperature = None
        self.specific_humidity = None
        self.liquid_ratio = None
        self.density = None
        self.buoyancy = None
        self.neutral_buoyancy_time = None
        self.hit_ground_time = None
        self.min_height_time = None
        self.neutral_buoyancy_height = None
        self.neutral_buoyancy_velocity = None
        self.hit_ground_velocity = None
        self.min_height = None
