# An example of a problem formulation that uses the xpress.Dot() operator
# to formulate constraints simply. Note that the NumPy dot operator is not
# suitable here as the result is an expression in the Xpress variables.
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp
import numpy as np

A = np.random.random(30).reshape(6, 5)  # A is a 6x5 matrix
Q = np.random.random(25).reshape(5, 5)  # Q is a 5x5 matrix

# Create a NumPy array of variables by using the xp.vars() function
x = xp.vars(5)
x0 = np.random.random(5)  # random vector

Q += 4 * np.eye(5)  # add 5 * the identity matrix

# 6 constraints (rows of A)
Lin_sys = xp.Dot(A, x) <= np.array([3, 4, 1, 4, 8, 7])

# One quadratic constraint
Conv_c = xp.Dot(x, Q, x) <= 1

p = xp.problem()

p.addVariable(x)
p.addConstraint(Lin_sys, Conv_c)
p.setObjective(xp.Dot(x-x0, x-x0))

p.solve()
