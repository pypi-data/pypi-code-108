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
from matplotlib.pyplot import *
from pyflosic2.ff.uff_params import UFF_params, UFF_key2idx
from pyflosic2 import parameters
from pyflosic2.atoms.bonds import Bonds
from pyflosic2.atoms.mmtypes import MMTypes
# Note: Unit conversion  
KCAL_TO_KJ = 4.1868
DEG_TO_RAD = numpy.pi/180

# UFF energy 
# E_UFF = E_R + E_theta + E_phi + E_omega + E_vdw (+ E_el)

# Ref.:
# [1] https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fjcc.24309&file=jcc24309-sup-0001-suppinfo.pdf
# [2] https://github.com/peteboyd/lammps_interface/blob/master/lammps_interface/uff.py
# [3] https://documentation.samson-connect.net/uff/
# [4] https://documentation.samson-connect.net/im-uff/
# [5] https://github.com/openbabel/openbabel/blob/08e23f39b0cc39b4eebd937a5a2ffc1a7bac3e1b/src/forcefields/forcefielduff.cpp
# [6] https://github.com/openbabel/openbabel/blob/08e23f39b0cc39b4eebd937a5a2ffc1a7bac3e1b/data/UFF.prm
# [7] https://github.com/DCoupry/autografs/blob/master/autografs/data/uff/rappe.csv
# [8] https://github.com/DCoupry/autografs/blob/master/autografs/utils/mmanalysis.py
# obenergy -ff UFF *xyz 
# https://pubs.acs.org/doi/pdf/10.1021/ja00051a040
# http://www.cosmologic-services.de/downloads/TM72-documentation/DOKse17.html

# Extensions 
# https://team.inria.fr/nano-d/files/2015/04/jaillet2017im-uff.pdf

class cls():
    """
        cls class 
        ---------
        Magically transforms a function 
        to a class instance. 
    """
    def __init__(self,f):
        self.f = f 
        self.rv = None 
        self.count = 0 

    def __call__(self,*args,**kwargs):
        self.count += 1 
        print('Function name: {}'.format(self.f.__qualname__))
        print('Doc string: {}'.format(self.f.__doc__))
        print('Count: {}'.format(self.count))
        print('Input: {} {}'.format(*args,**kwargs))
        self.rv = self.f(*args,**kwargs)
        for key in list(self.rv.keys()):
            setattr(self,key,self.rv[key])
        print('Output: {}'.format(self.rv))
        return self.rv

def sym2co(sym): 
    """
        Get coordination (co) from MMTypes 
        ----------------------------------
    """
    if len(sym) > 2:
        co = sym[2]
        if co == 'R': 
            co = 2 
        else: 
            co = int(co)
    else:
        co = int(1)
    return co 
    

def r_ij(r_i, r_j, sym_i, sym_j, n_ij, lam=0.1332):
    """ 
        Bond length (as defined by UFF) 
        -------------------------------
    """
    # BO   ... bond order correction
    # n_ij ... bond order, e.g., N2 BO = 3 
    # EN   ... electron negativity correction
    chi_i = UFF_params[sym_i][UFF_key2idx['Xi']]
    chi_j = UFF_params[sym_j][UFF_key2idx['Xi']]
    r_BO = -1 * lam * (r_i + r_j) * numpy.log(n_ij)
    r_EN = r_i * r_j * (numpy.sqrt(chi_i) - numpy.sqrt(chi_j)) ** (2.) / (chi_i * r_i + chi_j * r_j)
    # Note: correction 
    r_ij_tmp = r_i + r_j + r_BO - r_EN
    return r_ij_tmp

def r_ik(r_ij, r_jk, theta0_j):
    """
        Bond length for (i,k) in E_angle (e.g., E_theta) 
        ------------------------------------------------
    """
    r_ik_tmp = numpy.sqrt(r_ij**(2.)+r_jk**(2.)-2*r_ij*r_jk*numpy.cos(theta0_j))
    return r_ik_tmp

def k_ij(r_i, r_j, sym_i, sym_j, n_ij):
    """ 
        Calculate force constant for E_Bond (e.g., E_R_harmonic) 
        --------------------------------------------------------
    """
    Z_i = UFF_params[sym_i][UFF_key2idx['Z1']]
    Z_j = UFF_params[sym_j][UFF_key2idx['Z1']]
    return 664.12 * Z_i * Z_j / r_ij(r_i=r_i, r_j=r_j, sym_i=sym_i, sym_j=sym_j, n_ij=n_ij) ** (3.)

def r(r_i, r_j):
    """ 
        Norm of the position vector
    """
    return numpy.linalg.norm(r_i - r_j)

