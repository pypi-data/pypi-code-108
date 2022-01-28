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

"""High-level interface to run impedance computations."""

import warnings

import numpy as np

from openwind.technical import InstrumentGeometry, Player
from openwind.continuous import InstrumentPhysics
from openwind.frequential import FrequentialSolver


class ImpedanceComputation:
    """
    Compute the input impedance of a geometry at the frequencies specified.

    This high-level class bypasses several classes, each ones having its own
    options possibly indicated here.

    This high-level class performs more or less the following steps:

    .. code-block:: python

        my_geometry = InstrumentGeometry(*files)
        my_physics = InstrumentPhysics(my_geometry, temperature, player; **kwargs_phy)
        my_freq_model = FrequentialSolver(my_physics, frequencies, **kwargs_freq)
        my_freq_model.solve()
        self.impedance = my_freq_model.imped
        self.Zc = my_freq_model.get_ZC_adim()


    where `kwargs_phy`  and `kwargs_freq` are different options which can be
    specified by the user.

    See Also
    --------
    :py:class:`InstrumentGeometry <openwind.technical.instrument_geometry.InstrumentGeometry>`
        For information concerning how the geometry of the instrument is specified
    :py:class:`InstrumentPhysics <openwind.continuous.instrument_physics.InstrumentPhysics>`
        For information concerning the graph of the instrument and the options
        `[temperature, losses, convention, nondim, radiation_category, \
         spherical_waves, discontinuity_mass, matching_volume]`
    :py:class:`FrequentialSolver <openwind.frequential.frequential_solver.FrequentialSolver>`
        For information concerning the frequential domain resolution and the
        options: `[compute_method, l_ele, order, nb_sub, note]`
    :py:class:`Player <openwind.technical.player.Player>`
        For information concerning `player` option


    Parameters
    ----------
    fs : numpy.array
        Frequencies at which to compute the impedance.

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

    player : :py:class:`Player <openwind.technical.player.Player>`, optional
        An object specifying how the instrument is "played". Default is None,
        corresponding to a unitary flow imposed at each frequency.

    temperature : float or callable, optional
        Temperature along the instrument in Celsius degree. Default is 25
        See also : :py:class:`InstrumentPhysics\
        <openwind.continuous.instrument_physics.InstrumentPhysics>`

    losses : bool or {'bessel', 'wl','keefe','diffrepr', 'diffrepr+'}, optional
        Whether/how to take into account viscothermal losses. Default is True.
        If 'diffrepr+', use diffusive representation with explicit additional
        variables.
        See also : :py:mod:`thermoviscous_models <openwind.continuous.thermoviscous_models>`

    compute_method : {'FEM', 'TMM', 'hybrid'}, optional
        Method chose to compute the frequency response (Default 'FEM'):

        - 'FEM' = finite elements method
        - 'TMM' = transfer matrix method
        - 'hybrid' = TMM for cylinders, FEM either

        See also : :py:class:`FrequentialSolver <openwind.frequential.frequential_solver.FrequentialSolver>`

    l_ele, order : list, optional, only used for 'FEM' or 'hybrid'
        Elements lengths and orders. Default is None: automatic meshing.
        See also : :py:class:`Mesh <openwind.discretization.mesh.Mesh>`

    nb_sub: integer, optional, only used for TMM
        Number of subdivisions of each conical part. Default is 1.
        See also : :py:class:`FrequentialSolver <openwind.frequential.frequential_solver.FrequentialSolver>`,
        :py:class:`FrequentialPipeTMM <openwind.frequential.frequential_pipe_tmm.FrequentialPipeTMM>`

    note : str, optional
        The note name corresponding to the right fingering, as specified in the
        given :py:class:`FingeringChart<openwind.technical.fingering_chart.FingeringChart>`.
        The default is None, corresponding to all open fingering.

    convention: {'PH1', 'VH1'}, optional, only used for FEM
        Convention chooses whether P (pressure) or V (flow) is the H1 variable.
        Default is {'PH1'}.
        See also : :py:class:`InstrumentPhysics\
        <openwind.continuous.instrument_physics.InstrumentPhysics>`

    nondim : bool, optional
        Nondimensionalization mode. If activated, the physical quantities
        are nondimensionalized so that they are closer to 1. Default {False}.
        See also: :py:class:`InstrumentPhysics\
        <openwind.continuous.instrument_physics.InstrumentPhysics>`

    radiation_category : str, tuple, dict or :py:class:`PhysicalRadiation \
        <openwind.continuous.physical_radiation.PhysicalRadiation>` , optional
        Model of radiation impedance used. The string must be one of the
        available category ('unflanged', 'infinite_flanged', ...). The use of
        dict gives the possibility to use different condition at each opening.
        Default is 'unflanged'.
        See also: :py:class:`InstrumentPhysics \
            <openwind.continuous.instrument_physics.InstrumentPhysics>`
        More details on available model names in :py:meth:`radiation_model \
        <openwind.continuous.radiation_model.radiation_model>`.

    spherical_waves : Boolean, optional
        If true, spherical waves are assumed in the pipe. The default is False.
        See also: :py:class:`InstrumentPhysics \
            <openwind.continuous.instrument_physics.InstrumentPhysics>`

    discontinuity_mass : Boolean, optional
        If true, acoustic mass is included in the junction between two
        pipes with different cross section. The default is True.
        See also: :py:class:`InstrumentPhysics\
        <openwind.continuous.instrument_physics.InstrumentPhysics>`,
        :py:class:`JunctionDiscontinuity\
        <openwind.continuous.junction.JunctionDiscontinuity>`

    matching_volume : boolean, optional
        Include or not the matching volume between the main and the side
        tubes in the masses of the T-joint junctions. The default is False.
        See also: :py:class:`InstrumentPhysics\
        <openwind.continuous.instrument_physics.InstrumentPhysics>`,
        :py:class:`JunctionTjoint\
        <openwind.continuous.junction.JunctionTjoint>`

    Attributes
    -----------
    impedance : np.array
        The complex impedance at the entrance of the instrument at each
        frequency.

    Zc : float
        The real characteristics impedance (rho c / S) at the entrance of the
        instrument, usefull to scale the input impedance.

    """


    FMIN_disc = 2000.0 # provides a mesh adapted to at least FMIN_disc Hz
    """
    float
    The minimal frequency in Hz, for which the mesh is adapted. The mesh is
    adapted to the frequency max([frequencies, FMIN_disc])
    """

    def __init__(self, frequencies, main_bore, holes_valves=None,
                 fingering_chart=None, player = None, temperature=None,
                 losses=True,
                 compute_method='FEM', l_ele=None, order=None, nb_sub=1, note=None,
                 convention='PH1', nondim=True, radiation_category='unflanged',
                 spherical_waves=False, discontinuity_mass=True,
                 matching_volume=False,
                 enable_tracker_display=False):

        if isinstance(frequencies, int) or isinstance(frequencies, float):
            frequencies = np.array([frequencies])
        self.frequencies = frequencies
        if not player:
            player = Player()
        if not temperature:
            temperature=25
            warnings.warn('The default temperature is 25 degrees Celsius.')

        if losses == 'diffrepr+':
            # Use Diffusive Representation with additional variables
            losses = 'diffrepr'
            diff_repr_vars = True
        else:
            diff_repr_vars = False

        self.__instrument_geometry = InstrumentGeometry(main_bore, holes_valves,
                                                        fingering_chart)
        self.__instru_physics = InstrumentPhysics(self.__instrument_geometry, temperature, player=player,
                                      losses=losses,
                                      radiation_category=radiation_category,
                                      nondim=nondim, convention=convention,
                                      spherical_waves=spherical_waves,
                                      discontinuity_mass=discontinuity_mass,
                                      matching_volume=matching_volume)

        FMAX = np.max([np.max(frequencies), ImpedanceComputation.FMIN_disc])
        shortest_lambda = 346.3 / FMAX

        kwargs = {'diffus_repr_var':diff_repr_vars,
                  'l_ele':l_ele,
                  'order':order,
                  'shortestLbd':shortest_lambda,
                  'note':note,
                  'nb_sub':nb_sub}

        self.__freq_model = FrequentialSolver(self.__instru_physics, frequencies,
                                           compute_method=compute_method,
                                           **kwargs)
        self.__freq_model.solve(enable_tracker_display=enable_tracker_display)

        # Small hack : give visibility to ALL the attributes of __freq_model
        # self.__dict__.update(self.__freq_model.__dict__)

        self.impedance = self.__freq_model.imped # /freq_model.get_ZC_adim()
        self.Zc = self.__freq_model.get_ZC_adim()

    def __repr__(self):
        return ("<openwind.ImpedanceComputation("
                "\n{},".format(repr(self.__instru_physics)) +
                "\n{},".format(repr(self.__freq_model)) +
                "\n)>")

    def __str__(self):
        return ("{}\n\n" + 30*'*' + "\n\n{}").format(self.__instru_physics,
                                                     self.__freq_model)

    def set_note(self, note):
        """
        Update the note (fingering) apply to the instrument and compute the
        new impedance.

        See Also
        --------
        :py:meth:`FrequentialSolver.set_note() \
        <openwind.frequential.frequential_solver.FrequentialSolver.set_note>`

        Parameters
        ----------
        note : str
            The note name. It must correspond to one of the associated
            :py:class:`FingeringChart<openwind.technical.fingering_chart.FingeringChart>`.

        """
        self.__freq_model.set_note(note)
        self.__freq_model.solve()
        self.impedance = self.__freq_model.imped

    def set_frequencies(self, frequencies):
        """
        Update the frequency axis and compute the new impedance.

        See Also
        --------
        :py:meth:`FrequentialSolver.set_frequencies() \
        <openwind.frequential.frequential_solver.FrequentialSolver.set_frequencies>`

        Parameters
        ----------
        frequencies : array of float
            The new frequency axis.

        """
        self.frequencies = frequencies
        self.__freq_model.set_frequencies(frequencies)
        self.__freq_model.solve()
        self.impedance = self.__freq_model.imped

    def plot_instrument_geometry(self, figure=None, **kwargs):
        """
        Display the geometry and holes of the instrument.

        If a note name is given, also display the fingering of that note.

        Parameters
        ----------
        figure: matplotlib.figure.Figure, optional
            Which figure to use. By default opens a new figure.
        note: str, optional
            If a note name is given, closed holes are filled, whereas
            open holes are outlined.
            By default all holes are outlined.
        kwargs:
            Additional arguments are passed to the `plt.plot` function.

        """
        self.__instrument_geometry.plot_InstrumentGeometry(figure=figure,
                                                           **kwargs)

    def plot_impedance(self, **kwargs):
        """
        Plot the normalized impedance.

        It uses :py:func:`openwind.impedance_tools.plot_impedance`

        Parameters
        ----------
        **kwargs : keyword arguments
            They are transmitted to :py:func:`plot_impedance()\
            <openwind.impedance_tools.plot_impedance>`.

        """
        self.__freq_model.plot_impedance(**kwargs)

    def write_impedance(self, filename, column_sep=' ', normalize=False):
        """
        Write the impedance in a file.

        The file has the format
        "(frequency) (real part of impedance) (imaginary part of impedance)"

        See :py:func:`openwind.impedance_tools.write_impedance`

        Parameters
        ----------
        filename : string
            The name of the file in which is written the impedance (with the
            extension).
        column_sep : str, optional
            The column separator. Default is ' ' (space)
        normalize : bool, optional
            Normalize or not the impedance by the input characteristic
            impedance. The default is False.

        """
        self.__freq_model.write_impedance(filename, column_sep, normalize)

    def resonance_frequencies(self, k=5):
        """
        The resonance frequencies of the impedance

        It uses the function :func:`openwind.impedance_tools.resonance_frequencies`

        Parameters
        ----------
        k : int, optional
            The number of resonance included. The default is 5.

        Returns
        -------
        list of float

        """
        return self.__freq_model.resonance_frequencies(k)

    def antiresonance_frequencies(self, k=5):
        """
        The antiresonance frequencies of the impedance

        It uses the function :func:`openwind.impedance_tools.antiresonance_frequencies`

        Parameters
        ----------
        k : int, optional
            The number of resonance included. The default is 5.

        Returns
        -------
        list of float

        """
        return self.__freq_model.antiresonance_frequencies(k)

    def discretization_infos(self):
        """
        Information of the total mesh used to solve the problem.

        See Also
        --------
        :py:mod:`discretization <openwind.discretization>`

        :py:class:`Mesh <openwind.discretization.mesh.Mesh>`

        Returns
        -------
        str
        """
        self.__freq_model.discretization_infos()

    def technical_infos(self):
        """
        Print technical information on the instrument geometry and the player.

        See Also
        --------
        :py:mod:`technical <openwind.technical>`

        :py:class:`InstrumentGeometry <openwind.technical.instrument_geometry.InstrumentGeometry>`

        :py:class:`Player <openwind.technical.player.Player>`

        """
        print(self.__instrument_geometry)
        self.__instru_physics.player.display()

    def get_instrument_geometry(self):
        """
        The instrument geometry object.

        Returns
        -------
        :py:class:`InstrumentGeometry <openwind.technical.instrument_geometry.InstrumentGeometry>`

        """

        return self.__instrument_geometry

    def get_all_notes(self):
        """
        Return all the notes specified in the fingering chart

        Returns
        -------
        list[string]
            The list of the notes names
        """
        return self.__instrument_geometry.fingering_chart.all_notes()

    def get_nb_dof(self):
        """
        The total number of degrees of freedom (dof) used to solve the problem.

        Returns
        -------
        int

        """
        return self.__freq_model.n_tot
