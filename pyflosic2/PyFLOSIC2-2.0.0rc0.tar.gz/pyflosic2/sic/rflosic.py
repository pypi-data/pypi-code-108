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
import scipy
from pyscf import lib
from pyflosic2.sic.rflo import RFLO
from pyflosic2.io import flosic_io
from pyflosic2.sic.properties import dip_moment
import numpy


def kernel_sic(mf, p):
    """
        FLO-SIC kernel function
        -----------------------
        This is a a SIC kernel for a FLOSIC class not derived
        directly from a PySCF class.

        if p.optimize_FODs == False
            Density matrix (DM) optimization for fixed Fermi-orbital descriptors (FODs)

        if p.optimize_FODs == True
            Density matrix (DM) optimization and Fermi-orbital descriptors (FODs) optimization

        Input
        -----
        mf: PySCF mf object/instance
        p:  PyFLOSIC2 parameters object/instance
    """
    # Inital density matrix
    mol = mf.mol
    dm = mf.get_init_guess(mol, mf.init_guess)
    # verbose
    mf.verbose = 0

    # The inital energy
    h1e = mf.get_hcore(mol)
    s1e = mf.get_ovlp(mol)
    vhf = mf.get_veff(mol, dm)
    e_tot = mf.energy_tot(dm, h1e, vhf)
    scf_conv = False
    # DIIS
    # gives better SCF convergence
    if isinstance(mf.diis, lib.diis.DIIS):
        mf_diis = mf.diis
    elif mf.diis:
        assert issubclass(mf.DIIS, lib.diis.DIIS)
        mf_diis = mf.DIIS(mf, mf.diis_file)
        mf_diis.space = mf.diis_space
        mf_diis.rollback = mf.diis_space_rollback
    else:
        mf_diis = None

    # Start outer loop
    p.log.init_task('Outer loop', 'optimize DM, fixed FODs')
    for cycle in range(p.max_cycle):
        dm_last = dm
        last_hf_e = e_tot
        last_esic = p.obj_flo.esic
        # Start inner loop
        # in-scf FODs optimization
        if p.optimize_FODs:
            p.log.init_task('Inner loop', 'fixed DM, optimize FODs')
            fopt = rfodopt(p.obj_flo, p)
            fopt.optimize()
            p.log.end_task('Inner loop', 'fixed DM, optimize FODs')
            p.obj_flo.fod1 = fopt.p.fod1
        # End inner loop
        # DFT part
        fock = mf.get_fock(h1e, s1e, vhf, dm, cycle, mf_diis)
        mo_energy, mo_coeff = mf.eig(fock, s1e)
        mo_occ = mf.get_occ(mo_energy, mo_coeff)
        dm = mf.make_rdm1(mo_coeff, mo_occ)
        dm = lib.tag_array(dm, mo_coeff=mo_coeff, mo_occ=mo_occ)
        vhf = mf.get_veff(mol, dm, dm_last, vhf)
        e_dft = mf.energy_tot(dm, h1e, vhf)
        # norm_ddm = numpy.linalg.norm(dm - dm_last)
        # SIC part
        mf.mo_coeff = mo_coeff
        if p.update_esic:
            e_tot = p.obj_flo.kernel()
            esic = p.obj_flo.esic
        # Check: esic convergence
        if abs(last_esic - esic) <= p.conv_esic:
            p.update_esic = False
        vhf += p.obj_flo.hsic
        dm = mf.make_rdm1(p.obj_flo.flo, mo_occ)
        # Dipole moment and spin squared 
        dip = dip_moment(p, dm)
        # Get e_PZ = e_dft(DM_SIC) + esic(DM_SIC)
        e_tot = mf.energy_tot(dm, h1e, vhf) - esic
        p.log.write('>>>> FLO-SIC cycle {} EDFT = {:+.15f} [Ha] <<<<'.format(cycle, e_dft))
        p.log.write('>>>> FLO-SIC cycle {} ESIC = {:+.15f} [Ha] <<<<'.format(cycle, esic))
        p.log.write('>>>> FLO-SIC cycle {} EPZ  = {:+.15f} [Ha] <<<<'.format(cycle, e_tot))
        # in future reconsider gradients my fforces
        # and delta density matrix ddm here again
        if abs(e_tot - last_hf_e) < p.conv_tol:
            scf_conv = True
        if scf_conv:
            p.log.end_task('Outer loop', 'optimize DM, fixed FODs')
            p.log.write('The calculation is converged!')
            p.log.write('[Final] FLO-SIC energy = {:.15g} [Ha]'.format(e_tot))
            break
        # End outer loop
    return scf_conv, e_tot, mo_energy, mo_coeff, mo_occ, cycle, dip


