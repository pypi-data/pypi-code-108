# Construct a problem using addVariable and addConstraint, then use
# the Xpress API routines to amend the problem with rows and quadratic
# terms.
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import xpress as xp

p = xp.problem()

N = 5
S = range(N)

x = [xp.var(vartype=xp.binary) for i in S]

p.addVariable(x)

# vectors can be used whole or addressed with their index

c0 = xp.Sum(x) <= 10
cc = [x[i]/1.1 <= x[i+1]*2 for i in range(N-1)]

p.addConstraint(c0, cc)

p.setObjective(3 - x[0])

mysol = [0, 0, 1, 1, 1, 1.4]

# add a variable with its coefficients

p.addcols([4], [0, 3], [c0, 4, 2], [-3, 2.4, 1.4], [0], [2], ['YY'], ['B'])
p.write("problem1", "lp")

# load a MIP solution
p.loadmipsol([0, 0, 1, 1, 1, 1.4])

# Add quadratic term x[0]^2 - 2 x[0] x[1] + x[1]^2 to the second
# constraint. Note that the -2 coefficient for an off-diagonal element
# must be passed divided by two.
#
# The same effect would be obtained with p.addqmatrix (cc[0],
# [x[0],x[3],x[3]], [x[0],x[0],x[3]], [1,-1,1])
#
# As constraint vector 'cc' was added after c0

p.addqmatrix(1, [x[0], x[3], x[3]], [x[0], x[0], x[3]], [1, -1, 1])

# add seventh and eighth constraints:
#
#   x[0] + 2 x[1] + 3 x[2] >= 4
# 4 x[0] + 5 x[1] + 6 x[2] + 7 x[3] + 8 x[4] - 3 YY <= 4.4
#
# Note the new column named 'YY' added with its index 5 (variables'
# indices begin at 0). The same would happen if 5 were substituted by
# YY.

p.addrows(rowtype=['G', 'L'],
          rhs=[4, 4.4],
          start=[0, 3, 9],
          colind=[x[0], x[1], x[2], x[0], x[1], x[2], x[3], x[4], 5],
          rowcoef=[1, 2, 3, 4, 5, 6, 7, 8, -3],
          names=['newcon1', 'newcon2'])

p.solve()
p.write("amended", "lp")

slacks = []

p.calcslacks(solution=mysol, calculatedslacks=slacks)

print("slacks:", slacks)

# The five commands below are equivalent to the following:
#
# p.addcols ([4, 4, 4, 4, 4],
#            [0, 3, 6, 9, 12, 15],
#            [c0, 4, 2, c0, 4, 2, c0, 4, 2, c0, 4, 2, c0, 4, 2],
#            [3,  -2,  1,  -3,  2.4,  1.4, 3, 2, 1, -3, 2.4, 4, 3, 2, 1],
#            [0,0,0,0,0],
#            [2,10,1,2,2],
#            ['p1','p2','p3','p4','p5'],
#            ['I','C','S','P','R'])

p.addcols([4], [0, 3], [c0, 4, 2], [-3, -2, 1], [0], [2], ['p1'], ['I'])
p.addcols([4], [0, 3], [c0, 4, 2], [-3, 2.4, 1.4], [0], [10], ['p2'], ['C'])
p.addcols([4], [0, 3], [c0, 4, 2], [-3, 2, 1], [0], [1], ['p3'], ['S'])
p.addcols([4], [0, 3], [c0, 4, 2], [-3, 2.4, 4], [0], [2], ['p4'], ['P'])
p.addcols([4], [0, 3], [c0, 4, 2], [-3, 2, 1], [0], [2], ['p5'], ['R'])

p.solve()
try:
    print("new solution:", p.getSolution())
except:
    print("could not get solution, perhaps problem is infeasible")
