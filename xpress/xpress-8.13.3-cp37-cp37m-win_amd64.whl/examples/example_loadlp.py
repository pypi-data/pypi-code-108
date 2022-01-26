# Example of the loadproblem() functionality.
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp

p = xp.problem()

# fill in a problem with three variables and four constraints

p.loadproblem("",  # probname
              ['G', 'G', 'E', 'L'],  # qrtypes
              [-2.4, -3, 4, 5],  # rhs
              None,  # range
              [3, 4, 5],  # obj
              [0, 2, 4, 8],  # mstart
              None,  # mnel
              [0, 1, 2, 3, 0, 1, 2, 3],  # mrwind
              [1, 1, 1, 1, 1, 1, 1, 1],  # dmatval
              [-1, -1, -1],  # lb
              [3, 5, 8],  # ub
              colnames=['x1', 'x2', 'x3'],  # column names
              rownames=['row1', 'row2', 'row3', 'constr_04'])  # row    names

p.write("loadlp", "lp")
p.solve()

# Create another variable and add it, then modify the objective
# function. Note that the objective function is replaced by, not
# amended with, the new objective

x = xp.var()
p.addVariable(x)
p.setObjective(x**2 + 2*x + 444)
p.solve()
p.write("updated", "lp")
