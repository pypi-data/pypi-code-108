# Example: changing an optimization problem using the Xpress Python
# interface.
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp

x = xp.var()
y = xp.var()

cons1 = x + y >= 2
upperlim = 2*x + y <= 3

p = xp.problem()

p.addVariable(x, y)
p.setObjective((x-4)**2 + (y-1)**2)
p.addConstraint(cons1, upperlim)

p.write('original', 'lp')

p.chgcoef(cons1, x, 3)  # coefficient of x in cons1    becomes 3
p.chgcoef(1, 0, 4)      # coefficient of y in upperlim becomes 4

p.write('changed', 'lp')
