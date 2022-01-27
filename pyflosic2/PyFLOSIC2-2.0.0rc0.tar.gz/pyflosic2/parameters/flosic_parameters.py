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
from pyflosic2.log.logger import logger
from pyscf import gto
from pyflosic2.io.uflosic_io import atoms2flosic as uatoms2flosic, atoms2pyscf as uatoms2pyscf
from pyflosic2.io.rflosic_io import atoms2flosic as ratoms2flosic, atoms2pyscf as ratoms2pyscf
from pyflosic2.atoms.atoms import symbol2number


def set_grid(mf, value, prune=None):
    """
        set_grid
        --------
        PyFLOSIC2 handling of the PySCF grid. 
    """
    if isinstance(value, int):
        mf.grids.level = value
    if isinstance(value, tuple):
        mf.grids.atom_grid = value
    if not isinstance(value, tuple) and not isinstance(value, int):
        print(TypeError('grid needs to be a tuple (e.g., (30,302)) or an integer (0-9).'))
    return mf


class tier():
    """
        Computational parameters (defaults)
        -----------------------------------
        Defaults for essential parameters for the calculation (e.g., basis, grid).

        Input
        -----
        tier_name : str(), default='tier1', accuracy level of the calculation

    """
    # These are properties of the class (cls)
    # They can be used with making an instance
    tier1 = {'basis': 'sto3g',       'grid_level': 3}
    tier2 = {'basis': 'pc0'  ,       'grid_level': 3}
    tier3 = {'basis': 'pc1'  ,       'grid_level': 7}
    tier4 = {'basis': 'pc2'  ,       'grid_level': (150,1202) }
    tier5 = {'basis': 'aug-pc2',     'grid_level': (200,1454) }
    tier6 = {'basis': 'unc-aug-pc2', 'grid_level': (200,1454) }
    tier7 = {'basis': 'unc-aug-pc4', 'grid_level': (400,2030) }

    # Define more tiers
    tiers = {'tier1': tier1,
             'tier2': tier2,
             'tier3': tier3,
             'tier4': tier4,
             'tier5': tier5,
             'tier6': tier6,
             'tier7': tier7}

    def __init__(self, tier_name='tier1'):
        """
            Initialize the tier by name
        """
        self.tier_name = tier_name
        self.init_tier(self.tier_name)

    def init_tier(self, tier_name):
        """
            Set attributes of the class (cls)
            by the tier defaults
        """
        keys = list(tier.tiers[tier_name].keys())
        for key in keys:
            setattr(self, key, tier.tiers[tier_name][key])

    def update_p(self, p):
        """
            Update a parameter class instance (p)
        """
        keys = list(tier.tiers[self.tier_name].keys())
        for key in keys:
            setattr(p, key, getattr(self, key))

    def __repr__(self):
        """
            Representation
            --------------
            Representation printed e.g. using print(system()).
        """
        return "Tier('{}')".format(self.tier_name)


