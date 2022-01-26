# Demonstrate how variables, or arrays thereof, and constraints, or
# arrays of constraints, can be added into a problem. Prints the
# solution and all attributes/controls of the problem.
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import xpress as xp

N = 4
S = range(N)
v = [xp.var(name="y{0}".format(i)) for i in S]  # set name of a variable

m = xp.problem()

v1 = xp.var(name="v1", lb=0, ub=10, threshold=5, vartype=xp.continuous)
v2 = xp.var(name="v2", lb=1, ub=7, threshold=3, vartype=xp.continuous)
vb = xp.var(name="vb", vartype=xp.binary)

v = [xp.var(name="y{0}".format(i), lb=0, ub=2*N) for i in S]

# adds both v, a vector (list) of variables, and v1 and v2, two scalar
# variables.
m.addVariable(vb, v, v1, v2)

c1 = v1 + v2 >= 5

m.addConstraint(c1,  # Adds a list of constraints: three single constraints...
                2*v1 + 3*v2 >= 5,
                v[0] + v[2] >= 1,
                # ... and a set of constraints indexed by all {i in
                # S: i<N-1} (recall that ranges in Python are from 0
                # to n-1)
                (v[i+1] >= v[i] + 1 for i in S if i < N-1))

# objective overwritten at each setObjective()
m.setObjective(xp.Sum([i*v[i] for i in S]), sense=xp.minimize)

m.solve()

print("status: ", m.getProbStatus())
print("string: ", m.getProbStatusString())

print("solution:", m.getSolution())

print("Attributes: ----------------------------------------")
print(m.getAttrib())

print("Controls: -------------------------------------------")
print(m.getControl())
