#!/usr/bin/env python
# -*- coding: utf-8 -*

import dpdata
import numpy as np
from deepmd.infer import DeepPot

from sclmd.tools import get_atommass


class deepmddriver():
    def __init__(self, strinfile, fmt, pbinfile, label, atomname=None, md2ang=0.06466):
        self.deepmdstr(strinfile, fmt, label, atomname, md2ang)
        self.dpstart(pbinfile)

    def deepmdstr(self, strinfile, fmt, label, atomname, md2ang):
        if label == 'System':
            str = dpdata.System(strinfile, fmt)
            atomname = atomname
        elif label == 'LabeledSystem':
            str = dpdata.LabeledSystem(strinfile, fmt)
            atomname = str['atom_names']
        else:
            raise ValueError("Label must be 'System' or 'LabeledSystem'")
        str.to('lammps/lmp', 'data.lmp', frame_idx=0)
        str.to('vasp/poscar', 'POSCAR.vasp', frame_idx=0)
        self.number = len(str['atom_types'])
        self.type = str['atom_types']
        mass = [get_atommass(el) for el in atomname]
        self.els = []
        atomnamelist = []
        for type in self.type:
            self.els.append(mass[type])
            atomnamelist.append(atomname[type])
        self.xyz = str['coords'].flatten()
        self.conv = md2ang*np.array([3*[1.0/np.sqrt(mass)]
                                     for mass in self.els]).flatten()
        self.axyz = []
        for i, a in enumerate(self.els):
            self.axyz.append([atomnamelist[i], self.xyz[i*3],
                              self.xyz[i*3+1], self.xyz[i*3+2]])
        self.cell = str['cells']
        print("Structure imported")
        print("\n"+"System info:")
        print("Atom names:", atomname)
        print("Atom masses:", mass)
        print("Cell:", self.cell)
        print("Total:", self.number)
        print("Atom types:", self.type)
        print("Postions of atoms:", self.xyz)

    def dpstart(self, pbinfile):
        self.dp = DeepPot(pbinfile)
        print("Deepmdkit launched")
        # print(self.conv.shape)
        self.initforce()

    def newx(self, q):
        return self.xyz + self.conv*q

    def absforce(self, q):
        self.e, self.f, self.v = self.dp.eval(
            self.newx(q), self.cell, self.type)
        return self.conv*np.array(self.f.flatten())

    def initforce(self):
        print("Calculate zero displacement force")
        self.f0 = self.absforce(np.zeros(3*self.number))

    def force(self, q):
        return self.absforce(q) - self.f0

    def energy(self):
        return self.e


if __name__ == '__main__':
    import numpy as np
    import time
    from tqdm import tqdm
    dp = deepmddriver('water.lmp', 'lammps/lmp',
                      'graph-compress.pb', 'System', ['O', 'H'])
    #dp = deepmddriver('OUTCAR', 'vasp/outcar','graph-compress.pb', 'LabeledSystem')
    print('Energy: ', dp.energy())
    print('Structure: ', dp.axyz)
    print('Force init: ', dp.f0)
    st = time.time()
    tt = 1000
    for i in tqdm(range(tt)):
        dp.force(np.zeros(3*dp.number))
    print('Total:', (time.time()-st), 's')
    print('Average:', (time.time()-st)/tt, 's')
