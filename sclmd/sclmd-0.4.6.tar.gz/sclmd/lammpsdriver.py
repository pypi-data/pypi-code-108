#!/usr/bin/env python
# -*- coding: utf-8 -*

# LAMMPS driver for Langevin molecular dynamics
# Adapted from LAMMPS python wraper

import ctypes

import numpy as np
from lammps import lammps

from sclmd.tools import get_atomname

args = "-screen none"


class lammpsdriver(lammps):
    # create instance of LAMMPS
    def __init__(self, infile, label="",
                 constraints=[], tdir="./", lunit="Ang", eunit="eV", md2ang=0.06466,
                 name="", cmdargs=args.split(), ptr=None, comm=None
                 ):
        lammps.__init__(self, name=name, cmdargs=cmdargs, ptr=None, comm=None)
        self.infile = infile
        self.md2ang = md2ang
        self.constraints = constraints
        self.label = label
        self.lunit = lunit
        self.eunit = eunit
        if self.eunit == "eV":
            self.para = 1.0
        elif self.eunit == "Kcal/mole":
            self.para = 0.04336344201657351
        else:
            raise ValueError("Energy unit not recognized")
        # start lammps
        self.start()

    def start(self):
        print("LAMMPS launched")
        # todo:better to set the unit to metals here again
        #self.command("units metal")

        #lines = open(self.infile, 'r').readlines()
        #for line in lines: self.command(line)
        self.commands_list(self.infile)
        self.type = np.array(self.gather_atoms("type", 0, 1))
        #self.mass = np.array(self.gather_atoms("mass",1,1))
        self.mass = self.extract_atom("mass", 2)
        self.number = self.get_natoms()
        self.els = []
        for type in self.type:
            self.els.append(self.mass[type])
        self.xyz = self.gather_atoms("x", 1, 3)
        self.conv = self.md2ang*np.array([3*[1.0/np.sqrt(mass)]
                                          for mass in self.els]).flatten()
        self.type = np.array(self.gather_atoms("type", 0, 1))
        #self.mass = np.array(self.gather_atoms("mass",1,1))
        self.axyz = []
        for i, a in enumerate(self.els):
            self.axyz.append([get_atomname(a), self.xyz[i*3],
                              self.xyz[i*3+1], self.xyz[i*3+2]])
        # print(self.conv.shape)
        self.initforce()

    def quit(self):
        self.close()
        print("Mission completed.")

    def newx(self, q):
        newxyz = self.xyz + self.conv*q
        return newxyz.ctypes

    def absforce(self, q):
        self.scatter_atoms("x", 1, 3, self.newx(q))
        self.command("run 0")
        return self.para*self.conv*np.array(self.gather_atoms("f", 1, 3))

    def initforce(self):
        print("Calculate zero displacement force")
        self.f0 = self.absforce(np.zeros(3*self.number))

    def force(self, q):
        return self.absforce(q) - self.f0

    def energy(self, eargs="pe"):  # energy,eargs:"pe","ke" or "etotal".
        return self.get_thermo(eargs)

    def dynmat(self, q=None):
        if q is not None:
            self.scatter_atoms("x", 1, 3, self.newx(q))
            print("Calculate dynamical matrix")
        else:
            print("Calculate zero displacement dynamical matrix")
        self.command("dynamical_matrix all eskm 0.000001 file dynmat.dat")
        dynmatdat = np.loadtxt("dynmat.dat") # Dynmat units in ps^-2, THz^2
        dynlen = int(3*np.sqrt(len(dynmatdat)/3))
        rpc = 6.582119569e-4 # Reduced Planck constant in eV*ps
        dynmat = dynmatdat.reshape((dynlen, dynlen)) * \
            rpc**2  # Dynmat units in eV^2
        return (dynmat+dynmat.transpose())/2

    #def updatedynmat(self, q):
    #    displacement = np.amax(np.abs(self.conv*q))
    #    if displacement > 2:
    #        print("Large displacement: %f ang, re-calcuate dynamical matrix" % displacement)
    #        return self.dynmat(q)
