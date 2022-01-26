# Feasibility pump (prototype)
# using the Xpress Python interface
#
# (C) Fair Isaac Corp., 1983-2021

from __future__ import print_function

import xpress as xp


def getRoundedSol(sol, I):
    rsol = sol[:]
    for i in I:
        rsol[i] = round(sol[i])
    return rsol


def computeViol(p, viol, rtype, m):
    for i in range(m):
        if rtype[i] == 'L':
            viol[i] = -viol[i]
        elif rtype[i] == 'E':
            viol[i] = abs(viol[i])
    return max(viol[:m])


p = xp.problem()
p.read('test.lp')

n = p.attributes.cols  # number of columns
m = p.attributes.rows  # number of rows
N = range(n)

vtype = []                   # create empty vector
p.getcoltype(vtype, 0, n-1)  # obtain variable type ('C', for continuous)

I = [i for i in N if vtype[i] != 'C']  # discrete variables

V = p.getVariable()

p.lpoptimize()
sol = []
p.getlpsol(x=sol)
roundsol = getRoundedSol(sol, I)
slack = []
p.calcslacks(roundsol, slack)
rtype = []
p.getrowtype(rtype, 0, m - 1)

#
# If x_I is the vector of integer variables and x_I* is its LP value,
# the auxiliary problem is
#
# min |x_I - x_I*|_1
# s.t. x in X
#
# where X is the original feasible set. Add new variables y and set
# their sum as the objective, then define the l1 norm with the
# constraints
#
# y_i >= x_i - x_i*
# y_i >= - (x_i - x_i*)
#

y = [xp.var() for i in I]

p.addVariable(y)  # add variables for new objective
p.setObjective(xp.Sum(y))  # objective

# rhs to be configured later
defPenaltyPos = [y[i] >= V[I[i]] for i in range(len(I))]
defPenaltyNeg = [y[i] >= - V[I[i]] for i in range(len(I))]

p.addConstraint(defPenaltyPos, defPenaltyNeg)

slackTol = 1e-4

while computeViol(p, slack, rtype, m) > slackTol:

    # modify definition of penalty variable
    p.chgrhs(defPenaltyPos, [-roundsol[i] for i in I])
    p.chgrhs(defPenaltyNeg, [roundsol[i] for i in I])

    # reoptimize
    p.lpoptimize()
    p.getlpsol(x=sol)

    roundsol = getRoundedSol(sol, I)
    p.calcslacks(roundsol, slack)

# Found feasible solution

print('feasible solution:', roundsol[:n])
