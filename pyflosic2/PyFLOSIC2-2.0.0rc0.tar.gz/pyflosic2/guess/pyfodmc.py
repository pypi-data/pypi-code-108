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
import fodmc
from pyflosic2.time.timeit import tictoc
from pyflosic2.atoms.bonds import Bonds
import functools
import os
from ase.io import read
from ase.atoms import Atoms


def write_fodMC_system(ase_atoms, cm, options={'unit': 'angstrom', 'fix1s': 'fix1s'}):
    """
        Writes fodMC system file
        ------------------------
    """
    f = open('system', 'w')
    sym = ase_atoms.get_chemical_symbols()
    natoms = len(sym)
    pos = ase_atoms.get_positions()
    f.write('{}\n'.format(natoms))
    str_o = ''
    for o in list(options.keys()):
        str_o += options[o] + ' '
    f.write(str_o[:-1] + '\n')
    for a in range(natoms):
        f.write('{} {} {} {} \n'.format(sym[a], pos[a][0], pos[a][1], pos[a][2]))
    f.write('con_mat\n')
    f.write(cm)
    f.write('\n\n')
    f.close()


def read_atoms_bond_mol(f_name):
    """
        Adjusted ase MDF mol (chemical table format) reader
        ---------------------------------------------------
    """
    # Input:  mol file
    # Output: ase_atoms, connectivity matrix (cm)
    # Notes:  16.05.2020 -- currently only supports single, double, trible bonds
    #                       one need to descided how to input 5-3 etc bonds

    fileobj = open(f_name, 'r')
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
    BOtype = {'1': '(1-1)', '2': '(2-2)', '3': '(3-3)'}
    # Connectivity matrix
    cm = ''
    for l in range(4 + natoms, 4 + natoms + nbonds):
        line = lines[l]
        A, B, BO = line.split()[:3]
        cm += '({}-{})-{}'.format(A, B, BOtype[BO]) + ' '
    return Atoms(symbols=symbols, positions=positions), cm


def mol2fodmc(mol):
    """
        Converts mol2 format to fodMC system
        -------------------------------------
    """
    ase_atoms, cm = read_atoms_bond_mol(mol)
    write_fodMC_system(ase_atoms=ase_atoms, cm=cm)


def bond2fodmc(bonds):
    """
        Generate: fodMC input from bonds object
        ---------------------------------------
    """

    f = open('system', 'w')
    f.write('{}\n'.format(len(bonds.nuclei)))
    f.write('angstrom fix1s\n')
    for n in bonds.nuclei:
        f.write('{:2s} {:+10.9f} {:+10.9f} {:+10.9f}\n'.format(n.symbol, n.position[0], n.position[1], n.position[2]))
    f.write('con_mat\n')
    for k in list({**bonds.b1, **bonds.b2}.keys()):
        if k in bonds.b1:
            v1 = bonds.b1[k]
        else:
            v1 = 0
        if k in bonds.b2:
            v2 = bonds.b2[k]
        else:
            v2 = 0
        i, j = k.split('-')
        i, j = int(i) + 1, int(j) + 1
        f.write('({}-{})-({}-{})\n'.format(i, j, v1, v2))
    for k in list({**bonds.l1, **bonds.l2}.keys()):
        if k in bonds.l1:
            v1 = bonds.l1[k]
        else:
            v1 = 0
        if k in bonds.l2:
            v2 = bonds.l2[k]
        else:
            v2 = 0
        f.write('{}-({}-{})\n'.format(int(k) + 1, v1, v2))
    f.write('\n')