def E_R_harmonic(R_i, R_j, sym_i, sym_j, n_ij, verbose=3):
    """ 
        Bond stretch: harmonic expression 
        ---------------------------------
        Note: alias E_Bond = E_R()   
    
        Input 
        ------
        R_i, R_j    : numpy.array, nuclei positions 
        sym_i, sym_j: str(), MMTypes 
        n_ij        : float(), bond order between R_i and R_j 

    """
    if n_ij >= 1:
        r_i = UFF_params[sym_i][UFF_key2idx['r1']]
        r_j = UFF_params[sym_j][UFF_key2idx['r1']]
        rab = r(R_i, R_j) 
        r0 = r_ij(r_i=r_i, r_j=r_j, sym_i=sym_i, sym_j=sym_j, n_ij=n_ij)
        delta = rab - r0
        # kb ... force constant for E_Bond (index -> b) 
        #        energy units 
        kb = 0.5 * k_ij(r_i, r_j, sym_i, sym_j, n_ij) * KCAL_TO_KJ
        e = kb * (delta) ** 2
        if verbose >3: 
            # N_1   N_1    3.00   1.000      1.120     6404.265     -0.120     92.234
            tmp = [sym_i,sym_j,n_ij,rab,r0,kb,delta,e]
            print('E_bond: {:>3s} {:>3s} {:10.5f} {:10.5f} {:10.5f} {:10.5f} {:10.5f} {:10.5f}'.format(*tmp))
    else: 
        e = 0
        #if verbose >3: 
        #    print(f'E_bond: {e}')
    return e 

def E_R_morse(R_i, R_j, sym_i, sym_j, n_ij, D_ij=70):
    """" 
        Bond stretch: Morse expression 
    """
    r_i = UFF_params[sym_i][UFF_key2idx['r1']]
    r_j = UFF_params[sym_j][UFF_key2idx['r1']]
    alpha = (k_ij(r_i, r_j, sym_i, sym_j, n_ij) / (2. * D_ij)) ** (1 / 2.)
    return D_ij * (numpy.exp(-1 * alpha * (r(R_i, R_j) - r_ij(r_i=r_i, r_j=r_j, sym_i=sym_i, sym_j=sym_j, n_ij=n_ij))) - 1) ** (2.)

def theta(R_i, R_j, R_k):
    """ 
        Angle between R_i, R_j, R_k 
        ---------------------------
        Used by E_theta. 

        Input 
        -----
        R_i, R_j, R_k       : numpy.array, nuclei positions 
    """
    ba = R_j - R_i
    bc = R_j - R_k
    cosine_angle = numpy.dot(ba, bc) / (numpy.linalg.norm(ba) * numpy.linalg.norm(bc))
    angle = numpy.arccos(cosine_angle)
    return numpy.degrees(angle)

def k_ijk(r_i, r_j, r_k, sym_i, sym_j, sym_k, n_ij, n_jk):
    """
        Calculate force constant for E_theta
        ------------------------------------
        Alias ka = k_ijk() 

        Input
        -----
        r_i, r_j, r_k       : UFF param 
        sym_i, sym_j, sym_j : str(), MMTypes
        n_ij, n_jk          : float(), bond order between R_i/R_j and R_j/R_k
    """
    Z_i = UFF_params[sym_i][UFF_key2idx['Z1']]
    Z_k = UFF_params[sym_k][UFF_key2idx['Z1']]
    theta0_j = UFF_params[sym_j][UFF_key2idx['theta0']]*DEG_TO_RAD
    r_ij_tmp = r_ij(r_i=r_i, r_j=r_j, sym_i=sym_i, sym_j=sym_j, n_ij=n_ij)
    r_jk_tmp = r_ij(r_i=r_j, r_j=r_k, sym_i=sym_j, sym_j=sym_k, n_ij=n_jk)
    r_ik_tmp = r_ik(r_ij=r_ij_tmp, r_jk=r_jk_tmp, theta0_j=theta0_j)
    beta=664.12 * KCAL_TO_KJ * Z_i*Z_k/(r_ik_tmp**(5.)) 
    cos_theta =numpy.cos(theta0_j)
    k_ijk = beta*(3.0*r_ij_tmp*r_jk_tmp*(1-cos_theta**(2.))-r_ik_tmp**(2.)*cos_theta)
    return k_ijk

