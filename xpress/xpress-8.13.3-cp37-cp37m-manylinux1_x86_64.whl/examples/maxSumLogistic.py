'''
Maximize the sum of logistic curves subject to linear and piecewise linear constraints
Approximate the logistic curves using piecewise linear functions
(c) 2020 Fair Isaac Corporation
'''
import numpy as np
import xpress as xp
import matplotlib.pyplot as plt


def logistic(x, K, r, c):
    return K / (1 + np.exp(-r * (x - c)))


n_curves = 10
N = range(n_curves)
U = 10  # upper bound of the variables

# Create two numpy vectors of variables
x = xp.vars(N, ub=U, name='x')
y = xp.vars(N, name='y')

# Create a problem and add these two vectors
p = xp.problem(x, y)

n_intervals = 100
# define the breakpoints of the piecewise linear terms
breakpoints = np.array([(U / n_intervals) * i for i in range(n_intervals + 1)])

# compute the function values at breakpoints
y_vals = [logistic(breakpoints, U, np.random.uniform(0.5, 3), U / 2) for _ in N]

# Enable to visualize curves
for i in N:
    plt.plot(breakpoints, y_vals[i])

y_vals = np.array(y_vals).flatten().tolist()
x_vals = np.array([])
for i in N:
    x_vals = np.concatenate((x_vals, breakpoints))
x_vals = x_vals.tolist()

# Set the starting indices for the flattened piecewise linear function definitions
start = [i * (n_intervals + 1) for i in N]

# Add piecewise linear functions
p.addpwlcons(x, y, start, x_vals, y_vals)

# Add a constraint that limits the weighted sum of x variables
w = np.random.randint(1, 10, n_curves)
p.addConstraint(xp.Dot(w, x) <= 10)

# Maximize the sum of logistic functions
p.setObjective(xp.Dot(np.ones(n_curves), y), sense=xp.maximize)

p.write('test_logistic.mps', 'mps')

p.solve()
