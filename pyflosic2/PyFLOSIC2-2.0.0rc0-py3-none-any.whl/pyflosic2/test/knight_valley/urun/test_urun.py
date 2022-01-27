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
from pyflosic2 import Atoms
from pyflosic2.sic.urun import URUN
from pyflosic2.systems.uflosic_systems import CH4

ref = {'etot_level0': -40.207903752259696,
       'etot_level1': -40.20927715557367,
       'etot_level2': -40.2092771555737,
       'etot_level3': -40.20979685803429}

# SS, entropy, 25.10.2021 
# E(FLO-SIC,level=0) = -40.207903752259696
# E(FLO-SIC,level=1) = -40.20927715557367
# E(FLO-SIC,level=2) = -40.2092771555737
# E(FLO-SIC,level=3) = -40.20979685803429


def test_urun(ref=ref):
    # System: information
    atoms = CH4()
    # Workflow
    uwf = URUN(atoms)
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
    test_urun()
