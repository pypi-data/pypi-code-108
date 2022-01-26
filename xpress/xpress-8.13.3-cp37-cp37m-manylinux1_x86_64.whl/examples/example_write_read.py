# Create a few variables, then build a problem and save it to a file.
# Re-read that file into a new problem and solve it
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import xpress as xp

m = xp.problem()

c1 = xp.var(name="C1", lb=-xp.infinity, ub=xp.infinity)
c2 = xp.var(name="C2", lb=-xp.infinity, ub=200)
c3 = xp.var(name="C3", vartype=xp.partiallyinteger, threshold=10)
c4 = xp.var(name="C4", vartype=xp.semicontinuous, threshold=3, ub=6)
c5 = xp.var(name="C5", vartype=xp.integer)

m.addVariable(c1, c2, c3, c4, c5)

m.setObjective(c1 + c2)

m.addConstraint(c1**2 + c2**2 <= 6,
                2 * c1 + 3 * c2 + c3 == 2,
                -c3**2 + c4**2 + c5**2 <= 0,
                c4 == 0.316227766016838 * c1,
                c5 == 0.316227766016838 * c2)

m.write("example0", "lp")

m2 = xp.problem()

m2.read("example0.lp", "")

m2.solve()

print("objective value:", m2.getObjVal())
print("solution:", m2.getSolution())
