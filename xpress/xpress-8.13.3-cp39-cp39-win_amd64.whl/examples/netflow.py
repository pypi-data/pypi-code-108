# Example: solving a min-cost-flow problem
# using the Xpress Python interface
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import numpy as np  # for matrix and vector products
import xpress as xp

# digraph definition

V = [1, 2, 3, 4, 5]                                   # vertices
E = [[1, 2], [1, 4], [2, 3], [3, 4], [4, 5], [5, 1]]  # arcs

n = len(V)  # number of nodes
m = len(E)  # number of arcs

# Generate incidence matrix: begin with a NxM zero matrix
A = np.zeros((n,m))

# Then for each column i of the matrix, add a -1 in correspondence to
# the tail of the arc and a 1 for the head of the arc.  Because Python
# uses 0-indexing, the row of A should be the node index minus one.
for i, edge in enumerate(E):
    A[edge[0] - 1][i] = -1
    A[edge[1] - 1][i] =  1

print("incidence matrix:\n", A)

# One (random) demand for each node
demand = np.random.randint(100, size=n)
# Balance demand at nodes
demand[0] = - sum(demand[1:])

cost = np.random.randint(20, size=m)  # Integer, random arc costs

# Flow variables declared on arcs---use dtype parameter to ensure
# NumPy handles these as vectors of Xpress objects.
flow = np.array([xp.var() for i in E], dtype=xp.npvar)

p = xp.problem('network flow')

p.addVariable(flow)
p.addConstraint(xp.Dot(A, flow) == - demand)
p.setObjective(xp.Dot(cost, flow))

p.solve()

print(cost, demand)

for i in range(m):
    print('flow on', E[i], ':', p.getSolution(flow[i]))
