#!/usr/bin/env python3

from ase.io import iread
from dlpoly import DLPoly
import numpy as np

f = DLPoly(field="w40/FIELD")
trajectory = iread("w40/HISTORY",format="dlp-history")
m = f.field.molecules['Valinomycin']
charges = m.get_charges()
k = 1e-10*1.60217662e-19/3.33564e-30

d = []
for i, frame in enumerate(trajectory):
    dip = np.zeros(4)
    for i in range(m.nAtoms):
        r = frame[i].position
        for j in range(3):
            dip[j+1] += charges[i]*r[j]
        dip[0] = np.linalg.norm(dip[1:4])
    d.append(dip*k)

with open("dipole.dat",'w') as df:
    print("#{:16s}|{:13s} [D]|{:13s} [D]|{:13s} [D]|{:13s} [D]|".format("Frame", "D", "dx", "dy", "dz"), file=df)
    for i, x in enumerate(d):
        print("{:16d} {:16.8e} {:16.8e} {:16.8e} {:16.8e}".format(i, *x), file=df)