def E_theta(R_i, R_j, R_k, sym_i, sym_j, sym_k, n_ij, n_jk,verbose=3):
    """
        Note: alternative name E_angle 
        ------------------------------
        Alias E_Angle = E_theta() 

        Input 
        -----
        R_i, R_j, R_k       : numpy.array, nuclei positions 
        sym_i, sym_j, sym_j : str(), MMTypes 
        n_ij                : float(), bond order between R_i and R_j 
    """
    # https://github.com/openbabel/openbabel/blob/08e23f39b0cc39b4eebd937a5a2ffc1a7bac3e1b/src/forcefields/forcefielduff.cpp#L1163 
 
    r_i = UFF_params[sym_i][UFF_key2idx['r1']]
    r_j = UFF_params[sym_j][UFF_key2idx['r1']]
    r_k = UFF_params[sym_k][UFF_key2idx['r1']]
    theta0_j = UFF_params[sym_j][UFF_key2idx['theta0']]*DEG_TO_RAD
    # "real" angle 
    th = theta(R_i, R_j, R_k)
    # https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fjcc.24309&file=jcc24309-sup-0001-suppinfo.pdf
    # see Eq(7,8) 
    # https://github.com/openbabel/openbabel/blob/master/src/forcefields/forcefielduff.cpp#L1171
    n = 0
    sp = sym2co(sym_j)
    if sp == 1: 
        # linear case 
        #theta0_j = 180.0 *DEG_TO_RAD 
        n = 1 
    if sp == 2:
        # sp2
        #theta0_j = 120.0 *DEG_TO_RAD
        n = 3
    if sp in [4,5,6,7]:
        # sq. planar or octahedral
        #theta0_j = 90.0 *DEG_TO_RAD 
        n = 4
    if sp == 3: 
        # sp3 
        #theta0_j = 109.5 *DEG_TO_RAD 
        n = 0 
    # constants 
    C2 = 1/(4*numpy.sin(theta0_j)**2)
    C1 = -4*C2*numpy.cos(theta0_j)
    C0 = C2*(2*numpy.cos(theta0_j)**(2.)+1)
    th *= DEG_TO_RAD
    # ka ... force constant for angle term 
    ka = k_ijk(r_i=r_i, r_j=r_j, r_k=r_k, sym_i=sym_i, sym_j=sym_j, sym_k=sym_k, n_ij=n_ij, n_jk=n_jk)
    #if n != 0:
    if sp in [2,4,6]:
        ka *= 1/n**2 
    # https://github.com/openbabel/openbabel/blob/08e23f39b0cc39b4eebd937a5a2ffc1a7bac3e1b/src/forcefields/forcefielduff.cpp#L168
    if sp == 1: 
        e = ka*(1.0 + numpy.cos(th))
    if sp in [2,4,6]: 
        e = ka * (1 - numpy.cos(n*th)) + numpy.exp(-20.0*(th - theta0_j + 0.25))
    if sp not in [1,2,4,6]:
        # General Case (e.g., sp3) 
        e = ka*(C0+C1*numpy.cos(th)+C2*(2*numpy.cos(th)**2.-1.0))
    if verbose > 3:
        # obenergy/pybel format :
        #H_    O_3   H_    104.480     1.824      504.509      0.000      0.000
        #tmp = [sym_i,sym_j,sym_k,th*1/DEG_TO_RAD,theta0_j,ka,e,n]
        tmp = [sym_i,sym_j,sym_k,th*1/DEG_TO_RAD,theta0_j*1/DEG_TO_RAD,ka,e,n]
        print('E_angle {:>3s} {:>3s} {:>3s} {:10.5f} {:10.5f} {:10.5f} {:10.5f} {:10.0f}'.format(*tmp))
    return e 

def tor_ijkl(R_i,R_j,R_k,R_l):
    """
        Calculate torsion angle (tor) 
        -----------------------------
        Calculate (proper) torsion angle from 4 given coordinates. 
        Note: The torsion angle can be formulated in various ways. 
        We used here the definition from openbabel. 

        Input
        -----
        R_i, R_j, R_k, R_l : numpy.array, nuclei positions 
    """
    ab = (R_j - R_i) 
    bc = (R_k - R_j)
    cd = (R_l - R_k)
    abbc = numpy.cross(ab,bc) 
    norm_abbc = numpy.linalg.norm(abbc) 
    bccd = numpy.cross(bc,cd)
    norm_bccd = numpy.linalg.norm(bccd) 
    dotabbcbccd = numpy.dot(abbc,bccd)
    if not numpy.isclose(dotabbcbccd,0) and not numpy.isclose(norm_abbc*norm_bccd,0): 
        normed_dotabbcbccd = dotabbcbccd/(norm_abbc*norm_bccd)
        # if normed_dotabbcbccd >= -1.0000000000000002
        # we get nan
        normed_dotabbcbccd = numpy.round(normed_dotabbcbccd,10)
        # print(f'normed_dotabbcbccd : {normed_dotabbcbccd}')
        tor = numpy.arccos(normed_dotabbcbccd)
    if numpy.isclose(dotabbcbccd,0) or numpy.isclose(norm_abbc*norm_bccd,0):
        tor = 0
    if numpy.isclose(dotabbcbccd,0) or not numpy.isfinite(tor):
        tor = 1.0e-3
    if dotabbcbccd > 0:
       tor *= -1 
    return tor

