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
from pyflosic2.atoms.atoms import Atoms


def write_xyz(atoms, f_name='atoms.xyz'):
    """
        Write guess
        -----------
        Write PyCOM guess to xyz file

        Input
        -----
    """
    with open(f_name, 'w') as f:
        natoms = len(atoms)
        f.write('{:d}\n'.format(natoms))
        if atoms._elec_symbols[1] is not None:
            f.write("sym_fod1='{}' sym_fod2='{}'\n".format(atoms._elec_symbols[0], atoms._elec_symbols[1]))
        if atoms._elec_symbols[1] is None:
            f.write("sym_fod1='{}'\n".format(atoms._elec_symbols[0]))
        for s, (x, y, z) in zip(atoms.symbols, atoms.positions):
            f.write('{:2s} {:22.15f} {:22.15f} {:22.15f}\n'.format(s, x, y, z))


def get_data_xyz(f_file):
    """
        Read: xyz file (standard)
        -------------------------

        Input
        -----
        f_file: str(), xyz file name


        Output
        ------
        symbols: list(str()), Symbols
        positions: list(float()), Positions
    """
    f = open(f_file, 'r')
    lines = f.readlines()
    while len(lines) > 0:
        symbols = []
        positions = []
        natoms = int(lines.pop(0))
        lines.pop(0)  # Comment line; ignored
        for _ in range(natoms):
            line = lines.pop(0)
            symbol, x, y, z = line.split()[:4]
            symbol = symbol.lower().capitalize()
            symbols.append(symbol)
            positions.append([float(x), float(y), float(z)])
    return symbols, positions


def atoms2flosic(atoms, sym_fod1='X', sym_fod2='He'):
    """
        Convert: a joint atoms.object (nuclei + FODS) to three separate atoms.objects
        -----------------------------------------------------------------------------
        A simplified nuclei and FOD parser.

        Input
        -----
        atoms: Atoms(), atoms.object containing nuclei and fods

        Output
        ------
        nuclei: Atoms(), Nuclei information only
        fod1: Atoms(), FOD1 information only
        fod2: Atoms(), FOD2 information only
    """
    nuclei = atoms[[atom.index for atom in atoms if atom.symbol not in atoms._elec_symbols]]
    fod1 = atoms[[atom.index for atom in atoms if atom.symbol == sym_fod1]]
    fod2 = atoms[[atom.index for atom in atoms if atom.symbol == sym_fod2]]
    if not fod1:
        fod1 = None
    if not fod2:
        fod2 = None
    return [nuclei, fod1, fod2]


def read_xyz(f_file):
    """
        Read: FLO-SIC (nuclei + FOD) xyz file
        -------------------------------------
        Get sym_fod1 and sym_fod2 labels from comment.

        Input
        -----
        f_file: str(), xyz file name
    """
    f = open(f_file, 'r')
    ll = f.readlines()
    f.close()
    comments = ll[1].split()
    sym_fod1 = None
    sym_fod2 = None
    tag_sym_fod1 = 'sym_fod1'
    tag_sym_fod2 = 'sym_fod2'
    # First spin channel
    for c in comments:
        if c.find(tag_sym_fod1) != -1:
            sym_fod1 = c.replace("'", "").split('=')[-1]
            # once assigned, stop the loop ! Do not overwrite the sym_fod1 again!!
            break
    # Second spin channel
    for c in comments:
        if c.find(tag_sym_fod2) != -1:
            sym_fod2 = c.replace("'", "").split('=')[-1]
            # once assigned, stop the loop ! Do not overwrite the sym_fod1 again!!
            break
    symbols, positions = get_data_xyz(f_file)
    return symbols, positions, sym_fod1, sym_fod2


def atoms_from_xyz(f_file, spin=0, charge=0, split=False, verbose=3):
    sym, pos, sym_fod1, sym_fod2 = read_xyz(f_file)
    if sym_fod1 is None and sym_fod2 is None:
        msg = 'Nuclei only'
        # We assume we want to initialize FODs
        elec_symbols = ['X', 'He']
    if sym_fod1 is not None and sym_fod2 is None:
        msg = 'Nuclei and FOD1 (restricted)'
        elec_symbols = [sym_fod1, sym_fod2]
    if sym_fod1 is not None and sym_fod2 is not None:
        msg = 'Nuclei, FOD1, and FOD2 (unrestricted)'
        elec_symbols = [sym_fod1, sym_fod2]
    atoms = Atoms(sym, pos, spin=spin, charge=charge, elec_symbols=elec_symbols)
    if verbose > 4:
        print(msg)
    if not split:
        return atoms
    if split:
        [nuclei, fod1, fod2] = atoms2flosic(atoms, sym_fod1=sym_fod1, sym_fod2=sym_fod2)
        return [nuclei, fod1, fod2]


if __name__ == '__main__':
    atoms_from_xyz('uflo.xyz', verbose=4)
    atoms_from_xyz('rflo.xyz', verbose=4)
    atoms_from_xyz('nuclei.xyz', verbose=4)
