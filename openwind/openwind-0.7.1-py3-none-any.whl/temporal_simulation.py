#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021, INRIA
#
# This file is part of Openwind.
#
# Openwind is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openwind is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openwind.  If not, see <https://www.gnu.org/licenses/>.
#
# For more informations about authors, see the CONTRIBUTORS file

"""High-level interface to run time-domain simulations."""

import warnings

from openwind import Player, InstrumentGeometry
from openwind.continuous import InstrumentPhysics
from openwind.temporal import (TemporalSolver, RecordingDevice)


def simulate(duration, main_bore, holes_valves=None, fingering_chart=None,
             player = None,
             l_ele=None, order=None,
             nondim=False,
             temperature=None,
             losses=False,
             radiation_category='unflanged',
             convention='PH1',
             discontinuity_mass=True,
             matching_volume=False,
             record_energy=False,
             spherical_waves=False,
             cfl_alpha=0.9, n_steps=None,
             verbosity=1,
             theta_scheme_parameter=0.25):
    """
    Run time-domain simulation of an instrument.

    Parameters
    ----------
    duration : float
        Duration of the simulation, in (simulated-world) seconds.
    main_bore : str or list
        filename or list of data respecting the file format with the
        main bore geometry. See also : :py:class:`InstrumentGeometry \
        <openwind.technical.instrument_geometry.InstrumentGeometry>`
    holes_or_vales : str or list, optional
        filename or list of data respecting the file format, with the
        holes and/or valves geometries. The default is None corresponding to
        an instrument without hole or valve. See also : :py:class:`InstrumentGeometry \
        <openwind.technical.instrument_geometry.InstrumentGeometry>`
    fingering_chart : str or list, optional
        filename or list of data respecting the file format, indicating the
        fingering chart in accordance with the holes and/or valves. The default
        is None corresponding to no fingering (everything open).
        See also : :py:class:`InstrumentGeometry \
        <openwind.technical.instrument_geometry.InstrumentGeometry>`
    player : openwind.Player
        Description of the musician's control (embouchure and fingerings)
    l_ele, order :
        Discretization parameters.
        See :py:class:`Mesh <openwind.discretization.mesh.Mesh>` .
    nondim, temperature, losses, radiation_category, convention, \
    spherical_waves, discontinuity_mass, matching_volume :
        Model parameters.
        See :py:class:`InstrumentPhysics <openwind.continuous.instrument_physics.InstrumentPhysics>` .
    record_energy: bool
        Whether to calculate and record the energy exchanges during the simulation.
    cfl_alpha, n_steps:
        Temporal simulation parameters. See :py:meth:`TemporalSolver.run_simulation() <openwind.temporal.temporal_solver.TemporalSolver.run_simulation>` .
    verbosity: 0, 1 or 2
        0 does not print anything; 1 prints estimations of the duration
        of the simulation; 2 prints more information.
    theta_scheme_parameter:
        Parameter for reed numerical scheme :py:class:`TemporalReed1dof <openwind.temporal.treed1dof.TemporalReed1dof>` .

    Returns
    -------
    :py:class:`RecordingDevice <openwind.temporal.recording_device.RecordingDevice>`
        A object giving access to recorded simulation data.

    """

    if player is None:
        player = Player('IMPULSE_400us')
        warnings.warn("The default player for time simulations is used : %s" % repr(player))
    if temperature is None:
        temperature=25
        warnings.warn('The default temperature is 25 degrees Celsius.')


    instrument_geometry = InstrumentGeometry(main_bore, holes_valves, fingering_chart)
    instru_physics = InstrumentPhysics(instrument_geometry, temperature,
                                       player, losses=losses,
                                       radiation_category=radiation_category,
                                       nondim=nondim, convention=convention,
                                       spherical_waves=spherical_waves,
                                       discontinuity_mass=discontinuity_mass)
    t_solver = TemporalSolver(instru_physics, l_ele=l_ele, order=order,
                              cfl_alpha=cfl_alpha,
                              theta_scheme_parameter=theta_scheme_parameter)
    if verbosity>=2:
        print(t_solver)
    rec = RecordingDevice(record_energy=record_energy)
    t_solver.run_simulation(duration, callback=rec.callback,
                            enable_tracker_display=(verbosity>=1),
                            n_steps=n_steps)
    rec.stop_recording()

    return rec