def E_phi(R_i,R_j,R_k,R_l,sym_i,sym_j,sym_k,sym_l,n_jk,verbose=3):
    """
        E_phi
        Note: alternative name E_Torsion = E_phi() 

        Input 
        -----
        R_i, R_j, R_k, Rl          : numpy.array, nuclei positions 
        sym_i, sym_j, sym_j, sym_l : str(), MMTypes 
        n_jk                       : float(), bond order between R_j and R_k
    """
    # calculate "real" torsion angle 
    tor = tor_ijkl(R_i,R_j,R_k,R_l)
    phi0 = 0
    n = 0
    V = 0
    if sym2co(sym_j) == 3 and sym2co(sym_k) == 3:
        # sp3 - sp3  
        phi0 = 60.0 
        n = 3 
        vi = UFF_params[sym_j][UFF_key2idx['V1']]
        vj = UFF_params[sym_k][UFF_key2idx['V1']]
        # 8 -> O 
        if sym_j[0:1] == 'O': 
            vi = 2.0
            n = 2
            phi0 = 90.0 
        if sym_k[0:1] == 'O':
            vj = 2.0
            n = 2
            phi0 = 90.0
        
        # 16 -> S, 34 -> Se, 52 -> Te, 84 -> Po 
        if sym_j[0:1] in ['S_','Se','Te','Po']: 
            vi = 6.8 
            n = 2
            phi0 = 90. 
        # 16 -> S, 34 -> Se, 52 -> Te, 84 -> Po 
        if sym_k[0:1] in ['S_','Se','Te','Po']:
            vj = 6.8
            n = 2
            phi0 = 90.
        V = 0.5 * KCAL_TO_KJ * numpy.sqrt(vi * vj)
    if sym2co(sym_j) == 2 and sym2co(sym_k) == 2: 
        # sp2 - sp2
        phi0 = 180.0 
        Ui = UFF_params[sym_j][UFF_key2idx['Uj']]
        Uj = UFF_params[sym_k][UFF_key2idx['Uj']]
        n = 2 
        V = 0.5 * KCAL_TO_KJ * 5.0 * np.sqrt(Ui*Uj) *(1.0 + 4.18 * np.log(n_jk))
    if sym2co(sym_j) == 2 and sym2co(sym_k) == 3 or sym2co(sym_j) == 3 and sym2co(sym_k) == 2: 
        # sp3 - sp2 or sp2 - sp3 
        phi0 = 0.0
        n = 6
        V = 0.5 * KCAL_TO_KJ * 1.0 
        if sym_j[0:1] in ['S_','Se','Te','Po'] or sym_k[0:1] in ['S_','Se','Te','Po']: 
            n = 2.0 
            phi0 = 90.0
        if sym_j[0:1] in ['O_','S_','Se','Te','Po'] or sym_k[0:1] in ['O_','S_','Se','Te','Po']:
            n = 2.0
            phi0 = 90.0


    cosNPhi0 =  numpy.cos(n * DEG_TO_RAD * phi0)
    cosine = numpy.cos(tor * n) 
    e = V * (1.0 - cosNPhi0*cosine)
    if verbose > 3: 
        print(f'E_Phi {sym_i} {sym_j} {sym_k} {sym_l}  {tor*1/DEG_TO_RAD} {V} {e}')
    return e  

def E_vdw(R_i,R_j,sym_i,sym_j,n_ij,Rcut_vdw_min=4,verbose=3):
    """
        E_vdw 
        -----
        Van-der-Waals/Dispersion energy. 
        Alias E_vdW = E_vdw() 

        Input 
        ------
        R_i, R_j      : numpy.array, nuclei positions 
        sym_i, sym_j  : str(), MMTypes 
        n_ij          : float(), bond order between R_i and R_j 
        R_cut_vdw_min : float(), minmal cutoff parameter 
        verbose       : verbosity 

    """
    ka = UFF_params[sym_i][UFF_key2idx['D1']]
    kb = UFF_params[sym_j][UFF_key2idx['D1']]
    # geometric combination rule for depth well 
    kab = numpy.sqrt(ka * kb) * KCAL_TO_KJ 
    Ra = UFF_params[sym_i][UFF_key2idx['x1']]
    Rb = UFF_params[sym_j][UFF_key2idx['x1']]
    # geometric combination rule for distance 
    kaSquared =Ra * Rb 
    # Alternative combination rule 
    #  (1/2*(Ra+Rb))**2. 
    #print(Ra * Rb, (1/2*(Ra+Rb))**2.)
    rab = r(R_i,R_j)
    rab = rab
    rabSquared = rab**2 
    # Tested other cutoffs 
    if rabSquared > Rcut_vdw_min and kaSquared / rabSquared < Rcut_vdw_min/2.:
    #if rabSquared > Rcut_vdw_min and 2*kaSquared < Rcut_vdw_min*rabSquared:
    #if kaSquared / rabSquared < 2.5:
    #if rab > numpy.sqrt(Ra+Rb):
    #if rabSquared > Rcut_vdw_min and kaSquared / rabSquared > 1:
    #if rab > 2.4:
    #if kaSquared > Rcut_vdw_min:
    #if kaSquared/rabSquared > 1:
    #if rab > 0.5*(Ra + Rb): 
    #if 1.1*rab > (Ra + Rb):
        term6 = (kaSquared / rabSquared)**3 
        term12 = term6**2 
        e = kab * ((term12) - (2.0 * term6))
        #print(kaSquared,rabSquared,kaSquared / rabSquared,rab,numpy.sqrt(Ra+Rb),Rcut_vdw_min,n_ij,e)
    else: 
        e = 0
    if verbose > 3:
        # obenergy/pybel format :
        #N_3   N_3      0.016     0.289     1.236
        print(f'E_vdw : {sym_i} {sym_j} {rab} {kab} {e}')
    return e 

