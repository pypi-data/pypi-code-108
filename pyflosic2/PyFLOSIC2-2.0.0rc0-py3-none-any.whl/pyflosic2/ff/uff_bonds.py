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
import scipy

# Refs.
# [1] https://en.wikipedia.org/wiki/Cell_lists

# Notes
# 1) Cell list
#    - replacement for calculation double looping all species
#    - in a first step on can use my pymotif bo using ase

ATOM_key2idx = {
    'r': 0,
    'max_coord': 1
}

# Radii currently from
# https://jcheminf.biomedcentral.com/articles/10.1186/1758-2946-4-26#Sec11
# may need to change
# https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiU9qDo6O3rAhWNzaQKHYjEC8gQFjABegQIBRAB&url=https%3A%2F%2Fwww.ccdc.cam.ac.uk%2Fsupport-and-resources%2Fccdcresources%2FElemental_Radii.xlsx&usg=AOvVaw3UxV0aCOmX7Z6Oa_Wwc1OG
# http://crystalmaker.com/support/tutorials/atomic-radii/index.html

ATOM_data = {
    'H': (0.23, 1),
    'He': (0.93, 4),
    'Li': (0.68, 1),
    'Be': (0.35, 4),
    'B': (0.83, 4),
    'C': (0.68, 4),
    'N': (0.68, 4),
    'O': (0.68, 2),
    'F': (0.64, 1),
    'Ne': (1.12, 4),
    'Na': (0.97, 1),
    'Mg': (1.10, 4),
    'Al': (1.35, 4),
    'Si': (1.20, 4),
    'P': (1.05, 4),
    'S': (1.02, 4),
    'Cl': (0.99, 1),
    'Ar': (1.57, 4),
    'K': (1.33, 1),
    'Ca': (0.99, 6),
    'Sc': (1.44, 4),
    'Ti': (1.47, 6),
    'V': (1.33, 4),
    'Cr': (1.35, 6),
    'Mn': (1.35, 6),
    'Fe': (1.34, 6),
    'Co': (1.33, 6),
    'Ni': (1.50, 4),
    'Cu': (1.52, 4),
    'Zn': (1.45, 4),
    'Ga': (1.22, 4),
    'Ge': (1.17, 4),
    'As': (1.21, 4),
    'Se': (1.22, 4),
    'Br': (1.21, 1),
    'Kr': (1.91, 4),
    'Rb': (1.47, 1),
    'Sr': (1.12, 6),
    'Y': (1.78, 4),
    'Zr': (1.56, 4),
    'Nb': (1.48, 4),
    'Mo': (1.47, 6),
    'Tc': (1.35, 6),
    'Ru': (1.40, 6),
    'Rh': (1.45, 6),
    'Pd': (1.50, 4),
    'Ag': (1.59, 2),
    'Cd': (1.69, 4),
    'In': (1.63, 4),
    'Sn': (1.46, 4),
    'Sb': (1.46, 4),  # used the same value as for Sn
    'Te': (1.47, 4),
    'I': (1.40, 1),
    'Xe': (1.98, 4),
    'Cs': (1.67, 1),
    'Ba': (1.34, 6),
    'La': (1.87, 4),
    'Ce': (1.83, 6),
    'Pr': (1.82, 6),
    'Nd': (1.81, 6),
    'Pm': (1.80, 6),
    'Sm': (1.80, 6),
    'Eu': (1.99, 6),
    'Gd': (1.79, 6),
    'Tb': (1.76, 6),
    'Dy': (1.75, 6),
    'Ho': (1.74, 6),
    'Er': (1.73, 6),
    'Tm': (1.72, 6),
    'W' : (1.62, 6),# https://www.webelements.com/tungsten/atom_sizes.html
    'Pt': (1.36, 3),# https://www.webelements.com/platinum/atom_sizes.html
    'Au': (1.36, 2),# https://www.webelements.com/gold/atom_sizes.html
    'Hg': (1.32, 1) # https://www.webelements.com/mercury/atom_sizes.html
}


def detect_bond(s_i, s_j, p_i, p_j, eps=0.45):
    """ Get initial bonding order (0, 1) and bond length"""
    # d_ij < r_i + r_j + eps
    # d_ij ... distance
    # r_i  ... radius of i
    # r_j  ... radius of j
    r_i = ATOM_data[s_i][ATOM_key2idx['r']]
    r_j = ATOM_data[s_j][ATOM_key2idx['r']]
    r_ij = numpy.linalg.norm(p_j - p_i)
    print(s_i, s_j, r_i, r_j, r_ij)
    r_ij_EQ = r_i + r_j
    if r_ij < r_ij_EQ + eps:
        bo_connect = 1
    else:
        bo_connect = 0
    b_center = (p_i + p_j) / 2.
    e_check = ['B', 'Al']
    cond = s_i not in e_check and s_j not in e_check
    if cond:
        r_check = r_ij / r_ij_EQ
    if not cond:
        r_check = (r_ij - 0.2) / r_ij_EQ
    return bo_connect, r_check, b_center


