'''*******************************************************
  * Python Example Problems                             *
  *                                                     *
  * file trans.py                                       *
  * Example for the use of the Python language          *
  * (Network problem: transport from depots to          *
  *  customers)                                         *
  *                                                     *
  * (c) 2018 Fair Isaac Corporation                     *
  *******************************************************'''

import xpress as xp
from Data.trans_data import AVAIL, DEMAND, COST

p = xp.problem()

Suppliers = AVAIL.keys()
Customers = DEMAND.keys()
Pairs = COST.keys()

x = {(i, j): xp.var() for i, j in Pairs}

p.addVariable(x)

p.setObjective(xp.Sum(COST[i, j] * x[i, j] for i, j in Pairs))

p.addConstraint(xp.Sum([x[s, c] for c in Customers if (s, c) in Pairs])
                <= AVAIL[s] for s in Suppliers)
p.addConstraint(xp.Sum([x[s, c] for s in Suppliers if (s, c) in Pairs])
                >= DEMAND[c] for c in Customers)

p.solve()
