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
from copy import copy
from pyscf import scf
from pyflosic2.systems.rflosic_systems import H2O
from pyflosic2.time.timeit import tictoc
from pyflosic2.parameters.flosic_parameters import parameters
from pyflosic2.sic.rflosic import RFLOSIC, rfodopt
import numpy

# E(DFT) = -74.72911952523143
# E(FLO-SIC,level=1) = -75.55281887091387
# E(FLO-SIC,level=2) = -75.5551538282932
# E(FLO-SIC,level=3) = -75.55517830668863

ref = {'edft': -74.7291195252314,
       'etot_level1': -75.5528188709139,
       'etot_level2': -75.5551538282932,
       'etot_level3': -75.5551783066886}


def test_rflosic(ref=ref):
    # Standard parameters
    p = parameters(mode='restricted', log_name='RFLOSIC.log')

    # Computational parameter
    p.xc = 'LDA,PW'  # r2SCAN '497,498'
    p.verbose = 3
    p.conv_tol = 1e-8
    p.basis = 'pc0'
    p.grid_level = 3
    p.use_analytical_fforce = True
    p.opt_method = 'CG'

    # System information
    p.init_atoms(H2O())
    p.basis = 'sto3g'

    p0 = copy(p)

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
    mf0 = copy(mf)

    @tictoc(p)
    def flosic_level1(p, mf):
        """
            Density matrix (DM) for inital fixed Fermi orbital descriptors (FODs)
            DM : optimized
            FODs: not optimized
        """
        p.optimize_FODs = False
        mflo = RFLOSIC(mf=mf, p=p)
        etot = mflo.kernel()
        # SS: to be sure we do not influence other calcs
        del mflo
        return etot

    etot_level1 = flosic_level1(p, mf)
    # SS: to see the real performance we do not want to use
    # SS: information from previous steps
    mf = copy(mf0)
    p = copy(p0)

    @tictoc(p)
    def flosic_level2(p, mf):
        """
            Density matrix (DM) for Fermi orbital descriptors (FODs, optimized for DM_init)
            step1: DM_init: see opt_dm_fixed_fods
            step2: optimized FODs for fixed DM_init -> FODs(DM_init)
            step3: optimized DM for FODs(DM_init)
        """

        # Step1: DM for init FODs
        p.optimize_FODs = False
        mflo = RFLOSIC(mf=mf, p=p)
        etot = mflo.kernel()
        # Step2: opt FODs for DM
        fopt = rfodopt(mflo, p)
        fopt.optimize()
        # Step3: opt DM for opt FODs
        # FLO-SIC fixed pre-optimized FODs and optimize DM
        p.optimize_FODs = False
        mflo = RFLOSIC(mf=mf, p=p)
        etot = mflo.kernel()
        # SS: to be sure we do not influence other calcs
        del mflo
        return etot

    etot_level2 = flosic_level2(p, mf)
    mf = copy(mf0)
    p = copy(p0)

    @tictoc(p)
    def flosic_level3(p, mf):
        """
            Density matrix (DM) for Fermi orbital descriptors (FODs)
            Repeat outer and inner loop until DM is converged (SCF thresholds)
            and FODs are not changing (fmax).
            Tags: full-self-consistent (SCF) FLO-SIC, in-scf FLO-SIC

            outer loop: DM optimized for current FODs
            inner loop: FODs optimized for current DM

        """
        p.optimize_FODs = True
        mflo = RFLOSIC(mf=mf, p=p)
        etot = mflo.kernel()
        # SS: to be sure we do not influence other calcs
        del mflo
        return etot

    etot_level3 = flosic_level3(p, mf)
    # SS: to see the real performance we do not want to use
    # SS: information from previous steps
    mf = copy(mf0)
    p = copy(p0)

    p.log.write('Basis : {}'.format(p.basis))
    p.log.write('E(DFT) = {}'.format(edft))
    p.log.write('E(FLO-SIC,level=1) = {}'.format(etot_level1))
    p.log.write('E(FLO-SIC,level=2) = {}'.format(etot_level2))
    p.log.write('E(FLO-SIC,level=3) = {}'.format(etot_level3))

    assert numpy.isclose(edft, ref['edft'])
    assert numpy.isclose(etot_level1, ref['etot_level1'])
    assert numpy.isclose(etot_level2, ref['etot_level2'])
    assert numpy.isclose(etot_level3, ref['etot_level3'])
    p.log.write('Tests: passed [okay]')


if __name__ == '__main__':
    test_rflosic()
