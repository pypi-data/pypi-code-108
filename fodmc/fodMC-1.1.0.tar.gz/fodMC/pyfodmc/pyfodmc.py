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

# pyfodmc - Python interface for fodMC code to PyFLOSIC 
# Author:       Sebastian Schwalbe (SS)  
# Changelog:    11.02.2019 
#               SS update to the new fodmc.f90 
#               SS add new write_pyfodmc_molecules function 
#               15.05.2020 
#               re-included the python interface 

import fodmc 
from ase.io import read,write  
import os

def clean_files(): 
    '''
        clean_files

        Removes files
    '''
    files = ['system']
    for f in files: 
        try:
            if os.path.exists(f):
                os.remove(f)
        except: 'Nothing' 

def rename_xyz(name):
    '''
        rename_xyz

        Renames the standard output file
        Input: name, str()
    '''
    os.rename('fodMC.xyz',name+'.xyz')

def get_guess(output_mode='PyFLOSIC',output_name='fodMC.xyz'):
    '''
        get guess

        Generate the fodMC guess
        Input: output_mode, str()
               output_name, str()
    '''
    # magic to capture that output:
    # from http://stackoverflow.com/questions/977840/redirecting-fortran-called-via-f2py-output-in-python
    #      http://websrv.cs.umt.edu/isis/index.php/F2py_example
    output_file = 'fodMC.out' 
    if os.path.exists(output_file):
        os.remove(output_file)
    # open outputfile
    outfile = os.open(output_file, os.O_RDWR|os.O_CREAT)
    # save the current file descriptor
    save = os.dup(1)
    # put outfile on 1
    os.dup2(outfile, 1)
    # end magic
    # FORTAN call
    fodmc.fodmc_mod.get_guess(output_mode,output_name)
    # restore the standard output file descriptor
    os.dup2(save, 1)
    # close the output file
    os.close(outfile)
    f = open(output_file,'r')
    output = f.read()
    f.close()
    # rm files which are not needed 
    clean_files()
    # rename output xyz
    #rename_xyz(name)

def write_pyfodmc_atoms(sys):
    '''
        write_pyfodmc_atoms

        Write PyfodMC input for atoms
        Input: sys, str()
    '''
    #
    # write fodmc input for atoms 
    #
    # create system file 
    f = open('system','w')
    f.write('1 %s\n' % sys)
    f.write('angstrom fix1s\n')
    f.write('%s 0.0 0.0 0.0\n\n' %sys)
    f.close()

def write_pyfodmc_molecules(sys,con_mat):
    '''
        write_pyfodmc_molecules

        Write PyfodMC input for molecules
        Input: sys, str()
               con_mat, list(), Connectivity matrix
    '''
    ase_atoms = read(sys)
    sym = ase_atoms.get_chemical_symbols()
    pos = ase_atoms.get_positions() 
    natoms = len(ase_atoms.get_chemical_symbols())
    
    # create system file 
    f = open('system','w')
    f.write('%i %s\n' % (natoms,sys))
    f.write('angstrom fix1s\n')
    for p in range(len(pos)):
        f.write('%s %0.5f %0.5f %0.5f\n' %(sym[p],pos[p][0],pos[p][1],pos[p][2]))
    f.write('cont_mat\n')
    for cm in con_mat:
        f.write(cm+'\n')
    f.close()

if __name__ == "__main__":
    from fodMC.pyfodmc import pyfodmc
    def make_atom():
        # Simple test for atoms 
        # creat input 
        write_pyfodmc_atoms(sys='Kr')
        # Fortran call 
        pyfodmc.get_guess('PyFLOSIC','Kr_FODs.xyz')
    
    def make_molecule():
        # Simple test for molecule
        sys = 'SO2.xyz'
        con_mat = ['(1-2)-(2-2)','(1-3)-(2-2)\n']   
        write_pyfodmc_molecules(sys=sys,con_mat=con_mat)
        # Fortran call 
        fodmc.fodmc_mod.get_guess('PyFLOSIC','SO2_FODs.xyz')
    make_atom()
