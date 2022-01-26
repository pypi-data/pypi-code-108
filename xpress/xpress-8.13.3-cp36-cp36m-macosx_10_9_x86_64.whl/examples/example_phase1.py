# Example: given an infeasible LP, find an (infeasible) solution that minimize
# the total distance from the constraints.
#
# Then solve the obtained MaxFS problem.
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp

x = xp.var()
y = xp.var()

# build a very simple problem with pairs of incompatible constraints

p = xp.problem()

p.addVariable(x, y)

lhs1 = 2*x + 3*y
lhs2 = 3*x + 2*y
lhs3 = 4*x + 5*y

p.addConstraint(lhs1 >= 6, lhs1 <= 5)
p.addConstraint(lhs2 >= 5, lhs2 <= 4)
p.addConstraint(lhs3 >= 8, lhs3 <= 7)

p.solve()

assert(p.getProbStatus() == xp.lp_infeas)

# We verified the problem is infeasible. Add one binary for each
# constraint to selectively relax them.

m = p.attributes.rows

# get the signs of all constraints: 'E', 'L', or 'G'. Note that this example
# only works with inequality constraints only
sign = []
p.getrowtype(sign, 0, m - 1)

# big-M, large-enough constant to relax all constraints (quite conservative
# here)
M = 1e3

matval = [M]*m
for i in range(m):
    if sign[i] == 'L':
        matval[i] = -M

# Add m new binary columns

p.addcols([1]*m,  # obj. coefficients (as many 1s as there are constraints)
          range(m + 1),  # cumulative number of terms in each column:
                         # 0,1,2,...,m as there is one term per column
          range(m), matval,  # pairs (row_index, coefficient) for each column
          [0]*m, [1]*m,  # lower, upper bound (binary variables, so {0,1})
          ['b_{}'.format(i) for i in range(m)],  # names are b_i, with i is the
                                                 # constraint index
          ['B']*m)                               # type: binary

p.solve()

# Print constraints constituting a Maximum Feasible Subsystem

b = p.getSolution(range(p.attributes.cols - m, p.attributes.cols))

maxfs = [i for i in range(m) if b[i] > 0.5]

print('MaxFS has ', len(maxfs), 'constraints:', maxfs)