def omega_ijkl(R_i,R_j,R_k,R_l): 
    """
        Get angle omega for E_omega 
        ---------------------------
        Calculate inproper torsion/out-of-plane (OOP) 
        from for coordinates. 
        Used by E_omega. 

        Input
        -----
        R_i, R_j, R_k, R_l : numpy.array, nuclei positions
    """
    # This somehow does not work 
    #ac = R_i - R_k
    #bc = R_j - R_k
    #cd = R_k - R_l

    #n = numpy.cross(bc,cd)
    #dp = numpy.dot(n,ac)/(numpy.linalg.norm(n)*numpy.linalg.norm(ac))
    #if dp < -0.999999:
    #    dp = -0.9999999
    #if dp > 0.9999999:
    #    dp = 0.9999999
    #dp2 = numpy.arccos(dp)/DEG_TO_RAD 
    #omega = (90.0 - dp2)*DEG_TO_RAD
    
    # https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fjcc.24309&file=jcc24309-sup-0001-suppinfo.pdf
    # see 6.7.1 
    ba = R_j - R_i 
    cb = R_k - R_j 
    db = R_l - R_j
    
    ndb = numpy.linalg.norm(db)
    dp1 = numpy.cross(ba,cb)
    ndp1 = numpy.linalg.norm(dp1)
    if not numpy.allclose(dp1,0) and not numpy.allclose(ndp1,0):
        dp2 = dp1/ndp1
    if numpy.allclose(dp1,0) or numpy.allclose(ndp1,0):
        dp2 = numpy.zeros_like(dp1)
    dp3 = numpy.dot(db/ndb,dp2) 
    # catch numerical noise 
    if dp3 < -0.999999:
        dp3 = -0.9999999
    if dp3 > 0.9999999:
        dp3 = 0.9999999
    omega = numpy.pi/2 - numpy.arccos(dp3)
    # check if we have a number (not nan or inf) 
    if not numpy.isfinite(omega): 
        omega = 0
    return omega

def E_omega(R_i,R_j,R_k,R_l,sym_i,sym_j,sym_k,sym_l,n_jk,verbose=3):
    """
        E_omega 
        -------
        Calculate improper torsion/out-of-plane (OOP) energy. 
        Note: alternative name E_OOP  = E_omega() 

        Input 
        ------
        R_i, R_j, R_k, R_l          : numpy.array, nuclei positions 
        sym_i, sym_j, sym_k, sym_l  : str(), MMTypes 
        n_jk          : float(), bond order between R_j and R_k
        verbose       : verbosity 

        Variables
        --------
        koop : float(), force constant for E_omega/E_OOP 

        Tests (needed) : 
            - ['C_R','C_2','N_3','N_2','N_R','O_2','O_R']
            - 'O_2' 
            - ['P_3+3','As3+3','Sb3+3','Bi3+3']
    """
    c0 = 0
    c1 = 0
    c2 = 0
    koop = 0
    if sym_j in ['C_R','C_2','N_3','N_2','N_R','O_2','O_R']:
        c0 =  1.0
        c1 = -1.0
        c2 =  0.0 
        koop = 6 * KCAL_TO_KJ
        if sym_i == 'O_2' or sym_k == 'O_2' or sym_l == 'O_2':
            c0 = 1 
            c1 = -1 
            c2 = 0 
            koop = 50 * KCAL_TO_KJ 
    if sym_j in ['P_3+3','As3+3','Sb3+3','Bi3+3']:
        if sym_j == 'P_3+3':
            phi = 84.4339 * DEG_TO_RAD
        if sym_j == 'As3+3':
            phi = 86.9735 * DEG_TO_RAD
        if sym_j == 'Sb3+3':
            phi = 87.7047 * DEG_TO_RAD
        if sym_j == 'Bi3+3':
            phi = 90.0 * DEG_TO_RAD 
        c1 = -4.0 * numpy.cos(phi)
        c2 = 1.0 
        c0 =  -1.0*c1 * numpy.cos(phi) + c2*numpy.cos(2.0*phi)
        koop = 22.0 * KCAL_TO_KJ
    koop /= 3 
    omega = omega_ijkl(R_i=R_i,R_j=R_j,R_k=R_k,R_l=R_l)
    e = koop * (c0 + c1 * numpy.cos(omega) + c2 * numpy.cos(2.0*omega))
    if verbose > 3:
        tmp = [sym_i,sym_j,sym_k,sym_l,omega/DEG_TO_RAD,koop,e]
        print('E_omega {:>3s} {:>3s} {:>3s} {:>3s}  {:10.5f} {:10.5f} {:10.5f}'.format(*tmp))
    return e 

