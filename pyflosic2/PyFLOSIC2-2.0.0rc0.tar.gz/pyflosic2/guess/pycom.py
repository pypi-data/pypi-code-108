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
from pyscf.lo import boys, edmiston, pipek, ibo
from pyscf.tools.cubegen import orbital
from ase.io import cube
from pyflosic2.units.units import Bohr
from pyscf.dft import numint
from pyflosic2.atoms.atoms import Atoms
from pyflosic2.io.flosic_io import write_xyz


def do_localization(mf, p):
    """
        perform the localization
        ------------------------
        Perform localization using PySCF localization methods.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        p.pycom_orb : localized orbital mo_coeff
    """
    # Localization methods
    def pm2(mol, mo_coeff):
        return ibo.ibo(mol, mo_coeff, locmethod='PM', exponent=4)
    loc = {'FB': boys.Boys,
           'ER': edmiston.Edmiston,
           'PM': pipek.PipekMezey,
           'PM2': pm2}
    # only occupied orbitals
    pycom_orb = []
    for s in range(p.nspin):
        stop = False
        k_iter = 0
        orb = []
        # do this until every eigenvalue is positive
        while not stop:
            if k_iter == 0:
                # 1st iteration starting values
                if p.nspin == 2:
                    mo_occ = mf.mo_coeff[s][:, mf.mo_occ[s] > 0]
                elif p.nspin == 1:
                    mo_occ = mf.mo_coeff[:, mf.mo_occ > 0]
                myloc = loc[p.pycom_loc](mf.mol, mo_occ)
                myloc.verbose = 0  # p.verbose
            else:
                # for every iteration after the 1st one, take the latest values
                # as starting point
                mo_occ = orb
                myloc = loc[p.pycom_loc](mf.mol, mo_occ)
                myloc.verbose = 0  # p.verbose
                myloc.mo_coeff = orb
            orb = myloc.kernel()
            # key not rand or atomic
            u0 = myloc.get_init_guess(key='nottheotherkeys')
            # u0 =  myloc.get_init_guess(key='rand')
            # Check one electron per spin
            if len(u0) > 1:
                g, h_op, h_diag = myloc.gen_g_hop(u=u0)
                hessian = numpy.diag(h_diag)
                hval, hvec = numpy.linalg.eigh(hessian)
            else:
                break
            hval_min = hval.min()
            hval_argmin = hval.argmin()
            # eigenvector of the negative eigenvector
            hvec_max = hvec[:, 0]
            if p.verbose > 4:
                p.log.write('argmin {}'.format(hval_argmin))
            thres = 10e-8
            if numpy.sign(hval_min) == numpy.sign(-1) and abs(hval_min) > thres:
                stop = False
                # add some noise to the localized coefficients
                # the rattle value might need to be optimized
                if p.stability_analysis == 'simple':
                    noise = numpy.random.normal(0, 0.0005, orb.shape)
                    orb = orb + noise
            if numpy.sign(hval_min) == numpy.sign(+1) or abs(hval_min) <= thres:
                stop = True
            if p.verbose > 4:
                p.log.write('cost function: {}'.format(myloc.cost_function(u=u0)))
                p.log.write('min(eigenvalue(hessian) : {}'.format(hval_min))
                p.log.write(str(hvec_max))
            k_iter += 1
        pycom_orb.append(orb)
    p.loc = myloc
    p.pycom_orb = pycom_orb
    return p