class rfodopt():
    """
        FOD optimizer
        -------------
        Optimize Fermi-orbital descriptors (FODs)
        for a fixed density matrix (DM)
    """

    def __init__(self, mflo, p):
        """
            Initialize class
            ----------------

            Input
            -----
            mflo: RFLO(), restricted FLO class object/instance
            p   : parameters()
        """
        # intrinsic input parameter
        # mflo  ...  FLOSIC class object
        # x     ...  objective vector
        # p     ...  parameter class instance
        self.mflo = mflo
        self.p = p
        # transform FOD position in objective vector x
        self.pos2x()
        self.H0 = 70
        self.etot = None
        self.esic = None

    def pos2x(self):
        """
            Transformation
            --------------
            positions (fod1.get_positions()) to objective vector (pos1d)
            linearisation of the FOD positions
        """
        pos1d = []
        fod1 = numpy.array(self.mflo.p.obj_flo.p.fod1.get_positions()).flatten()
        pos1d.extend(fod1.tolist())
        self.pos1d = pos1d

    def x2pos(self, x):
        """
            Back transformation
            -------------------
            objective vector (x) to positions (fod1.get_positions())
        """
        x = numpy.reshape(x, (int(len(x) / 3.), 3))
        new_fod1 = []
        for f1 in range(0, len(self.p.fod1)):
            tmp_fod1 = x[f1]
            new_fod1.append(tmp_fod1.tolist())
        if self.p.verbose >= 4:
            self.p.log.info('x: {}'.format(x))
        self.p.fod1.positions = new_fod1
        return self.p.fod1

    def get_potential_energy(self, x):
        """
            Get FLO-SIC energy
            ------------------
            Get FLO-SIC energy for objective vector (x)

            Input
            -----
            x : objective vector
        """
        self.p.log.write('FODs: optimization, energy call')
        # back transformation of objective vector x to FOD positions
        new_fod1 = self.x2pos(x)
        self.mflo.fod1 = new_fod1
        self.p.fod1 = new_fod1

        # Optmizers can produce configurations
        # which will break FLO-SIC
        # and give nan in ESIC or Etot
        # we try to catch these errors
        try:
            # # we use the last dm as starting point
            # if self.p.use_dm_last:
            #     # start from last SIC density
            #     dm_last = self.mflo.p.obj_flo.make_rdm1()
            # if not self.p.use_dm_last:
            #     # start from DFT density
            #     dm_last = self.mflo.p.obj_flo.mf.make_rdm1()
            # update inner FOD1 objects
            self.mflo.p.obj_flo.p.fod1 = new_fod1
            etot = self.mflo.p.obj_flo.kernel()
            self.etot = etot
            esic = self.mflo.p.obj_flo.esic
            self.esic = esic
        except BaseException:
            # nan will break the optimization
            # we set it to a energetic unfovored
            # value
            esic = self.p.opt_fod_punishment
            etot = self.p.opt_fod_punishment
        if self.p.opt_fod_objective == 'esic':
            res = esic
        if self.p.opt_fod_objective == 'e_tot':
            res = etot
        return res  # /self.H0

    def get_fforces(self, x):
        """
            Get FOD forces
            --------------
            Get Fermi-orbital descriptor (FOD) forces
            for objective vector (x)

            Input
            -----
            x : objective vector
        """
        # back transformation of objective vector x to FOD positions
        self.p.log.write('FODs: optimization, force call')
        sign = {'e_tot': -1, 'esic': -1}
        new_fod1 = self.x2pos(x)
        self.mflo.fod1 = new_fod1
        self.p.fod1 = new_fod1

        ff = self.mflo.p.obj_flo.get_FOD_FORCES()
        self.ff = ff
        self.fmax = self.get_fmax(ff)
        # self.callback(x)

        # linearization of the forces (1d)
        ff1d = ff.flatten()
        if self.p.verbose >= 4:
            self.p.log.write(ff1d)

        self.callback(x)
        return sign[self.p.opt_fod_objective] * ff1d  # /self.H0

    def get_fmax(self, ff):
        """
            Get fmax
            --------
            Get maximal force component (fmax)

            Input
            -----
            ff : np.array(), FOD forces (ff)
        """
        fmax = numpy.sqrt((ff**2).sum(axis=1).max())
        return fmax

    def print_xyz(self):
        """
            Print xyz file
            --------------
            Print xyz file (nuclei, fod1) to log file
        """
        # Print xyz file containing nuc and fod1
        self.p.log.init_task('xyz', 'nuclei and FODs')
        atoms = self.p.nuclei + self.p.fod1
        self.p.log.print_xyz(atoms)
        self.p.log.end_task('xyz', 'nuclei and FODs')

    def write_xyz(self):
        """
            Write xyz file
            --------------
            Write xyz file (nuclei, fod1) as additional xyz file
        """
        atoms = self.p.nuclei + self.p.fod1
        flosic_io.write_xyz(atoms, f_name='{}.xyz'.format(self.p.opt_fod_name))

    def callback(self, x):
        """
            Callback
            --------
            Print new FOD configuration
            as well as energy and force to log file.

            Note: This is not a SciPy callback function.
            SciPy defines its iteration differently.
            We want to have the FOD configuration
            for each energy + force call.

            Input
            -----
            x : objective vector

        """
        self.p.log.write('FODs: optimization, callback')
        if self.etot is None or self.esic is None:
            self.p.log.write('[Debug] Forces called before energy?')
            self.get_potential_energy(x)
        self.p.log.init_task('FODs', 'New configuration')
        self.print_xyz()
        self.p.log.write('Etot (opt) = %0.9f [Ha]' % (self.etot))
        self.p.log.write('ESIC (opt) = %0.9f [Ha]' % (self.esic))
        self.p.log.write('fmax = %0.6f [Ha/Bohr]' % (self.fmax))

    def optimize(self):
        """
            Start FOD optimization
            ----------------------
            Start optimization of Fermi-orbital descriptors (FODs)
            for a given density matrix (DM)
        """
        # the actual optimization step
        # SS: 02.06.2021
        # SS: it seems that forces are called (scipy//1.3.3) before energy
        # SS: information for the forces are generated by energy call
        # SS: thus we call here the energy that the forces work
        # SS: in newer scipy version 1.6.3 the ordering is correct
        # SS: and we do not need this "fix"
        # e_init =self.mflo.p.obj_flo.kernel()
        if self.p.verbose >= 4:
            e_init = self.mflo.p.obj_flo.kernel()
            self.p.log.header('Initial energy')
            self.p.log.write('Etot(init) = {} [Ha]'.format(e_init))
            self.p.log.header('Initial forces')
            # self.p.log.write(ff_init)
            ff_init = self.mflo.p.obj_flo.get_FOD_FORCES()
            self.get_fmax(ff_init)
        i1 = 'using \t %s                 ' % (self.p.opt_method)
        i2 = 'use_analytical_fforce \t %s ' % (self.p.use_analytical_fforce)
        i3 = 'objective \t %s             ' % (self.p.opt_fod_objective)
        infos = [i1, i2, i3]
        self.p.log.init_task('FODs', 'start optimization', infos)
        # Optimize using a scipy optimizer
        # Use: finite difference forces
        if not self.p.use_analytical_fforce:
            result = scipy.optimize.minimize(
                self.get_potential_energy,
                x0=self.pos1d,
                method=self.p.opt_method,
                options={'disp': False},
                tol=1e-4)  # ,callback=self.callback)
        # Use: analytical FOD forces
        if self.p.use_analytical_fforce:
            result = scipy.optimize.minimize(
                self.get_potential_energy,
                x0=self.pos1d,
                jac=self.get_fforces,
                method=self.p.opt_method,
                options={'disp': False},
                tol=1e-4)  # ,callback=self.callback)
        i1 = 'see %s.xyz    ' % (self.p.opt_fod_name)
        infos = [i1]
        self.p.log.end_task('FODs', 'start optimization', infos)
        self.x = result.x
        if self.p.verbose >= 4:
            self.p.log.write('FODs: Last geometry')
            self.print_xyz()
            # check
            etot_last = self.get_potential_energy(self.x)
            self.p.log.header('Last energy')
            self.p.log.write(' Etot(%s) = %0.9f [Ha]' % (self.p.opt_fod_name, etot_last))
            self.p.log.header('Last forces')
            ff_opt = self.mflo.p.obj_flo.get_FOD_FORCES()
            # self.p.log.write(ff_opt)
            self.get_fmax(ff_opt)
        self.p.fod1 = self.x2pos(self.x)
        self.write_xyz()


