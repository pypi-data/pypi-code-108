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
from pyflosic2.atoms.atoms import Atoms
from pyscf import gto, scf
from pyflosic2.guess.pycom import pycom
from pyflosic2.io.rflosic_io import atoms2pyscf
from pyflosic2.parameters.flosic_parameters import parameters
from pyflosic2.sic.rflo import RFLO
from pyflosic2.sic.rflosic import RFLOSIC, rfodopt
from pyflosic2.parameters.flosic_parameters import set_grid

def dft(p):
    """
        Calculate: DFT (RKS)
        --------------------
        Perform a restricted Kohn-Sham (RKS) 
        density functional theory (DFT) 
        calculation.
    """
    p.mol = gto.M(atom=atoms2pyscf(p.nuclei), 
                  basis=p.basis, 
                  spin=p.spin, 
                  charge=p.charge, 
                  symmetry=p.symmetry)
    mf = scf.RKS(p.mol)
    # SS: b/c different logs
    # SS: PySCF has a different logger
    mf.verbose = 0
    mf.xc = p.xc
    mf.conv_tol = p.conv_tol
    # SS: Own handling of grid 
    mf = set_grid(mf,value=p.grid_level)    
    edft = mf.kernel()
    return p, mf, edft


def guess(mf, p):
    """
        Generate: initial FODs (guess)
        ------------------------------
        Currently using Python center of mass (PyCOM) procedure.
    """
    p.pycom_loc = ['PM', 'FB'][1]
    p.write_cubes = [True, False][1]
    pc = pycom(mf=mf, p=p)
    pc.get_guess()
    pos_fod1 = p.l_com[0]
    p.fod1 = Atoms(len(pos_fod1) * [p.sym_fod1], pos_fod1)
    p.atoms = p.nuclei + p.fod1


def flosic_level0(mf, p):
    """
        FLO-SIC(level=0)
        ----------------
        FLO construction for initial density matrix (DM) and 
        for initial fixed Fermi-orbital descriptors (FODs)
        DM : not optimized, initial DFT
        FODs: not optimized, initial FODs
    """
    p.show()
    flo = RFLO(mf=mf, p=p)
    flo.kernel()
    etot = flo.e_tot
    # SS: to be sure we do not influence other calcs
    del flo
    return etot


def flosic_level1(mf, p):
    """
        FLO-SIC(level=1)
        ----------------
        Update density matrix (DM) for initial fixed Fermi-orbital descriptors (FODs)
        DM : optimized
        FODs: not optimized
    """
    p.optimize_FODs = False
    mflo = RFLOSIC(mf=mf, p=p)
    etot = mflo.kernel()
    # SS: to be sure we do not influence other calcs
    del mflo
    return etot


def flosic_level2(mf, p):
    """
        FLO-SIC(level=2)
        ----------------
        Make density matrix (DM) coherent with initial FODs. 
        Update density matrix (DM) for 
        initial Fermi-orbital descriptors (FODs, optimized for DM_init).
        step1: DM_init: see opt_dm_fixed_fods
        step2: optimized FODs for fixed DM_init -> FODs(DM_init)
        step3: optimized DM for FODs(DM_init)
    """

    # Step1: DM for init FODs
    # Note: Step1 is may equal to flosic_level1
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


