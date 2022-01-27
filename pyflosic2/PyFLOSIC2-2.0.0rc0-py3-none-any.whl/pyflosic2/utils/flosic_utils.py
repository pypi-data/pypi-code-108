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
from pyflosic2.io.flosic_io import atoms2flosic
from pyflosic2.utils.symmetry import I, apply_all
import copy 

def apply_electric_field(mf, efield):
    """
        apply_electric_field
        --------------------
        Add/apply an electric field term to the Hamiltonian of an mf object.

        Reference
            - pyscf/pyscf/prop/polarizability/uks.py
            - pyscf/excamples/scf/40_apply_electric_field.py
    """
    mol = mf.mol
    charges = mol.atom_charges()
    coords = mol.atom_coords()
    charge_center = numpy.einsum(
        'i,ix->x', charges, coords) / charges.sum()
    # define gauge origin for dipole integral
    with mol.with_common_orig(charge_center):
        if mol.cart:
            ao_dip = mol.intor_symmetric('cint1e_r_cart', comp=3)
        else:
            ao_dip = mol.intor_symmetric('cint1e_r_sph', comp=3)
    h1 = mf.get_hcore()
    mf.get_hcore = lambda *args, **kwargs: h1 + \
        numpy.einsum('x,xij->ij', efield, ao_dip)

def vec_in_vecs(vec, vecs, tol=1e-4):
    """
        vec_in_vecs
        -----------
        Is vector vec in set of vectors vecs?

        Variables
        ---------
            - tol:   float(), tolerance for check 
            - check: bool(), True == vec is in vecs
            - dmin:  float(), minimal distance 
    
        Reference
        ---------
            - PySCF
    """
    norm = numpy.sqrt(len(vecs))
    data = numpy.einsum('ix->i', abs(vecs-vec))/norm
    idx = numpy.argmin(data)
    dmin = data[idx]
    check = dmin < tol
    #print(check,dmin,idx,tol)
    return dmin, check, idx

def vecs_in_vecs(v1,v2,tol=1e-4):
    """
        vecs_in_vecs
        ------------
        Is each point of v1 also in v2.
        Assumption: a linear projection v1[i] <-> v2[j]
    """
    dist = numpy.zeros(len(v1),dtype=float)
    checks = numpy.zeros(len(v1),dtype=bool)
    idxs = numpy.zeros(len(v1),dtype=int)
    for i,v in enumerate(v1):
        dist[i], checks[i], idxs[i] = vec_in_vecs(v,v2)
        # we remove the matched coordinate 
        # from the reference set 
        v2 = numpy.delete(v2,idxs[i],axis=0)
        #print(f'len(v2) : {len(v2)}')
    return dist, checks, idxs

class results:
    def __init__(self):
        pass

class Classify:
    def __init__(self,atoms,tol=1e-1,verbose=3):
        self.atoms = atoms
        self.tol = tol 
        self.verbose = verbose 

    def _classify(self,atoms):
        n, fa, fb = atoms2flosic(atoms)
        dist, checks, idxs = vecs_in_vecs(fa.positions,fb.positions)
        r = results()
        r.dist = dist
        r.dmin = dist.sum()
        r.checks = checks
        r.idxs = idxs
        return r

    def _check_LT(self):
        r = self._classify(self.atoms)
        return r

    def _check_LDQ(self):
        # Invert one spin channel
        # Make a copy to not change original atoms 
        atoms = copy.copy(self.atoms)
        atoms = apply_all(I(),atoms,only='He')
        r = self._classify(atoms)
        return r

    def kernel(self):
        rLT = self._check_LT()
        rLDQ = self._check_LDQ()
        checkLT = numpy.isclose(rLT.dmin,0,0,self.tol)
        checkLDQ = numpy.isclose(rLDQ.dmin,0,0,self.tol)
        if (checkLT and not checkLDQ) or (checkLT and checkLDQ):
            typ = 'LT'
        if not checkLT and checkLDQ:
            typ = 'LDQ'
        if not checkLT and not checkLDQ:
            typ = 'other'
        if self.verbose > 3: 
            print(f'typ : {typ} dminLT = {rLT.dmin} dminLDQ = {rLDQ.dmin}')
        return typ

    def __call__(self):
        return self.kernel()

def classify(atoms):
    typ = Classify(atoms)()
    return typ