def get_com_fast(mf, p):
    """
        Get COMS
        --------
        Calculate COMS in mo_coeff space.
        Note: fast.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        p.l_com : COMs of localized orbitals

    """
    ao1 = numint.eval_ao(mf.mol, mf.grids.coords)
    l_com = []
    for s in range(p.nspin):
        s_com = []
        if p.nspin == 2:
            occ = len(p.pycom_orb[s][mf.mo_occ[s] == 1])
        elif p.nspin == 1:
            occ = len(p.pycom_orb[s][mf.mo_occ == 2])
        for i in range(occ):
            phi = ao1.dot(p.pycom_orb[s][:, i])
            dens = numpy.conjugate(phi) * phi * mf.grids.weights
            # COM
            x = numpy.sum(dens * mf.grids.coords[:, 0]) * Bohr
            y = numpy.sum(dens * mf.grids.coords[:, 1]) * Bohr
            z = numpy.sum(dens * mf.grids.coords[:, 2]) * Bohr
            # p.log.write("{} COM: {} {} {}".format(p.pycom_loc,x,y,z))
            s_com.append([x, y, z])
        l_com.append(s_com)
    p.l_com = l_com
    return p


def write_cube(mf, p):
    """
        Write Cube files
        ----------------
        Write the localized orbitals as cube files.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        cube : cube files
    """
    l_cube = []  # list of all cube file names
    for s in range(p.nspin):
        s_cube = []
        occ = len(mf.mo_coeff[s][mf.mo_occ[s] == 1])
        for i in range(occ):
            f_cube = '{}_orb_{}_spin{}.cube'.format(p.pycom_loc, i, s)
            s_cube.append(f_cube)
            orbital(mf.mol, f_cube, p.pycom_orb[s][:, i], nx=p.nx, ny=p.ny, nz=p.nz)
        l_cube.append(s_cube)
    p.l_cube = l_cube
    return p


def calc_com(mf, p):
    """
        Calculate COMS
        --------------
        Calculate COMs for localized orbitals (from cube files).
        Note: slow.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        p.l_com : COMs of localized orbitals
    """
    l_com = []
    d_com = {}
    for s in range(p.nspin):
        s_com = []
        for f in p.l_cube[s]:
            # calling the wrapper
            com = get_com(f)
            s_com.append(com)
            p.log.write('{} COM: {} {} {}'.format(f, com[0], com[1], com[2]))
            d_com.update({f: com})
        l_com.append(s_com)
    p.l_com = l_com
    p.d_com = d_com
    return p


def get_com(f_cube):
    """
        Calculation of COM
        ------------------
        Utility function for calc_com function.

        Input
        -----
        f_cube : cube file name

        Output
        ------
        com : COM
    """
    orb = cube.read(f_cube)
    # cuba data in [Bohr**3]
    data = cube.read_cube_data(f_cube)
    # cell of cube in [Ang]
    cell = orb.get_cell()
    shape = numpy.array(data[0]).shape
    spacing_vec = cell / shape[0] / Bohr
    values = data[0]
    idx = 0
    unit = 1 / Bohr  # **3
    X = []
    Y = []
    Z = []
    V = []
    fv = open(f_cube, 'r')
    ll = fv.readlines()
    fv.close()
    vec_tmp = ll[2].split()
    vec_a = -1 * float(vec_tmp[1]) * Bohr
    vec_b = -1 * float(vec_tmp[2]) * Bohr
    vec_c = -1 * float(vec_tmp[3]) * Bohr
    vec = [vec_a, vec_b, vec_c]
    for i in range(0, shape[0]):
        for j in range(0, shape[0]):
            for k in range(0, shape[0]):
                idx += 1
                x, y, z = i * float(spacing_vec[0, 0]), j * float(spacing_vec[1, 1]), k * float(spacing_vec[2, 2])
                # approximate minus the Fermi hole h = 2*abs(phi_i)**2
                # see Bonding in Hypervalent Molecules from Analysis of Fermi Holes Eq(11)
                x, y, z, v = x / unit, y / unit, z / unit, 2. * numpy.abs(values[i, j, k])**2.
                X.append(x)
                Y.append(y)
                Z.append(z)
                V.append(v)
    X = numpy.array(X)
    Y = numpy.array(Y)
    Z = numpy.array(Z)
    V = numpy.array(V)
    x = sum(X * V)
    y = sum(Y * V)
    z = sum(Z * V)
    # shifting to the origin of the cube file
    com = (numpy.array([x / sum(V), y / sum(V), z / sum(V)]) - vec).tolist()
    return com


