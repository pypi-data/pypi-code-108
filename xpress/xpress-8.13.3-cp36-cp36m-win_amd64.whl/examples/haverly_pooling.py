# Pooling example
#
# (C) Fair Isaac Corp., 1983-2021

#----- crudeA ------/--- pool --|
#                  /            |--- finalX
#----- crudeB ----/             |
#                               |--- finalY
#----- crudeC ------------------|

import xpress as xp

p = xp.problem()

crudeA = xp.var(name="A", lb=0.0)
crudeB = xp.var(name="B", lb=0.0)
crudeC = xp.var(name="C", lb=0.0)

crudeC_flowX = xp.var(name="CX", lb=0.0)
crudeC_flowY = xp.var(name="CY", lb=0.0)

pool_flowX   = xp.var(name="PX", lb=0.0)
pool_flowY   = xp.var(name="PY", lb=0.0)

finalX = xp.var(name="X", lb=0.0, ub=100)
finalY = xp.var(name="Y", lb=0.0, ub=200)

poolQ  = xp.var(name="poolQ", lb=0.0)

cost    = xp.var(name="cost", lb=0.0)
income  = xp.var(name="income", lb=0.0)

p.addVariable(cost, income)
p.addVariable(crudeA, crudeB, crudeC, finalX, finalY)
p.addVariable(pool_flowX, pool_flowY, crudeC_flowX, crudeC_flowY)
p.addVariable(poolQ)

# cost and income
p.addConstraint(cost   == 6*crudeA + 16*crudeB + 10*crudeC,
                income == 9*finalX + 15*finalY)

# flow balances
p.addConstraint(finalX == pool_flowX + crudeC_flowX,
                finalY == pool_flowY + crudeC_flowY,
                crudeC == crudeC_flowX + crudeC_flowY,
                crudeA + crudeB == pool_flowX + pool_flowY)

# material balances
pool_sulfur = 3*crudeA + crudeB == (pool_flowX + pool_flowY)*poolQ

p.addConstraint(pool_sulfur,
                pool_flowX * poolQ <= 0.5*crudeC_flowX + 2.5*crudeC_flowY,
                pool_flowY * poolQ <= 1.5*pool_flowY - 0.5*crudeC_flowY)

p.controls.xslp_solver=0

# money
p.setObjective(income - cost,sense=xp.maximize)

p.nlpoptimize()

print('solution: income is', p.getSolution(income), 'and cost is', p.getSolution(cost))
