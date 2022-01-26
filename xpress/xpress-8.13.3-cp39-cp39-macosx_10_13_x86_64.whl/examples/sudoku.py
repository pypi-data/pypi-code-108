# Example using the Xpress Python interface
#
# Sudoku: place numbers from 1 to 9 into a 9x9 grid such that no
# number repeats in any row, in any column, and in any 3x3 sub-grid.
#
# More generally, replace 3 with q and 9 with q^2
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import xpress as xp

# We model this problem as an assignment problem where certain
# conditions must be met for all numbers in the columns, rows, and
# sub-grids.
#
# These subgrids are lists of tuples with the coordinates of each
# subgrid. In a 9x9 sudoku, for instance, subgrids[0,1] has the 9
# elements in the top square, i.e., the following:
#
#  ___ ___ ___
# |   |###|   |
# |   |###|   |
# |___|###|___|
# |   |   |   |
# |   |   |   |
# |___|___|___|
# |   |   |   |
# |   |   |   |
# |___|___|___|
#
# while subgrids[2,2] has the 9 elements in the bottom right square.

# The input is a starting grid where the unknown numbers are replaced by zero

q = 3

starting_grid = \
 [[8, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 3, 6, 0, 0, 0, 0, 0],
  [0, 7, 0, 0, 9, 0, 2, 0, 0],
  [0, 5, 0, 0, 0, 7, 0, 0, 0],
  [0, 0, 0, 0, 4, 5, 7, 0, 0],
  [0, 0, 0, 1, 0, 0, 0, 3, 0],
  [0, 0, 1, 0, 0, 0, 0, 6, 8],
  [0, 0, 8, 5, 0, 0, 0, 1, 0],
  [0, 9, 0, 0, 0, 0, 4, 0, 0]]

# Solve a 16x16 sudoku: Just uncomment the following lines.
#
# q = 4
#
# starting_grid = \
#  [[ 0, 0,12, 0, 0, 2, 0, 0, 0, 7, 3, 0,13,15, 0, 0],
#   [15, 0, 0, 0, 0, 3, 0, 0, 9, 0, 0, 0,12, 0, 0,10],
#   [ 0, 0, 0, 0, 9, 0, 6, 0, 0, 0,12, 0, 0, 0, 2, 5],
#   [ 6,11, 1, 0, 0,10, 5, 0, 0, 2, 0,15, 0, 0, 0, 0],
#   [ 4, 6, 3, 0, 0, 0,13,14, 0, 0, 0, 0, 0, 7, 0, 0],
#   [ 0,15,11, 0, 7, 0, 9, 0, 0, 0, 0, 0, 0, 0, 1, 0],
#   [ 0, 1, 0,10,15, 0, 0, 0,11, 3,14, 0, 6, 0, 0, 0],
#   [13, 0, 8, 7, 0, 5, 0, 0, 0, 1, 9,12, 0, 0, 0, 0],
#   [ 0, 0, 0, 6, 3, 7,15, 4, 0, 0, 0, 0, 0,14, 0, 0],
#   [ 0, 8, 0, 0, 0, 0, 0, 0, 0,11, 7, 0, 4, 0, 0, 0],
#   [ 0, 0, 0, 0, 0, 0, 0, 0,13, 0, 0, 6, 9, 0, 3, 0],
#   [ 0, 0, 0, 0, 2, 8,14, 0, 3, 0, 0,10, 0, 0,13, 7],
#   [ 0, 0, 0, 8, 0, 0, 0, 7,10, 0, 0, 0, 0, 0, 5, 1],
#   [ 0, 4,10, 1, 6, 0, 0, 0, 0,12, 0,14, 7, 3, 9,15],
#   [ 3, 0,15, 0, 0, 0, 0, 8, 0, 0, 1, 0,14,12, 0, 0],
#   [ 2, 0, 0, 9,12, 0, 0, 1, 0, 0, 0, 0, 0, 6, 8, 0]]

n = q**2  # the size must be the square of the size of the subgrids
N = range(n)

x = {(i, j, k): xp.var(vartype=xp.binary, name='x{0}_{1}_{2}'.format(i, j, k))
     for i in N for j in N for k in N}

# define all q^2 subgrids
subgrids = {(h, l): [(i, j) for i in range(q*h, q*h + q)
            for j in range(q*l, q*l + q)]
            for h in range(q)
            for l in range(q)}

vertical = [xp.Sum(x[i, j, k] for i in N) == 1 for j in N for k in N]
horizontal = [xp.Sum(x[i, j, k] for j in N) == 1 for i in N for k in N]
subgrid = [xp.Sum(x[i, j, k] for (i, j) in subgrids[h, l]) == 1
           for (h, l) in subgrids.keys() for k in N]

# Assign exactly one number to each cell

assign = [xp.Sum(x[i, j, k] for k in N) == 1 for i in N for j in N]

# Fix those variables that are non-zero in the input grid

init = [x[i, j, k] == 1 for k in N for i in N for j in N
        if starting_grid[i][j] == k+1]

p = xp.problem()

p.addVariable(x)
p.addConstraint(vertical, horizontal, subgrid, assign, init)

# we don't need an objective function, as long as a solution is found

p.solve()

print('Solution:')

for i in N:
    for j in N:
        l = [k for k in N if p.getSolution(x[i, j, k]) >= 0.5]
        assert(len(l) == 1)
        print('{0:2d}'.format(1 + l[0]), end='', sep='')
    print('')
