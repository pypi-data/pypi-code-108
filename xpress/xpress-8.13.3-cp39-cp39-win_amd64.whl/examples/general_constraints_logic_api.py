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

p = xp.problem(x)

# Creates a continuous list despite the 2 step in range()
y_and = [xp.var(vartype=xp.binary) for i in range(0, N-1, 2)]

y_or = [xp.var(vartype=xp.binary) for i in range(N-k)]

p.addVariable(y_and, y_or)

p.addgencons([xp.gencons_and] * (N//2) + [xp.gencons_or] * (N-k),
             y_and + y_or,  # two list of resultants
             [2*i for i in range(N // 2)] +  # colstart is the list [0, 2, 4...] for the AND constraint
             [2 * (N // 2) + k*i for i in range(N-k)],  # ... and then the list [0, k, 2*k...] displaced by 2N
             x[:2 * (N//2)] +                           # consider all original variables in this order
             [x[i+j] for j in range(k) for i in range(N-k)])  # and then variables [0..k-1, 1..k, 2..k+1, ...]

# Set time limit to 20 seconds
p.controls.maxtime = -20
p.solve()

print("solution: x = ", p.getSolution())
