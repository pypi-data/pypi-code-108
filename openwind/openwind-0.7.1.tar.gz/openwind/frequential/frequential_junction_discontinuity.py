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

import numpy as np
import scipy.sparse as ssp

from openwind.frequential import FrequentialComponent


class FrequentialJunctionDiscontinuity(FrequentialComponent):
    """
    Frequential representation of a junction between two pipes with mass in case
    of discontinuity of section.

    Assumes convention PH1. This component contributes only to the matrix
    :math:`A_h` :

    .. code-block::

                         ┌                        ┐
                         │ .  .  .  .  .  .  .  . │
                         │ .  .  .  .  .  1  .  . │ ← line of the 1st pipe end's d.o.f.
                         │ .  .  .  .  .  .  .  . │
                         │ .  .  .  .  .  .  .  . │
           Ah_contrib =  │ .  .  .  .  . -1  .  . │ ← line of the 2nd pipe end's d.o.f.
                         │ . -1  .  .  1 jwm .  . │ ← line of this component's d.o.f.
                         │ .  .  .  .  .  .  .  . │
                         │ .  .  .  .  .  .  .  . │
                         └                        ┘

    where `jwm`:math:`=j\\omega m`, with :math:`m` the acoustic mass specified
    in :py:class:`JunctionDiscontinuity<openwind.continuous.junction.JunctionDiscontinuity>`.

    Parameters
    ----------
    junc : :py:class:`JunctionDiscontinuity<openwind.continuous.junction.JunctionDiscontinuity>`
        The continuous version of the junction which is converted

    ends : list of 2 :py:class:`FPipeEnd <openwind.frequential.frequential_pipe_fem.FPipeEnd>`\
        or :py:class:`TMMPipeEnd <openwind.frequential.frequential_pipe_tmm.TMMPipeEnd>`
        The pipe ends this junction connects
    """

    def __init__(self, junc, ends):
        self.junc = junc
        assert len(ends) == 2
        self.ends = ends
        if any(end.convention != 'PH1' for end in ends):
            msg = ("FrequentialJunction does not yet support VH1 convention")
            raise ValueError(msg)

    def __get_physical_params(self):
        radii = []
        rhos = []
        for end in self.ends:
            radius, rho, _ = end.get_physical_params()
            radii.append(radius)
            rhos.append(rho)
        assert all(np.isclose(rhos, rho))
        rho = sum(rhos)/2.0
        r1, r2 = radii
        return r1, r2, rho

    def __get_masses(self):
        r1, r2, rho = self.__get_physical_params()
        mass = self.junc.compute_mass(r1, r2, rho)
        return mass

    def get_number_dof(self):
        return 1

    def get_contrib_freq(self, omegas_scaled):
        mass_junction = self.__get_masses()
        my_contrib = 1j * omegas_scaled * mass_junction
        # Place on our indices
        Ah_diags = np.zeros((self.ntot_dof, len(omegas_scaled)),
                            dtype='complex128')
        Ah_diags[self.get_indices(), :] = my_contrib
        return Ah_diags

    def get_contrib_indep_freq(self):
        assembled_interaction_matrix = ssp.lil_matrix((self.ntot_dof,
                                                       self.ntot_dof),
                                                      dtype='complex128')
        interaction = [-1, 1]
        for i in range(len(self.ends)):
            f_pipe_end = self.ends[i]
            assembled_interaction_matrix[self.get_indices(),
                                         f_pipe_end.get_index()] = interaction[i]
        return assembled_interaction_matrix - assembled_interaction_matrix.T

    # ----- differential -----
    def _get_diff_masses(self, diff_index):
        r1, r2, rho = self.__get_physical_params()

        d_radii = []
        for end in self.ends:
            d_radius = end.get_diff_radius(diff_index)
            d_radii.append(d_radius)
        dmass = self.junc.get_diff_mass(r1, r2, rho, d_radii[0], d_radii[1])
        return dmass

    def get_contrib_dAh_freq(self, omegas_scaled, diff_index):
        dmass = self._get_diff_masses(diff_index)
        local_dAh_diags = 1j * omegas_scaled * dmass
        # Place on our indices
        dAh_diags = np.zeros((self.ntot_dof, len(omegas_scaled)),
                             dtype='complex128')
        dAh_diags[self.get_indices(), :] = local_dAh_diags
        return dAh_diags
