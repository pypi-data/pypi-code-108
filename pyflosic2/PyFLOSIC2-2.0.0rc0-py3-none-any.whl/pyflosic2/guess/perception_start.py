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
from pyflosic2 import GUI
from pyflosic2.systems.uflosic_systems import C6H6,H2O,CH4, COH2
from pyflosic2.io.flosic_io import atoms2flosic
from pyflosic2.io.flosic_io import write_xyz
from pyflosic2.atoms.atoms import symbol2number
from pyflosic2.atoms.mmtypes import get_angle
from itertools import combinations, permutations 
from pyflosic2.ff.uff_params import UFF_params, UFF_key2idx
from copy import copy, deepcopy 

#  Covalent radii 
#  --------------
#
#  Reference
#  ---------
#   - [1] ase.data: Covalent radii revisited,
#         Beatriz Cordero, Verónica Gómez, Ana E. Platero-Prats, Marc Revés,
#         Jorge Echeverría, Eduard Cremades, Flavia Barragán and Santiago Alvarez,
#         Dalton Trans., 2008, 2832-2838 DOI:10.1039/B801115J
missing = 0.2
covalent_radii = numpy.array([
    missing,  # X
    0.31,  # H
    0.28,  # He
    1.28,  # Li
    0.96,  # Be
    0.84,  # B
    0.76,  # C
    0.71,  # N
    0.66,  # O
    0.57,  # F
    0.58,  # Ne
    1.66,  # Na
    1.41,  # Mg
    1.21,  # Al
    1.11,  # Si
    1.07,  # P
    1.05,  # S
    1.02,  # Cl
    1.06,  # Ar
    2.03,  # K
    1.76,  # Ca
    1.70,  # Sc
    1.60,  # Ti
    1.53,  # V
    1.39,  # Cr
    1.39,  # Mn
    1.32,  # Fe
    1.26,  # Co
    1.24,  # Ni
    1.32,  # Cu
    1.22,  # Zn
    1.22,  # Ga
    1.20,  # Ge
    1.19,  # As
    1.20,  # Se
    1.20,  # Br
    1.16,  # Kr
    2.20,  # Rb
    1.95,  # Sr
    1.90,  # Y
    1.75,  # Zr
    1.64,  # Nb
    1.54,  # Mo
    1.47,  # Tc
    1.46,  # Ru
    1.42,  # Rh
    1.39,  # Pd
    1.45,  # Ag
    1.44,  # Cd
    1.42,  # In
    1.39,  # Sn
    1.39,  # Sb
    1.38,  # Te
    1.39,  # I
    1.40,  # Xe
    2.44,  # Cs
    2.15,  # Ba
    2.07,  # La
    2.04,  # Ce
    2.03,  # Pr
    2.01,  # Nd
    1.99,  # Pm
    1.98,  # Sm
    1.98,  # Eu
    1.96,  # Gd
    1.94,  # Tb
    1.92,  # Dy
    1.92,  # Ho
    1.89,  # Er
    1.90,  # Tm
    1.87,  # Yb
    1.87,  # Lu
    1.75,  # Hf
    1.70,  # Ta
    1.62,  # W
    1.51,  # Re
    1.44,  # Os
    1.41,  # Ir
    1.36,  # Pt
    1.36,  # Au
    1.32,  # Hg
    1.45,  # Tl
    1.46,  # Pb
    1.48,  # Bi
    1.40,  # Po
    1.50,  # At
    1.50,  # Rn
    2.60,  # Fr
    2.21,  # Ra
    2.15,  # Ac
    2.06,  # Th
    2.00,  # Pa
    1.96,  # U
    1.90,  # Np
    1.87,  # Pu
    1.80,  # Am
    1.69,  # Cm
    missing,  # Bk
    missing,  # Cf
    missing,  # Es
    missing,  # Fm
    missing,  # Md
    missing,  # No
    missing,  # Lr
    missing,  # Rf
    missing,  # Db
    missing,  # Sg
    missing,  # Bh
    missing,  # Hs
    missing,  # Mt
    missing,  # Ds
    missing,  # Rg
    missing,  # Cn
    missing,  # Nh
    missing,  # Fl
    missing,  # Mc
    missing,  # Lv
    missing,  # Ts
    missing,  # Og
])

# Max coordination 
# ----------------
# Correspond/ respect UFF MMTypes
missing = 1
max_coordination = numpy.array([
    0, # X
    1,
    4,
    1,
    4,
    4,
    4,
    3, #4,
    2,
    1,
    4,
    1,
    4,
    4,
    4,
    4,
    4,
    1,
    4,
    1,
    6,
    4,
    6,
    4,
    6,
    6,
    6,
    6,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    1,
    4,
    1,
    6,
    4,
    4,
    4,
    6,
    6,
    6,
    6,
    4,
    2,
    4,
    4,
    4,
    4,  # used the same value as for Sn
    4,
    1,
    4,
    1,
    6,
    4,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,# https://www.webelements.com/tungsten/atom_sizes.html
    3,# https://www.webelements.com/platinum/atom_sizes.html
    2,# https://www.webelements.com/gold/atom_sizes.html
    1 # https://www.webelements.com/mercury/atom_sizes.html
    ])

# What are metals? 
# ----------------
# List containing metals. 
metals = ['Li', 'Be', 'Al', 'Sc', 'Ti', 'V',
            'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
            'Ga', 'Ge', 'Y', 'Zr', 'Nb', 'Mo',
            'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In',
            'Sn', 'Sb', 'La', 'Ce', 'Pr', 'Nd',
            'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho',
            'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta',
            'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
            'Tl', 'Pb', 'Bi', 'Po', 'Fr', 'Ra',
            'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am',
            'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md',
            'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs',
            'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl',
            'Mc', 'Lv', 'Ts', 'Og']

def get_nearest_neighbours(atoms,rc,eps=0.2,verbose=3): #0.2
    """
        Get nearest neighbours (numpy.array)
        ------------------------------------
        Find nearest neighbours for condition 
            
            r_ij < rc[i] + rc[j] + eps 

        
        Input
        -----
        atoms   : Atoms(), atoms object/instance 
        rc      : numpy.array(), covalent radii for symbols in Atoms() 
        eps     : float, threshold for condition 
        verbose : int(), integer for verbosity/ output level

    """
    nn_array = numpy.zeros((len(atoms),len(atoms)),dtype=int)
    for i,ni in enumerate(atoms):
        for j,nj in enumerate(atoms):
            if j > i:
                r_ij = numpy.linalg.norm(nj.position-ni.position)
                if r_ij < rc[i] + rc[j] + eps:
                    nn_array[i,j] = j
                    nn_array[j,i] = j
    if verbose > 3:
        print(nn_array)
    return nn_array 


def get_guess_bond_order(atoms):
    """
        Get guess bond order 
        --------------------
        Using nearst neighbours (numpy.arrays) 
        with different cutoffs (rc1, rc2, rc3) 
        for (single, double, triple) bonds 
        we guess the bond order matrix (bo).

        Rules 
            - Hydrogen bond order is set to 1 

        Input
        -----
        atoms   : Atoms(), atoms object/instance
    """
    symbols = numpy.array(atoms.symbols)
    rc1 = numpy.array([covalent_radii[symbol2number[ni.symbol]] for ni in atoms])
    rc2 = rc1 - 0.15 # 0.15
    rc3 = rc2 - 0.10 # 0.1 0.15
    # single bonds 
    nn1 = get_nearest_neighbours(atoms=atoms,rc=rc1)
    # double bonds 
    nn2 = get_nearest_neighbours(atoms=atoms,rc=rc2)
    # triple bonds 
    nn3 = get_nearest_neighbours(atoms=atoms,rc=rc3)
    NN = [nn1,nn2,nn3]
    
    # bond order (bo) matrix
    bo = numpy.zeros((len(atoms), len(atoms)))
    hydrogens = symbols == "H"
    for i,ni in enumerate(atoms.positions):
        idx1 = nn1[i].nonzero()[0].tolist()
        idx2 = nn2[i].nonzero()[0].tolist()
        idx3 = nn3[i].nonzero()[0].tolist()
        if idx1:
            bo[i,idx1] = 1.0
        if idx2:
            bo[i,idx2] = 2.0
        if idx3:
            bo[i,idx3] = 3.0
    # Hydrogen bond order 
    bo_h = bo[hydrogens]
    bo_h[bo_h > 1.0] = 1.0
    bo[hydrogens, :] = bo_h
    bo[:, hydrogens] = bo_h.T
    return nn1, bo 

def get_atomic_coordination(atoms,nn):
    """
        Get atomic coordination (co)  
        ----------------------------
        Atomic coordination (co) is the sum of 
        connected neighbours. 

        Input
        -----
        atoms   : Atoms(), atoms object/instance 
        nn      : numpy.array(), next nearest neighours numpy array

    """
    co = numpy.zeros(len(atoms))
    for i in range(0, len(atoms)):
        co[i] = len(nn[i].nonzero()[0])
    return co 

def check_overbonding(atoms,bo,verbose=3):
    """
        Check overbonding/ Maximum coordination check 
        ----------------------------------------------
        Check if the atomic valence (va) 
        is larger then the maximal valence of the species. 

        Input
        -----
        atoms   : Atoms(), atoms object/instance 
        bo      : numpy.array(), bond order matrix 
        verbose : int(), integer for verbosity/ output level

    """
    # Check overbonding 
    # atomic valence 
    va = numpy.zeros(len(atoms))
    va_max = numpy.zeros(len(atoms))
    for i in range(0, len(atoms)):
        # get current coordination per atom 
        va[i] = bo[i, :].sum()
        # max coordination for the current species 
        va_max[i] = max_coordination[symbol2number[atoms[i].symbol]]
    # total penalty score (tps)
    tps = (va - va_max).sum()
    # over bonding (ob)
    ob = numpy.multiply(va > va_max,1)
    if verbose > 3: 
        print(f'va \n {va}')
        print(f'va_max \n {va_max}')
        print(f'tps \n {tps}')
    return va, va_max,tps,ob

def clean_overbonding(atoms,nn,bo,btype='LEWIS'):
    """
        Clean over-bonding
        ------------------
        If the current coordination number/ atomic valence (va) 
        is larger then the maximal valence of the species, 
        the bond order (bo) needs to be reduced. 

        (1) Check overbonding 
        (2) Reduce bond order
        (3) Check overbonding 
            repeat (2),(3) until va == va_max 

        Refs 
            - [1] https://onlinelibrary.wiley.com/doi/epdf/10.1002/jcc.24309?saml_referrer
                  Journal of Computational Chemistry 2016, 37, 1191–1205 1193
        Input
        -----
        atoms   : Atoms(), atoms object/instance 
        nn      : numpy.array(), next nearest neighours numpy array 
        bo      : numpy.array(), bond order matrix 
        btype   : str(), bond type, e.g., 'LEWIS' or 'LDQ' 
                  adjust if in case of 'LEWIS' 1e is removed 
                  or in case of 'LDQ' only 0.5e is removed 
                  sets the del_e variable 

        TODO 
            - need to implement H BO for 2 H-B bonds equals 2 
    """
    bo = bo.copy()
    m = {'LEWIS' : 1.0, 'LDQ' : 0.5} 
    del_e = m[btype] 
    # covalent radii for symbols
    rc = numpy.array([covalent_radii[symbol2number[ni.symbol]] for ni in atoms]) 
    # initial values 
    va, va_max, tps, ob = check_overbonding(atoms,bo)
    for i in range(0, len(atoms)):
        if ob[i] == 1:
            nn_atoms = nn[i].nonzero()[0].tolist()
            r_tmp = numpy.zeros(len(nn_atoms),dtype=float)
            bo_tmp = numpy.zeros(len(nn_atoms),dtype=float) 
            while va[i] > va_max[i]:
                for it, j in enumerate(nn_atoms): 
                    # Adjust equilibrium references for Al-Al , B-B bonds 
                    # see Ref [1] page 1192 
                    if atoms[i].symbol == 'Al' and atoms[j].symbol == 'Al':
                        eps = -0.2 
                    if atoms[i].symbol == 'B' and atoms[j].symbol == 'B':
                        eps = -0.2 
                    else: 
                        eps = 0
                    r_ij = numpy.linalg.norm(atoms[j].position - atoms[i].position)
                    r_tmp[it] = r_ij/(rc[i] + rc[j]+eps) 
                    bo_tmp[it] = bo[i,j]
                if bo[i,nn_atoms[r_tmp.argmin()]] == bo_tmp.max():
                    # delete del_e for the smallest bond 
                    # if bond order is max for this bond 
                    idx = nn_atoms[r_tmp.argmin()]
                    bo[i,idx] -= del_e
                    bo[idx,i] -= del_e
                else: 
                    # delete del_e from bond with max bond order 
                    idx = nn_atoms[bo_tmp.argmax()]
                    bo[i,idx] -= del_e
                    bo[idx,i] -= del_e
                # update all values 
                va, va_max, tps, ob = check_overbonding(atoms,bo)
    return va, bo 