@cls 
def uff_energy(positions,bo,mmtypes,verbose=3):
    """
        UFF: energy calculation 
        -----------------------
        E_UFF = E_R + E_theta + E_phi + E_omega + E_vdw + (E_el)
        E_el is currently not implemented. 
    """
    print(f"debug:{positions} {mmtypes}")
    E_Bond = 0
    E_vdW = 0
    E_Angle = 0
    E_Torsion = 0
    E_OOP = 0 
    # E_Bond 
    for i, (sym_i, R_i) in enumerate(zip(mmtypes, positions)):
        for j, (sym_j, R_j) in enumerate(zip(mmtypes, positions)):
            if j > i:
                E_Bond += E_R_harmonic(R_i=R_i, R_j=R_j, sym_i=sym_i, sym_j=sym_j, n_ij=bo[i,j],verbose=verbose)
                E_vdW += E_vdw(R_i=R_i, R_j=R_j, sym_i=sym_i, sym_j=sym_j, n_ij=bo[i,j])
    # E_Angle
    for i, (sym_i, R_i) in enumerate(zip(mmtypes, positions)):
        for j, (sym_j, R_j) in enumerate(zip(mmtypes, positions)):
            if j != i:
                n_ij = bo[i,j]
                for k, (sym_k, R_k) in enumerate(zip(mmtypes, positions)):
                    n_jk = bo[j,k]
                    if k != i and k != j and n_ij > 0 and n_jk > 0: 
                        E_Angle += E_theta(R_i=R_i, R_j=R_j, R_k=R_k, sym_i=sym_i, sym_j=sym_j, sym_k=sym_k, n_ij=n_ij, n_jk=n_jk,verbose=verbose)
    # Note: We currently double count ijk(2,0,1) == ijk(1,0,2)
    E_Angle *=1/2.
    # E_Torsion 
    for i, (sym_i, R_i) in enumerate(zip(mmtypes, positions)):
        for j, (sym_j, R_j) in enumerate(zip(mmtypes, positions)):
            if j != i:
                n_ij = bo[i,j]
                for k, (sym_k, R_k) in enumerate(zip(mmtypes, positions)):
                    n_jk = bo[j,k]
                    if k != i and k != j and n_ij > 0 and n_jk > 0:
                        for l, (sym_l, R_l) in enumerate(zip(mmtypes, positions)):
                            n_kl = bo[k,l]
                            if l != k and l != j and l != i and n_ij > 0 and n_jk > 0 and n_kl >0:
                                E_Torsion +=  E_phi(R_i=R_i, R_j=R_j, R_k=R_k, R_l=R_l,sym_i=sym_i, sym_j=sym_j, sym_k=sym_k, sym_l=sym_l, n_jk=n_jk, verbose=verbose)
    # Note: We currently double count
    E_Torsion *=1/2.
    # E_OOP 
    for i, (sym_i, R_i) in enumerate(zip(mmtypes, positions)):
        for j, (sym_j, R_j) in enumerate(zip(mmtypes, positions)):
            if j != i:
                for k, (sym_k, R_k) in enumerate(zip(mmtypes, positions)):
                    if k != j and k != i:
                        for l, (sym_l, R_l) in enumerate(zip(mmtypes, positions)):
                            if l != k and k != j and k != i:
                                # j is bounded to i,k and l 
                                if bo[j,i] > 0 and bo[j,k] > 0 and bo[j,l] > 0:
                                    E_OOP += E_omega(R_i=R_i, R_j=R_j, R_k=R_k, R_l=R_l,sym_i=sym_i, sym_j=sym_j, sym_k=sym_k, sym_l=sym_l, n_jk=n_jk, verbose=verbose)
    # Note: We currently double count 
    E_OOP *=1/2.
    E_tot = E_Bond + E_Angle + E_Torsion + E_OOP + E_vdW 
    return {'E_Bond' : E_Bond, 'E_vdW': E_vdW, 'E_Angle' : E_Angle, 'E_Torsion': E_Torsion, 'E_OOP' : E_OOP, 'E_tot' : E_tot}

# Class definition 
class UFF(): 
    """
        UFF class 
        ---------
        Calculate UFF energy for atoms. 
        Using uff_energy() function. 
    """
    def __init__(self,atoms,bo,mmtypes,verbose=3):
        self.atoms = atoms 
        self.bo = bo
        self.mmtypes = mmtypes 
        self.verbose = verbose 

    def kernel(self):
        """
            Kernel function 
        """
        # rv  ... return value 
        # dct ... dictionary 
        rv_dct = uff_energy(self.atoms.positions,
                            self.bo,
                            self.mmtypes,
                            verbose=self.verbose) 
        # Update class instance with rv_dct values 
        for k in list(rv_dct.keys()):
            setattr(self,k,rv_dct[k])

# Predefined examples 
def H2O_dist1():
    # E_Bond + E_Angle 
    O1 = [0.000000000000000,  0.000000000000000, 0.117300000000000] 
    H1 = [1.000000000000000,  0.757200000000000,-0.469200000000000]
    H2 = [0.000000000000000, -0.757200000000000,-0.469200000000000]
    a = Atoms(['O']+['H']*2,[O1,H1,H2])
    write_xyz(a,'{}.xyz'.format('H2O_dist'))
    bo =  numpy.array([[0., 1., 1.],
                      [1., 0., 0.],
                      [1., 0., 0.]])
    mmtypes = ['O_3','H_','H_']
    return a, bo, mmtypes 

