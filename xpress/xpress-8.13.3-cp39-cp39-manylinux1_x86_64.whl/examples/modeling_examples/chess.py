'''*******************************************************
  * Python Example Problems                             *
  *                                                     *
  * file chess.py                                       *
  * Example for the use of the Python language          *
  * (Small LP-problem)                                  *
  *                                                     *
  * (c) 2018 Fair Isaac Corporation                     *
  *******************************************************'''

from __future__ import print_function
import xpress as xp

small = xp.var()
large = xp.var()

p = xp.problem()
p.addVariable(small, large)

# Now we have the constraints

p.addConstraint(3*small + 2*large <= 400)  # limit on available machine time
p.addConstraint(small + 3*large <= 200)  # limit on available wood

# Define the objective function
p.setObjective(5*small + 20*large, sense=xp.maximize)

p.solve()

print('')
print("Here are the LP results")
print("Objective value is ", p.getObjVal())
print("Make ", p.getSolution(small), " small sets, and ",
      p.getSolution(large), " large sets")

p.chgcoltype([small, large], ['I', 'I'])

p.solve()

print('')
print("Here are the IP results")
print("Objective value is ", p.getObjVal())
print("Make ", p.getSolution(small), " small sets, and ",
      p.getSolution(large), " large sets")
