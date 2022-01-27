#!/usr/bin/env python3

from dlpoly import DLPoly

dlp="/home/drFaustroll/playground/dlpoly/dl-poly-alin/build-mxatms/bin/DLPOLY.Z"

dlPoly = DLPoly(control="Ar.control", config="Ar.config",
                field="Ar.field", workdir="argon")
dlPoly.run(executable=dlp,numProcs = 4)

for T in range(200,601,50):
    print("Process T = {}".format(T))
    dlPoly = DLPoly(control="Ar.control", config="argon/REVCON", destconfig="Ar.config",
                field="Ar.field", workdir="argon-T{}".format(T))
    dlPoly.control['temp'] = T
    dlPoly.run(executable=dlp,numProcs = 4)