def write_mol(bonds, f_name='system.mol'):
    """
        Write: mol file from bonds object
        ---------------------------------
        Note: not fully working
        Usage: jmol, avogadro
    """
    # Note: It seems that AVOGADRO can not read zeros.
    # If a molecule is in x,y and z is zero it assumes 2D.
    # We shift all coordinates slightly (tshift) to omit
    # this behaviour.
    tshift = 0.0001
    natoms = len(bonds.nuclei)
    bond_keys = sorted({**bonds.b1, **bonds.b2}.keys())
    nbonds = len(bond_keys)
    # LDQ Check
    # We check if each entry in bo is an integer.
    # Only integer bo entries can be converted to mol file
    # bond order format.
    check_LDQ = bonds.bo - numpy.array(bonds.bo, dtype=int)
    check_LDQ = len(check_LDQ[check_LDQ > 0]) > 0
    if check_LDQ:
        print('ERROR: LDQ electronic configuration cannot be translated in mol file format!')
        return
    f = open(f_name, 'w')
    f.write('\n Simple Mol file\n \n')
    # natomlists = 0
    naddlines = '0999'  # additional lines
    # chiral = '0000'  # 0 or 1
    # nstext = 0
    molversion = 'V2000'
    f.write('{:>3}{:>3}  {}  {}  {}  {}  {}  {}  {}  {} {}\n'.format(
        natoms, nbonds, 0, 0, 0, 0, 0, 0, 0, naddlines, molversion))
    for n in bonds.nuclei:
        tmp = [n.position[0] + tshift, n.position[1] + tshift, n.position[2] + tshift, n.symbol,
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        f.write('  {:> 8.4f}  {:> 8.4f}  {:> 8.4f} {}   {}  {}  {}  {}  {}  {}  {}  {}  {}  {}  {}  {}\n'.format(*tmp))
    for k in bond_keys:
        if k in bonds.b1:
            v1 = bonds.b1[k]
        else:
            v1 = 0
        if k in bonds.b2:
            v2 = bonds.b2[k]
        else:
            v2 = 0
        i, j = k.split('-')
        i, j = int(i) + 1, int(j) + 1
        f.write('{:>3}{:>3}{:>3}{:>3}{:>3}{:>3}{:>3}\n'.format(i, j, int((v1 + v2) / 2.), 0, 0, 0, 0))
    f.write('M  END')
    f.close()


def write_pyfodmc_atoms(sys):
    """
         write fodmc input for atoms
    """
    # create system file
    f = open('system', 'w')
    f.write('1 %s\n' % sys)
    f.write('angstrom fix1s\n')
    f.write('%s 0.0 0.0 0.0\n\n' % sys)
    f.close()


def write_pyfodmc_molecules(sys, con_mat):
    """
        write fodmc input for molecules
    """
    ase_atoms = read(sys)
    sym = ase_atoms.get_chemical_symbols()
    pos = ase_atoms.get_positions()
    natoms = len(ase_atoms.get_chemical_symbols())

    # create system file
    f = open('system', 'w')
    f.write('%i %s\n' % (natoms, sys))
    f.write('angstrom fix1s\n')
    for p in range(len(pos)):
        f.write('%s %0.5f %0.5f %0.5f\n' % (sym[p], pos[p][0], pos[p][1], pos[p][2]))
    f.write('cont_mat\n')
    for cm in con_mat:
        f.write(cm + '\n')
    f.close()


class pyfodmc:
    """
        pyfodmc class
        -------------
        The fodMC generates Fermi-orbital descriptors (FODs)
        for a given set of nuclei as well as bonding information.
        This class captures the terminal content because the fodMC FOTRAN call.

        Input
        -----
        p : parameters()
        input_data :  str(), atoms (e.g., 'Kr')
                      str(), molecule (e.g., [system].mol [system].xyz)

        con_mat : optional, connectivity matrix

        Note:  tty :  TeleTYpewriter
        Ref.: https://stackoverflow.com/questions/10803579/copy-fortran-called-via-f2py-output-in-python
    """

    def __init__(self, p, input_data, con_mat=None, f_guess = 'fodMC_GUESS.xyz'):
        """
            Set everything up
        """
        self.f_guess = f_guess
        # call ... Fortran call fodMC
        self.call = lambda: fodmc.fodmc_mod.get_guess(output_mode='PyFLOSIC', output_name=self.f_guess)
        self.tmpFile = 'fodMC.out'
        self.ttyData = []
        self.outfile = False
        self.save = False
        self.p = p
        self.input_data = input_data
        self.con_mat = con_mat

    def init_fodmc(self):
        """
            Initialize fodMC input files
            ----------------------------
            Analyze input if bonding information is given (e.g., mol file)
            or not (e.g., xyz file).
            Atoms work without "bonding information".

        """
        # molecules (str(), bonds object)
        if isinstance(self.input_data, Bonds):
            bond2fodmc(self.input_data)

        # molecules (str(), [name].mol)
        # - no additional bonding information
        # - bonding information (Lewis) is included in the mol file
        if isinstance(self.input_data, str) and self.input_data.find('.mol') != -1:
            # mol2xyz
            mol2fodmc(self.input_data)
            # name = self.input_data.split('.')[0]

        # atoms (str(), e.g., 'Kr')
        # - information for FODs is read from database
        if isinstance(self.input_data, str) and self.input_data.find(
                '.mol') == -1 and self.input_data.find('.xyz') == -1:
            write_pyfodmc_atoms(self.input_data)
            # name = self.input_data

    def clean_files(self):
        """
            Clean output files
            ------------------
        """
        files = ['CLUSTER', 'FRMORB', 'system', 'xx_database_xx']
        for f in files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except BaseException:
                'Nothing'

    def start(self):
        """
            Start recording (TTY data)
            --------------------------
        """
        # open outputfile
        self.outfile = os.open(self.tmpFile, os.O_RDWR | os.O_CREAT)
        # save the current file descriptor
        self.save = os.dup(1)
        # put outfile on 1
        os.dup2(self.outfile, 1)
        return

    def stop(self):
        """
            Stop recording (TTY data)
            -------------------------
        """
        if not self.save:
            # Probably not started
            return
        # restore the standard output file descriptor
        os.dup2(self.save, 1)
        # parse temporary file
        self.ttyData = open(self.tmpFile, ).readlines()
        # close the output file
        os.close(self.outfile)
        # delete temporary file
        os.remove(self.tmpFile)

    def print_data(self):
        """
            Print data
            ----------
            Print recorded TTY data to log file.
        """
        for l in self.ttyData:
            self.p.log.write(l.replace('\n', ''))

    def kernel(self):
        """
            Get FOD guess
            -------------
        """
        @tictoc(self.p)
        @functools.wraps(self.kernel)
        def wrapper(*args, **kwargs):
            """
                Wrapper
                -------
                Needed to log the output from tictoc.
            """
            self.p.log.header('PyFODMC: FOD guess')
            self.init_fodmc()
            self.start()
            self.call()
            self.stop()
            self.clean_files()
            self.print_data()
        wrapper(self)

    def get_guess(self):
        """
            Get FOD guess
            -------------
            Wrapper function, calling self.kernel().
        """
        self.kernel()


def get_guess(p, input_data, con_mat=None):
    """
        Get FOD guess (fodMC)
        ---------------------
        The fodMC generates Fermi-orbital descriptors (FODs)
        for a given set of nuclei as well as bonding information.

        Input
        -----
        p : parameters()
        input_data :  str(), atoms (e.g., 'Kr')
                      str(), molecule (e.g., [system].mol [system].xyz)

        con_mat : optional, connectivity matrix
    """
    @tictoc(p)
    @functools.wraps(get_guess)
    def wrapper(*args, **kwargs):
        """
            Wrapper
            -------
            Needed to log the output from tictoc.
        """

        mc = pyfodmc(p=p, input_data=input_data)
        mc.kernel()

    wrapper(p, input_data, con_mat=None)


if __name__ == "__main__":

    def test_atom():
        from pyflosic2.parameters.flosic_parameters import parameters
        from pyflosic2.gui.view import GUI
        p = parameters()
        # Function call
        # get_guess(p,input_data='Kr')
        # Class
        g = pyfodmc(p=p, input_data='Kr')
        g.get_guess()
        GUI(g.f_guess, p=p)

    def test_unrestricted():
        from pyflosic2 import parameters
        from pyflosic2.systems.uflosic_systems import C6H6
        from pyflosic2.gui.view import GUI

        p = parameters(log_name='UFODMC.log')
        atoms = C6H6()
        b = Bonds(p, atoms)
        b.kernel(eps_val=1.8, eps_cor=1 / 3.)
        write_mol(b)

        g = pyfodmc(p=p, input_data=b)
        g.get_guess()
        GUI(g.f_guess, p=p)

    def test_restricted():
        from pyflosic2 import parameters
        from pyflosic2.systems.rflosic_systems import H2O  # , COH2
        from pyflosic2.gui.view import GUI

        p = parameters(log_name='RFODMC.log')
        atoms = H2O()  # COH2()
        b = Bonds(p, atoms)
        b.kernel(eps_val=1.8, eps_cor=1 / 3.)
        write_mol(b)

        g = pyfodmc(p=p, input_data=b)
        g.get_guess()
        GUI(g.f_guess, p=p)

    test_atom()
    test_unrestricted()
    test_restricted()
