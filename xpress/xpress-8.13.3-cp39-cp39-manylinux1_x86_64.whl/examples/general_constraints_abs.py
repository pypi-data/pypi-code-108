# Example using general constraints - the abs() operator
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp

# Here we use the abs operator of the Python interface to create a new
# optimization problem.

# Find the point that minimizes the l-1 norm within a given polytope,
# i.e. the sum of the absolute values of the coordinates of a point in
# a polytope.

p = xp.problem()

# Read data from a problem of MIPLIB 2017
p.read('pk1.mps.gz')

# Retrieve all variables of the original problem
x = p.getVariable()

# Change objective function to the l-1 norm of the variable vector, to
# be minimized.
p.setObjective (xp.Sum(xp.abs(v) for v in x))

# Set time limit to 20 seconds
p.controls.maxtime = -20
p.solve()

print("solution:", p.getSolution())