class parameters():
    """
        General parameter class
        -----------------------
        Collection of all essential variables, objects etc.
        for the calculation.

        Input
        -----
        mode      : str(), 'restricted' or 'unrestricted'
        tier_name : str(), default='tier1', accuracy level of the calculation
    """

    def __init__(self, mode='unrestricted', tier_name='tier1', log_name='pyflosic2.log'):
        """
            Intitialize class
            -----------------

            Input
            -----
                mode      : str(), 'restricted' or 'unrestricted'
                tier_name : str(), default='tier1', accuracy level of the calculation
        """
        # general params
        self.mode = mode
        self.tier_name = tier_name
        self.log_name = log_name
        self.verbose = 3
        # datatype for the wavefunctions
        self.datatype = numpy.float64
        # cartesian or spherical representation
        self.cart = False
        # symmetry in mol object 
        self.symmetry = False
        # calculation params
        self.xc = 'LDA,PW'
        self.max_memory = 2000
        self.conv_tol = 1e-5
        self.max_cycle = 300
        self.grid_symmetry = False
        self.init_guess = '1e'
        self.diis = None
        self.diis_space = 3
        # structural params
        self.charge = 0
        self.spin = 0
        # FOD species
        self.sym_fod1 = 'X'
        self.sym_fod2 = 'He'
        # FOD optimization params
        self.optimize_FODs = False
        self.opt_fod_name = 'fodopt'
        # During SCF with freez nuclei
        self.fix_nuc = True
        self.opt_method = ['CG', 'L-BFGS-B', 'FIRE'][1]
        # Starting from the last DM
        self.use_dm_last = False
        # We make a neutral selection
        # and punish nans with a high
        # positive number
        self.opt_fod_punishment = 1000000
        self.use_analytical_fforce = [True, False][0]
        self.opt_fod_objective = ['esic', 'e_tot'][1]
        # VSIC
        # carry vsics
        self.vsic = None
        self.ham_sic = 'HOOOV'
        # spacing for the FD calculation of nuclear forces
        self.dx = 0.001
        # spacing for the FD calculation of FOD forces
        self.da = None
        # spacing for the FD calculation of polarizabilities
        self.full_force = False
        # calculate combined nuclear (FD) and FOD (analytic) forces
        self.delec = None
        # nuclear ASE atoms object
        self.nuclei = None
        # FOD ASE atoms objects
        self.fod1 = None
        self.fod2 = None
        # errors
        self.lo_error_order = 1  # or 2
        # Logger
        # SS: init logger as screen output logger
        self.log = logger(self.log_name)
        # Tier
        self.tier = tier(tier_name)
        self.tier.update_p(self)
        # Grid 
        self._grids = None 

    def init_atoms(self, atoms):
        """
            Initialize systems
        """
        self.atoms = atoms
        self.charge = atoms._charge
        self.spin = atoms._spin
        self.sym_fod1 = atoms._elec_symbols[0]
        self.sym_fod2 = atoms._elec_symbols[1]
        self._check_electrons()
        if self.mode == 'unrestricted':
            # parse FODs with the user-definied symbols
            [nuclei, fod1, fod2] = uatoms2flosic(atoms, sym_fod1=self.sym_fod1, sym_fod2=self.sym_fod2)
            # on-the-fly: add nuclei,fod1,fod2 to p
            self.nuclei = nuclei
            self.fod1 = fod1
            self.fod2 = fod2
            # build PySCF mol object
            self.mol = gto.M(atom=uatoms2pyscf(self.nuclei), basis=self.basis, spin=self.spin, charge=self.charge, symmetry=self.symmetry)
        if self.mode == 'restricted':
            # parse FODs with the user-definied symbols
            self.sym_fod2 = None
            [nuclei, fod1] = ratoms2flosic(atoms, sym_fod1=self.sym_fod1)
            # on-the-fly: add nuclei,fod1 to p
            self.nuclei = nuclei
            self.fod1 = fod1
            # build PySCF mol object
            self.mol = gto.M(atom=ratoms2pyscf(self.nuclei), basis=self.basis, spin=self.spin, charge=self.charge, symmetry=self.symmetry)

    @property
    def basis(self):
        """
            basis set (special property)
            Note: A update of basis set cause a update of the PySCF mol file.
        """
        return self._basis

    @basis.setter
    def basis(self, value):
        """
            Setter for basis
        """
        self._basis = value
        self.update()

    @property
    def grids(self):
        return self._grids

    @grids.setter
    def grids(self,mf):
        """
            Setter for grids 
        """
        self._grids = set_grid(mf,self.grids_level)


    @grids.getter
    def grids(self,mf):
        """
            Getter for grids 
        """
        return self._grids

    @property
    def grids(self):
        return self._grids

    def update(self):
        """
            Update variables, objects which depend on changes (e.g., mol)
        """
        if self.nuclei is not None:
            self.log.write('mol: update instance!')
            if self.mode == 'unrestricted':
                self.mol = gto.M(atom=uatoms2pyscf(self.nuclei), basis=self.basis, spin=self.spin, charge=self.charge)
            if self.mode == 'restricted':
                self.mol = gto.M(atom=ratoms2pyscf(self.nuclei), basis=self.basis, spin=self.spin, charge=self.charge)
            self.log.write('Check basis: p:{} mol:{}'.format(self.basis, self.mol.basis))

    def show(self):
        """
            Print essential parameters
        """
        # Default values
        # printed at the start of a calculation
        print_vars = ['mode',
                      'verbose',
                      'xc',
                      'basis',
                      'charge',
                      'spin',
                      'grid_level',
                      'conv_tol',
                      'max_cycle',
                      'sym_fod1',
                      'sym_fod2',
                      'optimize_FODs',
                      'opt_fod_name',
                      'opt_method']
        self.log.header('Computational parameters')
        # SS: 1st idea was to print everything in self
        # SS: but large complex python arrays etc. should not be printed
        for v in print_vars:
            self.log.write('%-15s: %s' % (v, getattr(self, v)))

    def _check_electrons(self):
        # Number of electrons (Nele)
        # one may expect from atomic number
        Nele_ref = sum([symbol2number[s]
                       for s in self.atoms._symbols if s not in self.atoms._elec_symbols]) + self.charge
        if self.mode == 'restricted':
            Nele_ref /= 2
        check1 = int(self.atoms._Nele) == int(Nele_ref)
        msg1 = 'Nele is equal Nele_ref : {}'.format(check1)
        if self.mode == 'unrestricted':
            check2 = int(abs(self.atoms._Nalpha - self.atoms._Nbeta)) == int(self.atoms._spin)
            msg2 = 'Nalpha - Nbeta is equal spin: {}'.format(check2)
        if self.mode == 'restricted':
            check2 = int(0) == int(self.atoms._spin)
            msg2 = 'spin == 0: {}'.format(check2)
        rv = '{}\n{}'.format(msg1, msg2)
        self.log.write(rv)

    def __repr__(self):
        """
            Representation
            --------------
            Representation printed e.g. using print(system()).
        """
        params = [self.mode, self.tier_name]
        return "Parameters('{}','{}')".format(*params)


if __name__ == "__main__":
    from pyflosic2.atoms.atoms import Atoms

    # Parameters instance (p)
    p = parameters(mode='unrestricted', log_name='Uparameters.log', tier_name='tier2')

    # Update parameters with system instance (sys)
    atoms = Atoms(['He', 'X', 'Kr'], [[0, 0, 0], [0, 0, 0], [0, 0, 0]], spin=0, elec_symbols=['X', 'Kr'])
    p.init_atoms(atoms)

    # View of p
    p.show()

    # Parameters instance (p)
    p = parameters(mode='restricted', log_name='Rparameters.log')

    # Update parameters with system instance (sys)
    atoms = Atoms(['He', 'X'], [[0, 0, 0], [0, 0, 0]], spin=0, elec_symbols=['X', None])
    p.init_atoms(atoms)

    # View of p
    p.show()
    # 
    print(p.grids)
