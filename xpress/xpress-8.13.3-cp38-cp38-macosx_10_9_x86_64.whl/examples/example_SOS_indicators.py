# Construct a problem from scratch with variables of various
# types. Adds indicator constraints, Special Ordered Sets (SOSs), and
# shows how to retrieve such data once it has been added to the
# problem using the API functions.
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function
import xpress as xp

N = 40
S = range(N)

m = xp.problem("test restriction")

xp.controls.miprelstop = 0

#
# All variables used in this example
#

v1 = xp.var(lb=0, ub=10, threshold=5, vartype=xp.continuous)
v2 = xp.var(lb=1, ub=7, threshold=5, vartype=xp.continuous)
v3 = xp.var(lb=5, ub=10, threshold=7, vartype=xp.semicontinuous)
v4 = xp.var(lb=1, ub=7, threshold=3, vartype=xp.semiinteger)
vb = xp.var(vartype=xp.integer, lb=0, ub=1)

v = [xp.var(name="y{0}".format(i), lb=0, ub=2*N) for i in S]

cc = xp.constraint(body=v1 - v2, lb=2, ub=15)
cc0 = xp.constraint(body=v1 + v2, lb=2, ub=15)

# Adds both v, a vector (list) of variables, and v1 and v2, two scalar
# variables.
m.addVariable(vb, v, v1, v2, v3, v4)
m.addConstraint(cc)

# Indices of variables can be retrieved both using their name and
# their Python object.

print("index of v[0] from name: ", m.getIndexFromName(2, "y0"))
print("index of v[0]:           ", m.getIndex(v[0]))

# Indicator constraints consist of a tuple with a condition on a
# binary variable and a constraint).

ind1 = (vb == 1, v1 + v2 >= 6)
ind2 = (vb == 1, v1 + v3 >= 7)
# Adds the first indicator constraint
m.addIndicator(ind1)
# Adds another indicator constraint and the second one defined above
m.addIndicator((vb == 1, v1 + v3 <= 10), ind2)

s = xp.sos([v1, v2], [2, 4], name="mynewsos", type=2)

m.addSOS(s)

# Showcases the use of getIndex()

print("get index: var v1 -->", m.getIndex(v1), "; con cc -->",
      m.getIndex(cc), "; sos -->", m.getIndex(s))

ii_inds = []
ii_comps = []

m.getindicators(ii_inds, ii_comps, 1, 3)

print("getind: ", ii_inds, ii_comps)

print("SOS:", s.name, s)

# Objects such as SOSs, variables, constraints, etc. can be copied
# with the copy() method.

sos2 = s.copy()

# objective overwritten at each setObjective()
m.setObjective(xp.Sum([i*v[i] for i in S]))

m.solve()

# Retrieve a solution: first declare an empty string, then call the
# getmipsol() function to fill it up.

mipsol = []

m.getmipsol(mipsol)

s1 = m.getSolution(v1, v2, v[10:30])  # get a subset of the solutions
s2 = m.getSolution(S)                 # can get it with indices as well

print("v1: ", m.getSolution(v1),
      ", v2: ", m.getSolution(v2),
      "; sol vector: ", m.getSolution(),
      "; obj: ", m.getObjVal(),
      sep="")  # default separator between strings is " "

# Adds yet another constraint to the problem and saves it, then
# removes an SOS and saves another version

m.addConstraint((1.25 * v1 - 2.5*v2 + 4.3) * (3.1 * v2 - 2 * v1 - 5.2)
                + 72.5 * v1**2 + 73 * v2**2 <= 1950)

m.write("restriction", "lp")

m.delSOS(s)
m.write("restriction-noSOS", "lp")

m.solve()

# We create another problem, but can continue to use the objects
# created originally for the first problem. Note that the constraints
# must have been defined here as otherwise a constraint obtained from
# a previously read problem can't be added to another problem.

m2 = xp.problem()

cc2 = cc.copy()

print("name of copy:", cc2.name, ", orig:", cc.name)

m2.addVariable(v1, v2)
m2.addConstraint(cc2)

m2.addConstraint(xp.Sum(2*v1) <= 100)
m2.addConstraint(xp.Sum(44) <= 100)

m2.addSOS(sos2)

m2.addSOS(xp.sos([1, v1], [2, 4], name="mynewsos2", type=2))

m2.write("example3", "lp")
m2.read("example3.lp")

# This is how you can retrieve a SOS using its index
sss = m2.getSOS(0)

print("solution of the restricted problem: ", m.getSolution())
