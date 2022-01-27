#!/usr/bin/env python
# Copyright 2020-2022 The PyFLOSIC Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Sebastian Schwalbe <theonov13@gmail.com>
#
import numpy
from pyscf import scf
from pyflosic2.sic.uflo import UFLO
from pyflosic2.parameters.flosic_parameters import parameters
from pyflosic2.systems.uflosic_systems import H2O

SS_entropy_H2O_3_sto3g_04_06_2021 = {'edft': -74.72911919533095,
                                     'etot_level0': -75.5525758588907}


def test_uflo(ref=SS_entropy_H2O_3_sto3g_04_06_2021):
    """
        Test: uflo routine
    """
    # standard parameters
    p = parameters(mode='unrestricted')
    p.verbose = 3
    # System information
    p.init_atoms(H2O())
    p.basis = 'sto3g'

    # generate mf object
    # Choosing UKS
    mf = scf.UKS(p.mol)  # unrestricted
    # Note:
    # We set the verbosity to zero
    # because PySCF use a different logger
    mf.verbose = 0
    mf.xc = p.xc
    mf.grids.level = p.grid_level
    mf.conv_tol = p.conv_tol
    mf.max_cycle = p.max_cycle
    edft = mf.kernel()

    # Set up the SIC Hamiltonian
    p.ham_sic = 'HOOOV'
    p.show()
    # test FLO-SIC functions
    flo = UFLO(mf=mf, p=p)
    flo.kernel()
    flo.get_FOD_FORCES()
    ff = flo.p.fforces
    etot_level0 = flo.e_tot

    # Log results
    p.log.write('FOD forces')
    p.log.write(str(ff))
    p.log.write('Basis : {}'.format(p.basis))
    p.log.write('E(DFT) = {}'.format(edft))
    p.log.write('E(FLO-SIC,level=0) = {}'.format(etot_level0))

    assert numpy.isclose(edft, ref['edft'])
    assert numpy.isclose(etot_level0, ref['etot_level0'])
    p.log.write('Tests: passed [okay]')


if __name__ == '__main__':
    test_uflo()