def get_max_valence(symbol,co): 
    """
        Get maximal valence (ve) 
        ------------------------
        Is defined/limited by the available UFF MMTypes. 
    
        Adjustments: 
            - N, O fixes lone electrons/ pairs
              but breaks sp 
    """
    if symbol == 'H': 
        if co == 2: 
            ve = 2 
        else: 
            ve = 1 
    if symbol == 'C':
        ve = 4 
    if symbol == 'N':
        # KT: adjusted for NH3 
        ve = 5 # orig: 4 KT: 5 
    if symbol == 'O':
        # SS: added this for Conformer3D_CID_7861
        #     O_3 double bound - sp2 ? 
        #ve = 3 
        #if co == 2: 
        #    ve = 3 
        #### KT: adjusted for COH2 
        #else:
        #    ve = 6 # orig: 3 
        ve = 6 
    if symbol == 'Si':
        ve = 4 
    if symbol == 'P': 
        if co > 3: 
            ve = 4 
        else: 
            ve = 5 
    if symbol == 'S':
        if co == 2: 
            ve = 4 
        else: 
            ve = 6 
    return ve

def get_hybridization(atoms,nn,co,va,verbose=3):
    """
        Get hybridization 
        -----------------
        Get lone-pairs and sp - hybridization. 
        Limits: ['H','C','N','O','Si','P','S']

        sp = 1 : sp, linear hybridization 
        sp = 2 : sp2, trigonal hybridization 
        sp = 3 : sp3, tetrahedral hybridization 
    """
    # lone electrons
    l = numpy.zeros(len(atoms))
    # sp hybridization 
    sp = numpy.zeros(len(atoms))
    # atomic coordination 
    co = get_atomic_coordination(atoms,nn)
    for i in range(0, len(atoms)):
        if atoms[i].symbol in ['H','C','N','O','Si','P','S']:
            ve = get_max_valence(atoms[i].symbol,co[i])
            l[i] = (ve - va[i])
            sp[i] = co[i] + numpy.ceil(l[i]/2.) -1 
            if verbose > 3: 
                print(f'{atoms[i].symbol} co: {co[i]} , va: {va[i]}, ve: {ve}, l: {l[i]} sp: {sp[i]} va + li: {va[i] + l[i]}')
    if verbose > 3: 
        print(f'l: {l}')
        print(f'sp: {sp}') 
    return l, sp 

def clean_hybridization(atoms,nn,sp,verbose=3):
    """
        Clean hybridization
        -------------------
        Apply special rules 
        - for O if any neighbor is sp2 O is sp2 
          otherwise O is sp3 
          Ref.: https://pubs.acs.org/doi/suppl/10.1021/acs.jcim.0c00076/suppl_file/ci0c00076_si_001.pdf
    
    """
    for i in range(0, len(atoms)):
        # Special rules for O 
        if atoms[i].symbol == 'O':
            idx_j = nn[i].nonzero()[0].tolist() 
            nn_sp2 = (numpy.array(sp[idx_j]) == 2).any()
            if nn_sp2: 
                sp[i] = 2 
    return sp 

def get_formal_charges(atoms,nn,co,va,l,bo,verbose=3): 
    """
        Get formal charges
        ------------------
        Get formal charges for each symbol. 

            fc[i]= ve[i] - l[i] - va[i]
    """
    # formal charges 
    fc = numpy.zeros(len(atoms))
    for i in range(0, len(atoms)):
        ve = get_max_valence(atoms[i].symbol,co[i])
        fc[i] = ve - (l[i] + va[i])
        if verbose > 3: 
            print(f'{atoms[i].symbol} {fc[i]}')
    return fc 

def get_charge(ox,fc,verbose=3): 
    """
        Get charge
        ----------
        Get charge of the system. 
        - Sum of the oxidation numbers 
        - Sum of the formal charges 
    """
    charge_ox = ox.sum()  
    charge_fc = fc.sum()  
    if verbose > 3: 
        print(f'charge : sum ox_i : {charge_ox} sum fc_i : {charge_fc}')
    return charge_fc

def get_spin(l,verbose=3):
    """
        Get spin
        --------
        Get spin (multiplicity) of the system. 

            M = 2S + 1 = spin + 1 
            M = unpaired_elec + 1 

            spin = N_alpha - N_beta 

    """
    # Number of lone electrons 
    lone_elec = l.sum() 
    # integer devision 
    # Number of paired lone electrons 
    paired_elec = lone_elec // 2 * 2 
    # Number of unpaired lone electrons 
    unpaired_elec = lone_elec - paired_elec
    M = unpaired_elec + 1
    if verbose > 3: 
        print(f'l = {l}')
        print(f'M = {M}')
    return M 

def get_geometry_metal(atoms,nn): 
    """
        Get geometry type for metals 
        ----------------------------
    """
    mtyp_geo = numpy.empty((len(atoms)),dtype=object)
    for i in range(len(atoms)):
        if atoms[i].symbol in metals: 
            idx = nn[i].nonzero()[0]
            Nnn = len(idx)
            if Nnn < 4:
                typ_geo = 'tetrahedral'
            if Nnn > 4:
                typ_geo = 'octahedral'
            if Nnn == 4:
                typ_geo = ['tetrahedral','square_planar']
                angles = numpy.array([get_angle(atoms[a1], atoms[i], atoms[a3]) for a1, a3 in combinations(idx, 2)])
                for t in typ_geo: 
                    if t == 'tetrahedral': 
                        E_t = ((angles - 109.47)**2).sum() 
                    if t == 'square_planar': 
                        E_sp = numpy.array([(angles - 90)**2,(angles - 180)**2]).min().sum() 
                if E_sp < E_t: 
                    typ_geo = 'square_planar'
                if E_sp > E_t: 
                    typ_geo = 'tetrahedral'
            mtyp_geo[i] = typ_geo
    return mtyp_geo 

def get_uff_symbol(symbol):
    """
        Get UFF symbol
        --------------
        Get 1st two letters from UFF symbol. 
        (e.g., 'F_' vs. 'Fe')
    """
    if len(symbol) == 1: 
        return symbol+'_'
    else: 
        return symbol 

def get_oxidation_numbers(atoms,nn,bo,verbose=3):
    """
        Get oxidation numbers 
        ---------------------
    """
    ox = numpy.zeros(len(atoms)) 
    for i in range(len(atoms)): 
        for j in nn[i].nonzero()[0].tolist():
            symbols_i = [k for k in list(UFF_params.keys()) if k.find(get_uff_symbol(atoms[i].symbol))]  
            if symbols_i: 
                sym_i = symbols_i[0]
            symbols_j = [k for k in list(UFF_params.keys()) if k.find(get_uff_symbol(atoms[i].symbol))]
            if symbols_j:
                sym_j = symbols_j[0]
            #print(sym_i,sym_j)
            Xi = UFF_params[sym_i][UFF_key2idx['Xi']]
            Xj = UFF_params[sym_j][UFF_key2idx['Xi']]
            if Xj > Xi: 
                ox[i] += bo[i,j]
            if Xj < Xi:
                ox[i] -= bo[i,j]
            if Xj == Xi: 
                ox[i] += 0
    return ox 


def get_atomic_perception(atoms,nn,co,sp,ox,verbose=3):
    """
        Get atomic perception 
        ---------------------
        Assign MMTypes (e.g., UFF MMTypes). 
    """
    mmtypes = numpy.zeros(len(atoms),dtype=object)
    for i in range(len(atoms)):
        if atoms[i].symbol == 'H':
            # H assigment 
            # if H is bonded to 2 B it is 'H_b' 
            # otherwise it is 'H_'
            symbols_j = numpy.array([a.symbol for a in atoms[nn[i].nonzero()[0].tolist()]])
            values, counts = numpy.unique(symbols_j,return_counts=True) 
            for s,c in zip(values,counts):
                if s == 'B' and c >= 2: 
                    mmtypes[i] = 'H_b'
                else: 
                    mmtypes[i] = 'H_'
        else: 
            symbols_i = [k for k in list(UFF_params.keys()) if k.find(get_uff_symbol(atoms[i].symbol)) != -1 ]
            for sym in symbols_i:
                if len(sym) == 2: 
                    if atoms[i].symbol == sym:
                        mmtypes[i] = sym
                if len(sym) == 3: 
                    # sym + sp 
                    if verbose > 3:
                        print(sym[0:2],sym[2])
                        print(sym,sp[i],atoms[i].symbol+'_'+str(int(sp[i])))
                    if atoms[i].symbol+'_'+str(int(sp[i])) == sym: 
                        mmtypes[i] = sym
                if len(sym) == 5:
                    # sym + co + ox
                    if verbose > 3:
                        print(sym[0:2],sym[2],sym[3:])
                        print(sym,co[i],ox[i])
    if verbose > 3: 
        print(f'mmtypes: {mmtypes}')
    return mmtypes 

def get_DFS_cycles(graph, start, end):
    """
        
        Depth-first search (DFS)
        ------------------------
        Find cycles [A,A] in molecular graph. 
        Note: This is a generator, yielding one cycle at time. 

        Reference 
            - [1] https://stackoverflow.com/questions/40833612/find-all-cycles-in-a-graph-implementation
    """
    fringe = [(start, [])]
    while fringe:
        state, path = fringe.pop()
        if path and state == end:
            yield path
            continue
        for next_state in graph[state]:
            if next_state in path:
                continue
            fringe.append((next_state, path+[next_state]))


def get_DFS_path(G,v,seen=None,path=None):
    """
        Get DFS path 
        ------------
        Get connected nodes, i.e, path, in molecular graph 
        using deep first search (DFS) starting from v. 

        Input
        -----
        G: dct(), molecular graph 

    """
    if seen is None: seen = []
    if path is None: path = [v]

    seen.append(v)

    paths = []
    for t in G[v]:
        if t not in seen:
            t_path = path + [t]
            paths.append(t_path)
            paths.extend(get_DFS_path(G, t, seen[:], t_path))
    return paths

def get_DFS_longest_paths(G,keys=None):
    """
        Get DFS longest paths
        ---------------------
        Using get_DFS_path for every k starting point 
        in molecular graph to get all longest paths 
        for per k starting point. 

        Input
        -----
        G: dct(), molecular graph 

    """
    if keys is None: 
        keys = G.keys()
    all_paths = []
    k_all_paths = []
    k_max_paths = []
    max_paths = []
    for k in list(keys):
        k_paths = get_DFS_path(G, k)
        print(k_paths)
        k_max_len   = max(len(p) for p in k_paths)
        k_max_paths = [p for p in k_paths if len(p) == k_max_len]
        all_paths += k_paths 
        max_len = max(len(p) for p in all_paths)
        max_paths += k_max_paths
    return all_paths, max_len, max_paths

