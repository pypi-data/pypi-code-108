#!/usr/bin/env python3

import numpy as np
from quadrics import Quadric
import matplotlib.pyplot as plt

eps_test = pow(10, -6)

def test_initiate_quadrics():
    param = {}
    param['A'] = np.array([[2, 0.4], [0.4, -1]])
    param['b'] = np.array([1, 1])
    param['c'] = 0

    x0 = np.array([0, 1])

    Q = Quadric(param)
    print('Is it standardize?', Q.is_standardized)

    param['diagonalize'] = False
    Q = Quadric(param)

    param['diagonalize'] = None
    Q = Quadric(param)
    Q.is_feasible(x0)

    param['diagonalize'] = True
    Q = Quadric(param)
    return Q


def test_equivalence_std():
    param = {}
    param['A'] = np.array([[2, 0.4], [0.4, -1]])
    param['b'] = np.array([1, 1])
    param['c'] = 0


    Q = Quadric(param)
    assert Q.is_standardized
    x0_not_std = np.array([0, 1])
    print(Q.is_feasible(x0_not_std))
    x0 = Q.to_standardized(x0_not_std)
    assert abs(Q.evaluate_point(x0_not_std) - np.dot(np.dot(x0, Q.A_std), x0) - Q.c_std) < eps_test


    param = {}
    param['A'] = np.array([[-1, 0], [0, 2]])
    param['b'] = np.array([1, 0])
    param['c'] = -2
    param['diagonalize'] = True
    Q = Quadric(param)
    x0_not_std = np.array([1, 1])

    assert Q.is_feasible(x0_not_std), 'Two points are equivalent iff they are feasible'
    x0 = Q.to_standardized(x0_not_std)

    assert np.all(x0_not_std == Q.to_non_standardized(x0)), 'Transform to and from standardized yield an error'
    assert abs(Q.evaluate_point(x0_not_std) - np.dot(np.dot(x0, Q.A_std), x0) - Q.c_std) < eps_test

def test_plot_2D():
    show = False
    param = {}
    param['A'] = np.array([[2, 0.4], [0.4, 1]])
    param['b'] = np.array([1, 1])
    param['c'] = 0.3
    try:
        Q = Quadric(param)
    except Quadric.EmptyQuadric:
        print('Correctly catch empty quadric!')

    param = {}
    param['A'] = np.array([[2, 0.4], [0.4, -1]])
    param['b'] = np.array([1, 1])
    param['c'] = -1
    Q = Quadric(param)
    fig, ax = plt.subplots()
    Q.plot(ax, fig, show=show)
    
    param = {}
    param['A'] = np.array([[2, 0.4], [0.4, 1]])
    param['b'] = np.array([1, 1])
    param['c'] = -1
    Q = Quadric(param)
    fig, ax = plt.subplots()
    Q.plot(ax, fig, show=show)
    plt.close('all')


def test_plot_3D():

    show = False
    print('\n\n Ellipsoid \n\n')

    param = {}
    param['A'] = np.array([[2, 0.4, 0.5], [0.4, 1, 0.6], [0.5, 0.6, 3]])
    param['b'] = np.array([1, 1, 0])
    param['c'] = -1.5
    Q = Quadric(param)

    Q.plot(show=show)
    
    
    print('\n\n One sheet hyperboloid \n\n')

    param = {}
    param['A'] = np.array([[2, 0.4, 0.5], [0.4, 1, 0.6], [0.5, 0.6, -3]])
    param['b'] = np.array([1, 1, 0])
    param['c'] = -1.5
    Q = Quadric(param)

    Q.plot(show=show)
    
    print('\n\n One sheet hyperboloid \n\n')

    param = {}
    param['A'] = np.array([[-2, 0.4, 0.5], [0.4, 1, 0.6], [0.5, 0.6, -3]])
    param['b'] = np.array([1, 1, 0])
    param['c'] = -1.5
    Q = Quadric(param)

    Q.plot(show=show)
    plt.close('all')
