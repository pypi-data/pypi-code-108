# Example: use numpy to print the product of a matrix by a random vector.
#
# Uses xpress.Dot to on a matrix and a vector. Note that the NumPy dot operator
# works perfectly fine here.
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import numpy as np
import xpress as xp

x = [xp.var() for i in range(5)]

p = xp.problem()
p.addVariable(x)
p.addConstraint(xp.Sum(x) >= 2)

p.setObjective(xp.Sum(x[i]**2 for i in range(5)))

# The above four lines can be replaced by
#
# p = xp.problem(x, xp.Sum(x) >= 2, xp.Sum(x[i]**2 for i in range(5)))

p.solve()

A = np.array(range(30)).reshape(6, 5)  # A is a 6x5 matrix
sol = np.array(p.getSolution())  # suppose it's a vector of size 5
columns = A*sol         # not a matrix-vector product!
v = xp.Dot(A, sol)      # this is a matrix-vector product A*sol

print(v)
