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
from pyflosic2 import Atoms, WORKFLOW


def test_workflow():
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
    # Unrestricted workflow
    uwf = WORKFLOW(atoms, mode='unrestricted')
    # FLO-SIC approximations
    uwf.kernel(update=False, flevel=0)
    uwf.kernel(update=False, flevel=1)
    uwf.kernel(update=False, flevel=2)
    uwf.kernel(update=False, flevel=3)

    # Restricted workflow
    rwf = WORKFLOW(atoms, mode='restricted')
    # FLO-SIC approximations
    rwf.kernel(update=False, flevel=0)
    rwf.kernel(update=False, flevel=1)
    rwf.kernel(update=False, flevel=2)
    rwf.kernel(update=False, flevel=3)


if __name__ == '__main__':
    test_workflow()
