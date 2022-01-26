'''*******************************************************
  * Python Example Problems                             *
  *                                                     *
  * file burglar.py                                     *
  * Example for the use of the Python language          *
  * (Burglar problem)                                   *
  *                                                     *
  * (c) 2018 Fair Isaac Corporation                     *
  *******************************************************'''

from __future__ import print_function
import xpress as xp

Items = range(8)

WTMAX = 102  # Max weight allowed for haul

x = [xp.var(vartype=xp.binary) for _ in Items]

p = xp.problem()

p.addVariable(x)

VALUE = [15, 100, 90, 60, 40, 15, 10, 1]
WEIGHT = [2, 20, 20, 30, 40, 30, 60, 10]

# Objective: maximize total value
p.setObjective(xp.Sum(VALUE[i]*x[i] for i in Items),
               sense=xp.maximize)

# Weight restriction
p.addConstraint(xp.Sum(WEIGHT[i]*x[i] for i in Items) <= WTMAX)

p.solve()           # Solve the MIP-problem

# Print out the solution
print("Solution:\n Objective: ", p.getObjVal())
for i in Items:
    print(" x(", i, "): ", p.getSolution(x[i]))
