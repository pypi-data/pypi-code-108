# Problem: given n, find the n-sided polygon of largest area inscribed
# in the unit circle.
#
# While it is natural to prove that all vertices of a global optimum
# reside on the unit circle, here we formulate the problem so that
# every vertex i is at distance rho[i] from the center and at angle
# theta[i]. We would certainly expect that the local optimum found has
# all rho's are equal to 1.
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp
import math
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

N = 9

Vertices = range(N)

# Declare variables
rho = [xp.var(name='rho_{}'.format(i), lb=1e-5, ub=1.0) for i in Vertices]
theta = [xp.var(name='theta_{}'.format(i), lb=-math.pi, ub=math.pi)
         for i in Vertices]

p = xp.problem()

p.addVariable(rho, theta)

# The objective function is the total area of the polygon. Considering
# the segment S[i] joining the center to the i-th vertex and A(i,j)
# the area of the triangle defined by the two segments S[i] and S[j],
# the objective function is
#
# A[0,1] + A[1,2] + ... + A[N-1,0]
#
# Where A[i,i+1] is given by
#
# 1/2 * rho[i] * rho[i+1] * sin (theta[i+1] - theta[i])

p.setObjective(0.5 * (xp.Sum(rho[i] * rho[i-1] * xp.sin(theta[i] - theta[i-1])
                             for i in Vertices if i != 0)
                      # sum of the first N-1 triangle areas
                      + rho[0] * rho[N-1] * xp.sin(theta[0] - theta[N-1])),
               sense=xp.maximize)  # plus area between segments N and 1

# Angles are in increasing order, and should be different (the solver
# finds a bad local optimum otherwise).

p.addConstraint(theta[i] >= theta[i-1] + 1e-4 for i in Vertices if i != 0)

# solve the problem
p.solve()

# The following command saves the final problem onto a file
#
# p.write('polygon{}'.format(N), 'lp')

rho_sol = p.getSolution(rho)
theta_sol = p.getSolution(theta)

x_coord = [rho_sol[i] * math.cos(theta_sol[i]) for i in Vertices]
y_coord = [rho_sol[i] * math.sin(theta_sol[i]) for i in Vertices]

vertices = [(x_coord[i], y_coord[i]) for i in Vertices] + \
           [(x_coord[0], y_coord[0])]

moves = [Path.MOVETO] + [Path.LINETO] * (N-1) + [Path.CLOSEPOLY]

path = Path(vertices, moves)

fig = plt.figure()
sp = fig.add_subplot(111)

patch = patches.PathPatch(path, lw=1)

sp.add_patch(patch)

# Define bounds of picture, as it would be [0,1]^2 otherwise
sp.set_xlim(-1.1, 1.1)
sp.set_ylim(-1.1, 1.1)

plt.show()
