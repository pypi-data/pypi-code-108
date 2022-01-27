#!/usr/bin/env python
# -*- coding: utf-8 -*

import numpy as np
import py_brenner_module

from sclmd.units import *


class brenner:
    """
    construct necessory information to do a brenner force run
    devicedir   transport direction
    constrained fixed atom positions
    anr_constrained fixed atom numbers

    when calling brenner, adding some fixed atoms around the moving atoms
    also adding some vacuum gap after the fixed atoms by increasing the cell
    dimension.
    """

    def __init__(self, xyz, anr, cell, devicedir=1, constrained=[], anr_constrained=[], lunit="Ang", eunit="eV"):  # ,constraints=[]
        self.md2ang = 0.06466
        #self.constraints = constraints
        self.constrained = constrained  # extra atom positions fixed during MD.
        # type of extra atom fixed during MD.
        self.anr_constrained = anr_constrained
        # 1D array gives the coordinates of each atom
        # [xi,yi,zi],i=1,na
        # np.array([a[1:] for a in xyz],dtype='d').flatten() # position vector
        self.xyz = xyz
        self.anr = anr  # atomic numbers (1=H,6=C,...)
        # [a[0] for a in xyz] # Atom label (H,C,Au,...)
        self.els = [PeriodicTable[a] for (a) in (anr)]
        self.conv = self.md2ang*np.array([3*[1.0/np.sqrt(AtomicMassTable[a])]
                                          for a in self.els]).flatten()
        # 1D array gives the unit cell
        # x1,y1,z1,x2,y2,z2,x3,y3,z3
        self.cell = np.array(cell, dtype='d').flatten()
        # direction to include large unitcell vacuum (1=x,2=y,3=z,0=none->use cell directly)
        self.devicedir = devicedir
        self.lunit = lunit
        self.eunit = eunit

    def newx(self, q):
        """
        return the real coordinates from displacements got from MD
        performing unit conversion and remove the mass factor
        """
        return self.xyz + self.conv*q

    def absforce(self, q):
        """
        calculate the force from brenner
        q:  displacement list of all atoms, including those fixed
        """
        # Make new system including fixed regions:
        # [self.anr,self.anr_constrained]
        anr_b = np.concatenate((self.anr, self.anr_constrained))
        # [self.newx(q),self.constrained]
        newR = np.concatenate((self.newx(q), self.constrained))
        cell = self.cell
        if self.devicedir != 0:
            cell[self.devicedir-1] = self.cell[self.devicedir-1]+1000
        energy2, force, energy = py_brenner_module.brennerf(
            cell, anr_b[:], newR[:])
        force = force[0:len(q)]
        # print force,force[0:6]#,self.conv*force
        return self.conv*force

    def initforce(self):
        print "Calculate zero displacement force..."
        # equilibrium force
        extq = np.zeros(len(self.xyz))
        self.f0 = self.absforce(extq)

    def force(self, q):
        """
        calculate the relative force 
        q:  displacement list of all atoms, including those fixed
        """
        return self.absforce(q)-self.f0
