#!/usr/bin/env python
# Copyright 2020-2022 The fodMC Developers. All Rights Reserved.
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
# Author:   Sebastian Schwalbe <theonov13@gmail.com>
#           Kai Trepte <kai.trepte1987@gmail.com>
from ase.atoms import Atoms

def write_fodMC_system(ase_atoms,cm,options={'unit' : 'angstrom','fix1s' : 'fix1s'}):
    '''
        write_fodMC_system

        Writes fodMC system file, containing
        nuclei coordinates as well as bonding 
        and lone pair information

        Input: ase_atoms, ASE Atoms object containing nuclei coordinates
               cm, list(), Connectivity matrix
               options, dict(), Additional options for guess creation
                    unit  - units of the input coordinates (angstrom or bohr)
                    fix1s - Initialize FODs corresponding to 1s orbitals at the nuclear sites 
    '''
    f = open('system','w') 
    sym = ase_atoms.get_chemical_symbols() 
    natoms = len(sym) 
    pos = ase_atoms.get_positions() 
    f.write('{}\n'.format(natoms))
    str_o = ''
    for o in list(options.keys()):
        str_o += options[o] + ' '
    f.write(str_o[:-1]+'\n')
    for a in range(natoms):
        f.write('{} {} {} {} \n'.format(sym[a],pos[a][0],pos[a][1],pos[a][2]))
    f.write('con_mat\n') 
    f.write(cm)
    f.write('\n\n')
    f.close() 

def read_atoms_bond_mol(f_name):
    ''' 
        read_atoms_bond_mol

        Adjusted ase MDF mol (chemical table format) reader
        Input: f_name, str()
    ''' 
    # Input:  mol file 
    # Output: ase_atoms, connectivity matrix (cm) 
    # Notes:  16.05.2020 -- currently only supports single, double, trible bonds 
    #                       one need to descided how to input 5-3 etc bonds 

    fileobj = open(f_name,'r') 
    lines = fileobj.readlines()
    L1 = lines[3]
    
    # The V2000 dialect uses a fixed field length of 3, which means there
    # won't be space between the numbers if there are 100+ atoms, and
    # the format doesn't support 1000+ atoms at all.
    if L1.rstrip().endswith('V2000'):
        natoms = int(L1[:3].strip())
        nbonds = int(L1[3:6].strip())
    else:
        natoms = int(L1.split()[0])
        nbonds = int(L1.split()[1])
    positions = []
    symbols = []
    for line in lines[4:4 + natoms]:
        x, y, z, symbol = line.split()[:4]
        symbols.append(symbol)
        positions.append([float(x), float(y), float(z)])
    # Bonding types 
    BOtype = {'1' : '(1-1)','2' : '(2-2)','3' : '(3-3)'}
    # Connectivity matrix 
    cm = '' 
    for l in range(4+natoms,4+natoms+nbonds):
        line = lines[l]
        A, B, BO = line.split()[:3]
        cm +='({}-{})-{}'.format(A,B,BOtype[BO])+' '
    return Atoms(symbols=symbols, positions=positions),cm 

def mol2fodmc(mol):
    '''
        mol2fodmc

        Converts mol2 format to fodMC system
        Input: mol, str()
    '''
    ase_atoms, cm = read_atoms_bond_mol(mol)
    write_fodMC_system(ase_atoms=ase_atoms,cm=cm)