class RFLOSIC():
    """
        The RFLOSIC scf class
        ---------------------
        Performs a restricted FLO-SIC calculation. 
        The main function to be used is the kernel function.
    """

    def __init__(self, mf, p):
        """
            Initialize class
            ----------------

            Input
            -----
            mf : mf(), PySCF object
                 - carries all PySCF natural variables
            p  : Parameters(), Parameters object/instance
                 - carries all PyFLOSIC variables
        """

        # mf carries all PySCF natural variables
        self.mf = mf
        # p carries all PyFLOSIC variables
        self.p = p
        self.p.log.header('TASK: RFLOSIC')
        # update sic
        self.p.update_esic = True
        # convergence parameter for ESIC
        if not hasattr(self.p, 'conv_esic'):
            self.p.conv_esic = 1e-8
        self.p.show()

    def kernel(self):
        """
            Kernel function
            ---------------
            Similar as the PySCF kernel functions.
            Get the FLO-SIC energy in self-consistent field (SCF) cycles.

        """
        obj_flo = RFLO(mf=self.mf, p=self.p)
        self.p.obj_flo = obj_flo
        scf_conv, e_tot, mo_energy, mo_coeff, mo_occ, cycle, dip = kernel_sic(self.mf, p=self.p)
        self.mo_energy = mo_energy 
        self.cycle = cycle
        self.dip = dip
        return e_tot

    def __repr__(self):
        """
            Representation
            --------------
            Representation printed e.g. using print(RFLOSIC()).
        """
        params = [self.p.tier_name]
        return "RFLOSIC('{}')".format(*params)


if __name__ == "__main__":
    from pyflosic2.test.knight_valley.rflosic.test_rflosic import test_rflosic

    test_rflosic()
