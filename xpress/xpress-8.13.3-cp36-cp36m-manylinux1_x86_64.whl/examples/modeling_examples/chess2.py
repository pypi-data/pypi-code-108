'''*******************************************************
  * Python Example Problems                             *
  *                                                     *
  * file chess2.py                                      *
  * Example for the use of the Python language          *
  * (Small LP-problem)                                  *
  *                                                     *
  * (c) 2018 Fair Isaac Corporation                     *
  *******************************************************'''

from __future__ import print_function
import xpress as xp

DescrV = {}
DescrC = {}

xs = xp.var()
xl = xp.var()

mc_time = 3*xs + 2*xl <= 400  # Limit on available machine time
wood = xs + 3*xl <= 200  # Limit on available wood

# Define the variable and constraint descriptions. Since the arrays
# and the indexing sets are dynamic they grow with each new variable
# description added:
DescrV = {xs: " Number of small chess sets",
          xl: " Number of large chess sets"}

DescrC = {mc_time: " Limit on available machine time",
          wood: " Limit on available wood"}

p = xp.problem()
p.addVariable(xs, xl)
p.addConstraint(mc_time, wood)

# Define the objective function
p.setObjective(5*xs + 20*xl, sense=xp.maximize)

p.solve()

rhs = []
p.getrhs(rhs, 0, p.attributes.rows - 1)

# Print out the solution
print("Solution:\n Objective: ", p.getObjVal())
print(DescrV[xs], ":", p.getSolution(xs), ",",
      DescrV[xl], ":", p.getSolution(xl))

print(" Constraint activity:")
print(DescrC[mc_time], ": ", rhs[p.getIndex(mc_time)] - p.getSlack(mc_time), "\n",
      DescrC[wood],    ": ", rhs[p.getIndex(wood)]    - p.getSlack(wood), sep='')
