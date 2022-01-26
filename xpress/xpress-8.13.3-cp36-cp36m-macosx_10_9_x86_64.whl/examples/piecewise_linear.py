# Example that uses the xpress.pwl method to approximate nonlinear
# univariate functions.
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp
import math
import numpy as np

x = xp.var(ub=4)

# Piecewise linear, continuous concave function
pw1 = xp.pwl({(0, 1):      10*x,
              (1, 2): 10 +  3*(x-1),
              (2, 3): 13 +  2*(x-2),
              (3, 4): 15 +    (x-3)})

# Approximate sin(freq * x) for x in [0, 2*pi]

N = 100  # Number of points of the approximation
freq = 27.5  # frequency
step = 2 * math.pi / (N - 1)  # width of each x segment

breakpoints = np.array([i * step for i in range(N)])
values = np.sin(freq * breakpoints)  # value of the function
slopes = freq * np.cos(freq * breakpoints)  # derivative

# Piecewise linear, discontinuous function over N points: over the
# i-th interval, the function is equal to v[i] + s[i] * (y - b[i])
# where v, s, b are value, slope, and breakpoint.
pw2 = xp.pwl({(breakpoints[i], breakpoints[i+1]):
              values[i] + slopes[i] * (x - breakpoints[i]) for i in range(N - 1)})

p = xp.problem(x)  # create a problem and add variable x

p.setObjective (pw1 - pw2)

p.solve()

print("solution: x = ", p.getSolution(x))
print("values of piecewise linear functions:", xp.evaluate([pw1, pw2], problem=p))
print("objective function:", p.getObjVal())
