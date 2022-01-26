# Here we use the abs operator of the Python interface to create a new
# optimization problem.
#
# (C) Fair Isaac Corp., 1983-2021

# Find the point that minimizes the l-1 norm within a given polytope,
# i.e. the sum of the absolute values of the coordinates of a point in
# a polytope.

import xpress as xp

p = xp.problem()

# Read data from a problem of MIPLIB 2017
p.read('pk1.mps.gz')

# Retrieve all variables of the original problem
x = p.getVariable()

# Equivalently to general_constraint_abs.py, we want to minimize the
# sum of all absolute values of the original variables. We do so by
# using the API functions, but first create a set of variables which
# will be used in the objective function and that will be used in the
# call to addgencons() later
abs_x = [xp.var() for v in x]

N = len(x)

p.addVariable(abs_x)

p.addgencons([xp.gencons_abs]*N, abs_x, [i for i in range(N)], x)

# Change objective function to the l-1 norm of the variable vector, to
# be minimized.
p.setObjective (xp.Sum(abs_x))

# Set time limit to 20 seconds
p.controls.maxtime = -20
p.solve()

print("solution:", p.getSolution())
