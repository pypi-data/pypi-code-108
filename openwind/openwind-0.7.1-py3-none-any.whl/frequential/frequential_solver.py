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

import warnings

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.sparse import csr_matrix, SparseEfficiencyWarning, csc_matrix
from scipy.sparse.linalg import spsolve

import openwind.impedance_tools as tools
from openwind.design import Cone
from openwind.technical import Fingering
from openwind.continuous import (PhysicalRadiation, Excitator, Flow,
                                 JunctionTjoint, JunctionSimple, JunctionSwitch,
                                 ThermoviscousLossless, JunctionDiscontinuity,
                                 ThermoviscousDiffusiveRepresentation,
                                 RadiationPerfectlyOpen)
from openwind.frequential import (FrequentialPipeFEM, FrequentialRadiation,
                                  FrequentialJunctionTjoint,
                                  FrequentialJunctionSimple,
                                  FrequentialJunctionDiscontinuity,
                                  FrequentialJunctionSwitch,
                                  FrequentialSource,
                                  FrequentialInterpolation,
                                  FrequentialPipeDiffusiveRepresentation,
                                  FrequentialPipeTMM,
                                  FrequentialPressureCondition,
                                  FrequentialComponent)
from openwind.tracker import SimulationTracker


class FrequentialSolver:
    """
    Solve equations in the frequential domain.

    In the frequential domain, only the wave propagation into the instrument
    is solved. It allows the computation of the acoustic fields into the
    entire instrument and the impedance.

    Parameters
    ----------
    instru_physics : :py:class:`InstrumentPhysics<openwind.continuous.instrument_physics.InstrumentPhysics>`
        The object describing the physics of the instruments.
    frequencies : numpy.array
        Frequencies at which to compute the impedance.
    diffus_repr_var: bool, optional
        Whether to use additional variables when computing the diffusive
        representation. The default is False.
    note : str, optional
        The name of the note corresponding to the fingering which must be
        applied. The default is None and correspond to all holes open.
    compute_method: str in {'FEM', 'TMM', 'hybrid'}, optional
        Which method must be used, the default is FEM:

        - 'FEM': finite element method, usable with any geometry
        - 'TMM': Transfer Matrix Method, usable only with conical pipes
        - 'hybrid': mix between FEM and TMM: the cylinders are computed with\
        TMM (exact solution) and the other pipes with FEM

    discr_params : keyword arguments
        Discretization parameters. See: :py:class:`Mesh <openwind.discretization.mesh.Mesh>`

    Attributes
    ----------
    f_pipes, f_connectors: list of :py:class:`FrequentialComponent\
        <openwind.frequential.frequential_component.FrequentialComponent>`
        The list of the pipes and connectors in their frequential format.

    impedance : array of float
        The impedance at the entrance of the instrument (need to solve the \
        equations with :py:meth:`solve()<FrequentialSolver.solve()>` before)

    pressure, flow : array of float
        The pressure and flow along the instrument (need to solve the equations\
        with :py:meth:`solve(interp=True)<FrequentialSolver.solve()>` before)

    dpressure : array of float
        The spatial gradient of the pressure along the instrument (need to \
        solve the equations with
        :py:meth:`solve(interp_grad=True)<FrequentialSolver.solve()>` before)

    """

    def __init__(self, instru_physics, frequencies, diffus_repr_var=False,
                 note=None, compute_method='FEM', **discr_params):
        self.netlist = instru_physics.netlist
        self.discr_params = discr_params
        self.diffus_repr_var = diffus_repr_var   # When using 'diffrepr+'
        self.compute_method = compute_method   # FEM, TMM, or hybrid?

        frequencies = self._check_frequencies(frequencies, compute_method)
        self.frequencies = frequencies
        self._convert_frequential_components()
        self._organize_components()
        self._construct_matrices_pipes()
        self._set_note(note)
        self._construct_matrices()

    def __repr__(self):
        if len(self.frequencies) > 7:
            freq = ("array([{:.2e}, {:.2e}, ..., {:.2e}, "
                    "{:.2e}])".format(self.frequencies[0], self.frequencies[1],
                                     self.frequencies[-2], self.frequencies[-1]))
        else:
            freq = repr(self.frequencies)

        tmm_pipes = len([p for p in self.f_pipes
                         if p.__class__==FrequentialPipeTMM])
        fem_pipes = len(self.f_pipes) - tmm_pipes
        return ("<openwind.frequential.FrequentialSolver("
                "\n\tfrequencies={},".format(freq) +
                "\n\tnetlist={},".format(repr(self.netlist)) +
                "\n\tcompute_method='{:s}',".format(self.compute_method) +
                "\n\tnote='{}',".format(self.netlist.get_fingering_chart().get_current_note()) +
                "\n\tmesh_info:{{{} dof, {} TMM-pipes, {} FEM-pipes,"
                " elements/FEM-pipe:{}, "
                "order/element:{}}}\n)>".format(self.n_tot, tmm_pipes, fem_pipes,
                                          self.get_elements_mesh(),
                                          self.get_orders_mesh()))

    def __str__(self):
        if len(self.frequencies) > 7:
            freq = ("array([{:.2e}, {:.2e}, ..., {:.2e}, "
                    "{:.2e}])".format(self.frequencies[0], self.frequencies[1],
                                     self.frequencies[-2], self.frequencies[-1]))
        else:
            freq = repr(self.frequencies)
        return ("FrequentialSolver:\n" + "="*20 +
                "\nFrequencies:{}\n".format(freq) +"="*20 +
                "\n{}\n".format(self.netlist) + "="*20 +
                "\nCompute Method: '{:s}'\n".format(self.compute_method) + "="*20 +
                "\nCurrent Note: '{}'\n".format(self.netlist.get_fingering_chart().get_current_note()) + "="*20 +
                "\n" + self.__get_mesh_info())

    @property
    def imped(self):
        """
        The impedance, equivalent to :py:attr:`impedance<FrequentialSolver.impedance>`
        """
        return self.impedance

    @staticmethod
    def _check_frequencies(frequencies, compute_method):
        """
        Check that all the frequencies are positive and that it is an array

        In case of frequencies is a float or an int it is convert in array

        Returns
        -------
        np.array
        """
        if isinstance(frequencies, int) or isinstance(frequencies, float):
            frequencies = [frequencies]
        frequencies = np.array(frequencies)
        if np.any(frequencies <= 0):
            raise ValueError('The frequencies must be strictly positive!')
        if compute_method != 'TMM' and max(frequencies)/min(frequencies)>1000:
            warnings.warn('The frequency range is too big (fmax/fmin={:.0f}, advised: <1000). With FEM the use of'
                          'the same mesh for such range of frequencies can '
                          'induce numerical issue.'.format(max(frequencies)/min(frequencies)))
        return frequencies

    def _set_note(self, note):
        if not note:
            return
        if isinstance(note, str):
            fc = self.netlist.get_fingering_chart()
            self.fingering = fc.fingering_of(note)
        elif isinstance(note, Fingering):
            self.fingering = note
        self.fingering.apply_to(self.f_components)

    def set_note(self, note):
        """
        Update the note (fingering) apply to the instrument.

        Parameters
        ----------
        note : str
            The note name. It must correspond to one of the associated
            :py:class:`FingeringChart<openwind.technical.fingering_chart.FingeringChart>`.

        """
        self._set_note(note)
        # Since solve() assumes the matrices are constructed,
        # update the matrices.
        self._construct_matrices()

    def set_frequencies(self, frequencies):
        """
        Update the frequency axis.

        Parameters
        ----------
        frequencies : array of float
            The new frequency axis.

        """
        self.frequencies = self._check_frequencies(frequencies, self.compute_method)
        self._organize_components()
        self._construct_matrices_pipes()
        self._construct_matrices()

    def _convert_pipe(self, pipe):
        """
        Construct an appropriate instance of (a subclass of) FrequentialPipe.

        Parameters
        ----------
        pipe : `Pipe <openwind.continuous.pipe.Pipe>`
            Continuous model of the pipe.
        **discr_params : keyword arguments
            Discretization parameters, passed to the FPipe initializer.

        Returns
        -------
        `FrequentialPipeFEM <openwind.frequential.frequential_pipe_fem.FrequentialPipeFEM>`
        OR `FrequentialPipeTMM <openwind.frequential.frequential_pipe_tmm.FrequentialPipeTMM>`

        """
        # only give to each pipe its corresponding disc value

        tmm_keys = {'nb_sub'}
        disc_keys = set(list(self.discr_params.keys()))
        params_fem = {k: self.discr_params[k] for k in disc_keys - tmm_keys}
        params_tmm = {k: self.discr_params[k] for k in disc_keys
                      if k in tmm_keys}
        if ('l_ele' in params_fem and isinstance(params_fem['l_ele'], dict)):
            dict_l_ele = params_fem['l_ele']
            params_fem['l_ele'] = dict_l_ele[pipe.label]
        if ('order' in params_fem and isinstance(params_fem['order'], dict)):
            # only give to each pipe its corresponding disc value
            dict_order = params_fem['order']
            params_fem['order'] = dict_order[pipe.label]

        if self.compute_method == 'FEM':
            if (self.diffus_repr_var and
                isinstance(pipe.get_losses(), ThermoviscousDiffusiveRepresentation)):
                return FrequentialPipeDiffusiveRepresentation(pipe, **params_fem)
            return FrequentialPipeFEM(pipe, **params_fem)
        elif self.compute_method == 'TMM':
            return FrequentialPipeTMM(pipe, **params_tmm)
        elif self.compute_method == 'hybrid':
            # Use TMM when it is exact,
            # i.e. if the pipe is a cylinder,
            # or a lossless cone.
            # TODO Add test
            shape = pipe.get_shape()
            lossless = isinstance(pipe.get_losses(), ThermoviscousLossless)
            if isinstance(shape, Cone) and \
                (shape.is_cylinder() or lossless):
                return FrequentialPipeTMM(pipe, **params_tmm)
            return FrequentialPipeFEM(pipe, **params_fem)

        raise ValueError("compute_method must be in {'FEM', 'TMM', 'hybrid'}")

    def _convert_connector(self, connector, ends):
        """
        Construct the appropriate frequential version of a connector.

        Parameters
        ----------
        connector : :py:class:`NetlistConnector<openwind.continuous.netlist.NetlistConnector>`
            Continuous model for radiation, junction, or source.
        ends : list(`FPipeEnd <openwind.frequential.frequential_pipe_fem.FPipeEnd>`)
            The list of all `FPipeEnd`s this component connects to.

        Returns
        -------
        `FrequentialComponent <openwind.frequential.frequential_component.FrequentialComponent>`

        """

        if isinstance(connector, Excitator):
            # verify that source is a flow
            if not isinstance(connector, Flow):
                raise ValueError('The input type of player must be flow for frequential computation')
            f_source = FrequentialSource(connector, ends)
            # Register the source to know on which d.o.f. to measure impedance
            if (hasattr(self, 'source_ref') and
                f_source.source.label != self.source_ref.source.label):
                raise ValueError('Instrument has several Sources (instead of one).')
            else:
                self.source_ref = f_source
            return f_source
        #   return(FrequentialSource(connector, ends))
        elif isinstance(connector, PhysicalRadiation):
            if isinstance(connector, RadiationPerfectlyOpen):
                return FrequentialPressureCondition(0, ends)
            else:
                return FrequentialRadiation(connector, ends)
        elif isinstance(connector, JunctionTjoint):
            return FrequentialJunctionTjoint(connector, ends)
        elif isinstance(connector, JunctionSimple):
            return FrequentialJunctionSimple(connector, ends)
        elif isinstance(connector, JunctionDiscontinuity):
            return FrequentialJunctionDiscontinuity(connector, ends)
        elif isinstance(connector, JunctionSwitch):
            return FrequentialJunctionSwitch(connector, ends)

        raise ValueError("Could not convert connector %s" % str(connector))


    def _convert_frequential_components(self, **kwargs):
        self.f_pipes, self.f_connectors = \
            self.netlist.convert_with_structure(self._convert_pipe,
                                                self._convert_connector)

        self.f_components = self.f_pipes + self.f_connectors
        assert all([isinstance(f_comp, FrequentialComponent)
                    for f_comp in self.f_components])

        if not hasattr(self, 'source_ref'):
            raise ValueError('The input emplacement is not identified: '
                             'it is impossible to compute the impedance.')
        self.scaling = self.source_ref.get_scaling()


    def _organize_components(self):
        n_dof_cmpnts = self.get_dof_of_components()
        self.n_tot = sum(n_dof_cmpnts)
        # place the components
        beginning_index = np.zeros_like(self.f_components)
        beginning_index[1:] = np.cumsum(n_dof_cmpnts[:-1])
        for k, f_comp in enumerate(self.f_components):
            f_comp.set_first_index(beginning_index[k])
            f_comp.set_total_degrees_of_freedom(self.n_tot)

    def _construct_matrices_of(self, components):
        omegas_scaled = 2*np.pi*self.frequencies * self.scaling.get_time()
        # initiate matrices
        n_tot = self.n_tot
        Ah_comp_nodiag = csr_matrix((n_tot, n_tot), dtype='complex128')
        Ah_comp_diags = np.zeros((n_tot, len(omegas_scaled)), dtype='complex128')
        Lh_comp = csr_matrix((n_tot, 1), dtype='complex128')
        # fill the matrices
        for f_comp in components:
            Ah_comp_nodiag += f_comp.get_contrib_indep_freq()
            Ah_comp_diags += f_comp.get_contrib_freq(omegas_scaled)
            Lh_comp += f_comp.get_contrib_source()

        # Transfer the diagonal of Ah_nodiag onto Ah_diags
        # so that the diagonal data of Ah_nodiag can be replaced
        # by each column of Ah_diags
        Ah_comp_diags[:, :] += Ah_comp_nodiag.diagonal()[:, np.newaxis]
        return Ah_comp_nodiag, Ah_comp_diags, Lh_comp

    def _construct_matrices_pipes(self):
        nodiag, diag, Lh = self._construct_matrices_of(self.f_pipes)
        self.Ah_pipes_nodiag = nodiag
        self.Ah_pipes_diags = diag
        self.Lh_pipes = Lh

    def _construct_matrices(self):
        (Ah_conect_nodiag, Ah_conect_diags,
         Lh_conect) = self._construct_matrices_of(self.f_connectors)
        self.Ah_nodiag = self.Ah_pipes_nodiag + Ah_conect_nodiag
        self.Ah_diags = self.Ah_pipes_diags + Ah_conect_diags
        self.Lh = self.Lh_pipes + Lh_conect


    def get_dof_of_components(self):
        """
        The degree of freedom of each component constituing the frequential graph

        Returns
        -------
        n_dof_cmpts : list of int

        """
        n_dof_cmpts = np.array([f_cmpnt.get_number_dof()
                                for f_cmpnt in self.f_components], dtype='int')
        return n_dof_cmpts

    def solve_FEM(self, interp=False, pipes_label='main_bore', interp_grad=False,
                  interp_grid='original', observe_radiation=False,
                  enable_tracker_display=False):
        """
        An overlay of solve()

        .. deprecated:: 0.5
            This method will be replaced by \
            :py:meth:`solve()<FrequentialSolver.solve()>` instead
        """
        warnings.warn('The method FrequentialSolver.solve_FEM() is deprecated,'
                      ' please use solve() instead.')
        self.solve(interp, pipes_label, interp_grad, interp_grid,
                   observe_radiation, enable_tracker_display)


    def solve(self, interp=False, pipes_label='main_bore', interp_grad=False,
              interp_grid='original', enable_tracker_display=False):
        """
        Solve the acoustic equations.

        It gives access to :py:attr:`impedance<FrequentialSolver.impedance>`

        Parameters
        ----------
        interp : bool, optional
            to interpolate the acoustic fields on some given points along the \
            instrument (necessary to have access to \
            :py:attr:`pressure<FrequentialSolver.pressure>` and \
            :py:attr:`flow<FrequentialSolver.flow>`). Default is False.
        pipes_label : str or list of str, optional
            The label of the pipes on which interpolate. The default is "main_bore"
            and correspond to an interpolation on all the pipes of the main bore.
            Used only if interp=True or interp_grad=True.
        interp_grad : bool, optional
            to interpolate the gradient of pressure along the instrument
            (necessary to have access to
            :py:attr:`dpressure<FrequentialSolver.dpressure>`). Default is False
        interp_grid : {float, array(float), 'original', 'radiation'}, optional
            Determine the point on which are computed the interpolated data.
            you can give either

            - a list of points on which to interpolate
            - a float which is the step of the interpolation grid
            - 'original'{Default}, if you want to keep the GaussLobato grid
            - 'radiation' if you want to observe acoustic flow at the radiation opening

        enable_tracker_display: bool, optional
            Display simulation tracker to give some indication on the resting
            computation time. Defaults to False

        """

        # init save data
        ind_source = self.source_ref.get_source_index()

        entrance_H1 = np.empty(self.frequencies.shape, dtype=np.complex128)
        if interp or interp_grad:
            interpolation = FrequentialInterpolation(self, pipes_label, interp_grid)
            self.x_interp = interpolation.x_interp
            interp_H1 = list()
            interp_L2 = list()
            interp_gradH1 = list()

        tracker = SimulationTracker(len(self.frequencies),
                                    display_enabled=enable_tracker_display)

        Ah, ind_diag = self._initialize_Ah_diag()
        # the loop on the frequency
        for cpt in range(len(self.frequencies)):
            # the frequency dependant part of Ah is only on its diagonal
            # Ah.setdiag(self.Ah_diags[:, cpt])
            Ah.data[ind_diag] = self.Ah_diags[:, cpt]
            # solve the problem
            Uh = spsolve(Ah, self.Lh, permc_spec='COLAMD')
            tracker.update()
            # save the right data
            entrance_H1[cpt] = Uh[ind_source]
            if interp:
                interp_H1.append(interpolation.interpolate_H1(Uh))
                interp_L2.append(interpolation.interpolate_L2(Uh))
            if interp_grad:
                interp_gradH1.append(interpolation.interpolate_gradH1(Uh))

        # rescale data
        convention = self.source_ref.get_convention()
        if convention == 'PH1':
            self.impedance = self.scaling.get_impedance() * entrance_H1
            if interp:
                self.pressure = np.array(interp_H1) * self.scaling.get_scaling_pressure()
                self.flow = np.array(interp_L2) * self.scaling.get_scaling_flow()
            if interp_grad:
                self.dpressure = np.array(interp_gradH1) * self.scaling.get_scaling_pressure()
        elif convention == 'VH1':
            self.impedance = self.scaling.get_impedance() / entrance_H1
            if interp:
                self.pressure = np.array(interp_L2) * self.scaling.get_scaling_pressure()
                self.flow = np.array(interp_H1) * self.scaling.get_scaling_flow()

    def _initialize_Ah_diag(self):
        """
        Initialize diag of the sparse matrix Ah and return the corresponding indices

        for numerical purpose, it is interesting to initiate diag values and
        get the corresponding index in the "data" vector

        Returns
        -------
        Ah : csr sparse matrix
            The matrix Ah with abritrary values in diagonal
        ind_diag : array of int
            The indices corresponding to the diagonal values in the "data" attributes
            of the sparse matrix.
        """
        if not all(np.isfinite(self.Ah_nodiag.data)):
            raise ValueError('The matrix Ah contains non-finite value(s) (inf or NaN).')
        Ah = self.Ah_nodiag.tocsc()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SparseEfficiencyWarning)
            Ah.setdiag(np.NaN)
        ind_diag = np.where(np.isnan(Ah.data))[0]
        return Ah, ind_diag


    # %% several notes

    def get_flow_pressure_several_notes(self, notes, f_interest, interp_grid='original'):
        """
        Compute the acoustic fields for several notes.

        Parameters
        ----------
        notes : list of str
            The note names.
        f_interest : list of array
            The interesting frequencies for each notes (the same number of
            frequencies must be given for each note)
        interp_grid : {float, array(float), 'original'}, optional
            Determine the point on which are computed the interpolated data.
            you can give either

            - a list of points on which to interpolate
            - a float which is the step of the interpolation grid
            - 'original'{Default}, if you want to keep the GaussLobato grid
            - 'radiation' if you want to observe acoustic flow at the radiation opening

        Returns
        -------
        flow_notes , pressure_notes : 3D-array
            The flow and pressure for each frequency, for each interpolation \
            point and each note

        """
        assert len(notes) == len(f_interest)
        flow_notes = list()
        pressure_notes = list()

        for note, freq in zip(notes, f_interest):
            self.set_frequencies(freq)
            self.set_note(note)
            self.solve(interp=True, interp_grid=interp_grid)
            flow_notes.append(self.flow)
            pressure_notes.append(self.pressure)

        self.flow_notes = np.array(flow_notes)
        self.pressure_notes = np.array(pressure_notes)
        return flow_notes, pressure_notes

    def impedance_several_notes(self, notes):
        """
        Compute the impedance for several notes

        Parameters
        ----------
        notes : list of str
            The note names.

        Returns
        -------
        impedances : list of array
            The list of the impedance corresponding to each note.

        """
        impedances = list()
        for note in notes:
            self.set_note(note)
            self.solve()
            impedances.append(self.impedance)
        return impedances


    # %% output
    def get_ZC_adim(self):
        """
        The caracteristic impedance at the entrance of the instrument

        .. math::
            Z_c = \\frac{\\rho c}{S_0}

        Returns
        -------
        float

        """
        return self.source_ref.get_Zc0()


    # %% --- Plotting functions ---

    def plot_flow(self, freq=0):
        """
        Plot the acoustic flow for a given frequency inside the instrument.

        It correspond to the interpolation grid used in
        :py:meth:`solve()<FrequentialSolver.solve()>`.

        Parameters
        ----------
        freq : float, optional
            The expected frequency (it uses the first higher frequency computed).
            The default is 0.

        """
        ifreq = np.where(self.frequencies >= freq)[0][0]
        plt.plot(self.x_interp, np.real(self.flow[ifreq]))

    def plot_pressure(self, freq=0):
        """
        Plot the acoustic pressure for a given frequency inside the instrument.

        It correspond to the interpolation grid used in
        :py:meth:`solve()<FrequentialSolver.solve()>`.

        Parameters
        ----------
        freq : float, optional
            The expected frequency (it uses the first higher frequency computed).
            The default is 0.

        """
        ifreq = np.where(self.frequencies >= freq)[0][0]
        plt.plot(self.x_interp, np.real(self.pressure[ifreq]))

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
        tools.plot_impedance(self.frequencies, self.impedance,
                             self.get_ZC_adim(), **kwargs)

    def plot_var3D(self, dbscale=True, var='pressure'):
        """
        Plot with a 3D surface one acoustic field in the instrument for every
        frequency.

        .. warning::
            This method uses the external module `plotly` which must be
            installed by the user.

        Parameters
        ----------
        dbscale : bool, optional
            Plot the fields with a dB scale or not. The default is True.
        var : 'pressure' or 'flow', optional
            Which field must be plotted. The default is 'pressure'.

        """
        try:
            import plotly.graph_objs as go
            import plotly.offline as py
        except ImportError as err:
            msg = "Function plot_var3D() requires plotly."
            raise ImportError(msg) from err

        """Plot either the pressure or the flow for every frequency inside the
        entire instrument.
        """
        X = self.x_interp
        Y = self.frequencies
        if var == 'pressure':
            Z = self.pressure
            filename = 'pressure_3D.html'
        elif var == 'flow':
            Z = self.flow
            filename = 'flow_3D.html'
        else:
            raise ValueError("possible values are pressure or flow")
        if dbscale:
            Zplot = 20*np.log10(np.abs(Z))
        else:
            Zplot = np.real(Z)
        try:
            layout_3D = go.Layout(scene=dict(xaxis=dict(title='Position',
                                                        autorange='reversed'),
                                             yaxis=dict(title='Frequency',
                                                        autorange='reversed'),
                                             zaxis=dict(title='Field')))

            data_u3D = [go.Surface(x=X, y=Y, z=Zplot,
                                   contours=go.surface.Contours(
                                           x=go.surface.contours.X(
                                                   highlightcolor="#42f462",
                                                   project=dict(x=True)),
                                           y=go.surface.contours.Y(
                                                   highlightcolor="#42f462",
                                                   project=dict(y=True))
                                                                 )
                                   )
                        ]
            fig_u3D = go.Figure(data=data_u3D, layout=layout_3D)
            py.plot(fig_u3D, filename=filename)
        except:
            print('Impossible to load plotly: no 3D plot')

    def plot_acoustics_fields(self, notes, variable='power', logscale=False,
                              scaled=False, **kwargs):
        """
        A map plotting the norm of an acoustic quantity at each interpolation
        point for each note.

        The acoustic quantity can be the flow, the pressure or the power (flow
        time pressure).

        Parameters
        ----------
        notes : list of str
            the notes name.
        variable : {'flow', 'pressure', 'power'}, optional
            The acoustic quantity which is plotted. The default is 'power'.
        logscale : bool, optional
            If true the color scale is logarithmic. The default is False.
        scaled : bool, optional
            If true, the acoustic quantity is scaled fingering, by fingering.
            The default is False.
        **kwargs : keyword arguments
            Keyword givent to :py:meth:`matplotlib.pyplot.imshow`

        """
        if variable == 'flow':
            ac_field = np.linalg.norm(self.flow_notes, axis=1)
            title = 'Acoustic flow'
        elif variable == 'pressure':
            ac_field = np.linalg.norm(self.pressure_notes, axis=1)
            title = 'Acoustic pressure'
        elif variable == 'power':
            ac_field = np.linalg.norm(self.flow_notes*self.pressure_notes,
                                      axis=1)
            title = 'Acoustic power'

        if scaled:
            ac_field = (np.abs(ac_field)
                        / np.sum(np.abs(ac_field), 1)[:, np.newaxis])

        if logscale:
            Z = np.log10(ac_field.T)

        else:
            Z = ac_field.T

        fig_test, ax_test = plt.subplots()
        im = ax_test.imshow(Z, **kwargs)


        ax_test.set_xticks(np.arange(0, len(notes), 1))
        ax_test.set_xticks(np.arange(-.5, len(notes)+.5, 1), minor=True)
        ax_test.set_xlim(-.5, len(notes)-.5)
        ax_test.set_xticklabels(notes)

        fig_test.suptitle(title)
        ax_test.xaxis.tick_top()
        ax_test.grid(which='minor', color='k', linestyle='-', linewidth=1.5)

        divider = make_axes_locatable(ax_test)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig_test.colorbar(im, cax=cax)


    # %% --- Post-processing functions ---

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
        if normalize:
            impedance = self.impedance/self.get_ZC_adim()
        else:
            impedance = self.impedance
        tools.write_impedance(self.frequencies, impedance, filename, column_sep)

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
        return tools.resonance_frequencies(self.frequencies, self.impedance, k)

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
        return tools.antiresonance_frequencies(self.frequencies, self.impedance, k)

    def get_lengths_pipes(self):
        """
        Returns
        -------
        list of float
            The length of each pipe (in meter)
        """
        return [f_pipe.pipe.get_length() for f_pipe in self.f_pipes]

    def get_orders_mesh(self):
        """
        Returns
        -------
        list of list of int
            The order of each elements of each pipe
        """
        return [f_pipe.mesh.get_orders().tolist() for f_pipe in self.f_pipes
                if f_pipe.__class__ != FrequentialPipeTMM]

    def get_elements_mesh(self):
        """
        Returns
        -------
        list of int
            The number of elements on each pipe.
        """
        return [len(x) for x in self.get_orders_mesh()]

    def __get_mesh_info(self):
        msg = "Mesh info:"
        msg += '\n\t{:d} degrees of freedom'.format(self.n_tot)
        msg += "\n\tpipes type: {}".format([t for t in self.f_pipes])
        lengths = self.get_lengths_pipes()
        msg += "\n\t{:d} pipes of length: {}".format(len(lengths), lengths)

        # Orders contains one sub-list for each pipe.
        orders = self.get_orders_mesh()
        elem_per_pipe = self.get_elements_mesh()
        msg += ('\n\t{} elements distributed on FEM-pipes '
                'as: {}'.format(sum(elem_per_pipe), elem_per_pipe))
        msg += '\n\tOrders on each element: {}'.format(orders)
        return msg

    def discretization_infos(self):
        """
        Information of the total mesh used to solve the problem.

        See Also
        --------
        :py:class:`Mesh <openwind.discretization.mesh.Mesh>`

        Returns
        -------
        str
        """
        print(self.__get_mesh_info())
