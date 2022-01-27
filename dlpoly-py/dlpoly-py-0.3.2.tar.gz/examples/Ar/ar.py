#!/usr/bin/env python3

from dlpoly import DLPoly
from dlpoly.field import Field
import os

dlPoly = DLPoly(control="Ar.control", config="Ar.config",
                field="Ar.field", workdir="argon")
dlPoly.run(numProcs = 4)

dlPoly = DLPoly(control="Ar.control", config="argon/REVCON", destconfig="Ar.config",
                field="Ar.field", workdir="argon-T310")
dlPoly.control['temp'] = 310.0
dlPoly.run(numProcs = 4)

wkd='argon-neweps'
field = Field("Ar.field")
field.vdws[0].params=['125.0','3.0']
field.write('Ar-n.field')

dlPoly = DLPoly(control="Ar.control", config="argon/REVCON", destconfig="Ar.config",
                field='Ar-n.field', workdir=wkd)

dlPoly.run(numProcs = 4)
