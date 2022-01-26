# Example: create a MIQCQP using the loadproblem() function
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp

p = xp.problem()

# fill in a problem with three variables and four constraints

p.loadproblem("",  # probname
              ['G', 'G', 'L', 'L'],  # qrtypes
              [-2.4, -3, 4, 5],  # rhs
              None,  # range
              [3, 4, 5],  # obj
              [0, 2, 4, 8],  # mstart
              None,  # mnel
              [0, 1, 2, 3, 0, 1, 2, 3],  # mrwind
              [1, 1, 1, 1, 1, 1, 1, 1],  # dmatval
              [-1, -1, -1],  # lb
              [3, 5, 8],  # ub
              [0, 0, 0, 1, 1, 2],  # mqobj1
              [0, 1, 2, 1, 2, 2],  # mqobj1
              [2, 1, 1, 2, 1, 2],  # dqe
              [2, 3],  # qcrows
              [2, 3],  # qcnquads
              [1, 2, 0, 0, 2],  # qcmqcol1
              [1, 2, 0, 2, 2],  # qcmqcol2
              [3, 4, 1, 1, 1],  # qcdqval
              ['I', 'B'],  # qgtype
              [0, 1],  # mgcols
              [0, 2],  # dlim
              colnames=['y01', 'y02', 'y03'],  # column names
              rownames=['row01', 'row02', 'row03', 'row04'])  # row    names

p.write("loadedqcg", "lp")
p.solve()
print(p.getSolution())
