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
from pyflosic2.systems.uensemble_systems import Na_1, Na_2, Na_fodmc1, Na_fodmc2, Na_fodmc3, lewis1_benzene, lewis2_benzene, linnett_benzene, linnett2_benzene
from pyflosic2.time.timeit import tictoc
from pyflosic2.parameters.flosic_parameters import parameters
from pyflosic2.sic.uflo import UFLO
from pyflosic2.sic.uflosic import UFLOSIC, ufodopt
from pyflosic2.sic.uworkflow import dft, flosic_level1
from pyflosic2.sic.properties import dip_moment, spin_square
from pyscf import lib
from copy import copy 

from pyflosic2.sic.uflo import make_rdm1
from pyscf.tools.cubegen import density, orbital


""" WORK IN PROGRESS. Do not use if you are not S. Schwalbe, K. Trepte or S. Lehtola! """


def write_cube(mf, p, label='orb',n=[80,80,80]):
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
    nx, ny, nz = n
    l_cube = []  # list of all cube file names
    den = numpy.zeros_like(p.obj_flo.flo[0][:, 0]) 
    dm = make_rdm1(p.obj_flo.flo, mf.mo_occ, p)
    dm = dm[0] + dm[1].transpose()
    density(mf.mol, f'den_test.cube', dm)
    for s in range(p.nspin):
        s_cube = []
        occ = len(mf.mo_coeff[s][mf.mo_occ[s] == 1])
        for i in range(occ):
            f_cube = '{}_orb_{}_spin{}.cube'.format(label, i, s)
            d_cube = '{}_den.cube'.format(label, i, s)
            s_cube.append(f_cube)
            orbital(mf.mol, f_cube, p.obj_flo.flo[s][:, i], nx=nx, ny=ny, nz=nz)
            den += abs(p.obj_flo.flo[s][:, i])**2
        l_cube.append(s_cube)
    orbital(mf.mol, d_cube, den, nx=nx, ny=ny, nz=nz)
    p.l_cube = l_cube
    return p

def write_ensemble_cube(mf, p, mo_coeff, label='orb',n=[80,80,80]):
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
    nx, ny, nz = n
    l_cube = []  # list of all cube file names
    den = numpy.zeros_like(p.obj_flo.flo[0][:, 0])
    dm = make_rdm1(mo_coeff, mf.mo_occ, p)
    dm = dm[0] + dm[1].transpose()
    density(mf.mol, f'den_test.cube', dm)
    for s in range(p.nspin):
        s_cube = []
        occ = len(mf.mo_coeff[s][mf.mo_occ[s] == 1])
        for i in range(occ):
            f_cube = '{}_orb_{}_spin{}.cube'.format(label, i, s)
            d_cube = '{}_den.cube'.format(label, i, s)
            s_cube.append(f_cube)
            orbital(mf.mol, f_cube, mo_coeff[s][:, i], nx=nx, ny=ny, nz=nz)
            den += abs(mo_coeff[s][:, i])**2
        l_cube.append(s_cube)
    orbital(mf.mol, d_cube, den, nx=nx, ny=ny, nz=nz)
    p.l_cube = l_cube
    return p


