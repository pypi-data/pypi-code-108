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
from pyflosic2.atoms.atoms import Atoms


def atoms2pyscf(atoms):
    """
        Convert: atoms.object (nuclei) to pyscf.mol
        -------------------------------------------
        Transform an atoms.object containing only nuclei into the PySCF input format.

        Input
        -----
        atoms: Atoms(), Nuclei only
    """
    return [[atom.symbol, atom.position] for atom in atoms]


def atoms2ase(atoms):
    """
        Convert: atoms.object (PyFLOSIC2) to ase.atoms object
        --------------------------------------------------------

        Input
        -----
        atoms: Atoms(), Nuclei, Electrons or Nuclei +  Electrons
    """
    from ase.atoms import Atoms as ASEAtoms
    return ASEAtoms(atoms.symbols, atoms.positions)


def atoms2flosic(atoms, sym_fod1='X'):
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
    fod1 = []
    if len(atoms) > 1:
        idx_fod1 = [atom.index for atom in atoms if atom.symbol == sym_fod1]
        nuclei = atoms[[atom.index for atom in atoms if atom.index < numpy.min(idx_fod1)]]
        fod1 = atoms[idx_fod1]
    else:
        nuclei = atoms
    return [nuclei, fod1]


def read_flosic_xyz(f_file):
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
    if not comments:  # this enables reading flosic.xyz files which do not have a comment
        sym_fod1 = 'X'
    tag_sym_fod1 = 'sym_fod1'
    # First spin channel
    for c in comments:
        if c.find(tag_sym_fod1) != -1:
            sym_fod1 = c.replace("'", "").split('=')[-1]
            # once assigned, stop the loop ! Do not overwrite the sym_fod1 again!!
            break
        else:  # this enables reading flosic.xyz files which have something like 'xyz' or 'angstrom' as comment
            sym_fod1 = 'X'
    symbols, positions = read_xyz(f_file)  # read(f_file)
    atoms = Atoms(symbols, positions, elec_symbols=[sym_fod1, None])
    [nuclei, fod1] = atoms2flosic(atoms, sym_fod1=sym_fod1)
    return atoms, sym_fod1


def read_xyz(f_file):
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


def write_xyz(atoms, f_name='system.xyz', comment=None):
    """
        Write FLO-SIC xyz file
        ----------------------

        Input
        -----
        atoms : Atoms(), atoms object/instance
        f_name : str(), output xyz file
        comment: str(), comment line in xyz file
    """
    f = open(f_name, 'w')
    if comment is None:
        comment = 'sym_fod1={}'.format(atoms._elec_symbols[0])
    if '\n' in comment:
        raise ValueError('Comment line should not have line breaks.')
    natoms = len(atoms)
    f.write('{:d}\n{:s}\n'.format(natoms, comment))
    for s, (x, y, z) in zip(atoms.symbols, atoms.positions):
        f.write('{:2s} {:22.15f} {:22.15f} {:22.15f}\n'.format(s, x, y, z))


if __name__ == "__main__":
    atoms = Atoms(['He', 'X'], [[0, 0, 0], [0, 0, 0]], elec_symbols=['X', 'Kr'])
    [nuclei, fod1] = atoms2flosic(atoms)
    print(nuclei)
    print(fod1)
    atoms = Atoms(['He', 'Kr'], [[0, 0, 0], [0, 0, 0]])
    [nuclei, fod1] = atoms2flosic(atoms, sym_fod1='Kr')
    print(nuclei)
    print(fod1)
