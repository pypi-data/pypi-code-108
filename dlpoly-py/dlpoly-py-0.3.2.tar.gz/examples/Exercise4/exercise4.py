#!/usr/bin/env python3

from dlpoly import DLPoly
from dlpoly.rdf import rdf
from dlpoly.output import output
import matplotlib
import matplotlib.pyplot as plt


def showrdf(loc):
    m = rdf(loc)
    for i in range(len(m.labels)):
        plt.plot(m.x, m.data[i,:,0],label = "-".join(m.labels[i]))
    plt.xlabel("r [Å])")
    plt.ylabel("gofr [a.u.])")
    plt.legend()


dlp="/home/drFaustroll/playground/dlpoly/dl-poly-alin/build-check/bin/DLPOLY.Z"

dlPoly = DLPoly(control="CONTROL", config="CONFIG",
                field="FIELD", workdir="w40")

dlPoly.control.timing["steps"] = 10000
dlPoly.run(executable=dlp,numProcs = 1)

out = output("w40/OUTPUT")
print(out)

showrdf("w40/RDFDAT")
plt.show()