def get_bonds(struct):
    """Get bonds"""
    # bond order, connectivity matrix
    o = numpy.zeros((len(struct), len(struct)), dtype=numpy.float64)
    # bond lengths matrix
    b = numpy.zeros((len(struct), len(struct)), dtype=numpy.float64)
    # center of the bond: vector[x,y,z]
    b_center = numpy.zeros((len(struct), len(struct), 3), dtype=numpy.float64)
    # connected symbols matrix
    nsym = numpy.zeros((len(struct), len(struct)), dtype=str)

    c = numpy.zeros((len(struct)), dtype=numpy.float64)
    pos = struct.get_positions()
    a = struct.get_chemical_symbols()
    # Build connectivity matrix
    for i in range(0, len(struct)):
        for j in range(0, len(struct)):
            s_i, p_i = a[i], pos[i]
            s_j, p_j = a[j], pos[j]
            if i != j:
                o[i, j], b[i, j], b_center[i, j] = detect_bond(s_i, s_j, p_i, p_j)
                if o[i, j] == 1:
                    c[i] += 0.5 
                    c[j] += 0.5
                #if o[i, j] == 1:
                #nsym[i, j] = s_i+s_j
                #nsym[i, j] = s_i+s_j
    print(c)
    return a, o, b, b_center #, nsym


def get_num_bonds(a, o):
    """ count bonds per symbol """
    c = numpy.zeros((len(a)), dtype=numpy.float64)
    c_max = numpy.zeros((len(a)), dtype=numpy.float64)
    r_cov = numpy.zeros((len(a)), dtype=numpy.float64)
    for i in range(0, len(a)):
        c[i] = o[i, :].sum()
        c_max[i] = ATOM_data[a[i]][ATOM_key2idx['max_coord']]
        r_cov[i] = ATOM_data[a[i]][ATOM_key2idx['r']]
        o[i,i] = c[i]
    print(o)

    return c, c_max, r_cov


def check_overbinding(a, o, b, c, c_max, r_cov):
    """ check and correct overbinding, reorder after r_cov """
    # sort r_cov in ascending order
    idx_asc = numpy.argsort(r_cov)
    print('idx_asc: {}'.format(idx_asc))
    # re-sort idx in descending order
    idx_des = idx_asc[::-1]
    print('idx_des: {}'.format(idx_des))
    # sort a, c and c_max descending r_cov order
    a = a[idx_des]
    c = c[idx_des]
    c_max = c_max[idx_des]
    r_cov = r_cov[idx_des]
    b = b[idx_des, :][:, idx_des]
    o = o[idx_des, :][:, idx_des]
    print('b : {}'.format(b))
    print(idx_des, c, c_max)
    for i in range(len(c)):
        if c[i] > c_max[i]:
            print('overbonded {}: bonds: {} max_coord: {}'.format(a[i], c[i], c_max[i]))
            for v in range(int(c[i] - c_max[i])):
                print(v)
                j = (b[i, :].argmax())
                print('removed ij: {} {}'.format(i, j))
                b[i, j] = 0
                o[i, j] = 0
                c[i] = c[i] - 1
    # backsort
    # a = a[idx_asc]
    # c = c[idx_asc]
    # c_max = c_max[idx_des]
    # b = b[idx_asc, :][:, idx_asc]
    # o = o[idx_asc, :][:, idx_asc]
    return a, o, b, c, c_max, r_cov


def write_xyz(atoms, prefix='pybff'):
    """ write xyz file"""
    sym = atoms.get_chemical_symbols()
    pos = atoms.get_positions()
    nsym = len(sym)
    o = open('{}.xyz'.format(prefix), 'w')
    o.write('{}\n\n'.format(nsym))
    for i in range(nsym):
        o.write('{} {} {} {}\n'.format(sym[i], pos[i][0], pos[i][1], pos[i][2]))
    o.close()


#class Atoms:
#    """ simplified atoms class """
#
#    def __init__(self, sym, pos):
#        self.sym = numpy.array(sym)
#        self.pos = numpy.array(pos)
#
#    def get_chemical_symbols(self):
#        return self.sym
#
#    def get_positions(self):
#        return self.pos
#
#    def __len__(self):
#        return len(self.pos)


def test():
    """ Test """
    ## define nuclei positions
    #p1 = [0.0000, 0.0000, -0.25]
    #p2 = [0.0000, 0.0000, 0.25]
    #p3 = [0.0000, -0.500, 0.00]
    #sym = ['H', 'N', 'H']
    #struct = Atoms(sym, [p1, p2, p3])
    #write_xyz(struct)
    from ase.io import read 
    struct = read('C6H6.xyz')
    # define valence motif
    a, o, b, b_center = get_bonds(struct)
    print(a,o,b,b_center)
    c, c_max, r_cov = get_num_bonds(a, o)
    print('c: {} c_max: {} r_conv: {}'.format(c, c_max, r_cov))
    #a, o, b, c, c_max, r_cov = check_overbinding(a, o, b, c, c_max, r_cov)
    #print('a: {} o: {} c: {}'.format(a, o, c))
    #a, o, b, c, c_max, r_cov = check_overbinding(a, o, b, c, c_max, r_cov)
    #print(a, o, c, c_max)


if __name__ == '__main__':
    test()