def H2O_dist2():
    # E_Bond + E_Angle 
    O1 = [0.000000000000000,  0.000000000000000, 0.117300000000000]
    H1 = [1.000000000000000,  0.757200000000000,-0.469200000000000]
    H2 = [-1.000000000000000, -0.757200000000000,-0.469200000000000]
    a = Atoms(['O']+['H']*2,[O1,H1,H2])
    write_xyz(a,'{}.xyz'.format('H2O_dist'))
    bo =  numpy.array([[0., 1., 1.],
                      [1., 0., 0.],
                      [1., 0., 0.]])
    mmtypes = ['O_3','H_','H_']
    return a, bo, mmtypes

def test_knight_valley(f_name='C6H6'):
    """
        Class example for PyFLOSIC2 systems 
    """
    p = parameters()
    # Contains: Nuclei + FODs 
    s = eval(f_name)() 
    b = Bonds(p,s)
    b.kernel(eps_val=1.8,eps_cor=1/3.)
    # Bond order 
    bo = b.bo
    print(f'Bonder order matrix (bo) \n {bo}')
    # MMTypes 
    mm = MMTypes(p=p,s=s,bo=bo)
    mmtypes = mm.kernel()
    #if f_name == 'COH2':
    #    # for initial comparision 
    #    # use the ones provided by openbabel 
    #    mm.mmtypes = ['O_2','C_2','H_','H_']
    print(f'MMTypes: {mmtypes}')
    # UFF as class 
    uff = UFF(s,bo,mmtypes,verbose=4) # SS: HANS 
    uff.kernel()
    print(vars(uff))
    check(f_name,uff)

def test_uff_energy():
    """
        "Function" example 
    """
    a, bo, mmtypes = H2O_dist1()
    # use the function 
    res = uff_energy(a.positions, bo, mmtypes)
    print(res)
    # Our function is yet also a class instance
    # This is the power of pure magic! 
    print(uff_energy,type(uff_energy),uff_energy.count)
    check('H2O_dist1',uff_energy) 
    
def test_C2H6():
    # Example to test:  
    # E_Bond + E_Angle + E_Torsion + E_vdW 
    C1 = [-0.75600000, 0.00000000, 0.00000000]    
    C2 = [ 0.75600000, 0.00000000,-0.00000000]
    H1 = [-1.14040000, 0.65860000, 0.78450000]
    H2 = [-1.14040000, 0.35010000,-0.96260000]
    H3 = [-1.14050000,-1.00870000, 0.17810000]
    H4 = [ 1.14040000,-1.02041275,-0.08903142]
    H5 = [ 1.14050000, 0.43310216, 0.92823371]
    H6 = [ 1.14040000, 0.58731059,-0.83920229]
    p = parameters()
    a = Atoms(['C']*2+['H']*6,[C1,C2,H1,H2,H3,H4,H5,H6])
    mmtypes = ['C_3']*2 + ['H_']*6 
    for s in ['C_3']*2+['H_']*6: 
        print(sym2co(s))
    wf= WORKFLOW(a,mode='unrestricted')
    s = wf.p.atoms
    b = Bonds(p,s)
    b.kernel(eps_val=1.8,eps_cor=1/3.)
    bo = b.bo
    print(f'Bonder order matrix (bo) \n\n {bo}')
    mm = MMTypes(p=p,s=s,bo=bo)
    mmtypes = mm.kernel()
    print(f'MMTypes: {mmtypes}')
    uff = UFF(s,bo,mmtypes) # SS
    uff.kernel()
    print(vars(uff))
    check('C2H6',uff)

