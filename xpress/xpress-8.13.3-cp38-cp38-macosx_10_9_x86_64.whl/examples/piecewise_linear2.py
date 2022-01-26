# Example that uses the xpress.pwl method to approximate nonlinear
# univariate functions. This is equivalent to piecewise_linear.py,
# where we use xpress.pwl instead of problem.addpwlcons for
# readability.
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp
import math
import numpy as np

x = xp.var(ub=4)

# When using the API functions, we have to define new variables. Note
# that for defining a function that is unrestricted in sign we have to
# define a free variable
y1 = xp.var()
y2 = xp.var(lb=-xp.infinity)

# Approximate sin(freq * x) for x in [0, 2*pi]

N = 100  # Number of points of the approximation
freq = 27.5  # frequency
step = 2 * math.pi / (N - 1)  # width of each x segment

breakpoints = np.array([i * step for i in range(N)])
values = np.sin(freq * breakpoints)  # value of the function
slopes = freq * np.cos(freq * breakpoints)  # derivative

# Create new problem with three variables
p = xp.problem(x, y1, y2)

values2 = values + slopes * step

p.addpwlcons([x, x],    # independent variables
             [y1, y2],  # variables defined as piecewise linear
             [0, 4],    # starting points, within the following
                        # two lists, of the points of each function.

             # x values:
             # for the first pwl function, the breakpoints 0,1,2,3
             [0,  1,  2,  3] +
             # for the second one, we alternate between the beginning
             # and the end of each segment. Note that we use both
             # beginning and end of each interval.
             list(np.hstack(np.array([breakpoints[:-1],breakpoints[1:]]).transpose())),

             # y values:
             # for the first pwl function, the corresponding values of
             # the function.
             [0, 10, 13, 15] +
             # similar to the above, for the second one we add the y
             # values for both beginning and end of each segment,
             # because of the discontinuity.
             list(np.hstack(np.array([values[:-1],values2[:-1]]).transpose())))


# The objective is the difference of the two variables defined as
# piecewise linear functions.
p.setObjective (y1 - y2)

p.solve()

print("solution: x = ", p.getSolution(x))
print("values of piecewise linear functions:", p.getSolution(y1,y2))
print("objective function:", p.getObjVal())
