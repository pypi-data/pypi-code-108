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
from pyscf import scf
from pyflosic2.sic.flo import FLO
from pyflosic2.systems.systems import H2O
from pyflosic2.time.timeit import tictoc
from pyflosic2.parameters.flosic_parameters import parameters
import numpy

# E(U-DFT) = -74.72911952528801
# E(U-FLO-SIC,level=0) = -75.55257872829964
# E(R-DFT) = -74.72911952523145
# E(R-FLO-SIC,level=0) = -75.55257872186598

SS_entropy_H2O_3_sto3g_10_06_2021 = {'uedft': -74.72911952528801,
                                     'uetot_level0': -75.55257872829964,
                                     'redft': -74.72911952523145,
                                     'retot_level0': -75.55257872186598}


def init_UKS():
    """
        Initialize UKS-DFT using PySCF
        ------------------------------
    """
    # Standard parameters
    p = parameters(mode='unrestricted', log_name='UFLO.log')

    # Computational parameter
    p.xc = 'LDA,PW'  # r2SCAN '497,498'
    p.verbose = 3
    p.conv_tol = 1e-8
    p.basis = 'sto3g'
    p.grid_level = 3

    # System information: example
    sys = H2O(p)
    p.init_atoms(sys)

    # DFT
    @tictoc(p)
    def dft(p):
        mf = scf.UKS(p.mol)
        # SS: b/c different logs
        # SS: PySCF has a different logger
        mf.verbose = 0
        mf.xc = p.xc
        mf.conv_tol = p.conv_tol
        mf.grids.level = p.grid_level
        edft = mf.kernel()
        return p, mf, edft

    p, mf, edft = dft(p)
    return mf, p, edft


def init_RKS():
    """
        Initialize RKS-DFT using PySCF
        ------------------------------
    """
    # Standard parameters
    p = parameters(mode='restricted', log_name='RFLO.log')

    # Computational parameter
    p.xc = 'LDA,PW'  # r2SCAN '497,498'
    p.verbose = 3
    p.conv_tol = 1e-8
    p.basis = 'sto3g'
    p.grid_level = 3

    # System information
    sys = H2O(p)
    p.init_atoms(sys)

    # DFT
    @tictoc(p)
    def dft(p):
        mf = scf.RKS(p.mol)
        # SS: b/c different logs
        # SS: PySCF has a different logger
        mf.verbose = 0
        mf.xc = p.xc
        mf.conv_tol = p.conv_tol
        mf.grids.level = p.grid_level
        edft = mf.kernel()
        return p, mf, edft

    p, mf, edft = dft(p)
    return mf, p, edft


def test_flo(ref=SS_entropy_H2O_3_sto3g_10_06_2021):
    """
        TEST: flo.py
        ------------
    """
    mf, p, uedft = init_UKS()
    p.show()
    flo = FLO(mf, p)
    uetot_level0 = flo.kernel()
    p.log.write(str(uedft))
    p.log.write(str(uetot_level0))

    mf, p, redft = init_RKS()
    p.show()
    flo = FLO(mf, p)
    retot_level0 = flo.kernel()
    p.log.write(str(redft))
    p.log.write(str(retot_level0))

    p = parameters()
    p.log.write('Basis : {}'.format(p.basis))
    p.log.write('E(U-DFT) = {}'.format(uedft))
    p.log.write('E(U-FLO-SIC,level=0) = {}'.format(uetot_level0))
    p.log.write('E(R-DFT) = {}'.format(redft))
    p.log.write('E(R-FLO-SIC,level=0) = {}'.format(retot_level0))

    assert numpy.isclose(uedft, ref['uedft'])
    assert numpy.isclose(uetot_level0, ref['uetot_level0'])
    assert numpy.isclose(redft, ref['redft'])
    assert numpy.isclose(retot_level0, ref['retot_level0'])
    p.log.write('Tests: passed [okay]')


if __name__ == '__main__':
    test_flo()