def test_KT_C6H6():
    """
        KT_C6H6 example
    """
    p = parameters() 
    dz = 0.09997599
    sym = ['C']*6+['H']*6
    p0 = [-1.2131,-0.6884,0.0]
    p1 = [-1.2028,0.7064,0.0001]
    p2 = [-0.00839783,-1.39371265,0.0+dz]
    p3 = [0.0104,1.3948,-0.0001]
    p4 = [1.2028,-0.7063,0.0]
    p5 = [1.2131,0.6884,0.0]
    p6 = [-2.1577,-1.2244,0.0]
    p7 = [-2.1393,1.2564,0.0001]
    p8 = [-0.0184,-2.4809,-0.0001]
    p9 = [0.0184,2.4808,0.0]
    p10 = [2.1394,-1.2563,0.0001]
    p11 = [2.1577,1.2245,0.0]
    pos = [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11]
    charge = 0
    spin = 0
    a = Atoms(sym,pos,charge=charge,spin=spin)
    s = a 
    wf= WORKFLOW(a,mode='unrestricted')
    s = wf.p.atoms
    b = Bonds(p,s)
    b.kernel(eps_val=1.8,eps_cor=1/3.)
    bo = b.bo
    print(bo)
    # insert a LDQ bond order 
    # openbabel seems to adjust Lewis automatically to LDQ 
    # this influences E_Bond, E_Torsion 
    # we want to control this externally via bo 
    bo = numpy.array([[0. , 1.5, 1.5, 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 0. ],
                      [1.5, 0. , 0. , 1.5, 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. ],
                      [1.5, 0. , 0. , 0. , 1.5, 0. , 0. , 0. , 1. , 0. , 0. , 0. ],
                      [0. , 1.5, 0. , 0. , 0. , 1.5, 0. , 0. , 0. , 1. , 0. , 0. ],
                      [0. , 0. , 1.5, 0. , 0. , 1.5, 0. , 0. , 0. , 0. , 1. , 0. ],
                      [0. , 0. , 0. , 1.5, 1.5, 0. , 0. , 0. , 0. , 0. , 0. , 1. ],
                      [1. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
                      [0. , 1. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
                      [0. , 0. , 1. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
                      [0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
                      [0. , 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ],
                      [0. , 0. , 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 0. , 0. ]])
    b.bo = bo 
    print(f'Bonder order matrix (bo) \n {bo}')
    mm = MMTypes(p=p,s=s,bo=bo)
    mmtypes = mm.kernel()
    print(f'MMTypes: {mmtypes}')
    uff = UFF(s,bo,mmtypes)
    uff.kernel()
    check('KT_C6H6',uff)

# cmd: obenergy -ff UFF -v C6H6.xyz 
#      python3.7 ob.py C6H6.xyz 
# openbabel: 3.1.0
ref_openbabel = {'C6H6' : {'E_Bond' : 3.019,
                           'E_Angle': 0.121,
                           'E_Torsion' : 0.000,
                           'E_OOP' :  0.000,
                           'E_vdW'  : 41.502,
                           'E_tot' : 44.642,
                           'mmtypes'  : ["C_R","C_R","C_R","C_R","C_R","C_R","H_","H_","H_","H_","H_","H_"]},
                'CH4' :  {'E_Bond' : 2.159,
                          'E_vdW'  : 0, 
                          'E_tot'  : 2.159,
                          'mmtypes': ["C_3","H_","H_","H_","H_"]},
                'H2O' :  {'E_Bond' : 4.946,
                          'E_Angle': 0,
                          'E_vdW'  : 0,
                          'E_tot'  : 4.946,
                          'mmtypes': ["O_3","H_","H_"]},
                'COH2':  {'E_Bond' : 26.445,
                          'E_Angle': 0.020,
                          'E_vdW'  : 0,
                          'E_tot'  : 26.465,
                          'mmtypes': ["O_2","C_2","H_","H_"]},
                'H2O_dist1' : {'E_Bond'    : 367.222,
                               'E_Angle'   : 1.621,
                               'E_Torsion' : 0,
                               'E_vdW'     : 0,
                               'E_tot'     : 368.84299999999996,
                               'mmtypes'   : ["O_3","H_","H_"]},
                'C2H6' : {'E_Bond'    :  1.962,
                          'E_Angle'   :  0.907,
                          'E_Torsion' : 68.153,
                          'E_vdW'     :  3.150,
                          'E_tot'     : 74.17200000000001,
                          'mmtypes'   : []},
                'KT_C6H6': {'E_Bond'   :  3.561, 
                            'E_Angle'  :  0.231,
                            'E_Torsion': 20.975,
                            'E_OOP'    :  0.813,
                            'E_vdW'    : 41.448,
                            'E_tot'    : 67.028,
                            'mmtypes'  : ["C_R","C_R","C_R","C_R","C_R","C_R","H_","H_","H_","H_","H_","H_"]}}


def check(key,uff,ref=ref_openbabel): 
    """
        Compare rests to reference values  
        ---------------------------------

        Input
        -----
        key : str(), name of system/ entry in ref dct 
        uff : UFF(), instance of UFF 
        ref : dct(), ref dct 
    """
    for e in ref[key].keys():
        val = ref[key][e]
        if isinstance(val,float) or isinstance(val,int):
            print('{} my: {:>10.3f} ref: {:>10.3f}'.format(e,getattr(uff,e),val))
            if e == 'E_tot':
                e_check = numpy.isclose(getattr(uff,e),val,0,1e-3)
        if e == 'mmtypes':
            mm_check = numpy.array([mm == getattr(uff,e)[i] for i,mm in enumerate(val)]).all() 
            print('{} are equal {}'.format(e,mm_check))
    return e_check, mm_check
            

if __name__ == '__main__':
    from pyflosic2 import Atoms, WORKFLOW
    from pyflosic2.systems.uflosic_systems import CH4, H2O
    from pyflosic2.io.flosic_io import write_xyz
    
    #test_knight_valley(f_name='CH4') 
    test_uff_energy() 
    #test_C2H6()
    #test_KT_C6H6()

    # Notes: 
    # - mmtypes should be atoms not s 
    # - sview needs to be fixed for nuclei only 
    # - E_Torsion: 
    #   - we need more torsion tests (sp2- sp2, sp3 -sp2, sp3- sp3 various elements, O, S, Se, Te, Po) 
 
