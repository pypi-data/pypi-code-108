from quadproj import quadrics
from quadproj.project import project, plot_x0_x_project

# import quadrics
# from project import project, plot_x0_x_project

from os.path import join


import matplotlib.pyplot as plt
import numpy as np


# Snippet 1

# creating random data
dim = 42
_A = np.random.rand(dim, dim)
A = _A + _A.T  # make sure that A is positive definite
b = np.random.rand(dim)
c = -1.42


param = {'A': A, 'b': b, 'c': c}
Q = quadrics.Quadric(param)

x0 = np.random.rand(dim)
x_project = project(Q, x0)


# Snippet 2


A = np.array([[1, 0.1], [0.1, 2]])
b = np.zeros(2)
c = -1
Q = quadrics.Quadric({'A': A, 'b': b, 'c': c})

x0 = np.array([2, 1])
x_project = project(Q, x0)

fig, ax = plot_x0_x_project(Q, x0, x_project)
plt.savefig(join('output', 'ellipse_no_circle.png'))


#  Snippet 3

fig, ax = plot_x0_x_project(Q, x0, x_project, flag_circle=True)
plt.savefig(join('output', 'ellipse_circle.png'))


#  Snippet 4

x0 = Q.to_non_standardized(np.array([0, 0.1]))
x_project = project(Q, x0)
fig, ax = plot_x0_x_project(Q, x0, x_project, flag_circle=True)
plt.savefig(join('output', 'ellipse_degenerated.png'))
plt.show()

#  Snippet 5

A[0, 0] = -2
Q = quadrics.Quadric({'A': A, 'b': b, 'c': c})
x0 = Q.to_non_standardized(np.array([0, 0.1]))
x_project = project(Q, x0)
fig, ax = plot_x0_x_project(Q, x0, x_project, flag_circle=True)
plt.savefig(join('output', 'hyperbola_degenerated.png'))
plt.show()


#  Snippet 6

dim = 3
A = np.eye(dim)
A[0, 0] = 4
A[1, 1] = 0.5

b = np.zeros(dim)
c = -1


#  Snippet 7

show = False
step = 5

param = {'A': A, 'b': b, 'c': c}
Q = quadrics.Quadric(param)
Q.plot(show=show)
Q.get_gif(step=step, gif_path=Q.type+'.gif')


#  Snippet 8

A[0, 0] = -4
param = {'A': A, 'b': b, 'c': c}
Q = quadrics.Quadric(param)
Q.plot(show=show)
Q.get_gif(step=step, gif_path=Q.type+'.gif')


#  Snippet 9

_A = np.random.rand(dim, dim)
A = _A + _A.T  # make sure that A is positive definite

A = np.eye(dim)
A[0, 0] = 4
A[1, 1] = -2
A[2, 2] = -1

b = np.random.rand(dim)

param = {'A': A, 'b': b, 'c': c}


Q = quadrics.Quadric(param)
Q.plot(show=show)
Q.get_gif(step=step, gif_path=Q.type+'.gif')
