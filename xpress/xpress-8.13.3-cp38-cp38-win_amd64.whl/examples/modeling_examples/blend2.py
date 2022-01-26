'''*******************************************************
  * Python Example Problems                             *
  *                                                     *
  * file blend2.py                                      *
  * Example for the use of the Python language          *
  * (Blending problem from XPRESS-MP User Guide)        *
  *                                                     *
  * Data given in the model.                            *
  *                                                     *
  * (c) 2018 Fair Isaac Corporation                     *
  *******************************************************'''

import xpress as xp

p = xp.problem()

ROres = range(2)
REV = 125                     # Unit revenue of product
MINGRADE = 4                  # Min permitted grade of product
MAXGRADE = 5                  # Max permitted grade of product

COST = [85.00, 93.00]
AVAIL = [60.00, 45.00]
GRADE = [2.1, 6.3]

x = [xp.var(ub=AVAIL[o]) for o in ROres]

p.addVariable(x)

# Objective: maximize total profit
p.setObjective(xp.Sum((REV - COST[o]) * x[o] for o in ROres),
               sense=xp.maximize)

# Lower and upper bounds on ore quality
p.addConstraint(xp.Sum((GRADE[o] - MINGRADE) * x[o] for o in ROres) >= 0)
p.addConstraint(xp.Sum((MAXGRADE - GRADE[o]) * x[o] for o in ROres) >= 0)

p.solve()
