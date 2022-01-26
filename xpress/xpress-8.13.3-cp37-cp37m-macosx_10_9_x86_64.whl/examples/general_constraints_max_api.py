# Here we use the max operator of the Python interface to create a new
# optimization problem.
#
# (C) Fair Isaac Corp., 1983-2021

# Find the point that minimizes the maximum variable within a given
# polytope.

import xpress as xp

p = xp.problem()

# Read data from a problem of MIPLIB 2017
p.read('pk1.mps.gz')

# Retrieve all variables of the original problem
x = p.getVariable()

# Change objective function to the maximum of all variables, to
# be minimized.
p.setObjective (xp.max(*x))

# Set time limit to 20 seconds
p.controls.maxtime = -20
p.solve()

print("solution: x = ", p.getSolution())
