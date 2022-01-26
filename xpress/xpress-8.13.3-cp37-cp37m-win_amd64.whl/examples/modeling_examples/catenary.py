'''*********************************************************************
   Python NL examples
   file catenary.py
   QCQP problem (linear objective, convex quadratic constraints)
   Based on AMPL model catenary.mod
   (Source: http://www.orfe.princeton.edu/~rvdb/ampl/nlmodels)

   This model finds the shape of a hanging chain by
   minimizing its potential energy.

   (c) 2018 Fair Isaac Corporation
*********************************************************************'''

from __future__ import print_function
import xpress as xp

N = 100                       # Number of chainlinks
L = 1                         # Difference in x-coordinates of endlinks
H = 2*L/N                     # Length of each link

RN = range(N+1)

x = xp.vars(N+1, lb=-xp.infinity, name="x")
y = xp.vars(N+1, lb=-xp.infinity, name="y")

p = xp.problem()

p.addVariable(x, y)

# Objective: minimise the potential energy
p.setObjective(xp.Sum((y[j-1] + y[j]) / 2 for j in range(1, N+1)))

# Bounds: positions of endpoints
# Left anchor
p.addConstraint(x[0] == 0)
p.addConstraint(y[0] == 0)
# Right anchor
p.addConstraint(x[N] == L)
p.addConstraint(y[N] == 0)

# Constraints: positions of chainlinks
p.addConstraint((x[j] - x[j-1])**2 + (y[j] - y[j-1])**2 <= H**2
                for j in range(1, N+1))

# Uncomment to export the matrix file
# p.write('catenary.mat', 'l')

p.solve()

print("Solution: ", p.getObjVal())
for j in RN:
    print("{0:10.5f} {1:10.5f}".format(p.getSolution(x[j]),
                                       p.getSolution(y[j])))
