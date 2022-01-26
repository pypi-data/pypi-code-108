# Test for the main features of the Xpress Python interface
#
# Adds a vector of N=5 variables and sets constraints and objective. The
# problem is a convex QCQP
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import xpress as xp

N = 5
S = range(N)

v = [xp.var(name="y{0}".format(i)) for i in S]

m = xp.problem("problem 1")

print("variable:", v)

m.addVariable(v)

m.addConstraint(v[i] + v[j] >= 1 for i in range(N - 4) for j in range(i, i+4))
m.addConstraint(xp.Sum([v[i]**2 for i in range(N - 1)]) <= N**2 * v[N - 1]**2)

# Objective overwritten at each setObjective()
m.setObjective(xp.Sum([i*v[i] for i in S]) * (xp.Sum([i*v[i] for i in S])))

# Compact (equivalent) declaration:
#
# m = xp.problem(v,                                                              # variable
#                v[i] + v[j] >= 1 for i in range(N - 4) for j in range(i, i+4),  # constraint
#                xp.Sum([v[i]**2 for i in range(N - 1)]) <= N**2 * v[N - 1]**2,  # constraint
#                xp.Sum([i*v[i] for i in S]) * (xp.Sum([i*v[i] for i in S])),    # objective
#                name="problem 1")

m.solve()

print("solution: ", m.getSolution())
