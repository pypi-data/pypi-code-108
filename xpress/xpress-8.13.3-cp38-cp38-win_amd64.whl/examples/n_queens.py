# Example using the Xpress Python interface
#
# The n queens: place n queens on an nxn chessboard so that none of
# them can be eaten in one move.
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import xpress as xp

n = 8  # the size of the chessboard
N = range(n)

# Create a "dictionary" of variables, i.e. a mapping from all tuples
# (i,j) to a variable.

x = {(i, j): xp.var(vartype=xp.binary, name='q{0}_{1}'.format(i, j))
     for i in N for j in N}

vertical = [xp.Sum(x[i, j] for i in N) <= 1 for j in N]
horizontal = [xp.Sum(x[i, j] for j in N) <= 1 for i in N]

diagonal1 = [xp.Sum(x[k-j, j] for j in range(max(0, k-n+1), min(k+1, n))) <= 1
             for k in range(1, 2*n-2)]
diagonal2 = [xp.Sum(x[k+j, j] for j in range(max(0, -k), min(n-k, n))) <= 1
             for k in range(2-n, n-1)]

p = xp.problem()

p.addVariable(x)
p.addConstraint(vertical, horizontal, diagonal1, diagonal2)
# What's the largest number of queens we can place on the chessboard?
p.setObjective(xp.Sum(x), sense=xp.maximize)

p.solve()

for i in N:
    for j in N:
        if p.getSolution(x[i, j]) == 1:
            print('@', sep='', end='')
        else:
            print('.', sep='', end='')
    print('')
