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
from pyflosic2.io.flosic_io import read_xyz


def gen_systems_from_xyz(f_name, charge=0, spin=0):
    """
        Generate: System information from xyz files
        -------------------------------------------
        Powered by lazyness.
        Please use with great care!
    """
    name = f_name.split('.')[0]
    print('def {}():'.format(name))
    print('    """')
    print('        {} example'.format(name))
    print('    """')
    sym, pos, sym_fod1, sym_fod2 = read_xyz(f_name)
    values, index, counts = numpy.unique(sym, return_counts=True, return_index=True)
    # Note: numpy.unique sorts everything internally
    # We need to reconstruct the correct order.
    idx = index.argsort()
    values = values[idx]
    counts = counts[idx]
    s = ''
    for v, w in zip(values, counts):
        s += "['{}']*{}+".format(v, w)
    s = s[:-1]
    print("    sym = {}".format(s))
    ptot = '['
    for i, p in enumerate(pos):
        print('    p{} = [{},{},{}]'.format(i, p[0], p[1], p[2]))
        ptot += "p{},".format(i)
    ptot = ptot[:-1] + ']'
    print('    pos = {}'.format(ptot))
    print('    charge = {}'.format(charge))
    print('    spin = {}'.format(spin))
    print("    atoms = Atoms(sym,pos,charge=charge,spin=spin,elec_symbols=['{}','{}'])".format(sym_fod1, sym_fod2))
    print("    return atoms")


if __name__ == '__main__':
    gen_systems_from_xyz(f_name='C6H6.xyz', 
                         charge=0, 
                         spin=0)