def get_nn_bonds(atoms,rc,eps=0.2,verbose=3):
    """
        Get nn and bonds
        ------------------------------------
        Find nearest neighbours for condition 
            
            r_ij < rc[i] + rc[j] + eps 
        
        and determine bonds. 
        
        Input
        -----
        atoms   : Atoms(), atoms object/instance 
        rc      : numpy.array(), covalent radii for symbols in Atoms() 
        eps     : float, threshold for condition 
        verbose : int(), integer for verbosity/ output level

        Output
        ------ 
        nn_array : numpy.array(), next nearest neighbours numpy array 
        Bonds    : Bonds(), Bonds() object/instance    

    """
    bonds = []
    nn_array = numpy.zeros((len(atoms),len(atoms)),dtype=int)
    for i,ni in enumerate(atoms):
        for j,nj in enumerate(atoms):
            if j > i:
                r_ij = numpy.linalg.norm(nj.position-ni.position)
                if r_ij < rc[i] + rc[j] + eps:
                    nn_array[i,j] = j
                    nn_array[j,i] = j
                    bonds.append(Bond(i,j,0))
    if verbose > 3:
        print(nn_array)
    return nn_array, Bonds(bonds)

class Bond:
    """
        Bond class
        ----------
        Class holding bonding information 
        for a single bond. 

    """
    def __init__(self,i,j,bo):
        self.i = i
        self.j = j
        self.bo = bo
        self.status = 'unassigned'

    def __repr__(self):
        """
            Representation 
            --------------
            For usage with, e.g., print(Bond()) . 

        """
        return f'Bond:({self.i},{self.j},{self.bo})'


class Bonds:
    """
        Bonds class
        -----------
        Holds all possible bonds for an atoms object.
    """
    def __init__(self,bonds):
        self.bonds = bonds
        self.Nbonds = len(bonds)
        self.unassigned = self.Nbonds
        self.assigned = 0

    def __next__(self):
        next(self.iter)
        return self

    def __iter__(self):
        self.iter = iter(self.bonds)
        return self.iter

    def __repr__(self):
        return f'{[(b.i,b.j,b.bo) for b in self.bonds]}'

    def get_bond(self,i,j):
        """
            Get bond 
            --------
            Get bond between atom i and atom j. 
        """
        bond = [b for b in self.bonds if (b.i == i and b.j == j) or (b.i == j and b.j == i)] #[0]
        #print(f'bond: {i} {j} {bond} \n {self.bonds}')
        return bond[0]

    def set_bond(self,i,j,bond):
        """
            Set Bond 
            --------
            Replace the bond between atom i and atom j 
            with a new bond object. 
        """
        bonds = numpy.array(self.bonds)
        bonds[bonds == self.get_bond(i,j)] = bond
        self.bonds = bonds.tolist()

def get_score(atoms,path):
    """
        Score
        -----
        Classifier for paths (pi) in a molecular graph.
        If two paths p1 und p2 have the same score
        then they may assumed to be identical.
        Note: This score has nothing to do with tps/aps.
    """
    score = 0
    for i in path:
        ascore = i*0.11 + symbol2number[atoms[i].symbol]*0.08
        score += ascore
    return score

def get_molgraph(atoms,nn,verbose=3):
    """
        Get molgraph
        ------------
        Get molecular graph.
    """
    # molecule as graph 
    molgraph = {}
    for i in range(len(atoms)):
        dct_tmp = {i : nn[i].nonzero()[0].tolist()}
        molgraph.update(dct_tmp)
    if verbose > 3:
        print(f'molgraph: {molgraph}')
    return molgraph

def MagicBonds(atoms,verbose=3):
    """
        MagicBonds
        ----------
        Calculate perform a inspired Antechamber
        but modified bond assignment procedure.

        Workflow
        --------
            - [1] determine molecular graph
            - [2] find longest connected paths in molecular graph
            - [3] set trial bond orders until every bond is assigned

        References
        ----------
            - [1]  http://ambermd.org/antechamber/antechamber.pdf

        Input
        -----
        atoms   : Atoms(), Atoms() object/instance
        verbose : int(), verbosity/output level

        Output
        ------
        nn      : numpy.array(), next nearest neighbours numpy array
        bo      : numpy.array(), bond order matrix

    """
    rc = numpy.array([covalent_radii[symbol2number[ni.symbol]] for ni in atoms])
    nn, bonds = get_nn_bonds(atoms,rc=rc)
    if verbose > 3:
        print(f'bonds: {bonds}')
    co = numpy.zeros(len(atoms))
    va = numpy.zeros(len(atoms))
    bo = numpy.zeros((len(atoms),len(atoms)))
    # molecule as graph
    molgraph = get_molgraph(atoms,nn,verbose=verbose)
    # Determine longest paths in molecular graph
    # using DFS
    longest_paths = get_DFS_longest_paths(G=molgraph)
    for i in range(len(atoms)):
        co[i] = len(nn[i].nonzero()[0])
        va[i] = max_coordination[symbol2number[atoms[i].symbol]]
    # Loop of longest paths in molgraph
    for path in longest_paths[2]:
        score = get_score(atoms,path)
        if verbose > 3:
            print(f'score: {score}')
        # Loop over connected nodes in path
        for idx in range(len(path)-1):
            # construct connected indicies (i,j)
            # this way we loop over all connected
            # bonds in the path
            i,j = path[idx],path[idx+1]
            b = bonds.get_bond(i,j)
            if b.status == 'unassigned':
                # Loop over trial bond orders
                for bo_trial in [1,2,3]:
                    b_tmp = copy(b)
                    co_tmp = co.copy()
                    va_tmp = va.copy()
                    for idx in [b.i,b.j]:
                        co_tmp[idx] -= 1
                        va_tmp[idx] -= bo_trial
                    if verbose > 3:
                        print(f'iter: co: {co_tmp} va: {va_tmp}')
                    # Check if condition for acceptance is fullfilled
                    # we only update (co,va,bonds)
                    # if conditions are fullfilled
                    if co_tmp[b.i] == 0 and va_tmp[b.i] ==0:
                        # condition fullfilled for b.i
                        b_tmp.status = 'assigned'
                        b_tmp.bo = bo_trial
                        b = copy(b_tmp)
                        co = co_tmp.copy()
                        va = va_tmp.copy()
                        bonds.set_bond(b.i,b.j,b)
                        break
                    if co_tmp[b.j] == 0 and va_tmp[b.j] ==0:
                        # condition fullfilled for b.j
                        b_tmp.status = 'assigned'
                        b_tmp.bo = bo_trial
                        b = copy(b_tmp)
                        co = co_tmp.copy()
                        va = va_tmp.copy()
                        bonds.set_bond(b.i,b.j,b)
                        break

    # Bond order (bo) matrix
    bo = numpy.zeros((len(atoms),len(atoms)))
    for b in bonds:
        if verbose > 3:
            print(b.status,b.bo)
        bo[b.i,b.j] = b.bo
        bo[b.j,b.i] = b.bo
    for i in range(0, len(atoms)):
        # get current coordination per atom
        va[i] = bo[i, :].sum()
    if verbose > 3:
        print(f'bo : \n {bo}')
    return nn, bo, va, bonds


# atomic penalty score (aps) 
# --------------------------
# atom_symbol : ftype : va : value 
# 
# Reference:
# - [1] Automatic Molecular Structure Perception for the Universal Force Field
#       Table. 1

