#!/usr/bin/env python3

from dlpoly import DLPoly
from dlpoly.rdf import rdf
from dlpoly.output import output

dlp="/home/drFaustroll/playground/dlpoly/dl-poly-alin/build-check/bin/DLPOLY.Z"

dlPoly = DLPoly(control="CONTROL", config="CONFIG",
                field="FIELD", workdir="w40")

dlPoly.run(executable=dlp,numProcs = 1)

out = output("w40/OUTPUT")
print(out)

