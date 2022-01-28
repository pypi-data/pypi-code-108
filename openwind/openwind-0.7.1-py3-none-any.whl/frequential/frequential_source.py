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
from scipy.sparse import csr_matrix
from openwind.frequential import FrequentialComponent


class FrequentialSource(FrequentialComponent):
    """
    Computes the source terme Lh for the linear system to solve

    .. math::

        Ah.Uh = Lh

    This component contributes only to the :math:`L_h` matrix with:

    .. code::

                         ┌   ┐
                         │ . │
                         │ . │
            Lh_contrib = │ . │
                         │ 1 │ ← line of the pipe end's d.o.f H1 variable
                         │ . │
                         └   ┘


    Parameters
    ----------
    source : :py:class:`Excitator <openwind.continuous.excitator.Excitator>`
        Excitator. Must be :py:class:`Flow <openwind.continuous.excitator.Flow>`.
    ends : list of :py:class:`FPipeEnd <openwind.frequential.frequential_pipe_fem.FPipeEnd>`
        Frequential Pipe end associated to this source condition.

    """

    def __init__(self, source, ends):
        self.end, = ends  # Unpack one
        self.source = source

    def get_scaling(self):
        """
        Return the scaling associated to the source

        Returns
        -------
        :py:class:`Scaling<openwind.continuous.scaling.Scaling>`

        """
        return self.source.scaling

    def get_convention(self):
        """
        The convention at the source end

        Returns
        -------
        {'PH1', 'VH1'}

        """
        return self.end.convention

    def get_number_dof(self):
        return 0

    def get_contrib_source(self):
        index_source = self.get_source_index()
        return csr_matrix(([1], ([index_source], [0])),
                          shape=(self.ntot_dof, 1))

    def get_source_index(self):
        """
        Get index where this source brings a nonzero term.

        Returns
        -------
        int
        """
        return self.end.get_index()

    def get_Zc0(self):
        """
        Return the real characteristic impedance at the source end

        .. math::
            Z_c = \\frac{\\rho c}{S}

        Returns
        -------
        float

        """
        radius, rho, c = self.end.get_physical_params()
        return rho*c/(np.pi*radius**2)
