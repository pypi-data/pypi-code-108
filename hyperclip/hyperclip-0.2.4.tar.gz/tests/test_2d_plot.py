# -*- coding: utf-8 -*-

import numpy as np
import hyperclip
from matplotlib import pyplot as plt

n = 2
m = 3

np.random.seed(29)
hyperplanes = [hyperclip.Hyperplane().set_by_points(np.random.random((n,n))) for i_m in range(m)]
np.random.seed(None)

X = np.random.random((10**6,n))

id_pos_side = np.ones(X.shape[0])
for hyp in hyperplanes:
    id_pos_side = np.all((id_pos_side, hyp.side(X)), axis=0)

# fig, axs = plt.subplots()
# axs.set_aspect('equal', 'box')
# plt.scatter(X[id_pos_side, 0], X[id_pos_side, 1], s=2, color='gray')

for hyp in hyperplanes:
    sol = hyp.compute_n_solutions()
    x_a, y_a, x_b, y_b = sol.flat
    
    a = (y_b-y_a)/(x_b-x_a)
    b = y_a - x_a * a
    
    y_0 = b
    y_1 = a * 1 + b
    
    # plt.plot([0, 1], [y_0, y_1])
# plt.xlim([0,1])
# plt.ylim([0,1])

hc = hyperclip.Hyperclip().set_hyperplanes(hyperplanes)


A = np.array([[-1.,   1,  0],
                [ 0,    0,  1],
              [-1,   -2, -1]]).T
R = np.array([0.5, 
                -0.5, 
              3])

A = np.array([[0.25585178874659287],
              [0.022416578071991308]])
R = np.array([2.5814930867384747])

hc = hyperclip.Hyperclip(cython=True, verbose=1).set_A_R(A, R)

from time import time
st = time()
vol = hc.volume()
et = time()
print('vol', vol, 'time', et-st)

# st = time()
# cond_A = hc._clipping_condition_A()
# et = time()
# print('A python', cond_A, et-st)

# print('B cond', hyperclip.hyperfunc.clipping_condition_B_numpy(A, R))

# st = time()
# vol = hyperclip.hyperfunc.volume_numpy(A, R, check_A=True)
# et = time()
# print('vol cython', vol, et-st)

# st = time()
# vol = hc.volume()
# et = time()
# print('vol python', vol, et-st)

# A = np.array([[-1],
              # [4.6*10**-310]])

# hc.check()
# vol = hc.volume()
# print('10**6 MonteCarlo : ', id_pos_side.mean(), 'Hyperclip :', vol)

# plt.text(0.25,0.2, "10**6 MonteCarlo : "+str(round(id_pos_side.mean(),4)))
# plt.text(0.25,0.1, "Hyperclip : "+str(round(vol,4)))
# plt.show()

# A = np.array([[10,12.5,2.1],
#               [4,5.5,3.2],
#               [5.1,6.3,-5.4]])
# # A = np.array([[1, 0, 2, -1],
# #            [3, 0, 0, 5],
# #            [2, 1, 4, -3],
# #            [1, 0, 5, 0]]).astype(np.double)
# print(np.linalg.det(A))

# hyperclip.hyperfunc.determinant_numpy(A)