def kernel_cc_sic(mf, p, P):
    """
        CC-FLO-SIC kernel function
        -----------------------
     
        if p.optimize_FODs == False
            Density matrix (DM) optimization for fixed Fermi-orbital descriptors (FODs)

        if p.optimize_FODs == True
            Density matrix (DM) optimization and Fermi-orbital descriptors (FODs) optimization

        Input
        -----
        mf: PySCF mf object/instance
        P:  Set of p, PyFLOSIC2 parameters object/instance
    """
    # Stuff
    Nconf = len(P)
    esic = 0
    p.esic = 0
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
        last_esic = p.esic
        # Start inner loop
        # in-scf FODs optimization
        for pi in P: 
            if pi.optimize_FODs:
                pi.log.init_task('Inner loop', 'fixed DM, optimize FODs')
                fopt = ufodopt(pi.obj_flo, pi)
                fopt.optimize()
                pi.log.end_task('Inner loop', 'fixed DM, optimize FODs')
                pi.obj_flo.fod1 = fopt.p.fod1
                pi.obj_flo.fod2 = fopt.p.fod2
        # End inner loop
        # DFT part
        fock = mf.get_fock(h1e, s1e, vhf, dm, cycle, mf_diis)
        mo_energy, mo_coeff = mf.eig(fock, s1e)
        mo_occ = mf.get_occ(mo_energy, mo_coeff)
        dm = mf.make_rdm1(mo_coeff, mo_occ)
        dm = lib.tag_array(dm, mo_coeff=mo_coeff, mo_occ=mo_occ)
        vhf = mf.get_veff(mol, dm, dm_last, vhf)
        e_dft = mf.energy_tot(dm, h1e, vhf)
        #dip = mf.dip_moment() 
        #SS, M = mf.spin_square()
        #print(dip, SS, M) 
        dip = dip_moment(p, dm)
        SS, M  = spin_square(p, mf)
        # norm_ddm = numpy.linalg.norm(dm - dm_last)
        # SIC part
        mf.mo_coeff = mo_coeff
        esic_conf = 0
        vhf_conf = numpy.zeros_like(vhf)
        # Update: SIC properties of each configuration pi 
        for pi in P: 
            if pi.update_esic:
                e_tot = pi.obj_flo.kernel()
                esic_tmp = pi.obj_flo.esic
                esic_conf += pi.obj_flo.esic
            # Check: esic convergence
            #if abs(last_esic - esic) <= pi.conv_esic:
            #    pi.update_esic = False
            #    esic_conf += pi.obj_flo.esic
            vhf_conf += pi.obj_flo.hsic
        # Update: ensemble esic and vhf  
        vhf_conf /= Nconf
        esic_conf /= Nconf 
        esic = esic_conf 
        p.esic = esic 
        vhf += vhf_conf
        # Get e_PZ = e_dft(DM_SIC) + esic(DM_SIC)
        e_tot = mf.energy_tot(dm, h1e, vhf) - esic
        p.log.write('>>>> CC-FLO-SIC cycle {} EDFT = {:+.15f} [Ha] <<<<'.format(cycle, e_dft))
        p.log.write('>>>> CC-FLO-SIC cycle {} ESIC = {:+.15f} [Ha] <<<<'.format(cycle, esic))
        p.log.write('>>>> CC-FLO-SIC cycle {} EPZ  = {:+.15f} [Ha] <<<<'.format(cycle, e_tot))
        # in future reconsider gradients my fforces
        # and delta density matrix ddm here again
        if abs(e_tot - last_hf_e) < p.conv_tol:
            scf_conv = True
        if scf_conv:
            p.log.end_task('Outer loop', 'optimize DM, fixed FODs')
            p.log.write('The calculation is converged!')
            p.log.write('[Final] CC-FLO-SIC energy = {:.15g} [Ha]'.format(e_tot))
            break
        # End outer loop
    return scf_conv, e_tot, mo_energy, mo_coeff, mo_occ


def flosic_level1(mf,p):
    p.optimize_FODs = False
    mflo = UFLOSIC(mf=mf, p=p)
    etot = mflo.kernel()
    return mflo, etot 

def test1(conf):
    p = parameters(mode='unrestricted', log_name='UENSEMBLE.log')
    p.init_atoms(conf)
    p.symmetry = None
    p.basis = 'pc0'
    p, mf, edft = dft(p) 
    dm = mf.make_rdm1()
    dip0 = mf.dip_moment() 
    dip = dip_moment(p, dm) 
    SS0, M0 =  mf.spin_square()
    print(dip0,dip)
    SS, M  = spin_square(p, mf)
    print(SS0, M0, SS, M)
    mflo, eflosic = flosic_level1(mf, p)
    dm = mf.make_rdm1()
    dip = dip_moment(p, dm)
    SS, M  = spin_square(p, mf)
    print(dip, SS, M)

