'''*******************************************************
  * Python Example Problems                             *
  *                                                     *
  * file blend.py                                       *
  * Example for the use of the Python language          *
  * (Blending problem)                                  *
  *                                                     *
  * Reading data from file.                             *
  *                                                     *
  * (c) 2018 Fair Isaac Corporation                     *
  *******************************************************'''

from __future__ import print_function
import xpress as xp
from Data.blend_data import COST, AVAIL, GRADE

p = xp.problem()

ROres = range(2)
REV = 125                     # Unit revenue of product
MINGRADE = 4                  # Min permitted grade of product
MAXGRADE = 5                  # Max permitted grade of product

x = [xp.var(ub=AVAIL[o]) for o in ROres]

p.addVariable(x)

# Objective: maximize total profit
p.setObjective(xp.Sum((REV - COST[o]) * x[o] for o in ROres),
               sense=xp.maximize)

# Lower and upper bounds on ore quality
p.addConstraint(xp.Sum((GRADE[o] - MINGRADE) * x[o] for o in ROres) >= 0)
p.addConstraint(xp.Sum((MAXGRADE - GRADE[o]) * x[o] for o in ROres) >= 0)

p.solve()

# Print out the solution
print("Solution:\n Objective:", p.getObjVal())
for o in ROres:
    print(" x(", o, "): ", p.getSolution(x[o]))
print("Grade: ", sum(GRADE[o] * p.getSolution(x[o]) for o in ROres)
      / sum(p.getSolution(x[o]) for o in ROres),
      " [min,max]: [", MINGRADE, ",", MAXGRADE, "]")
