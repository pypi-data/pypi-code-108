from project import  get_poles, get_KKT_point_root,\
        bisection, my_newton, double_newton, project

import fun
from quadrics import Quadric

import matplotlib.pyplot as plt
import numpy as np

eps = pow(10, -6)


def test_get_e1():
    dim = 6
    A = np.eye(dim)
    A[0, 0] = 0.5
    A[2, 2] = -2
    param = {'A': A, 'b': np.zeros(dim), 'c': -2}
    Q = Quadric(param)
    print(A)

    x0_not_std = np.zeros(dim)
    x0_not_std[0] = 1
    x0_not_std[2] = 3
    x0 = Q.to_standardized(x0_not_std)
    print(x0)

    e1 = fun._get_e1(Q, x0)
    print('e1 = ', e1)
    
    A = np.eye(dim)
    A[0, 0] = 0.5
    A[2, 2] = -2
    A[5, 5] = -4
    param = {'A': A, 'b': np.zeros(dim), 'c': -2}
    Q = Quadric(param)
    print(A)

    x0_not_std = np.ones(dim)
    x0_not_std[0] = 10
    x0_not_std[1] = 2
    x0_not_std[2] = 3
    x0 = Q.to_standardized(x0_not_std)
    print(x0)
    e1 = fun._get_e1(Q, x0)
    print('e1 = ', e1)
    e2 = fun._get_e2(Q, x0)
    print('e2 = ', e2)
    
    dim = 6
    A = np.eye(dim)
    A[0, 0] = -0.5
    A[2, 2] = -2
    param = {'A': A, 'b': np.zeros(dim), 'c': -2}
    Q = Quadric(param)

    x0_not_std = np.zeros(dim)
    x0_not_std[0] = 1
    x0_not_std[2] = 3
    x0 = Q.to_standardized(x0_not_std)
    assert fun._get_e1(Q, x0) == -np.inf


def test_get_poles():
    dim = 6
    A = np.eye(dim)
    A[0, 0] = -0.5
    A[2, 2] = -2
    param = {'A': A, 'b': np.zeros(dim), 'c': -2}
    Q = Quadric(param)
    x0_not_std = np.zeros(dim)
    x0 = Q.to_standardized(x0_not_std)
    print(A, x0)
    poles = get_poles(Q, x0)
    assert len(poles) == 0
    
    x0_not_std[0] = 1
    x0_not_std[1] = 0.3
    x0 = Q.to_standardized(x0_not_std)
    poles = get_poles(Q, x0)
    assert len(poles) == 2

def test_f():
    show = False
    dim = 6
    A = np.eye(dim)
    A[0, 0] = -0.5
    A[2, 2] = -2
    param = {'A': A, 'b': np.zeros(dim), 'c': -2}
    Q = Quadric(param)

    x0_not_std = np.zeros(dim)
    x0_not_std[0] = 0
    x0_not_std[1] = 1
    print(A, x0_not_std)
    x0 = Q.to_standardized(x0_not_std)

    F = fun.Fun(Q, x0)

    print('e_1, e_2', F.e1, F.e2)
    if F.e1 is not - np.inf:
        if F.e2 == np.inf:
            mu_1 = bisection(F, 'right')

    output_newton = my_newton(F, mu_1)

    print(output_newton)

    if show:
        t = np.linspace(F.e1, F.e2, 50)
        plt.plot(t, F.f(t))
        plt.show()

def test_double_newton():
    dim = 6
    A = np.eye(dim)
    A[0, 0] = -0.5
    A[2, 2] = -2
    param = {'A': A, 'b': np.zeros(dim), 'c': -2}
    Q = Quadric(param)

    x0_not_std = np.zeros(dim)
    x0_not_std[0] = 0
    x0_not_std[1] = 1
    print(A, x0_not_std)
    x0 = Q.to_standardized(x0_not_std)
    F = fun.Fun(Q, x0)

    output_newton = double_newton(F)
    print(output_newton)


def test_double_newton_2():
    dim = 6
    #np.random.seed(42)
    _A = np.random.rand(dim, dim)

    A = (_A + _A.T)/2
    

    param = {'A': A, 'b': np.zeros(dim), 'c': -2}
    Q = Quadric(param)

    x0_not_std = np.zeros(dim)
    x0_not_std[0] = 0
    x0_not_std[1] = 1
    x0 = Q.to_standardized(x0_not_std)
    F = fun.Fun(Q, x0)

    output_newton = double_newton(F)
    print('quadric is ', Q.type)
    print('quadric is empty ? ', Q.is_empty)
    mu_star, x_star = get_KKT_point_root(Q, x0_not_std)
    print('x_star')
    print(Q.is_feasible(x_star))

def test_project():
    dim = 6
    #np.random.seed(42)
    _A = (np.random.rand(dim, dim))*2

    A = (_A + _A.T)/2 - 3*np.eye(dim)
    

    param = {'A': A, 'b': np.zeros(dim), 'c': -2}
    Q = Quadric(param)

    x0_not_std = np.zeros(dim)
    x0_not_std[0] = 0
    x0_not_std[1] = 1
    x0 = Q.to_standardized(x0_not_std)
    F = fun.Fun(Q, x0)
    x_project = project(Q, x0_not_std)
    print(Q.is_feasible(x_project))
    print('L', Q.L)


def test_project_2D():
    #np.random.seed(42)
    dim = 2
    A = np.random.rand(dim, dim)
    A = A+ A.T
    A[0, 0] = 2

    param = {'A': A, 'b': np.random.rand(dim), 'c': -2}
    Q = Quadric(param)

    x0_not_std = np.zeros(dim)
    x0_not_std[0] = 0
    x0_not_std[1] = 3
    x0 = Q.to_standardized(x0_not_std)
    F = fun.Fun(Q, x0)
    x_project = project(Q, x0_not_std)
    Q.plot()
    print(np.linalg.norm(x0_not_std - x_project), F.dist(x_project))
    circle1 = plt.Circle(x0_not_std, F.dist(x_project), edgecolor='r', facecolor='None')
    ax = plt.gca()
    ax.add_artist(circle1)

    plt.scatter(x0_not_std[0], x0_not_std[1], c='black')
    plt.scatter(x_project[0], x_project[1], c='red')
    plt.show()
    print(Q.is_feasible(x_project))
    print('L', Q.L)