class pycom():
    """
        PyCOM - Python center of mass
        -----------------------------
        Get Fermi-orbital descriptors (FODs)
        using center of mass / centroids
        of localized orbitals.

        Input
        -----
        mf : mf(), PySCF object
             - carries all PySCF natural variables
        p  : Parameters(), Parameters object/instance
             - carries all PyFLOSIC variables

        Output
        ------
        xyz: FOD guess in xyz format


    """

    def __init__(self, mf, p):
        """
            Initialization of the class
            ---------------------------

            Input
            -----
            mf : mf(), PySCF object
                 - carries all PySCF natural variables
            p  : Parameters(), Parameters object/instance
                 - carries all PyFLOSIC variables

        """
        self.mf = mf
        self.p = p
        self.p.stability_analysis = 'simple'
        # resolution of orbs on grid
        self.p.nx = 80
        self.p.ny = 80
        self.p.nz = 80
        self.p.nspin = numpy.array(mf.mo_occ).ndim
        if not hasattr(self.p, 'write_cubes'):
            self.p.write_cubes = False
        if not hasattr(self.p, 'pycom_loc'):
            self.p.pycom_loc = 'FB'

    def kernel(self):
        """
            Get FOD Guess
            -------------
        """
        self.p = do_localization(mf=self.mf, p=self.p)
        self.p.f_guess = '{}_GUESS_COM.xyz'.format(self.p.pycom_loc)
        self.f_guess = self.p.f_guess
        if not self.p.write_cubes:
            # calculate COMs only
            get_com_fast(mf=self.mf, p=self.p)
        else:
            # writes CUBES and calculate COMs
            self.p = write_cube(mf=self.mf, p=self.p)
            self.p = calc_com(mf=self.mf, p=self.p)
            # dict: CUBE and COM relation
            self.d_com = self.p.d_com
        if self.p.mode == 'unrestricted':
            fod1 = self.p.l_com[0]
            fod2 = self.p.l_com[1]
        if self.p.mode == 'restricted':
            fod1 = self.p.l_com[0]
            fod2 = []
        self.p.fod1 = Atoms([self.p.sym_fod1] * len(fod1), fod1, elec_symbols=[self.p.sym_fod1, self.p.sym_fod2])
        self.p.fod2 = Atoms([self.p.sym_fod2] * len(fod2), fod2, elec_symbols=[self.p.sym_fod1, self.p.sym_fod2])
        self.p.atoms = self.p.nuclei + self.p.fod1 + self.p.fod2
        write_xyz(self.p.atoms, f_name=self.p.f_guess)
        self.p.log.print_xyz(self.p.atoms)

    def get_guess(self):
        """
            Get FOD Guess
            -------------
            Utility function, calling self.kernel()
        """
        self.kernel()


if __name__ == '__main__':
    from pyflosic2.parameters.flosic_parameters import parameters
    from pyflosic2.io.uflosic_io import atoms2pyscf
    from pyflosic2.systems.uflosic_systems import CH4
    from pyflosic2.gui.view import GUI
    from pyscf import gto, scf

    # parameters for CH4
    p = parameters(mode='unrestricted')
    p.init_atoms(CH4())
    p.symmetry = False
    p.basis = 'pc0'

    # PySCF DFT
    mol = gto.M(atom=atoms2pyscf(p.nuclei), basis=p.basis, spin=p.spin, charge=p.charge, symmetry=p.symmetry)
    mf = scf.UKS(mol)
    mf.verbose = 0
    mf.kernel()

    # PyCOM
    p.pycom_loc = ['PM', 'FB'][1]
    p.write_cubes = [True, False][1]
    pc = pycom(mf=mf, p=p)
    pc.get_guess()

    # Visualization
    GUI(pc.f_guess, p=p)
