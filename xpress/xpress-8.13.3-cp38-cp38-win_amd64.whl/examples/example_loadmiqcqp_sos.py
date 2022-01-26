# Example that uses loadproblem() to create a Mixed Integer
# Quadratically Constrained Quadratic Programming problem with two
# Special Ordered Sets
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp

p = xp.problem()

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
              ['I', 'S'],  # qgtype
              [0, 1],  # mgcols
              [0, 2],  # dlim
              ['1', '1'],  # qstype
              [0, 2, 4],  # msstart
              [0, 1, 0, 2],  # mscols
              [1.1, 1.2, 1.3, 1.4])      # dref

p.write("loadedqcgs", "lp")
p.solve()
