#!/usr/bin/env python3

from dlpoly import DLPoly
from dlpoly.rdf import rdf
import matplotlib
import matplotlib.pyplot as plt


def showrdf(loc):
    m = rdf(loc)
    for i in range(len(m.labels)):
        plt.plot(m.x, m.data[i,:,0],label = "-".join(m.labels[i]))
    plt.xlabel("r [Å])")
    plt.ylabel("gofr [a.u.])")
    plt.legend()

dlPoly = DLPoly(control="CONTROL", config="CONFIG",
                field="FIELD", workdir="w40")
dlPoly.run(numProcs = 1)
showrdf("w40/RDFDAT")

dlPoly = DLPoly(control="CONTROL", config="CONFIG",
                field="FIELD", workdir="w20")
dlPoly.control['pressure'] = 12
dlPoly.control['temp'] = 500
dlPoly.run(numProcs = 1)
showrdf("w20/RDFDAT")
plt.show()
