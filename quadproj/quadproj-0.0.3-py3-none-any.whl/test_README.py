#from quadproj import quadrics
#from quadproj.project import project

import quadrics
from project import project

import matplotlib.pyplot as plt
import numpy as np


# creating random data
dim = 3
_A = np.random.rand(dim, dim)
A = _A + _A.T  # make sure that A is positive definite
b = np.random.rand(dim)
c = -1


param = {'A': A, 'b': b, 'c': c}
Q = quadrics.Quadric(param)

x0 = np.random.rand(dim)
x_project = project(Q, x0)


if dim <= 3 and False:
    fig, ax = Q.plot()
    plt.show()

dim = 3
A = np.eye(dim)
A[0, 0] = 4
A[1, 1] = 0.5

b = np.zeros(dim)
c = -1

show = False
param = {'A': A, 'b': b, 'c': c}
Q = quadrics.Quadric(param)
Q.plot(show=True)
Q.get_gif(step=2, gif_path=Q.type+'.gif')

A[0, 0] = -4
param = {'A': A, 'b': b, 'c': c}
Q = quadrics.Quadric(param)
Q.plot(show=True)
Q.get_gif(step=2, gif_path=Q.type+'.gif')

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
Q.get_gif(step=2, gif_path=Q.type+'.gif')
