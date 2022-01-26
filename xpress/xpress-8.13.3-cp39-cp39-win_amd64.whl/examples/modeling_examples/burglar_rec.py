'''******************************************************
   Python Example Problems

   file burglar_rec.py

   (c) 2018 Fair Isaac Corporation
*******************************************************'''

from __future__ import print_function
import xpress as xp
from Data.burglar_rec_dat import I

WTMAX = 102  # Maximum weight allowed
ITEMS = set(["camera", "necklace", "vase", "picture", "tv", "video",
             "chest", "brick"])  # Index set for items

take = {i: xp.var(vartype=xp.binary) for i in I.keys()}

p = xp.problem()

p.addVariable(take)

# Objective: maximize total value
p.setObjective(xp.Sum(I[i][0] * take[i] for i in ITEMS),
               sense=xp.maximize)

# Weight restriction
p.addConstraint(xp.Sum(I[i][0] * take[i] for i in ITEMS) <= WTMAX)

p.solve()  # Solve the MIP-problem

# Print out the solution
print("Solution:\n Objective: ", p.getObjVal())
for i in ITEMS:
    print(" take(", i, "): ", p.getSolution(take[i]))