nodef = numpy.nan
aps_bo = {'C' : {
                 'default' : {1: 128,
                              2:  64,
                              3:  32,
                              4 :  0,
                              5 : nodef,
                              6 : nodef},
                 'COO'     : {1 : nodef,
                              2 : nodef,
                              3 : 64,
                              4 : 0,
                              5 : nodef,
                              6 : nodef}
                 },
         'Si' : {
                'default' : {1: 8,
                             2: 4,
                             3: 2,
                             4: 0,
                             5: nodef,
                             6: nodef}
                },
         'N' : {
                1         : {1: 64,
                             2:  2,
                             3:  0,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                2         : {1:  nodef,
                             2:  4,
                             3:  0,
                             4 : 2,
                             5 : nodef,
                             6 : nodef},
                3         : {1:  nodef,
                             2:  nodef,
                             3:  0,
                             4 : 1,
                             5 : nodef,
                             6 : nodef},
                4         : {1:  nodef,
                             2:  nodef,
                             3:  nodef,
                             4 : 0,
                             5 : nodef,
                             6 : nodef},
                'NOO'     : {1:  nodef,
                             2:  nodef,
                             3:  64,
                             4 : 0,
                             5 : nodef,
                             6 : nodef},
               },
         'O' : {
                1         : {1:  2,
                             2:  0,
                             3:  16,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                2         : {1:  nodef,
                             2:  0,
                             3:  16,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                3         : {1:  nodef,
                             2:  nodef,
                             3:  0,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef}},
         'P' : {
                1         : {1: 64,
                             2:  2,
                             3:  0,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                2         : {1:  nodef,
                             2:  4,
                             3:  0,
                             4 : 2,
                             5 : nodef,
                             6 : nodef},
                3         : {1:  nodef,
                             2:  nodef,
                             3:  0,
                             4 : 1,
                             5 : 2,
                             6 : nodef},
                4         : {1:  nodef,
                             2:  nodef,
                             3:  nodef,
                             4 : 1,
                             5 : 0,
                             6 : nodef}},
         'S' : {
                1         : {1:  2,
                             2:  0,
                             3:  64,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                2         : {1:  nodef,
                             2:  0,
                             3:  32,
                             4 : 1,
                             5 : nodef,
                             6 : nodef},
                3         : {1:  nodef,
                             2:  nodef,
                             3:  1,
                             4 : 0,
                             5 : 2,
                             6 : 2},
                4         : {1:  nodef,
                             2:  nodef,
                             3:  nodef,
                             4 : 4,
                             5 : 2,
                             6 : 0}}
         }


def eval_bond_order(atoms,nn,bo,verbose=3):
    """
        Evalutate bond order
        --------------------
        Calculate total penalty score (tps).
        The optimum is tps = 0.0.

    """
    co = numpy.zeros(len(atoms))
    va = numpy.zeros(len(atoms))
    va_max = numpy.zeros(len(atoms))
    nn_opt = numpy.zeros(len(atoms))
    ftype = numpy.zeros(len(atoms),dtype=object)
    tps = numpy.zeros(len(atoms))
    for i in range(len(atoms)):
        co[i] = len(nn[i].nonzero()[0])
        va[i] = bo[i, :].sum()
        va_max[i] = max_coordination[symbol2number[atoms[i].symbol]]
        nn_atoms = nn[i].nonzero()[0].tolist()
        sym_i = atoms[i].symbol
        symbols_j = atoms[nn_atoms].symbols
        values, counts = numpy.unique(symbols_j,return_counts=True)
        if sym_i == 'C':
            for s,c in zip(values,counts):
                # len(symbols_j) to not eval CO2 molecule
                if len(symbols_j) > 2 and s == 'O' and c == 2:
                    typ = 'COO'
                else:
                    typ = 'default'
        if sym_i == 'N':
            for s,c in zip(values,counts):
                # len(symbols_j) to not eval NO2 molecule
                if len(symbols_j) > 2 and s == 'O' and c == 2:
                    typ = 'NOO'
                else:
                    typ = co[i]

        if sym_i in ['C','N','Si']:
            ftype[i] = typ
            try: 
                aps = aps_bo[sym_i][typ][va[i]]
            except: 
                aps = nodef 
            tps[i] = aps
    if verbose > 3:
        print(f'total pentalty score (tps) : {tps.sum()}')
    return tps.sum()

# Pi electron count 
# https://pubchem.ncbi.nlm.nih.gov//edit3/index.html
# CC(C)C  -> 1 Pi
# CC(C=)C -> 1 Pi
# CC(C)=C -> 1 Pi
# CCC     -> 1 Pi
# CC=C    -> 1 Pi

def get_aromatic_perception(atoms,nn,bo,mmtypes,btype='LEWIS',verbose=3):
    """
        Get aromatic perception 
        -----------------------
        Determine aromatic rings in atoms. 

        Workflow 
            - [1] find cycles (5,6 ring) in molecular graph 
            - [2] check coplanarity 
            - [3] use LDQ bo to check bo_ij == 1.5 
    """
    aromatic = numpy.zeros(len(atoms),dtype=int)
    visited = numpy.zeros(len(atoms),dtype=int)
    # molecule as graph 
    molgraph = {}
    for i in range(len(atoms)): 
        dct_tmp = {i : nn[i].nonzero()[0].tolist()}
        molgraph.update(dct_tmp)
    # find 5 rings and 6 rings 
    cycles = [path for node in molgraph for path in get_DFS_cycles(molgraph, node, node) if len(path) == 5 or len(path) == 6]
    print(f'cycles: {cycles}')
    if not cycles: 
        print("We break out of get_aromatic_perception") 
        return aromatic, mmtypes, cycles, bo
    cycles = numpy.array(cycles)
    sort_cycles = numpy.sort(cycles) 
    # find unique cycles/rings 
    #unique,index,counts = numpy.unique(cycles,return_counts=True,return_index=True) 
    sorted_unique_cycles, idx  =numpy.unique(sort_cycles,axis=0,return_index=True)
    unique_cycles = cycles[idx]

    for unique in unique_cycles:
        print(f'cycle: {unique}')
        # check coplanarity 
        # are combinations of 4 points from ring/cycle 
        # in one plane? 
        pos = atoms[unique.tolist()].positions
        dets = numpy.array([numpy.linalg.det(numpy.array(x[:3]) - x[3]) for x in combinations(pos, 4)])
        eps = 0.1 
        coplanar = (dets < eps).all()
        print(f'coplanar: {coplanar}')
        if coplanar:
            for idx in range(len(unique)):
            # construct connected indicies (i,j)
            # this way we loop over all connected
            # bonds in the path
                #if visited[i] == 1:
                #   check_idx_j = nn[i].nonzero()[0] 
                #   co = len(check_idx_j) 
                #   check_idx_j = (check_idx_j[check_idx_j!= j]).tolist()
                #   ve = get_max_valence(atoms[i].symbol,co)
                #   bo_j = bo[i,check_idx_j].sum()
                #   print(f'visited[i]: {i} {j} {check_idx_j} {bo[i,check_idx_j].sum()} {ve}')
                #if visited[i] == 0: 
                #   bo_j = 0
                #   check_idx_j = nn[i].nonzero()[0]
                #   co = len(check_idx_j)
                #   ve = get_max_valence(atoms[i].symbol,co)

                if idx < len(unique)-1:
                    i,j = unique[idx],unique[idx+1]
                if idx == len(unique)-1:
                    i,j = unique[-1],unique[0]
                if btype == 'LDQ':
                    bo[i,j] = 1.5
                    bo[j,i] = 1.5
                if btype == 'LEWIS':
                    if idx % 2: 
                        bo_tmp = 1 
                    if not idx % 2:
                        bo_tmp = 2
                    #if bo_j + bo_tmp > ve or bo_j + bo_tmp < ve: 
                    #    print('adjusted by condition')
                    #    bo_tmp = ve - bo_j
                    #    print(f'adjusted by condition: bo_tmp {bo_tmp} ve {bo_j+bo_tmp} vmax {ve}')
                    #print(f'captain lewis : {i} {j} {bo_tmp}')
                    bo[i,j] = bo_tmp
                    bo[j,i] = bo_tmp 
                mmtypes[i] = atoms[i].symbol +'_R'
                mmtypes[j] = atoms[j].symbol +'_R'
                aromatic[i] = 1 
                aromatic[j] = 1 
                # 
                visited[i] = 1 
    if verbose > 3: 
        print(aromatic,mmtypes)
    return aromatic, mmtypes, unique_cycles, bo 

def assign_bond(atoms,nn,bonds,aromatic,bo,i,j,btype='LEWIS'):
    b = bonds.get_bond(i,j)
    #if b.status == 'unassigned' and btype == 'LDQ':
    #    bo_tmp = 1.5 
    #    status_tmp = 'assigned'
    #    bo[i,j] = bo_tmp
    #    bo[j,i] = bo_tmp
    #    b.status = status_tmp
    #    b.bo = bo_tmp
    #    bonds.set_bond(i,j,b)
    #    bonds.set_bond(j,i,b)

    if b.status == 'unassigned':
            set_double = True
            b_nn_j = 0
            b_nn_i = 0
            # check neighbours of node i
            idx_j = nn[i].nonzero()[0].tolist()
            for nnj in idx_j:
                bij= bonds.get_bond(i,nnj)
                if nnj != j:
                    b_nn_j += bij.bo
                # if one neigbour already has bo > 1
                # we may not want to set the current bo > 1
                if bij.bo > 1:
                    set_double = False
            # check neigbours of node j
            idx_i = nn[j].nonzero()[0].tolist()
            for nni in idx_i:
                bji= bonds.get_bond(j,nni)
                if nni != i:
                    b_nn_i += bji.bo
                # if one neigbour already has bo > 1
                # we may not want to set the current bo > 1
                if bji.bo > 1:
                   set_double = False
            print(f'set_double: {set_double} b_nn_j: {b_nn_j} b_nn_i: {b_nn_i}')
            sym_bi = atoms[i].symbol
            max_va = get_max_valence(sym_bi,len(idx_j))
            max_bo_tmp_j = max_va - b_nn_j
            max_bo_tmp_i = max_va - b_nn_i
            if btype == 'LEWIS':
                if max_bo_tmp_j == 2 and set_double == True:
                    bo_tmp = 2
                    status_tmp = 'assigned'
                    aromatic[i] = 1
                    aromatic[j] = 1
                if max_bo_tmp_j == 2 and set_double == False:
                    bo_tmp = 1
                    status_tmp = 'assigned'
                if max_bo_tmp_j ==1:
                    bo_tmp = 1
                    status_tmp = 'assigned'
                    aromatic[i] = 1
                    aromatic[j] = 1
            if btype == 'LDQ':
                print(f'>>>>>>>>>>>>> max_bo_tmp_j : {max_bo_tmp_j}')
                bo_tmp = max_bo_tmp_j # 1.5
                status_tmp = 'assigned'

                if max_bo_tmp_j == 1: 
                     bo_tmp = 1
                     status_tmp = 'assigned'
                if max_bo_tmp_j == 1.5:
                     bo_tmp = 1.5
                     status_tmp = 'assigned'
                     aromatic[i] = 1
                     aromatic[j] = 1
                if max_bo_tmp_j == 2:
                     bo_tmp = 2
                     status_tmp = 'assigned'
                
                #if max_bo_tmp_j == 2 and set_double == True:
                #    bo_tmp = 1.5
                #    status_tmp = 'assigned'
                #if max_bo_tmp_j == 2.5 and set_double == True:
                #    bo_tmp = 1.5
                #    status_tmp = 'assigned'
                #if max_bo_tmp_j == 3 and set_double == True:
                #    bo_tmp = 1
                #    status_tmp = 'assigned'
                #if max_bo_tmp_j == 2 and set_double == False:
                #    bo_tmp = 1
                #    status_tmp = 'assigned'
            print(f'{atoms[bij.i].symbol} {atoms[bij.j].symbol} {bij.status} {bij.bo} max_bo_tmp: {max_bo_tmp_j} bo_tmp: {bo_tmp} max_va: {max_va} ')
            bo[i,j] = bo_tmp
            bo[j,i] = bo_tmp
            b.status = status_tmp
            b.bo = bo_tmp
            bonds.set_bond(i,j,b)
            bonds.set_bond(j,i,b)
    return bonds, aromatic, bo

def magic_aromatic_perception(atoms,nn,bo,mmtypes,btype='LEWIS',verbose=3):
    aromatic = numpy.zeros(len(atoms),dtype=int)
    rc = numpy.array([covalent_radii[symbol2number[ni.symbol]] for ni in atoms])
    nn, bonds = get_nn_bonds(atoms,rc=rc)
    if verbose > 3:
        print(f'bonds: {bonds}')
    co = numpy.zeros(len(atoms))
    va = numpy.zeros(len(atoms))
    #bo = numpy.zeros((len(atoms),len(atoms)))
    # molecule as graph
    molgraph = get_molgraph(atoms,nn,verbose=verbose)
    # Get unique cycles 
    # find 5 rings and 6 rings 
    cycles = [path for node in molgraph for path in get_DFS_cycles(molgraph, node, node) if len(path) == 5 or len(path) == 6]
    if not cycles: 
        return aromatic, mmtypes, cycles, bo
    cycles = numpy.array(cycles)
    print(f'cycles: {cycles} number cycles : {len(cycles)}')
    sort_cycles = numpy.sort(cycles)
    # find unique cycles/rings 
    sorted_unique_cycles, idx = numpy.unique(sort_cycles,axis=0,return_index=True)
    unique_cycles = cycles[idx]
    #print(f'unique_cycles: {unique_cycles} number unique_cycles : {len(unique_cycles)}')
    #u, ind, c = numpy.unique(sort_cycles,return_counts=True,return_index=True)
    #print(u,ind,c)
    #print(atoms[unique_cycles[0].tolist()])
    ##GUI(atoms[u.tolist()])
    #cyclic_atoms = atoms[u.tolist()]
    #cyclic_molgraph = get_molgraph(cyclic_atoms,nn,verbose=verbose)
    #fused_cycles = [path for node in cyclic_molgraph for path in get_DFS_cycles(molgraph, node, node)]
    #fused_cycles = numpy.array(fused_cycles)
    #sort_fused_cycles = numpy.sort(fused_cycles)
    #fused_cycles = [path for node in cyclic_molgraph for path in get_DFS_path(molgraph,node)]
    #print(f'fused cycles: {fused_cycles} len: {fused_cycles} len(cyc_molgraph) : {len(cyclic_molgraph)}')
    #p_max = get_DFS_longest_paths(molgraph,cyclic_molgraph.keys())
    #print(p_max[1])
    # find unique cycles/rings
    #unique,index,counts = numpy.unique(cycles,return_counts=True,return_index=True)
    #sorted_unique_fused_cycles, idx = numpy.unique(sort_fused_cycles,axis=0,return_index=True)
    #unique_fused_cycles = fused_cycles[idx]
    #print(unique_fused_cycles)

    for i in range(len(atoms)):
        co[i] = len(nn[i].nonzero()[0])
        va[i] = max_coordination[symbol2number[atoms[i].symbol]]
    # Assign for all bonds bo = 1 
    # Fill X-H bonds, may correct 
    for b in bonds: 
        b.bo = 1
        bo[b.i,b.j] = 1 
        bo[b.j,b.i] = 1
        if atoms[b.i].symbol == 'H' or atoms[b.j].symbol == 'H':
            b.status = 'assigned'
    # We have now a list of all aromatic cycles. 
    # We determine a all permutations of these aromatic cycles. 
    # We assign the bond orders starting with different orders of the cycles. 
    # We run this as long we find (hopefully) a good tps. 
    perm_list = [p for p in permutations(unique_cycles,len(unique_cycles))]
    Nperm = len(perm_list) 
    Niter = 0
    tps = 200
    if btype == 'LDQ': 
        for unique in unique_cycles:
            print(f'unique_cycle: {unique}')
            # Loop over connected nodes in path
            for idx in range(len(unique)):
                # construct connected indicies (i,j)
                # this way we loop over all connected
                # bonds in the path
                if idx < len(unique)-1:
                    i,j = unique[idx],unique[idx+1]
                if idx == len(unique)-1:
                    i,j = unique[-1],unique[0]
                b = bonds.get_bond(i,j)
                b.bo = 1.5
                bo[b.i,b.j] = 1.5 
                bo[b.j,b.i] = 1.5 
                bonds.set_bond(i,j,b)
                bonds.set_bond(j,i,b)
                #aromatic[i] = 1
                #aromatic[j] = 1

    bo_ref = bo.copy()
    bonds_ref = deepcopy(bonds)
    while tps > 0 and Niter < Nperm: 
        bo = bo_ref.copy()
        bonds = deepcopy(bonds_ref)
        for unique in perm_list[Niter]:
            print(f'unique_cycle: {unique}')
            # Loop over connected nodes in path
            for idx in range(len(unique)):
                # construct connected indicies (i,j)
                # this way we loop over all connected
                # bonds in the path
                if idx < len(unique)-1:
                    i,j = unique[idx],unique[idx+1]
                if idx == len(unique)-1:
                    i,j = unique[-1],unique[0]
                bonds, aromatic, bo = assign_bond(atoms,nn,bonds,aromatic,bo,i,j,btype)
                aromatic[i] = 1
                aromatic[j] = 1
        for b in bonds:
            print(f'bond {b.i} {b.j} {atoms[b.i].symbol} {atoms[b.j].symbol} {b.status} {b.bo}')
        tps = eval_bond_order(atoms,nn,bo,verbose=3)
        print(f'>>>>> Niter: {Niter} TPS: {tps}')
        Niter += 1
            #if count > 0: 
            #    break 
    
    # After the aromatic perception there can be still 
    # unassigned bonds. 
    # In principle a more general magicbonds can be applied here.
    # But the iternal logic of magicbonds is different. 
    for b in bonds: 
        bonds, aromatic, bo = assign_bond(atoms,nn,bonds,aromatic,bo,b.i,b.j)
        print(f'bond {b.i} {b.j} {atoms[b.i].symbol} {atoms[b.j].symbol} {b.status} {b.bo}')
    for i in range(0, len(atoms)):
        # get current coordination per atom
        va[i] = bo[i, :].sum()
    print(f'magic aromatic va: {va}')
    return aromatic, mmtypes, unique_cycles, bo

def get_is_amide(idx,atoms,nn,bo,mmtypes,rules='UFF'): 
    """
        Functional group check: Amide 
        -----------------------------
        if is_amide: 
            bo[C,N] = bo[N,C] = 1.41 
            mmtypes[C] = 'C_R'
            mmtypes[N] = 'N_R'
    """
    is_amide = False
    has_O = False 
    idx_O = None
    has_N = False
    idx_N = None 
    
    if atoms[idx].symbol == 'C': 
        idx_j = nn[idx].nonzero()[0].tolist()
        for j in idx_j: 
            sym_j = atoms[j].symbol 
            if 'O' == sym_j:
                has_O = True 
                idx_O = j 
            if 'N' == sym_j:
                has_N = True
                idx_N = j
            if has_O and has_N: 
                is_amide = True
                # Change types to aromatic 
                if rules == 'UFF': 
                    mmtypes[idx] = 'C_R' 
                    mmtypes[idx_N] = 'N_R' 
                if rules == 'openbabel': 
                    mmtypes[idx] = 'C_2'
                    mmtypes[idx_N] = 'N_2'
                # Change bond order
                bo[idx,idx_N] = 1.41 
                bo[idx_N,idx] = 1.41 
    return is_amide, bo,  mmtypes 

def get_is_nitro(idx,atoms,nn,bo,mmtypes):
    """
        Functional group check: Nitro
        -----------------------------
        if is_nitro and c == 2:
            bo[N,O] = bo[O,N] = 1.5
            mmtypes[O] = 'O_R'
            mmtypes[N] = 'N_R'
        if is_nitro and c == 3 :
            bo[N,O] = bo[O,N] = 1.33
            mmtypes[N] = 'N_R'
            mmtypes[O] = 'O_R'
    """
    is_nitro = False
    
    if atoms[idx].symbol == 'N':
        idx_j = nn[idx].nonzero()[0].tolist()
        
        symbols_j = numpy.array([a.symbol for a in atoms[idx_j]])
        values, counts = numpy.unique(symbols_j,return_counts=True)
        for s,c in zip(values,counts):
            if s == 'O' and c == 2:
                bo_tmp = 1.5
                mmtypes[idx] = 'N_R'
                is_nitro = True
            if s == 'O' and c == 3:
                bo_tmo = 1.33
                mmtypes[idx] = 'N_R'
                is_nitro = True
        if is_nitro:
            for j in idx_j: 
                if atoms[j].symbol == 'O':
                    bo[j,idx] = bo_tmp 
                    bo[idx,j] = bo_tmp 
                    # Change types to aromatic
                    mmtypes[j] = 'O_R'
    return is_nitro, bo, mmtypes


def get_is_carboxylate(idx,atoms,nn,bo,mmtypes,rules='UFF'):
    """
        Functional group check: Carboxylate
        -----------------------------
        if is_carboxylate and c == 2:
            bo[C,O] = bo[O,C] = 1.5
            mmtypes[C] = 'C_R'
            mmtypes[O] = 'O_R'
        if is_carboxylate and c == 3: 
            bo[C,O] = bo[O,C] = 1.33
            mmtypes[C] = 'C_R'
            mmtypes[O] = 'O_R'
    """
    is_carboxylate = False

    if atoms[idx].symbol == 'C':
        idx_j = nn[idx].nonzero()[0].tolist()

        symbols_j = numpy.array([a.symbol for a in atoms[idx_j]])
        values, counts = numpy.unique(symbols_j,return_counts=True)
        for s,c in zip(values,counts):
            if s == 'O' and c == 2:
                if rules == 'UFF':
                    bo_tmp = 1.5
                    mmtypes[idx] = 'C_R'
                if rules == 'openbabel':
                    bo_tmp = 1.0
                    mmtypes[idx] = 'C_2'
                is_carboxylate = True
            if s == 'O' and c == 3:
                if rules == 'UFF':
                    bo_tmp = 1.33
                    mmtypes[idx] = 'C_R'
                if rules == 'openbabel':
                    bo_tmp = 1
                    mmtypes[idx] = 'C_2'
                is_carboxylate = True
        if is_carboxylate: 
            for j in idx_j:
                if atoms[j].symbol == 'O':
                    # Change types to aromatic
                    if rules == 'UFF':
                        mmtypes[j] = 'O_R'
                    if rules == 'openbabel':
                        mmtypes[j] = 'O_2'
                        if j % 2: 
                            bo_tmp *=2 
                    bo[j,idx] = bo_tmp
                    bo[idx,j] = bo_tmp

    return is_carboxylate, bo, mmtypes

def get_is_enol_ether(idx,atoms,nn,bo,mmtypes):
    """
        Functional group check: Enol Ether 
        -----------------------------
        if is_enol_either: 
            mmtypes[O] = 'O_R'
    """
    is_enol_either = False
    has_O = False
    idx_C = None
    has_C = False
    idx_C = None

    if atoms[idx].symbol == 'C':
        idx_j = nn[idx].nonzero()[0].tolist()
        for j in idx_j:
            sym_j = atoms[j].symbol
            if 'O' == sym_j:
                has_O = True
                idx_O = j
            if 'C' == sym_j:
                has_N = True
                idx_N = j
            if has_O and has_C:
                is_enol_either = True
                # Change types to aromatic 
                mmtypes[idx_O] = 'O_R'
    return is_enol_either, bo,  mmtypes


def get_functional_group_perception(atoms,nn,bo,mmtypes,rules,verbose=3): 
    """
        Function group perception 
        -------------------------
    """
    is_amide = numpy.zeros(len(atoms),dtype=bool)
    is_nitro = numpy.zeros(len(atoms),dtype=bool)
    is_carboxylate = numpy.zeros(len(atoms),dtype=bool)
    is_enol_ether = numpy.zeros(len(atoms),dtype=bool)
    # Amide:  O - C - N 
    # (N,C), (C,N) -> BO = 1.41 
    for i in range(len(atoms)):
        if atoms[i].symbol == 'C': 
            tmp_is_amide, bo, mmtypes = get_is_amide(i,atoms,nn,bo,mmtypes,rules) 
            is_amide[i] = tmp_is_amide
            tmp_is_carboxylate, bo, mmtypes = get_is_carboxylate(i,atoms,nn,bo,mmtypes,rules)
            is_carboxylate[i] = tmp_is_carboxylate
            tmp_is_enol_ether, bo, mmtypes = get_is_enol_ether(i,atoms,nn,bo,mmtypes)
            is_enol_ether[i] = tmp_is_enol_ether
            if verbose > 3: 
                print(f'is_amide: {tmp_is_amide} {is_amide}')
                print(f'is_carboxylate: {tmp_is_carboxylate} {is_carboxylate}')
                print(f'is_enol_ether: {tmp_is_enol_ether} {is_enol_ether}')
        if atoms[i].symbol == 'N':
            tmp_is_nitro, bo, mmtypes = get_is_nitro(i,atoms,nn,bo,mmtypes)
            is_nitro[i] = tmp_is_nitro
            if verbose > 3: 
                print(f'is_nitro: {tmp_is_nitro} {is_nitro}')

    return is_amide, is_nitro, is_carboxylate, is_enol_ether, bo, mmtypes 

class CoreMotifs: 
    """
        CoreMotifs class 
        ----------------
    """
    def __init__(self,C,atom,symbols,positions,elec_symbols=['X','He']):
        self.C = C 
        self.symbol = atom.symbol 
        self.position = atom.position 
        self.sym_fod1 = elec_symbols[0]
        self.sym_fod2 = elec_symbols[1]
        self.offset = 0.002 
        self.symbols = symbols
        self.positions = positions
        self._Na = 0
        self._Nb = 0 

    def _count_e(self,symbol): 
        if symbol == self.sym_fod1: 
            self._Na += 1 
        if symbol == self.sym_fod2:
            self._Nb += 1

    def _set_e(self,symbol,offset=0): 
        self._count_e(symbol)
        self.symbols += [symbol]
        self.positions.append(self.position+offset)

    def kernel(self): 
        if self.C == 1: 
            # 1s 
            self._set_e(self.sym_fod1) 
        if self.C == 2: 
            # two 1s 
            self._set_e(self.sym_fod1)
            self._set_e(self.sym_fod2,offset=self.offset)
        if self.C == 3:
            # triangle
            self._set_e(self.sym_fod1)
            self._set_e(self.sym_fod2,offset=self.offset)
            self._set_e(self.sym_fod1,offset=[self.offset[0],self.offset[1],self.offset[2]*4])
        if self.C == 4:
            # tetrahedron 
            self._set_e(self.sym_fod1)
            self._set_e(self.sym_fod2,offset=self.offset)
            self._set_e(self.sym_fod1,offset=[self.offset[0],self.offset[1],self.offset[2]*(+40)])
            self._set_e(self.sym_fod1,offset=[self.offset[0],self.offset[1],self.offset[2]*(-40)])

def perpendicular_vector(v):
    """
        perpendicular vector
        --------------------
        
        Output 
        ------
        app : numpy.array(), arbitary perpendicular point (app) 
    """
    if v[1] == 0 and v[2] == 0:
        if v[0] == 0:
            raise ValueError('zero vector')
        else:
            return numpy.cross(v, [0, 1, 0])
    return numpy.cross(v, [1, 0, 0])

def rotation_matrix(axis, theta):
    """
        Rotation matrix 
        ---------------
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.

        Input 
        -----
        axis:   numpy.array(), rotation axis 
        theta:  float(), rotation angles [radians] 

    """
    axis = numpy.asarray(axis)
    axis = axis / numpy.sqrt(numpy.dot(axis, axis))
    a = numpy.cos(theta / 2.0)
    b, c, d = -axis * numpy.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return numpy.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

class LoneMotifs: 
    """
        LoneMotifs class 
        ----------------
    """
    def __init__(self,R,idx,atoms,nn,sp,symbols,positions,elec_symbols=['X','He']):
        self.R = R 
        self.i = idx
        self.pos = atoms[idx].position
        self.atoms = atoms 
        self.nn = nn 
        self.sp = sp 
        self.sym_fod1 = elec_symbols[0]
        self.sym_fod2 = elec_symbols[1]
        self.offset = 0 #0.002
        self.symbols = symbols 
        self.positions = positions 
        self._Na = 0
        self._Nb = 0

    def _count_e(self,symbol):
        if symbol == self.sym_fod1:
            self._Na += 1
        if symbol == self.sym_fod2:
            self._Nb += 1

    def _set_e(self,symbol,position,offset=0):
        self._count_e(symbol)
        self.symbols += [symbol]
        self.positions.append(position+offset)

    def _get_ba(self):
        """
            Get ba
            ------
            Get direction/orientation 
            for lone electrons. 
        """
        idx_j = self.nn[self.i].nonzero()[0].tolist()
        ba = numpy.zeros_like(self.pos)
        BA = []
        for j in idx_j:
            tmp_ba = self.atoms[j].position - self.pos
            BA.append(tmp_ba) 
            ba += tmp_ba 
        print(f'lonemotif: pos: {self.pos} ba: {ba} sp {self.sp[j]} {self.sp[self.i]}')
        n = numpy.linalg.norm(ba)
        # Workaround for ZeroDevision 
        if n > 0:
            # sign choice depends on the defintion of ba (or ab) 
            ba = -1*ba/n
        ba /=2 
        ba += self.pos 
        return ba, BA  

    def kernel(self): 
        ba, BA = self._get_ba()
        
        if self.R == 1 or self.R == 2: 
            check1_sp = self.sp[self.i] == 3
            idx_j = self.nn[self.i].nonzero()[0].tolist()
            sp_j = self.sp[idx_j]
            print(f'check1_sp: {check1_sp} {sp_j}')
            if check1_sp:
                print('Lone: special case N sp3')
                # e.g., Conformer3D_CID_142199 
                # see https://stackoverflow.com/questions/4372556/given-three-points-on-a-tetrahedron-find-the-4th
                # Find a position for the lone electron on a tetrahedra.
                # Or in other words find the 4th point on a tetrahedra 
                # spanned by the nuclei around the current one. 
                idx_j = self.nn[self.i].nonzero()[0].tolist()
                pos_j = self.atoms[idx_j].positions 
                sym_j = self.atoms[idx_j].symbols 
                com = pos_j.mean(axis=0)
                axis = numpy.cross(pos_j[2] - pos_j[0],pos_j[1] - pos_j[0])
                n = numpy.linalg.norm(axis) 
                axis /= n 
                axis *= numpy.sqrt(2/3)
                # SS: [Question] : How to determine if top of bottom? 
                # top 
                # ba2 = com + axis 
                # botton 
                ba2 = com - axis
                # If ba2 is parallel to ba (and with the atom) 
                # the the original ba has the correct sign (top vs. bottom). 
                # If this case is fullfilled we stay with the original ba 
                # otherwise we take the new ba. 
                n = numpy.linalg.norm(numpy.cross(ba-self.pos,ba2-self.pos))
                check =  numpy.isclose(n,0,0,1e-3)
                if not check: 
                    ba = ba2

        if self.R == 1: 
            # We have one lone electron
            # We need to deside which spin channel the lone electrons belongs to.
            Na, Nb, M  = check_spin(self.symbols)
            if Na > Nb:
                sym_X = self.sym_fod2
            if Nb >= Na:
                sym_X = self.sym_fod1
            self._set_e(sym_X,ba)

        if self.R == 2:
            # We have two lone electrons 
            self._set_e(self.sym_fod1,ba)
            self._set_e(self.sym_fod2,ba,offset=self.offset)

        if self.R == 3:
            # We have three lone electrons 
            if len(BA) == 2 or len(BA) == 3: # SS: 3? 
                app = numpy.cross(BA[0],BA[1])
            if len(BA) == 1:
                # DANGER: This is not optimal
                # arbitary perpendicular point
                angle = [0,numpy.pi/2.][-1]
                rot_mat = rotation_matrix(ba-self.pos,angle)
                app = perpendicular_vector(ba)
                app = numpy.dot(rot_mat,app)
            n = numpy.linalg.norm(app)
            app /= n
            app /= 2
            self._set_e(self.sym_fod1,ba+app-[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba+app-[20*self.offset,0,0],offset=self.offset)
            # We have two unpaired electron pairs and one lone electron. 
            # We need to deside which spin channel the lone electrons belongs to. 
            Na, Nb, M  = check_spin(self.symbols)
            if Na > Nb:
                sym_X = self.sym_fod2
            if Nb >= Na:
                sym_X = self.sym_fod1
            self._set_e(sym_X,ba-app+[20*self.offset,0,0])

        if self.R == 4:
            # We have 4 lone electrons 
            print(f'len(BA): {BA}')
            if len(BA) == 2 or len(BA) == 3: # SS: 3 ? 
                app = numpy.cross(BA[0],BA[1]) 
            if len(BA) == 1:
                # DANGER: This is not optimal
                # arbitary perpendicular point
                angle = [0,numpy.pi/2.][-1]
                rot_mat = rotation_matrix(ba-self.pos,angle)
                app = perpendicular_vector(ba)
                app = numpy.dot(rot_mat,app)
            n = numpy.linalg.norm(app) 
            app /= n
            app /= 2
            self._set_e(self.sym_fod1,ba+app-[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba+app-[20*self.offset,0,0],offset=self.offset)
            self._set_e(self.sym_fod1,ba-app+[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba-app+[20*self.offset,0,0],offset=self.offset)

        if self.R == 5: 
            # We have 5 lone electrons 
            # Idea is the case as R == 6 - 1 
            if len(BA) == 2:
                app = numpy.cross(BA[0],BA[1])
            if len(BA) == 1:
                # DANGER: This is not optimal
                # arbitary perpendicular point
                angle = [0,numpy.pi/2.][-1]
                rot_mat = rotation_matrix(ba-self.pos,angle)
                app = perpendicular_vector(ba)
                app = numpy.dot(rot_mat,app)
                app2 = perpendicular_vector(app)
            n = numpy.linalg.norm(app)
            app /= n
            app /= 2
            self._set_e(self.sym_fod1,ba+app-[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba+app-[20*self.offset,0,0],offset=self.offset)
            self._set_e(self.sym_fod1,ba-app+[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba-app+[20*self.offset,0,0],offset=self.offset)
            # We have two unpaired electron pairs and one lone electron. 
            # We need to deside which spin channel the lone electrons belongs to. 
            Na, Nb, M  = check_spin(self.symbols)
            if Na > Nb: 
                sym_X = self.sym_fod2 
            if Nb >= Na:
                sym_X = self.sym_fod1
            self._set_e(sym_X,self.pos+app2+[20*self.offset,0,20*self.offset])

        if self.R == 6: 
            # We have 6 lone electrons 
            if len(BA) == 2:
                app = numpy.cross(BA[0],BA[1])
            if len(BA) == 1:
                # DANGER: This is not optimal
                # arbitary perpendicular point
                angle = [0,numpy.pi/2.][-1]
                rot_mat = rotation_matrix(ba-self.pos,angle)
                app = perpendicular_vector(ba)
                app = numpy.dot(rot_mat,app)
                app2 = perpendicular_vector(app)
            n = numpy.linalg.norm(app)
            app /= n
            app /= 2
            self._set_e(self.sym_fod1,ba+app-[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba+app-[20*self.offset,0,0],offset=self.offset)
            self._set_e(self.sym_fod1,ba-app+[20*self.offset,0,0])
            self._set_e(self.sym_fod2,ba-app+[20*self.offset,0,0],offset=self.offset)
            self._set_e(self.sym_fod1,self.pos+app2+[20*self.offset,0,20*self.offset])
            self._set_e(self.sym_fod2,self.pos+app2+[20*self.offset,0,20*self.offset],offset=self.offset)

class BondMotifs: 
    """
        BondMotifs class 
        ----------------
    """
    def __init__(self,bo,bo_ref,sp,nn,i,j,atoms,symbols,positions,elec_symbols=['X','He']):
        self.bo = bo
        self.bo_ref = bo_ref
        self.sp = sp
        self.nn = nn 
        self.i = i 
        self.j = j
        self.posA = atoms[i].position
        self.posB = atoms[j].position
        self.atoms = atoms 
        self.sym_fod1 = elec_symbols[0]
        self.sym_fod2 = elec_symbols[1]
        self.offset = numpy.array([0.0,0.0,0.0])
        self.symbols = symbols
        self.positions = positions
        self._Na = 0
        self._Nb = 0

    def _count_e(self,symbol):
        if symbol == self.sym_fod1:
            self._Na += 1/2.
        if symbol == self.sym_fod2:
            self._Nb += 1/2.


    def _set_e(self,symbol,position,offset=numpy.array([0,0,0])):
        """
            Set e
            -----
            "Set the electron" means 
            update symbols and positions. 
        """
        self._count_e(symbol)
        self.symbols += [symbol]
        self.positions.extend([position+offset])

    def _get_bond_center(self):
        """
            Get bond center 
            ---------------
        """
        return (self.posA+self.posB)/2.

    def _get_posAB(self): 
        """
            Get posAB
            ---------
            Get vector between points A and B. 
        """
        return self.posB - self.posA

    def kernel(self): 
        """
            Kernel function 
            ---------------

            Rules
            -----
            bo = 1 and 1.41 is mapped to single bond 
            bo = 1.5 is mapped to LDQ (1,2) or (2,1) bond 
            bo = 2 is mapped to double bond 
            bo = 3 is mapped to triple bond 
        """
        bc = self._get_bond_center()
        posAB = self._get_posAB() 
        n = numpy.linalg.norm(posAB)
        posAB /= n
        # Single bond 
        if self.bo == 1 or self.bo == 1.41:
            # Special rule for X-H, H-X bonds. 
            # The bonding electrons are placed closer to the H atom. 
            if self.atoms[self.i].symbol == 'H' or self.atoms[self.j].symbol == 'H': 
                bc += posAB*0.3 
            # Point motif: motif_1 
            self._set_e(self.sym_fod1,bc)
            self._set_e(self.sym_fod2,bc,offset=self.offset)

        # Double bond or 1.5 bond  
        if self.bo == 2 or self.bo == 1.5: 
            # Line motif: motif_2 
            motif_2 = numpy.array([[0,0,+1.0],
                                   [0,0,-1.0]])*0.75
            # if z-component of posAB is close to zero -> 
            # no need to rotate (posAB automatically 
            # aligned with perpendicular direction of motif_2)
            if numpy.isclose(posAB[2],0,0,1e-3):
                v1 = motif_2[0,:]
                v2 = motif_2[1,:]
            else:
                # Rotate the motif such that its perpendicular direction 
                # aligns with the bond axis (posAB)
                axis = [0,1,0] # perpendicular axis for the motif
                n_axis = numpy.linalg.norm(axis)
                angle = numpy.arccos(numpy.dot(posAB,numpy.array(axis))/(n*n_axis))
                rot_axis = numpy.cross(numpy.array(axis),posAB)
                self.rot_mat = rotation_matrix(rot_axis,angle)
                v1 = numpy.dot(self.rot_mat,motif_2[0,:])
                v2 = numpy.dot(self.rot_mat,motif_2[1,:])

            # If the A and/or B are sp2 hybridized 
            # the bonding electrons have a rotational 
            # degree of freedom. 
            # We check for the hybridization of A/B 
            # and if one of them is sp2, 
            # we calculate the molecular plane 
            # and the bonding electrons are placed 
            # perpendicular to this plane
            check1_sp = self.sp[self.i] == 2 # posA 
            check2_sp = self.sp[self.j] == 2 # posB 
            if check1_sp:
                ref_idx = self.i
                idx_j = self.nn[ref_idx].nonzero()[0].tolist()
                if len(idx_j) < 2:
                    ref_idx = self.j
                    idx_j = self.nn[ref_idx].nonzero()[0].tolist()
            if check2_sp:
                ref_idx = self.j
                idx_j = self.nn[ref_idx].nonzero()[0].tolist()
                if len(idx_j) < 2:
                    ref_idx = self.i 
                    idx_j = self.nn[ref_idx].nonzero()[0].tolist()
            if check1_sp or check2_sp:
                ## ref_idx 
                #rot_axis = numpy.cross(self.atoms[idx_j[0]].position-self.atoms[ref_idx].position,self.atoms[idx_j[1]].position-self.atoms[ref_idx].position)
                #v1v2 = v2 - v1
                #n1 = numpy.linalg.norm(rot_axis) 
                #n2 = numpy.linalg.norm(v1v2)
                #angle = numpy.arccos(numpy.dot(v1v2,rot_axis)/(n1*n2)) 
                ## rotate around posAB
                #self.rot_mat = rotation_matrix(posAB,angle) 
                #v1 = numpy.dot(self.rot_mat,v1) 
                #v2 = numpy.dot(self.rot_mat,v2)
                # Determine perpendicular vector to molecular plane
                # Place bond FODs at bond center using this vector
                #
                app = numpy.cross(self.atoms[idx_j[0]].position-self.atoms[ref_idx].position,self.atoms[idx_j[1]].position-self.atoms[ref_idx].position)
                n1 = numpy.linalg.norm(app)
                app /= n1 # normalize
                app *= 0.75 # scale down; shorten the lengths 
                v1 = app
                v2 = -1.0*app 
        
        # Double bound 
        if self.bo == 2: 
            self._set_e(self.sym_fod1,bc,offset=v1)
            self._set_e(self.sym_fod1,bc,offset=v2)
            self._set_e(self.sym_fod2,bc,offset=v1)
            self._set_e(self.sym_fod2,bc,offset=v2)
        
        # Trible bond 
        if self.bo == 3:
            # Triangle motif: motif_3 
            # motif_3: app =[0,1,0]
            motif_3 = numpy.array([[0,0,1.0],
                                   [numpy.sqrt(0.75),0,-0.5],
                                   [-1*numpy.sqrt(0.75),0,-0.5]])

            # if posAB is equal to the y-axis: No need to rotate
            axis = [0,1,0]
            if numpy.allclose(posAB,axis,0,1e-3):
                v1 = motif_2[0,:]
                v2 = motif_2[1,:]
                v2 = motif_3[2,:]
            else:
                angle = numpy.arccos(numpy.dot(posAB,numpy.array(axis))/n)
                rot_axis = numpy.cross(numpy.array(axis),posAB)
                self.rot_mat = rotation_matrix(rot_axis,angle)
                v1 = numpy.dot(self.rot_mat,motif_3[0,:])
                v2 = numpy.dot(self.rot_mat,motif_3[1,:])
                v3 = numpy.dot(self.rot_mat,motif_3[2,:])
            self._set_e(self.sym_fod1,bc,offset=v1)
            self._set_e(self.sym_fod1,bc,offset=v2)
            self._set_e(self.sym_fod1,bc,offset=v3)
            self._set_e(self.sym_fod2,bc,offset=v1)
            self._set_e(self.sym_fod2,bc,offset=v2)
            self._set_e(self.sym_fod2,bc,offset=v3)

        # For bo = 1.5 we use a Lewis reference bo 
        # to easy separate between (1,2) and (2,1) 
        # bonds. 
        
        print('>>>>>>>>>>>>>>>>>>> HANS PETER <<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        print(self.symbols,check_spin(self.symbols),self._Na, self._Nb)
        print(f'{self.i} {self.j} bo bonds: {self.bo} {self.bo_ref}')
        # Lewis aromatic single bond
        local_spin = check_spin(self.symbols)
        local_Na = self._Na #local_spin[0][0]
        local_Nb = self._Nb #local_spin[1][0]
        if local_Na >= local_Nb: 
            sym_majority = self.sym_fod2 
            sym_minority = self.sym_fod1
        if local_Nb > local_Na:
            sym_majority = self.sym_fod1
            sym_minority = self.sym_fod2
        if self.bo == 1.5:
            self._set_e(sym_majority,bc,offset=v1)
            self._set_e(sym_minority,bc)
            self._set_e(sym_majority,bc,offset=v2)
        #if self.bo == 1.5 and self.bo_ref == 1.0:
        #    #self._set_e(self.sym_fod1,bc,offset=[0,0,0.5])
        #    self._set_e(self.sym_fod1,bc,offset=v1)
        #    self._set_e(self.sym_fod2,bc)
        #    #self._set_e(self.sym_fod1,bc,offset=[0,0,-0.5])
        #    self._set_e(self.sym_fod1,bc,offset=v2)
        ## Lewis aromatic double bound 
        #if self.bo == 1.5 and self.bo_ref == 2.0:
        #    #self._set_e(self.sym_fod2,bc,offset=[0,0,0.5])
        #    self._set_e(self.sym_fod2,bc,offset=v1)
        #    self._set_e(self.sym_fod1,bc)
        #    #self._set_e(self.sym_fod2,bc,offset=[0,0,-0.5])
        #    self._set_e(self.sym_fod2,bc,offset=v2)

def check_spin(symbols,elec_symbols=['X','He']):
    """
        Check spin
        ----------
        Get Na and Nb from current symbols. 
    """
    sym_fod1, sym_fod2 = elec_symbols 
    values, counts = numpy.unique(numpy.array(symbols),return_counts=True)
    Na = counts[values==sym_fod1]
    Nb = counts[values==sym_fod2]
    spin = abs(Na - Nb)
    M = spin + 1 
    return Na, Nb, M 


def electron_perception(atoms,nn,bo,va,l,fc,sp,verbose,elec_symbols=['X','He'],btype='LDQ'):
    """
        Electron perception 
        -------------------
        This conceptional based on the original idea 
        of PyLEWIS. 

        Workflow
        --------
            - [1] Core electron perception 
            - [2] Lone electron perception 
            - [3] Bond electron perception  
                  - btypes = ['LEWIS','LDQ'] 
    """
    sym_fod1 = elec_symbols[0]
    sym_fod2 = elec_symbols[1]
    # fill symbols with nuclei symbols
    symbols = atoms.symbols
    # fill positions with nuclei positions 
    positions = atoms.positions.tolist()
    # For LDQ we are calculating a reference Lewis bo 
    # this enables easy assignment of X-He-X vs He-X-He 
    if btype == 'LDQ' or btype == 'LEWIS':
        _, bo_ref = get_guess_bond_order(atoms)
        _, bo_ref = clean_overbonding(atoms,nn,bo_ref,btype='LEWIS')
        mmtypes = numpy.zeros(len(atoms),dtype=object) 
        _, _, _, bo_ref = get_aromatic_perception(atoms,nn,bo_ref, mmtypes,btype='LEWIS')
        _, _, _, bo_ref = magic_aromatic_perception(atoms=atoms,nn=nn,bo=bo_ref,mmtypes=mmtypes,btype='LEWIS')
    #if btype == 'LEWIS':
    #    bo_ref = copy(bo)
    mol_Na = 0
    mol_Nb = 0
    for i in range(len(atoms)):
        atom_Na = 0
        atom_Nb = 0 
        sym = atoms[i].symbol
        pos = atoms[i].position
        # N: Total number of electrons 
        N = symbol2number[sym]
        # V: Valence number of electrons 
        V = va[i]
        # R: Radical/lone number of electrons 
        R = l[i]
        # F: Formal charge 
        F = fc[i]
        # C: Number of core electrons
        C = N-V-R-F
        if verbose > 3: 
            print(f'{atoms[i].symbol} #core-e- : {C} #valenc-e- {V} #lone-e- {R}')
        # core electron perception
        cm = CoreMotifs(C,atoms[i],symbols,positions) 
        cm.kernel() 
        # update
        symbols = cm.symbols
        positions = cm.positions 
        atom_Na += cm._Na 
        atom_Nb += cm._Nb 
        # lone electron perception 
        lm = LoneMotifs(R,i,atoms,nn,sp, symbols, positions)
        lm.kernel() 
        # update 
        symbols = lm.symbols 
        positions = lm.positions 
        atom_Na += lm._Na
        atom_Nb += lm._Nb
        # bond electron perception 
        idx_j = nn[i].nonzero()[0].tolist()
        for j in idx_j: 
           if j > i:
               bm = BondMotifs(bo[i,j], bo_ref[i,j],sp,nn, i, j, atoms,symbols,positions)
               #bm._Na = atom_Na 
               #bm._Nb = atom_Nb
               bm.kernel()
               # update 
               symbols = bm.symbols
               positions = bm.positions 
               atom_Na += bm._Na
               atom_Nb += bm._Nb
        mol_Na += atom_Na 
        mol_Nb += atom_Nb
        print(f'Atom: {atom_Na} {atom_Nb}')
    # Check: Na, Nb and M 
    Na, Nb, M = check_spin(symbols,elec_symbols=elec_symbols)
    M0 = get_spin(l)
    if verbose > 3: 
        print(f'Na : {Na} Nb: {Nb} M : {M} M0 : {M0}')
        print(f'Na : {mol_Na} Nb : {mol_Nb}')
    atoms = Atoms(symbols,positions) 
    return atoms 

class Perception():
    """
        Perception class
        ----------------
        Automatic molecular perception
        using the universal force field (UFF).

        References
        ----------
            - [1] For general workflow: Automatic molecular perception using UFF
                  https://onlinelibrary.wiley.com/doi/epdf/10.1002/jcc.24309?saml_referrer
                  https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002%2Fjcc.24309&file=jcc24309-sup-0001-suppinfo.pdf
                  Journal of Computational Chemistry 2016, 37, 1191–1205 1197
            - [2] For: get_guess_bonding_matrix()
                  https://github.com/DCoupry/autografs
                  autografs/utils/mmanalysis.py

        Workflow
        --------
            - [1] Bonds perception
            - [2] Atoms perception
            - [3] Resonances perception

        Output
        ------
        nn: numpy.array, next nearest neighbours
            len(atoms)
        co: numpy.array, atomic coordination number
            len(atoms)
        va: numpy.array, atomic valence
            len(atoms)
        bo: numpy.array, bond order matrix
            len(atoms)xlen(atoms)
        tps: int() or nodef, total penality score for bo 
             goal is tps == 0
        l : numpy.array, lone electrons
            len(atoms)
        sp: numpy.array, sp hybridization

    """
    def __init__(self,atoms,verbose=3):
        # we only need nuclei information
        [nuclei,fod1,fod2] = atoms2flosic(atoms)
        self.atoms = nuclei
        self.verbose = verbose
        self.bo_status = 'incorrect'

    def _bonds_perception(self,btype='LEWIS'):
        """
            1.a Bond detection
            1.b Bond assignment 
                - 1st simple: get_guess_bond_order 
                - 2nd advanced: magicbonds 
            1.c Bond order anlysis
            if tps != 0: 
                1.b (advanced) and 1.c 

        """
        # 1.a and 1.b (simple) 
        self.nn, self.bo = get_guess_bond_order(self.atoms)
        self.co = get_atomic_coordination(self.atoms,self.nn)
        self.va, self.bo = clean_overbonding(self.atoms,self.nn,self.bo,btype=btype)
        # 1.c Check if bo is optimal (tps value)
        self.tps = eval_bond_order(self.atoms,self.nn,self.bo,verbose=self.verbose)
        print(f"tps = {self.tps}") 
        # 1.d == 3.c pre check aromaticity 
        # Aromatic rings (5,6 rings)
        # magicbonds may only work for non-aromatic systems currently. 
        self.mmtypes = numpy.zeros(len(self.atoms),dtype=object)
        self.aromatic, self.mmtypes, self.cycles, self.bo = get_aromatic_perception(self.atoms,self.nn,self.bo, self.mmtypes,btype=btype)
        # If we adjust the bo we need to recalculate va. 
        self.va, va_max, tps, ob = check_overbonding(self.atoms,self.bo)
        print(self.va,va_max,tps,ob)
        # DANGERHANS
        #self.va, self.bo = clean_overbonding(self.atoms,self.nn,self.bo,btype=btype)

        use_magicbonds = bool(self.aromatic.sum() == 0)
        print(f"bo_status = {self.bo_status} use_magic_bonds == {use_magicbonds}")
        # If tps == 0.0 the guess is good 
        if self.tps == 0.0: 
            self.bo_status  = 'valid' 
        # If tps != 0.0 the guess is not good 
        # If we use btype='LDQ' we get a maybe a wrong tps, 
        # and magicbonds may not work correctly with bo[i] = 1.5.
        print(self.bo_status,self.bo_status == 'incorrect',use_magicbonds)
        if self.bo_status == 'incorrect' and use_magicbonds: 
            # 1.b (advanced)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>Start magic")
            self.nn, self.bo, self.va, self.bonds = MagicBonds(self.atoms,verbose=self.verbose)
            print("after MagicBonds",self.bo,self.va)
            self.tps = eval_bond_order(self.atoms,self.nn,self.bo,verbose=self.verbose)
            if self.tps == 0.0:
                self.bo_status = 'valid'
            else: 
                self.bo_status =  'undefined' 

    def _atoms_perception(self):
        """
            2.a Hybridization and metal center geometries
            2.b Oxidation numbers computation
            2.c Atom types assignment
            2.d Charge and spin computation 
        """
        # 2.a
        # hybridization: general 
        self.l, self.sp = get_hybridization(self.atoms,self.nn,self.co,self.va)
        # hybridization: special rules 
        self.sp = clean_hybridization(self.atoms,self.nn,self.sp,verbose=self.verbose)
        # formal charges 
        self.fc = get_formal_charges(self.atoms,self.nn,self.co,self.va,self.l,self.bo,verbose=3)
        # geometries of metals
        self.mtype_geo = get_geometry_metal(self.atoms,self.nn)
        # 2.b
        self.ox = get_oxidation_numbers(self.atoms,self.nn,self.bo,verbose=self.verbose)
        # 2.c
        self.mmtypes = get_atomic_perception(self.atoms,self.nn,self.co,self.sp,self.ox,verbose=self.verbose)
        # 2.d 
        # charge of the system 
        self.charge = get_charge(self.ox,self.fc,verbose=self.verbose)
        # spin of the system 
        self.M = get_spin(self.l,verbose=self.verbose) 

    def _resonances_perception(self,rules='UFF',btype='LEWIS'):
        """
            3.a Functional group perception
            3.b Aromatic rings perception

            Input
            -----
            rules: str(), UFF (resonant bonds in 3.a and resonant mmtypes) 
                          openbabel (resonant bonds in 3.a no resonant mmtypes) 
        """
        # 3.a 
        # Functional group perception 
        # - check if it is amide 
        # - check if it is nitro 
        # - check if it is carboxylate 
        # - check if it is enol ether 
        self.is_amide, self.is_nitro, self.is_carboxylate, self.is_enol_ether, self.bo, self.mmtypes = get_functional_group_perception(self.atoms,self.nn,self.bo,self.mmtypes,rules,verbose=self.verbose)
        # 3.b
        # Aromatic rings (5,6 rings)
        self.aromatic, self.mmtypes, self.cycles, self.bo = get_aromatic_perception(self.atoms,self.nn,self.bo, self.mmtypes,btype=btype)
        self.aromatic, self.mmtypes, self.cycles, self.bo = magic_aromatic_perception(atoms=self.atoms,nn=self.nn,bo=self.bo,mmtypes=self.mmtypes,btype=btype,verbose=self.verbose)
        ## If we adjust the bo we need to recalculate va. 
        #self.va, va_max, tps, ob = check_overbonding(self.atoms,self.bo)
        ## DANGERHANS
        #self.va, self.bo = clean_overbonding(self.atoms,self.nn,self.bo,btype=btype) 
    def _electron_perception(self,btype='LEWIS'):
        """
            4.a Electron perception
            This step produce a electronic geometry, 
            which can be used within FLO-SIC. 
        """
        self.atoms = electron_perception(self.atoms,self.nn,self.bo,self.va,self.l,self.fc,self.sp,verbose=self.verbose,btype=btype)
        self.write_xyz() 

    def kernel(self,btype='LEWIS',rules='UFF'):
        """
            Kernel function
            ---------------
        """
        self._bonds_perception(btype=btype)
        self._atoms_perception()
        self._resonances_perception(rules=rules,btype=btype)
        self._electron_perception(btype=btype) 
        return self.bo, self.mmtypes

    def write_xyz(self,f_name='perception'): 
        write_xyz(self.atoms,f'{f_name}.xyz')

if __name__ == '__main__':
    from pyflosic2.ff.uff import uff_energy,check, UFF 
    from pyflosic2.ff.uff_systems import * 

    def my_pprint(rv): 
        print('{}: Etot - Etot,ref: {}, mmtypes - mmtypes,ref: {}'.format(rv[0],rv[1],rv[2]))

    def run(f_name,btype='LEWIS',rules='openbabel',verbose=3):    
        """
            run: f_name
            -----------
        """
        # Atoms 
        atoms = eval(f_name)()
        # Gui 
        #GUI(atoms) 
        # Molecular perception 
        mp = Perception(atoms,verbose=verbose)
        mp.write_xyz(f_name)
        bo, mmtypes = mp.kernel(btype=btype,rules=rules) 
        GUI(mp.atoms)
        print(f'after perception bo \n {bo}')
        print(f'l: {mp.l} va: {mp.va}')
        # UFF energy     
        # mmtypes = ref_openbabel[f_name]['mmtypes']
        ff = UFF(atoms,bo,mmtypes)
        ff.kernel() 
        e_check, mm_check = check(f_name,ff,ref_openbabel)
        return f_name, e_check, mm_check, ff

    # Benchmark sets 
    # UFF benchmark 
    uff_systems = ['Conformer3D_CID_6334',  # C, H
                   'Conformer3D_CID_8252',  # C, H
                   'Conformer3D_CID_7845',  # C, H 
                   'Conformer3D_CID_6335',  # C, H 
                   'Conformer3D_CID_674',   # N 
                   'Conformer3D_CID_1146',  # N 
                   'Conformer3D_CID_142199',# N 
                   'Conformer3D_CID_6342',  # N 
                   'Conformer3D_CID_14055', # N 
                   'Conformer3D_CID_7855',  # N 
                   'Conformer3D_CID_8254',  # O 
                   'Conformer3D_CID_10903', # O 
                   'Conformer3D_CID_7861',  # O 
                   'Conformer3D_CID_177',   # O 
                   'Conformer3D_CID_180',   # O 
                   'Conformer3D_CID_12222', # O 
                   'Conformer3D_CID_7847',  # O 
                   'Conformer3D_CID_7865', 
                   'Conformer3D_CID_178',   # N 
                   'Conformer3D_CID_31254']  # N 

    # PyFLOSIC KnightValley benchmark 
    knight_valley = ['H2O','CH4','COH2']

    def run_all(systems,btype='LEWIS',rules='openbabel',verbose=3):  
        """
            run_all: systems
            ----------------
        """
        RV = []
        for f_name in systems: 
            print(f"f_name: {f_name}")
            rv = run(f_name,btype=btype,rules=rules,verbose=verbose) 
            RV.append(rv) 
        for rv in RV: 
            my_pprint(rv)
    
    systems = [knight_valley, uff_systems][-1]
    run(f_name="Conformer3D_CID_142199",btype='LEWIS',rules='openbabel')
    #run_all(systems=systems,btype='LEWIS',rules='openbabel')
    
    # For C6H6 we need btype='LDQ' 
    #run('C6H6',btype='LDQ',rules='openbabel',verbose=3)                        # KT: Fine
    #run('Conformer3D_CID_10903',btype='LDQ',rules='openbabel',verbose=3)       # KT: Fine
    #run('H2O_KT',btype='LDQ',rules='openbabel',verbose=4)                      # KT: Fine
    #run('Conformer3D_CID_7855_KT',btype='LEWIS',rules='openbabel',verbose=4)   # KT: Fine
    #run('Conformer3D_CID_7865',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
   
    # C-H systems  
    #run('Conformer3D_CID_6334',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_8252',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_7845',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_6335',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
   
    # O systems 
    #run('Conformer3D_CID_8254',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_10903',btype='LEWIS',rules='openbabel',verbose=4)     # KT: Fine
    #run('Conformer3D_CID_7861',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_177',btype='LEWIS',rules='openbabel',verbose=4)       # KT: Fine
    #run('Conformer3D_CID_180',btype='LEWIS',rules='openbabel',verbose=4)       # KT: Fine
    #run('Conformer3D_CID_12222',btype='LEWIS',rules='openbabel',verbose=4)     # KT: Fine
    #run('Conformer3D_CID_7847',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_7865',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    
    # N systems 
    #run('Conformer3D_CID_674',btype='LEWIS',rules='openbabel',verbose=4)       # KT: Fine
    #run('Conformer3D_CID_1146',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_142199',btype='LEWIS',rules='openbabel',verbose=4)    # KT: Fine 
    #run('Conformer3D_CID_6342',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_14055',btype='LEWIS',rules='openbabel',verbose=4)     # KT: Fine
    #run('Conformer3D_CID_7855',btype='LEWIS',rules='openbabel',verbose=4)      # KT: Fine
    #run('Conformer3D_CID_178',btype='LEWIS',rules='openbabel',verbose=4)       # KT: Fine
    #run('Conformer3D_CID_31254',btype='LEWIS',rules='openbabel',verbose=4)     # KT: Fine

    #TODO 
    # Special case: N in planar geometry 
    # Special case: bond order bo = 1.41 

    # Aromatics 
    #Lewis = run('C6H6',btype='LEWIS',rules='openbabel',verbose=4)              # KT: E_bond off
    #LDQ = run('C6H6',btype='LDQ',rules='openbabel',verbose=4)                  # KT: Fine
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    #Lewis = run('Conformer3D_CID_931',btype='LEWIS',rules='openbabel',verbose=4)   # KT: no good
    #LDQ = run('Conformer3D_CID_931',btype='LDQ',rules='openbabel',verbose=4)       # KT: not quite right, but close
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    # Trans-sibelene 
    #Lewis = run('Conformer3D_CID_638088',btype='LEWIS',rules='openbabel',verbose=4)    # KT: no good
    #LDQ = run('Conformer3D_CID_638088',btype='LDQ',rules='openbabel',verbose=4)        # KT: Fine
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    #Lewis = run('Conformer3D_CID_9115',btype='LEWIS',rules='openbabel',verbose=4)      # KT: no good
    #LDQ = run('Conformer3D_CID_9115',btype='LDQ',rules='openbabel',verbose=4)          # KT: also off
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    #Lewis = run('Conformer3D_CID_8418',btype='LEWIS',rules='openbabel',verbose=4)      # KT: no good
    #LDQ = run('Conformer3D_CID_8418',btype='LDQ',rules='openbabel',verbose=4)          # KT: Slightly off
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')
    #Lewis = run('Conformer3D_CID_31423',btype='LEWIS',rules='openbabel',verbose=4)     # KT: no good
    #LDQ = run('Conformer3D_CID_31423',btype='LDQ',rules='openbabel',verbose=4)         # KT: no good
    #print(f'Lewis: {Lewis[-1].E_tot} LDQ: {LDQ[-1].E_tot}')