class UCCFLOSIC():
    """
        The UCCFLOSIC scf class
        ---------------------
    """

    def __init__(self, mf, p, cc):
        """
            Initialize class
            ----------------

            Input
            -----
            mf : mf(), PySCF object
                 - carries all PySCF natural variables
            p  : Parameters(), Parameters object/instance
                 - carries all PyFLOSIC variables
            cc : list of coupled configurations (cc) 
        """

        # mf carries all PySCF natural variables
        self.mf = mf
        # p carries all PyFLOSIC variables
        self.p = p
        self.cc = cc 
        self.P = []
        self.p.log.header('TASK: UFLOSIC')
        # update sic
        self.p.update_esic = True
        # convergence parameter for ESIC
        if not hasattr(self.p, 'conv_esic'):
            self.p.conv_esic = 1e-8
        self.p.show()

    def __init__cc(self): 
        for i,ci in enumerate(self.cc):
            pi = parameters(mode='unrestricted', log_name=f'UCONFIGURATION{i}.log')
            # Update pi's properties from global p
            for attr in vars(self.p):
                value = getattr(self.p, attr)
                setattr(pi,attr,value)
            pi.opt_fod_name = f'fodopt_config{i}'
            pi.update_esic = True
            pi.init_atoms(ci())
            pi.obj_flo = UFLO(mf=self.mf, p=pi)
            self.P.append(pi) 

    def _get_HOMO(self, mo_energy): 
        Na = len(self.p.fod1) 
        Nb = len(self.p.fod2)
        HOMO_a = mo_energy[0][Na-1]
        if Nb >= Na: 
            HOMO_b = mo_energy[0][Nb-1]
            if HOMO_a < HOMO_b:
                HOMO = HOMO_b 
            else: 
                HOMO = HOMO_a 
        else: 
            HOMO = HOMO_a
        return HOMO 

    def _get_ORBITALS(self):
        for i,pi in enumerate(self.P):
            write_cube(self.mf,pi,label=f'conf{i}')


    def kernel(self):
        """
            Kernel function
            ---------------
            Similar as the PySCF kernel functions.
            Get the FLO-SIC energy in self-consistent field (SCF) cycles.

        """
        self.__init__cc() 
        scf_conv, e_tot, mo_energy, mo_coeff, mo_occ = kernel_cc_sic(self.mf, p=self.p, P=self.P)
        self.mo_energy, self.mo_coeff =  mo_energy, mo_coeff
        write_ensemble_cube(self.mf, self.P[0], mo_coeff, label='avengers_hans',n=[80,80,80])
        self._get_ORBITALS()
        return e_tot

    def __repr__(self):
        """
            Representation
            --------------
            Representation printed e.g. using print(UFLOSIC()).
        """
        params = [self.p.tier_name]
        return "UCCFLOSIC('{}')".format(*params)


def test2():
    conf1 = lewis1_benzene #Na_2 # Na_fodmc1 #Na_2
    conf2 = lewis2_benzene #Na_2 # Na_fodmc3 #Na_1
    # Global calculations object is p 
    p = parameters(mode='unrestricted', log_name='UENSEMBLE.log')
    # The configurations are called pi 
    p1 = parameters(mode='unrestricted', log_name='UENSEMBLE1.log')
    p1.update_esic = True 
    p2 = parameters(mode='unrestricted', log_name='UENSEMBLE2.log')
    p2.update_esic = True
    p.init_atoms(conf1())
    p1.init_atoms(conf1())
    p1.symmetry = None
    p2.init_atoms(conf2()) 
    p2.symmetry = None
    # basis 
    p.basis = 'pc0'
    p1.basis = 'pc0' 
    p2.basis = 'pc0' 
    p1, mf, edft = dft(p1)
    p2, mf, edft = dft(p2)
    p1.obj_flo = UFLO(mf=mf, p=p1)
    p2.obj_flo = UFLO(mf=mf, p=p2)
    p1.conv_esic = 1e-8
    p2.conv_esic = 1e-8

    # Configurations 
    P = (p1,p2)
    scf_conv, e_tot, mo_energy, mo_coeff, mo_occ = kernel_cc_sic(mf,p, P)
    dm = mf.make_rdm1()
    dip = dip_moment(p, dm)
    SS, M  = spin_square(p, mf)
    print(dip, SS, M)


