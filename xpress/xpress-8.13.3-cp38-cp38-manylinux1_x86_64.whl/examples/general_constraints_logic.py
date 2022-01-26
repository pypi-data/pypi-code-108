# Here we use the and/or operators of the Python interface to create a
# new optimization problem.
#
# (C) Fair Isaac Corp., 1983-2021

# Solve a simple SAT problem by finding the solution with the fewest
# True variables that satisfy all clauses

import xpress as xp

p = xp.problem()

N = 10
k = 5

x = [xp.var(vartype=xp.binary) for _ in range(N)]

# At most one of each pair can be True
con0 = [(x[i] & x[i+1]) == 0 for i in range(0, N-1, 2)]

# At least a quarter of all OR clauses on continuous groups of k
# clauses must be True
con1 = xp.Sum(xp.Or(*(x[i:i+k])) for i in range(N-k)) >= N/4

p = xp.problem(x, con0, con1)

# Set time limit to 20 seconds
p.controls.maxtime = -20
p.solve()

print("solution: x = ", p.getSolution())
