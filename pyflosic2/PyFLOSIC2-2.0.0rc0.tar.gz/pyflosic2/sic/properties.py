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
from functools import reduce
from pyflosic2.units.units import AU2DEBYE

def dip_moment(p, dm, unit='Debye'):
    """
        dip_moment
        ----------
        Get the dipole moment from mol and dm. 

    """
    # Ref.: https://github.com/pyscf/pyscf/blob/master/pyscf/scf/hf.py

    if not (isinstance(dm, numpy.ndarray) and dm.ndim == 2):
        # UHF denisty matrices
        dm = dm[0] + dm[1]

    with p.mol.with_common_orig((0,0,0)):
        ao_dip = p.mol.intor_symmetric('int1e_r', comp=3)
    el_dip = numpy.einsum('xij,ji->x', ao_dip, dm).real

    charges = p.mol.atom_charges()
    coords  = p.mol.atom_coords()
    nucl_dip = numpy.einsum('i,ix->x', charges, coords)
    mol_dip = nucl_dip - el_dip

    if unit.upper() == 'DEBYE':
        mol_dip *= AU2DEBYE
        p.log.write('Dipole moment(X, Y, Z, Debye): {:8.5f}, {:8.5f}, {:8.5f}'.format(*mol_dip))

    else:
        p.log.write('Dipole moment(X, Y, Z, A.U.): {:8.5f}, {:8.5f}, {:8.5f}'.format(*mol_dip))
    return mol_dip

def spin_square(p, mf):
    """
        spin_square 
        -----------
        Get the multiplicity M and spin expectation value <S^2>. 
    """
    mo = (mf.mo_coeff[0][:,mf.mo_occ[0]>0], mf.mo_coeff[1][:,mf.mo_occ[1]>0])
    s = p.mol.intor('int1e_ovlp')
    mo_a, mo_b = mo
    nocc_a = mo_a.shape[1]
    nocc_b = mo_b.shape[1]
    s = reduce(numpy.dot, (mo_a.conj().T, s, mo_b))
    ssxy = (nocc_a+nocc_b) * .5 - numpy.einsum('ij,ij->', s.conj(), s)
    ssz = (nocc_b-nocc_a)**2 * .25
    ss = (ssxy + ssz).real
    s = numpy.sqrt(ss+.25) - .5
    M = s*2+1
    p.log.write(f'M : {M} <S^2> : {ss}')
    return ss, M
