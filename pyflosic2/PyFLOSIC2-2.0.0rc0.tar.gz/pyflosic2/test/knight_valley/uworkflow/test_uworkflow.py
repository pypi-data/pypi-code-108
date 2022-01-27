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
from pyflosic2.sic.uworkflow import Atoms, UWORKFLOW

# SS, entropy, 15.05.2021
# EFLOSIC(level=0) = -40.20623077182638 [Ha]
# EFLOSIC(level=1) = -40.208487189436646 [Ha]
# EFLOSIC(level=2) = -40.20936762773774 [Ha]
# EFLOSIC(level=3) = -40.20982895523991 [Ha]

ref = {'etot_level0': -40.20623077182638,
       'etot_level1': -40.208487189436646,
       'etot_level2': -40.20936762773774,
       'etot_level3': -40.20982895523991}

def test_uworkflow(ref=ref):
    # Nuclei
    sym = ['C'] + 4 * ['H']
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
    uwf = UWORKFLOW(atoms)
    # FLO-SIC approximations
    etot_level0 = uwf.kernel(update=False, flevel=0)
    etot_level1 = uwf.kernel(update=False, flevel=1)
    etot_level2 = uwf.kernel(update=False, flevel=2)
    etot_level3 = uwf.kernel(update=False, flevel=3)

    p = uwf.p
    p.log.write('Basis : {}'.format(p.basis))
    p.log.write('E(FLO-SIC,level=0) = {}'.format(etot_level0))
    p.log.write('E(FLO-SIC,level=1) = {}'.format(etot_level1))
    p.log.write('E(FLO-SIC,level=2) = {}'.format(etot_level2))
    p.log.write('E(FLO-SIC,level=3) = {}'.format(etot_level3))

    assert numpy.isclose(etot_level0, ref['etot_level0'])
    assert numpy.isclose(etot_level1, ref['etot_level1'])
    assert numpy.isclose(etot_level2, ref['etot_level2'])
    assert numpy.isclose(etot_level3, ref['etot_level3'])
    p.log.write('Tests: passed [okay]')


if __name__ == '__main__':
    test_uworkflow()