def flosic_level3(mf, p):
    """
        FLO-SIC(level=3)
        ----------------
        Self-consistent cycle (SCF) update of density matrix (DM) 
        and Fermi-orbital descriptors (FODs). 
        Repeat outer and inner loop until DM is converged (SCF threshold)
        and FODs are not changing (fmax reached threshold).
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


class RWORKFLOW():
    """
        RWORKFLOW class 
        ---------------
        Performs an automatic restricted FLO-SIC calculation 
        from scratch, i.e., 
        only providing chemical symbols and positions 
        of the nuclei. 
        Main function to be used is the kernel function. 
    """
    def __init__(self, atoms, **kwargs):
        """
            Initialize class
            ----------------

            Input
            -----
            - system information
                atoms: atoms, nuclei only
                spin: int(), 2S = Nalpha - Nbeta, spin
                charge: int(), charge of the system
            - calculation information
                sym_fod1: str(), symbol FODs
                tier_name: str(), default numerical parameter levels, e.g., 'tier1'
                flevel: int(), FLO-SIC approximation (0-3), (low - high accuracy)
                log_name: str(), output log file name
        """
        # Get secondary input parameters 
        self._set_kwargs(kwargs)
        # Parameters instance (p)
        self.p = parameters(mode='restricted',
                            tier_name=self.tier_name,
                            log_name=self.log_name)
        self.p.xc = self.xc
        self.p.nuclei = atoms
        self.p.spin = atoms._spin
        self.p.charge = atoms._charge
        self.p.sym_fod1 = atoms._elec_symbols[0]
        self.p.sym_fod2 = None
        self.p.symmetry = False
        self.p.flevel = self.flevel
        # Setup
        self.setup()

    def _set_kwargs(self,kwargs):
        """
            _set_kwargs
            Set secondary input parameters. 
            If not set from the user, 
            default values will be used. 
        """
        self.tier_name = kwargs.get("tier_name","tier1")
        self.flevel = kwargs.get("flevel",0)
        self.log_name = kwargs.get("log_name","pyflosic2.log")
        self.xc = kwargs.get("xc","LDA,PW")

    def dft(self):
        """
            Calculatue: DFT
            ---------------
        """
        self.p, self.mf, self.edft = dft(self.p)
        # Reference for mf: mf0
        self.mf0 = copy(self.mf)
        self.p.log.write('EDFT = {} [Ha]'.format(self.edft))

    def guess(self):
        """
            Get: FOD guess
            --------------
        """
        guess(self.mf, self.p)

    def atoms(self):
        """
            Get: atoms
            -----------
        """
        self.p.init_atoms(self.p.atoms)
        # Reference for p: p0
        self.p0 = copy(self.p)

    def setup(self):
        """
            Setup: Nuclei and inital FODs
            -----------------------------
        """
        self.dft()
        self.guess()
        self.atoms()

    def flosic(self, update, flevel=None):
        """
            Calculate: FLO-SIC
            ------------------
        """
        if flevel is not None:
            self.p.flevel = flevel
        if self.p.flevel == 0:
            self.etot = flosic_level0(self.mf, self.p)
        if self.p.flevel == 1:
            self.etot = flosic_level1(self.mf, self.p)
        if self.p.flevel == 2:
            self.etot = flosic_level2(self.mf, self.p)
        if self.p.flevel == 3:
            self.etot = flosic_level3(self.mf, self.p)
        self.p.log.write('EFLOSIC(level={}) = {} [Ha]'.format(self.p.flevel, self.etot))
        if not update:
            self.reset()

    def reset(self):
        """
            Restore starting point
            ----------------------
            This can be useful to produce correct timings.
            If one aims to compare different flevel.
        """
        self.mf = copy(self.mf0)
        self.p = copy(self.p0)

    def kernel(self, update=True, flevel=None):
        """
            Kernel function
            ---------------
        """
        self.flosic(update=update, flevel=flevel)
        return self.etot


if __name__ == '__main__':
    # Nuclei
    sym = 'C' + 4 * 'H'
    p0 = [+0.00000000, +0.00000000, +0.00000000]
    p1 = [+0.62912000, +0.62912000, +0.62912000]
    p2 = [-0.62912000, -0.62912000, +0.62912000]
    p3 = [+0.62912000, -0.62912000, -0.62912000]
    p4 = [-0.62912000, +0.62912000, -0.62912000]
    pos = [p0, p1, p2, p3, p4]
    # System: information
    charge = 0
    spin = 0
    atoms = Atoms(sym, pos, spin=spin, charge=charge)
    # Workflow
    rwf = RWORKFLOW(atoms)
    # FLO-SIC approximations
    rwf.kernel(update=False, flevel=0)
    rwf.kernel(update=False, flevel=1)
    rwf.kernel(update=False, flevel=2)
    rwf.kernel(update=False, flevel=3)