def test3(P):
    # Global calculations object is p
    p = parameters(mode='unrestricted', log_name='UENSEMBLE.log')
    p.symmetry = None
    #p.basis = 'pc0'
    p.init_atoms(P[0]())
    p, mf, edft = dft(p)
    cc = UCCFLOSIC(mf, p, P)
    cc.kernel()

def test4(conf): 
    p = parameters(mode='unrestricted', log_name='UDFT.log')
    p.symmetry = None
    p.init_atoms(conf())
    p, mf, edft = dft(p)
    BASIS = ['sto3g','pc0','pc1']
    for basis in BASIS: 
        p.basis = basis
        p, mf, edft = dft(p)
        print(f'{basis} {edft}')


if __name__ == '__main__': 
    #test1(Na_1())
    # ESIC = +1.116190664955710 
    # EPZ  = -160.321885530365137 
    # SPIN = 0.7500855714509118 2.0000855696203717
    # DIP = [-0.34632238  0.00984353 -0.00036783] 
    #test1(Na_2())
    # ESIC = +1.115874470330883
    # EPZ  = -160.32154431948
    # SPIN = 0.7500998323278676 2.0000998298363686 
    # DIP  = [0.33972,  0.01088, -0.00639]
    #test1(Na_fodmc1())
    #test1(Na_fodmc3())
    #test2()
    # Current 
    # P = (Na_1, Na_2) 
    #>>>> FLO-SIC cycle 5 EDFT = -159.206947232941104 [Ha] <<<<
    #>>>> FLO-SIC cycle 5 ESIC = +1.112109046739736 [Ha] <<<<
    #>>>> FLO-SIC cycle 5 EPZ  = -160.319056279680836 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -160.319056279681 [Ha]
    #Dipole moment(X, Y, Z, Debye): -0.00262,  0.00781, -0.00320


    # P = (Na_1, Na_1) 
    # >>>> FLO-SIC cycle 6 EDFT = -159.205694675797702 [Ha] <<<<
    # >>>> FLO-SIC cycle 6 ESIC = +1.116191006377694 [Ha] <<<<
    # >>>> FLO-SIC cycle 6 EPZ  = -160.321885682175406 [Ha] <<<<
    # ---------------------------------------------
    #  [End]   Outer loop : optimize DM, fixed FODs
    # ---------------------------------------------
    # The calculation is converged!
    # [Final] FLO-SIC energy = -160.321885682175 [Ha]
    # Dipole moment(X, Y, Z, Debye): -0.34632,  0.00993, -0.00038

    # P = (Na_2, Na_2) 
    # >>>> FLO-SIC cycle 6 ESIC = +1.115874853014281 [Ha] <<<<
    # >>>> FLO-SIC cycle 6 EPZ  = -160.321544506293662 [Ha] <<<<
    # ---------------------------------------------
    #  [End]   Outer loop : optimize DM, fixed FODs
    # ---------------------------------------------
    # The calculation is converged!
    # [Final] FLO-SIC energy = -160.321544506294 [Ha]
    # Dipole moment(X, Y, Z, Debye):  0.33972,  0.01097, -0.00637

    # Na_fodmc1 
    #[Final] FLO-SIC energy = -160.436512163728 [Ha]
    #Dipole moment(X, Y, Z, Debye):  0.43350, -0.00038, -0.01740
    #M : 2.0001672309600007 <S^2> : 0.7501672379515494
                                                    

    # Na_fodmc1 + Na_fodmc3
    #M : 2.0001657008347706 <S^2> : 0.7501657076989625
    #>>>> CC-SIC cycle 5 EDFT = -159.209310204297282 [Ha] <<<<
    #>>>> CC-SIC cycle 5 ESIC = +1.223304025904053 [Ha] <<<<
    #>>>> CC-SIC cycle 5 EPZ  = -160.432614230201324 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -160.432614230201 [Ha]
    #Dipole moment(X, Y, Z, Debye):  0.00000,  0.00000, -0.00000
    #M : 2.0001660151783014 <S^2> : 0.7501660220685613
    
    #test1(lewis1_benzene())
    # lewis1_benzene  
    #>>>> FLO-SIC cycle 4 EDFT = -227.224733090804648 [Ha] <<<<
    #>>>> FLO-SIC cycle 4 ESIC = +3.010075322753234 [Ha] <<<<
    #>>>> FLO-SIC cycle 4 EPZ  = -230.234808413557488 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -230.234808413557 [Ha]
    #Dipole moment(X, Y, Z, Debye):  0.00037,  0.00000, -0.00000
    #M : 1.000000006969259 <S^2> : 3.484629473859968e-09
    
    #test1(lewis2_benzene())
    #>>>> FLO-SIC cycle 4 EDFT = -227.224733090803909 [Ha] <<<<
    #>>>> FLO-SIC cycle 4 ESIC = +3.010075322753231 [Ha] <<<<
    #>>>> FLO-SIC cycle 4 EPZ  = -230.234808413557374 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -230.234808413557 [Ha]
    #Dipole moment(X, Y, Z, Debye): -0.00037,  0.00000, -0.00000
    #M : 1.0000000069692803 <S^2> : 3.4846401320010045e-09
    
    #test1(linnett_benzene())
    #>>>> FLO-SIC cycle 4 EDFT = -227.224450047309915 [Ha] <<<<
    #>>>> FLO-SIC cycle 4 ESIC = +3.010945039532370 [Ha] <<<<
    #>>>> FLO-SIC cycle 4 EPZ  = -230.235395086842061 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -230.235395086842 [Ha]
    #Dipole moment(X, Y, Z, Debye): -0.00000, -0.00000, -0.00000
    #M : 1.2007976931647353 <S^2> : 0.11047877497743741
   
    # linnett2_benzene 
    # Dipole moment(X, Y, Z, Debye):  0.00000, -0.00000, -0.00000
    # M : 1.1887169455418793 <S^2> : 0.1032619941546038
    # Elapsed time (UFLO.kernel) = +16.689716100692749 [s]
    # >>>> CC-FLO-SIC cycle 4 EDFT = -227.224450047310768 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 4 ESIC = +3.010945039532370 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 4 EPZ  = -230.235395086843141 [Ha] <<<<
    # ---------------------------------------------
    #  [End]   Outer loop : optimize DM, fixed FODs
    # ---------------------------------------------
    # The calculation is converged!
    # [Final] CC-FLO-SIC energy = -230.235395086843 [Ha]


    #test2() 
    # Ensemble: P = (lewis1_benzene, lewis2_benzene)
    #>>>> CC-SIC cycle 4 EDFT = -227.237410855406665 [Ha] <<<<
    #>>>> CC-SIC cycle 4 ESIC = +2.981058447899157 [Ha] <<<<
    #>>>> CC-SIC cycle 4 EPZ  = -230.218469303305824 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -230.218469303306 [Ha]
    #Dipole moment(X, Y, Z, Debye): -0.00000,  0.00000,  0.00000
    #M : 1.0000000197838543 <S^2> : 9.891927277294599e-09
   
    # Ensemble: P = (linnett_benzene, linnett2_benzene)
    # Dipole moment(X, Y, Z, Debye):  0.00000, -0.00000, -0.00000
    # M : 1.000000139669166 <S^2> : 6.983458789022734e-08
    # elapsed time (UFLO.kernel) = +16.821850538253784 [s]
    # elapsed time (UFLO.kernel) = +17.667411088943481 [s]
    # >>>> CC-FLO-SIC cycle 4 EDFT = -227.237410855406893 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 4 ESIC = +2.981058447899148 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 4 EPZ  = -230.218469303305994 [Ha] <<<<
    # ---------------------------------------------
    #  [End]   Outer loop : optimize DM, fixed FODs
    # ---------------------------------------------
    # The calculation is converged!
    # [Final] CC-FLO-SIC energy = -230.218469303306 [Ha]



    # Ensemble: P = (lewis1_benzene, lewis1_benzene)
    #>>>> CC-SIC cycle 4 EDFT = -227.224733090804193 [Ha] <<<<
    #>>>> CC-SIC cycle 4 ESIC = +3.010075322753229 [Ha] <<<<
    #>>>> CC-SIC cycle 4 EPZ  = -230.234808413557431 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -230.234808413557 [Ha]
    #Dipole moment(X, Y, Z, Debye):  0.00037,  0.00000, -0.00000
    #M : 1.000000006969266 <S^2> : 3.484633026573647e-09

    # Ensemble: P = (lewis2_benzene, lewis1_benzene)
    #>>>> CC-SIC cycle 4 EDFT = -227.237410855407347 [Ha] <<<<
    #>>>> CC-SIC cycle 4 ESIC = +2.981058447899166 [Ha] <<<<
    #>>>> CC-SIC cycle 4 EPZ  = -230.218469303306449 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -230.218469303306 [Ha]
    #Dipole moment(X, Y, Z, Debye):  0.00000, -0.00000,  0.00000
    #M : 1.0000000197838543 <S^2> : 9.891927277294599e-09

    # Ensemble: P = (lewis2_benzene, lewis2_benzene)
    #>>>> CC-SIC cycle 4 EDFT = -227.224733090804023 [Ha] <<<<
    #>>>> CC-SIC cycle 4 ESIC = +3.010075322753231 [Ha] <<<<
    #>>>> CC-SIC cycle 4 EPZ  = -230.234808413557261 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -230.234808413557 [Ha]
    #Dipole moment(X, Y, Z, Debye): -0.00037, -0.00000,  0.00000
    #M : 1.000000006969259 <S^2> : 3.484629473859968e-09

    # pc0: test1(lewis1_benzene())
    #>>>> FLO-SIC cycle 5 EDFT = -229.506341296431003 [Ha] <<<<
    #>>>> FLO-SIC cycle 5 ESIC = +2.971818288556644 [Ha] <<<<
    #>>>> FLO-SIC cycle 5 EPZ  = -232.478159584987424 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -232.478159584987 [Ha]
    #Dipole moment(X, Y, Z, Debye):  0.00005,  0.00000, -0.00000
    #M : 1.0000000094336414 <S^2> : 4.716820711792025e-09

    # pc0: test1(lewis2_benzene())
    #>>>> FLO-SIC cycle 5 EDFT = -229.506341296431629 [Ha] <<<<
    #>>>> FLO-SIC cycle 5 ESIC = +2.971818288556626 [Ha] <<<<
    #>>>> FLO-SIC cycle 5 EPZ  = -232.478159584988418 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -232.478159584988 [Ha]
    #Dipole moment(X, Y, Z, Debye): -0.00005, -0.00000,  0.00000
    #M : 1.0000000094336272 <S^2> : 4.716813606364667e-09

    # pc0: test1(linnett_benzene())
    #>>>> FLO-SIC cycle 5 EDFT = -229.505909833962733 [Ha] <<<<
    #>>>> FLO-SIC cycle 5 ESIC = +2.973053045257611 [Ha] <<<<
    #>>>> FLO-SIC cycle 5 EPZ  = -232.478962879220234 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -232.47896287922 [Ha]
    #Dipole moment(X, Y, Z, Debye): -0.00000,  0.00000, -0.00000
    #M : 1.2261293256802688 <S^2> : 0.1258482808232877

    #test2()
    # pc0: Ensemble: P = (lewis1_benzene, lewis2_benzene)
    #>>>> CC-SIC cycle 4 EDFT = -229.519096871688077 [Ha] <<<<
    #>>>> CC-SIC cycle 4 ESIC = +2.942826542658226 [Ha] <<<<
    #>>>> CC-SIC cycle 4 EPZ  = -232.461923414346415 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] FLO-SIC energy = -232.461923414346 [Ha]
    #Dipole moment(X, Y, Z, Debye): -0.00000, -0.00000,  0.00000
    #M : 1.0000002104311312 <S^2> : 1.0521557669562753e-07

    # pc1: lewis1_benzene 
    #Dipole moment(X, Y, Z, Debye): -0.00023, -0.00000, -0.00000
    #M : 1.0000007537481397 <S^2> : 3.7687421183818515e-07
    #elapsed time (UFLO.kernel) = +32.033262729644775 [s]
    #>>>> CC-FLO-SIC cycle 5 EDFT = -230.002876474268760 [Ha] <<<<
    #>>>> CC-FLO-SIC cycle 5 ESIC = +3.008779908609469 [Ha] <<<<
    #>>>> CC-FLO-SIC cycle 5 EPZ  = -233.011656382878073 [Ha] <<<<
    #---------------------------------------------
    # [End]   Outer loop : optimize DM, fixed FODs
    #---------------------------------------------
    #The calculation is converged!
    #[Final] CC-FLO-SIC energy = -233.011656382878 [Ha]

    # pc1: lewis2_benzene 
    # Dipole moment(X, Y, Z, Debye):  0.00023, -0.00000, -0.00000
    # M : 1.0000007537481184 <S^2> : 3.768742011800441e-07
    # elapsed time (UFLO.kernel) = +31.840979337692261 [s]
    # >>>> CC-FLO-SIC cycle 5 EDFT = -230.002876474267737 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 5 ESIC = +3.008779908609483 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 5 EPZ  = -233.011656382877163 [Ha] <<<<
    # ---------------------------------------------
    #  [End]   Outer loop : optimize DM, fixed FODs
    # ---------------------------------------------
    # The calculation is converged!
    # [Final] CC-FLO-SIC energy = -233.011656382877 [Ha]

    # pc1: linnett_benzene 
    # Dipole moment(X, Y, Z, Debye): -0.00000, -0.00000,  0.00000
    # M : 1.2674165577381058 <S^2> : 0.15158618270717739
    # elapsed time (UFLO.kernel) = +31.322213888168335 [s]
    # >>>> CC-FLO-SIC cycle 5 EDFT = -230.001614071918652 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 5 ESIC = +3.011836785792930 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 5 EPZ  = -233.013450857711575 [Ha] <<<<
    # ---------------------------------------------
    #  [End]   Outer loop : optimize DM, fixed FODs
    # ---------------------------------------------
    # The calculation is converged!
    # [Final] CC-FLO-SIC energy = -233.013450857712 [Ha]

    # pc1: Ensemble: P =(lewis1_benzene, lewis2_benzene)
    # Dipole moment(X, Y, Z, Debye): -0.00000,  0.00000,  0.00000
    # M : 1.0000058474791862 <S^2> : 2.923748141370197e-06
    # elapsed time (UFLO.kernel) = +31.843395233154297 [s]
    # elapsed time (UFLO.kernel) = +31.309290647506714 [s]
    # >>>> CC-FLO-SIC cycle 4 EDFT = -230.018960859218964 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 4 ESIC = +2.973329269739009 [Ha] <<<<
    # >>>> CC-FLO-SIC cycle 4 EPZ  = -232.992290128958018 [Ha] <<<<
    # ---------------------------------------------
    #  [End]   Outer loop : optimize DM, fixed FODs
    # ---------------------------------------------
    # The calculation is converged!
    # [Final] CC-FLO-SIC energy = -232.992290128958 [Ha]

    #cc = (linnett_benzene, linnett2_benzene)
    #test3(cc)

    test4(lewis1_benzene) 
    test4(lewis2_benzene)
    test4(linnett_benzene)
