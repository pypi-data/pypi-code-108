#!/usr/bin/env python3

from itertools import product
import scipy
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import os
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
import time
import unittest

import quadproj.quadrics

import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib import cm
from matplotlib.patches import Rectangle
from matplotlib.legend_handler import HandlerBase
from matplotlib.collections import LineCollection

fontP = FontProperties()
fontP.set_size('xx-small')
mm = 3


def colored_line(x, y, s, e, cmap, ax, n_points, m=mm):
    lx = len(x)
    if m == 0:
        xx = x
        yy = y
        cc = np.arange(s, e)
    else:
        xx = x[m-1:lx-m+1]
        yy = y[m-1:lx-m+1]
        cc = np.arange(s+m-1, e-m+1)

    points = np.array([xx, yy]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(0, n_points-1)
    if m == 0:
        lc = LineCollection(segments, cmap=cmap, norm=norm, linestyle='dotted')
    else:
        lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(cc)
    line = ax.add_collection(lc)
    if m != 0:
        colored_line(x[:m], y[:m], s, s+m, cmap, ax, n_points, 0)
        colored_line(x[lx-m:], y[lx-m:], e-m, e, cmap, ax, n_points, 0)
    return line


class HandlerColormap(HandlerBase):
    def __init__(self, cmap, num_stripes=8, **kw):
        HandlerBase.__init__(self, **kw)
        self.cmap = cmap
        self.num_stripes = num_stripes
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        stripes = []
        for i in range(self.num_stripes):
            s = Rectangle([xdescent + i * width / self.num_stripes, ydescent],
                          width / self.num_stripes,
                          height,
                          fc=self.cmap((2 * i + 1) / (2 * self.num_stripes)),
                          transform=trans)
            stripes.append(s)
        return stripes


def _get_demand(str_data):
    f = open(os.path.join(str_data, 'Demand.csv'), "r")
    line = f.readline()
    f.close()
    return line.split(',')[1]


def _get_ranges(_str_data):
    str_data_max = os.path.join('data', _str_data, 'MaxRunCapacity.csv')
    x_max = np.array(pd.read_csv(str_data_max, header=None).iloc[:, 1])
    str_data_min = os.path.join('data', _str_data, 'MinRunCapacity.csv')
    x_min = np.array(pd.read_csv(str_data_min, header=None).iloc[:, 1])
    return x_min, x_max


def test_exact_proj():
    param = {}
    param['A'] = np.array([[2, 0.4], [0.4, -1]])
    param['b'] = np.array([2, 0.5])
    param['c'] = -1
    param['projection_type'] = 'exact'  # quasi exact quasi-dir
    param_alg = Param_alg('alternate-projection', dim=2)
    param['alg'] = param_alg
    Q = Quadric(param)
    p0 = Q.V[:, 0]
    x_feas = Q.project(p0)
    dim = param['b'].shape[0]
    x_n = abs(np.random.rand(dim)*100)
    x_m = abs(np.random.rand(dim)*100)
    x_min = x_feas - x_n
    x_max = x_feas + x_m

    B = Box(x_min, x_max)
    x0 = x_min + ( x_max - x_min)/2
    x_proj = exact_proj(B, Q, x0)
    print('x_proj', x_proj)
    print(Q.is_feasible(x_proj))
    assert is_feasible(B, Q, x_proj), 'Projection yields to infeasible point'

def test_compare_proj(dim=2):
    param = {}
    s = 0.00001
    _A = (np.random.rand(dim, dim)-0.)*s
    param['A'] = (_A + _A.T)/2 + 0.0001 * np.eye(dim)
    param['b'] = -1+0.001*np.random.rand(dim)
    param['c'] = 150*dim
    param['projection_type'] = 'quasi'  # quasi exact quasi-dir
    param_alg = Param_alg('alternate-projection', dim)
    param['alg'] = param_alg
    param['projection_type'] = 'exact'
    plt.close()
    plt.clf()
    fig = plt.figure(1)
    Q = Quadric(param)
    #  One should create a feasible problem !
    try:
        x_min, x_max, x_feas = get_feas_ranges(Q, scale=100)  # 100 shift
    except NoFeasibleDirection:
        print('Coucou')
        return test_compare_proj(dim)
    param['x_min'] = x_min
    param['x_max'] = x_max
    B = Box(x_min, x_max)
    Om = Omega(B, Q, x_feas)
    Om.print_info()
    Om = get_omega(param)
    B = Om.B
    Q = Om.Q
    x0 = (x_max + x_min)/2
    if dim == 2:
        ax = fig.add_subplot()
        Q.plot(ax, fig)
        B.plot(ax, fig)
        #Om.plot_planes_relax(ax, fig)
        plt.scatter(x0[0], x0[1], color='black')
        plt.show()
    elif dim == 3 and True:
        ax = fig.add_subplot(projection='3d')
        Q.plot(ax, fig)
        B.plot(ax, fig)
        #Om.plot_planes_relax(ax, fig)
        plt.scatter(x0[0], x0[1], s=x0[2], color='black')
        plt.show()
    tic_alt = time.time()
    iterates, _ = project(B, Q, x0, param)
    time_alt = time.time() - tic_alt
    print(iterates)
    if not is_feasible(B, Q, iterates[-1]):
        #raise TODO
        plt.show()
        raise
        pass
    tic_exact = time.time()
    x_exact = exact_proj(B, Q, x0)
    time_exact = time.time() - tic_exact
    if x_exact is None:
        x_exact = iterates[-1]
        err_exact = np.inf
    else:
        print('||x_alt - x0|| =', np.linalg.norm(iterates[-1] - x0))
        print('||x_exact - x0|| =', np.linalg.norm(x_exact - x0))
        err_exact = np.linalg.norm(x_exact - x0)
    err_alt = np.linalg.norm(iterates[-1] - x0)
    return (err_alt, err_exact), (time_alt, time_exact)

def test_data(_str_data = 'data_3', flag_show=False):
    str_data = os.path.join('data', _str_data)
    str_A = os.path.join(str_data, 'Bloss.csv')
    str_b = os.path.join(str_data, 'Bloss_0.csv')
    str_c = os.path.join(str_data, 'Bloss_00.csv')
    D = _get_demand(str_data)
    param = {}
    x_min, x_max = _get_ranges(_str_data)
    param['A'] = np.genfromtxt(str_A, delimiter=',')
    dim = param['A'].shape[0]
    if os.path.exists(str_b):
        param['b'] = -1+np.genfromtxt(str_b, delimiter=',') 
    else:
        param['b'] = -np.ones(dim)
    if os.path.exists(str_c):
        param['c'] = np.genfromtxt(str_c, delimiter=',') + float(D)
    else:
        param['c'] = float(D)
    param['x_min'] = x_min
    param['x_max'] = x_max
    param['projection_type'] = 'quasi'
    param['standardize'] = False
    param_alg = Param_alg('alternate-projection', dim=dim)
    param['alg'] = param_alg
    Om = get_omega(param)
    x0 = (Om.B.x_max + Om.B.x_min)/2
    Om.set_planes_relax()
    x0 = Om.get_point_in_relaxation()
    tic_alt = time.time()
    iterates, _ = project(Om.B, Om.Q, x0, param)
    time_alt = time.time() - tic_alt
    tic_exact = time.time()
    x_exact = exact_proj(Om.B, Om.Q, x0)
    time_exact = time.time() - tic_exact
    print('||x_alt - x0|| = %s obtained in %s seconds' % (np.linalg.norm(iterates[-1] - x0), time_alt))
    print(x_exact, x0)
    print('||x_exact - x0|| = %s obtained in %s seconds' % (np.linalg.norm(x_exact - x0), time_exact))

    fig, ax = Om.plot(flag_show=False)

    ax.set_xlim([x_min[0]-10, x_max[0]+10])
    ax.set_ylim([x_min[1]-10, x_max[1]+10])
    ax.set_zlim([x_min[2]-10, x_max[2]+10])
    if flag_show:
        plt.show()


def plot_comparison():
    n_dim = range(2, 4)
    m = 100
    err_alt = {}
    err_exact = {} 
    time_alt = {}
    time_exact = {}
    rel_err = {}
    time_rel = {}
    for dim in n_dim:
        print('\n\n ********* Dim = %s ********* \n\n' % dim)
        err_alt[dim] = np.zeros(m)
        err_exact[dim] = np.zeros(m)
        rel_err[dim] = np.zeros(m)
        time_alt[dim] = np.zeros(m)
        time_exact[dim] = np.zeros(m)
        time_rel[dim] = np.zeros(m)
        for _m in range(m):
            _err, _time = test_compare_proj(dim)
            err_alt[dim][_m] = _err[0]
            err_exact[dim][_m] = _err[1]
            rel_err[dim][_m] = _err[0]/_err[1]
            time_alt[dim][_m] = _time[0]
            time_exact[dim][_m] = _time[1]
            time_rel[dim][_m] = _time[0]/_time[1]
        mean_nan = np.mean(time_rel[dim][not np.isnan(time_rel[dim]).all()])
        # time_rel[dim][np.isnan(time_rel[dim]).all()] = 42
    data_to_pickle = {'err_alt': err_alt, 'err_exact': err_exact, 'time_alt': time_alt,
                      'rel_err': rel_err, 'time_rel': time_rel, 'time_exact': time_exact, 'm': m, 'n_dim': n_dim}
    with open('tmp/comparison.pickle', 'wb') as handle:
        pickle.dump(data_to_pickle, handle, protocol=pickle.HIGHEST_PROTOCOL)
    

    ax2 = ax1.twinx()
    color_err = 'blue'
    color_time = 'red'
    ax1.plot(n_dim, [np.mean(rel_err[dim]) for dim in n_dim], color=color_err, label='Alt error')
    ax2.plot(n_dim, [np.mean(time_rel[dim]) for dim in n_dim], color=color_time, label='Time')
    ax1.set_xlabel('dim')
    ax1.set_ylabel(r'mean((d_alt - d_ex)/d_ex)  ', color=color_err)
    ax2.set_ylabel(r'mean(log( 1 + (time_ex - time_alt)/time_alt))', color=color_time)
    fig.savefig('Comparison.eps')
    fig.savefig('Comparison.png')

def test_ellipsoid():
    param = {}
    param['A'] = np.array([[1, 0.4], [0.4, 1]])
    param['b'] = np.array([0, 0])
    param['c'] = -1
    param['projection_type'] = 'quasi'  # quasi exact quasi-dir
    param_alg = Param_alg('alternate-projection', dim=2)
    param['alg'] = param_alg
    Q = Quadric(param)
    fig, ax = plt.subplots()
    Q.plot(ax, fig)
    p = np.array([0.5, 0])
    #print(Q.is_feasible(p))
    ranges = {'x_min': 0, 'x_max': 1, 'y_min': 0.5, 'y_max': 1}
    x_min = np.array([0, 0.5])
    x_max = np.array([1, 1])
    B = Box(x_min, x_max)

    x = []
    iterates = []

    iterates.append([0.25, 1.5])  # first iterate
    
    #q = retraction(Q, iterates[0])
    q = box_proj(B, iterates[0])

    print('q =  ', q)
    print('In box ?', B.is_feasible(q))
    print('In box ?', B.is_feasible([1.5, 1]))
    iterates.append(q)
    x0 = np.array([-1, -1])
    x0 = (np.random.rand(2)-0.5)*2
    iterates, _ = project(B, Q, x0, param)
    iterates_np = np.array(iterates)

    plot_iterates(iterates_np, ax, fig)
    iterates_np = np.array(iterates)
    plot_iterates(iterates_np, ax, fig)
    fig, ax = plt.subplots()
    B.plot(ax, fig, save=True)

def test_omega(dim=2):
    param = {}
    s = 0.00001
    s = 0.001
    _A = (np.random.rand(dim, dim)-0.5)*s
    param['A'] = (_A + _A.T)/2 + np.mean(_A) * np.eye(dim)
    param['b'] = 0.1*np.random.rand(dim)
    param['c'] = -1
    param['projection_type'] = 'quasi'
    param_alg = Param_alg('alternate-projection')
    param['alg'] = param_alg
    x_n = abs(np.random.rand(dim)*10)
    x_m = abs(np.random.rand(dim)*10)
    Q = Quadric(param)
    print('Initial eig', Q.eig)
    if np.all(Q.eig < 0):
        return test_omega(dim=dim)
    p0 = Q.d +  np.random.rand(dim)
    print('My current eig', Q.eig)
    x_feas = Q.project(p0, forced_projection='exact')
    assert Q.is_feasible(x_feas)
    print('Eigenvalue', Q.eig)
    print(Q.is_feasible(x_feas))
    x_min = x_feas - x_n
    x_max = x_feas + x_m
    B = Box(x_min, x_max)
    x0 = ( x_max + x_min)/2

    Om = Omega(B, Q, x_feas)
    #Om.reduce_box()
    plt.close()
    plt.clf()
    fig = plt.figure(1)
    if dim == 2:
        ax = fig.add_subplot()
    elif dim == 3:
        ax = fig.add_subplot(projection='3d')
    if dim in [2, 3]:
        Q.plot(ax, fig, show=False)
        B.plot(ax, fig)
        Om.B.plot(ax, fig, color='r', show=False)
    print('Initializing random point and start iterating')
    

    x0 = (Om.B.x_max + Om.B.x_min)/2
    Om.set_planes_relax()
    x0 = Om.get_point_in_relaxation()
    tic_alt = time.time()
    iterates, _ = project(B, Q, x0, param)
    time_alt = time.time() - tic_alt
    tic_exact = time.time()
    x_exact = exact_proj(Om.B, Om.Q, x0)
    time_exact = time.time() - tic_exact
    print('||x_alt - x0|| =', np.linalg.norm(iterates[-1] - x0))
    print('||x_exact - x0|| =', np.linalg.norm(x_exact - x0))
    err_alt = np.linalg.norm(iterates[-1] - x0)
    err_exact = np.linalg.norm(x_exact - x0)
    if False or not is_feasible(B, Q, iterates[-1]):
        iterates_np = np.array(iterates)
        plot_iterates(iterates_np, ax, fig)
        #Om.plot_planes_relax(ax, fig)
        plt.show()



def test_run_project_2D():
    param = {}
    dim = 2
    param['A'] = np.array([[2, 0.4], [0.4, 1]])
    param['b'] = np.array([2, 0.5])
    param['c'] = -1
    param['projection_type'] = 'exact'  # quasi exact quasi-dir
    param_alg = Param_alg('douglas-rachford', dim)
    param_alg = Param_alg('dykstra', dim)
    param_alg = Param_alg('alternate-projection', dim)
    param['alg'] = param_alg
    x_min = np.array([0, 0.5])
    x_max = np.array([1, 1])
    for i in range(1):
        run_project(param, gif_name=str(i) + '_out.gif')

def test_run_project_3D():
    param = {}

    # Ellipsoid 
    param['A'] = np.array([[2, 0.4, -0.1], [0.4, 1, 0.2], [-0.1, 0.2, 0.4]])
    # Two sheets hyperboloid
    param['A'] = np.array([[1, 0.4, -0.1], [0.4, 0, 0.2], [-0.1, 0.2, -1]])
    # One sheet hyperboloid
    param['A'] = np.array([[1, 0.4, -0.1], [0.4, 0, 0.2], [-0.1, 0.2, 0]])
    param['projection_type'] = 'quasi'
    param_alg = Param_alg('alternate-projection', dim=3)
    param['alg'] = param_alg


    param['b'] = np.array([2, 0.5, 0])
    param['c'] = -10
    x_min = np.array([0, 0.5, 0.25])
    x_max = np.array([1, 1, 1])
    for i in range(1):
        run_project(param, gif_name=str(i) + '_out.gif', gif='iterates')

def test_run_project_n_D(dim=2):
    param = {}
    plt.close()
    plt.clf()
    s = 10
    _A = (np.random.rand(dim, dim)-0.5)*s
    param['A'] = (_A + _A.T)/2 + 0.0001 * np.eye(dim)
    param['b'] = -1+0.001*np.random.rand(dim)
    param['c'] = 150*dim
    param['projection_type'] = 'quasi'
    param_alg = Param_alg('alternate-projection', dim)
    param['alg'] = param_alg
    Q = Quadric(param)
    try:
        x_min, x_max, x_feas = get_feas_ranges(Q, scale=10)
    except NoFeasibleDirection:
        fig, ax = plt.subplots()
        Q.plot(ax, fig)
        plt.show()
    B = Box(x_min, x_max)
    x0 = x_min + 1.5*(x_max-x_min)

    fig = plt.figure(1)
    if dim == 2 and False:
        ax = fig.add_subplot()
        Q.plot(ax, fig, show=False)
    elif dim == 3:
        ax = fig.add_subplot(projection='3d')
        Q.plot(ax, fig, show=False)
    
     

    # One should create a feasible problem !
    param['x_min'] = x_min
    param['x_max'] = x_max
    Om = get_omega(param, Q)
    print('x0 is', x0)
    print(is_feasible(B, Q, x0))
    print('Initializing random point and start iterating')
    iterates, _ = project(B, Q, x0, param)
    if True or not is_feasible(B, Q, iterates[-1]) and dim <=3:
        fig, ax = get_fig_ax(Q.dim)
        B.plot(ax, fig)
        Q.plot(ax, fig)
        iterates_np = np.array(iterates)
        plot_iterates(iterates_np, ax, fig)
        ax.legend(loc='lower left')
        fig.savefig('tmp/fig.png')
        fig.savefig('tmp/fig.pdf')
        plt.show()

def test_exact_proj_quadric():

    param_hyperbole = {}
    param_hyperbole['A'] = np.array([[-0.003, 0.00894], [0.00894, -0.00145778]]) # 2 0.4 // 0.4-1
    param_hyperbole['b'] = np.array([1, 1]) # 2 0.5
    param_hyperbole['c'] = -1

    param_ellipse = {}
    param_ellipse['A'] = np.array([[1, 0], [0, 2]])
    param_ellipse['b'] = np.array([2, 0.5])
    param_ellipse['c'] = -1
    param_hyperboloid = {}
    s = 0.01
    dim = 2
    _A = (np.random.rand(dim, dim)-0.5)*s
    param_hyperboloid['A'] = (_A + _A.T)/2 + 0.00001 * np.eye(dim)
    param_hyperboloid['b'] = -1+0.001*np.random.rand(dim)
    param_hyperboloid['c'] = -150
    print(np.linalg.eig(param_hyperboloid['A'])[0])
    print(param_hyperboloid['A'])
    print(param_hyperboloid['b'])
    print(param_hyperboloid['c'])
    param_list = [param_ellipse, param_hyperbole, param_hyperboloid]
    param_list =[param_hyperboloid]
    for param in param_list:
        if np.all(np.linalg.eig(param['A'])[0] < 0):
            print('Switching equality sign')
            param['A'] = - param['A']
            param['b'] = - param['b']
            param['c'] = - param['c']
        param['projection_type'] = ['exact']
        Q = Quadric(param)
        x0 = np.random.rand(Q.dim)*1
        x1_quasi = Q.project(x0)
        Q.projection_type = 'exact'
        Q.alg_exact_projection = 'dichotomy'
        x1_dichotomy = Q.project(x0)
        fig = plt.figure(1)
        if Q.dim == 2:
            ax = fig.add_subplot()
            ax.axis('equal')
        else:
            ax = fig.add_subplot(projection='3d')

        Q.plot(ax, fig)
        Q.scatter(ax, x0, options={'marker': 'x', 'label': r'$x_0$', 'zorder': 2})
        if x1_quasi is not None:
            Q.scatter(ax, x1_quasi, options={'marker': 'x', 'label': r'$x_0$', 'zorder': 2})

        Q.scatter(ax, x1_dichotomy, options={'marker': 'x', 'label': r'$x_0$', 'zorder': 2})
        xs = [x0, x1_quasi]
        dists = np.array([dist(Q.d, x0), dist(Q.d, x1_quasi)])
       
        dists = np.where(dists != float('inf'), dists, -float('inf'))
        idx = np.argmax(dists)
        print(xs, idx, Q.d, dists)
        if Q.dim == 2:

            ax.plot([Q.d[0], xs[idx][0]], [Q.d[1], xs[idx][1]], '--', zorder=1)
        else:
            ax.plot([Q.d[0], xs[idx][0]], [Q.d[1], xs[idx][1]], [Q.d[2], xs[idx][2]], '--', zorder=1)
        fig.tight_layout()
        #ax.legend()
        plt.show()

    pass
    # TODO
def test_exact_proj_quadric_2():
    flag_red_circle = False
    param_hyperbole = {}
    param_hyperbole['A'] = np.array([[2, 0.4], [0.4, -1]]) # 2 0.4 // 0.4-1
    param_hyperbole['b'] = np.array([2, 0.5]) # 2 0.5
    param_hyperbole['c'] = -1

    param_ellipse = {}
    param_ellipse['A'] = np.array([[1, 0], [0, 2]])
    param_ellipse['b'] = np.array([2, 0.5])
    param_ellipse['c'] = -0.5
    
    param_hyperboloid = {}
    s = 0.01
    dim = 2
    _A = (np.random.rand(dim, dim)-0.5)*s
    param_hyperboloid['A'] = (_A + _A.T)/2 + 0.00001 * np.eye(dim)
    param_hyperboloid['b'] = -1+0.001*np.random.rand(dim)
    param_hyperboloid['c'] = -150
    print(np.linalg.eig(param_hyperboloid['A'])[0])
    print(param_hyperboloid['A'])
    print(param_hyperboloid['b'])
    print(param_hyperboloid['c'])
    param_list =[param_hyperboloid]
    param_list = [param_ellipse, param_hyperbole, param_hyperboloid]
    for param in param_list:
        param['projection_type'] = 'exact'  # quasi exact quasi-dir
        param_alg = Param_alg('alternate-projection', dim)
        param['alg'] = param_alg
        if np.all(np.linalg.eig(param['A'])[0] < 0):
            print('Switching equality sign')
            param['A'] = - param['A']
            param['b'] = - param['b']
            param['c'] = - param['c']
        Q = Quadric(param)
        x0 = np.random.rand(Q.dim)*1
        x1_quasi = Q.project(x0, forced_projection='quasi')  # current-grad?
        x1_APG = Q.project(x0, forced_projection='current-grad')  # current-grad?
        if x1_quasi is None:
            raise
        Q.projection_type = 'exact'
        Q.alg_exact_projection = 'dichotomy'
        x1_dichotomy = Q.project(x0)
        fig = plt.figure(1)
        if Q.dim == 2:
            ax = fig.add_subplot()
            ax.axis('equal')
        else:
            ax = fig.add_subplot(projection='3d')

        Q.plot(ax, fig)
        Q.scatter(ax, x0, options={'marker': 'x', 'label': r'$\mathbf{x}_0$', 'zorder': 2})
        if x1_quasi is not None:
            Q.scatter(ax, x1_quasi, options={'marker': 's', 'label': r'$\mathrm{P}_1 (\mathbf{x}^0)$', 'zorder': 2})
        Q.scatter(ax, x1_APG, options={'marker': 's', 'label': r'$\mathrm{P}_2 (\mathbf{x}^0)$', 'zorder': 2})

        Q.scatter(ax, x1_dichotomy, options={'color': 'red', 'marker': 'x', 'label': r'$\mathbf{x}^*$', 'zorder': 2})
        xs = [x0, x1_quasi]
        dists = np.array([dist(Q.d, x0), dist(Q.d, x1_quasi)])
        
        dists = np.where(dists != np.inf, dists, -np.inf)
        idx = np.argmax(dists)
        print(xs, idx, Q.d, dists)
        if Q.dim == 2:
            circle1 = plt.Circle(x0, np.linalg.norm(x0-x1_dichotomy), edgecolor='red', facecolor='None')
            if flag_red_circle:
                ax.add_patch(circle1)
            ax.plot([Q.d[0], xs[idx][0]], [Q.d[1], xs[idx][1]], '--', zorder=1)
            if x1_quasi is not None:
                ax.scatter(xs[1][0], xs[1][1], color='black')
        else:
            ax.plot([Q.d[0], xs[idx][0]], [Q.d[1], xs[idx][1]], [Q.d[2], xs[idx][2]], '--', zorder=1)
        fig.tight_layout()
        
        ax.legend(loc='lower left')
        ax.axis('equal')
        fig.savefig('exact_vs_quasi_proj_hyperbola.pdf')
        plt.show()


def test_compare_alg():
    dims = np.arange(2, 5)
    n_instances = 10

    for dim in dims:
        pass

def test_run_compare_alg():
    dim = 3
    run_compare_alg(dim)

def run_compare_alg_dim():
    dims = np.arange(2, 101)
    dims = np.arange(2, 4)
    dims = [10*d for d in dims]
    dims = np.arange(3, 10)
    dims = [900, 1000]
    dims = [100]
    dims = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    dims = [80, 90]
    dims = [80]
    dims = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    dims = 100*np.arange(1, 11)
    alg_proj = get_alg_proj()
    df_timeout = pd.DataFrame(columns=alg_proj)
    df_time = pd.DataFrame(columns=alg_proj)
    df_distance = pd.DataFrame(columns=alg_proj)
    df_iteration = pd.DataFrame(columns=alg_proj)
    df_out = pd.DataFrame(columns=alg_proj)
    quantities = ['distance', 'iteration', 'time', 'deviation', 'total-time']
    quantiles = ['max', 'min', 'mean', 'median']
    dic_out = {q1+'-'+q2: pd.DataFrame(columns=alg_proj) for q1 in quantiles for q2 in quantities}
    dic_out['timeout'] = pd.DataFrame(columns=alg_proj)
    for dim in dims:
        _df = run_compare_alg(dim)
        print('_df', _df)
        for index in _df.index:
            print(index)
            dic_out[index].loc[dim] = _df.loc[index]
        print('dic_out', dic_out)
    with open('tmp/compare_alg/comparison.pickle', 'wb') as handle:
        pickle.dump(dic_out, handle, protocol=pickle.HIGHEST_PROTOCOL)


def test_mu_ellipse():
    text_params = {'ha': 'center', 'va': 'center', 'family': 'sans-serif',
                   'fontsize': 12}
    param = {}
    param['A'] = np.array([[-2, 0], [0, 1.2]]) # 2 and 1 or 2 and 1/2
    param['b'] = np.array([0, 0])
    param['c'] = -1
    param['projection_type'] = 'exact'
    Q = Quadric(param)
    fig, axs = plt.subplots(2, 2, figsize=(10, 7))
    ax1 = axs[0, 0]
    ax2 = axs[0, 1]
    ax3 = axs[1, 0]
    ax4 = axs[1, 1]
    ax1.axis('equal')
    
    Q.plot(ax1, fig)


    R = np.sort(-1/Q.eig)
    I = np.argsort(-1/Q.eig)
    l1 = Q.eig[0]
    l2 = Q.eig[1]
    
    X0 = np.array([0.1, 0.4]) # 0.3, 0.2  (0.3,0) 
    x0 = X0  # Or transpose ? TBD
    x0_std = Q.to_standardized(X0)
    mu_min, x_min, _ = Q._get_lambda_dichotomy(x0, return_xd=True)
    mu_max, x_max, xd = Q._get_lambda_dichotomy(x0, flag_max=True, flag_all=True, return_xd=True)
    print('xd', xd)
    E = np.ones(Q.dim)
    L_diag = np.diag(Q.L)
    inv_I_lA = lambda l: np.dot(np.dot(Q.U, np.diag(1/(E+l*L_diag))), Q.U.T)
    n_points = 600 # 600
    points = [0, n_points//3, 2*n_points//3, n_points]
    colormap = cm.get_cmap('autumn', n_points)
    colormap = cm.get_cmap('RdYlBu_r', n_points)
    def x(l):
        return inv_I_lA(l) @ (x0 - 0.5*l*Q.b)

    def fun(l):
        _xx = x(l)
        return _xx.T @ Q.A @ _xx + Q.b.T @ _xx + Q.c
    def d_fun(l):
        _inv_I_lA = inv_I_lA(l)
        out = (2*Q.A @ x(l)+Q.b).T @ (- _inv_I_lA @ Q.A @ _inv_I_lA @ (x0 -0.5*l*Q.b) - 0.5 * _inv_I_lA @ Q.b)
        return out


    def norm(l):
        return np.linalg.norm(x(l)-x0)

    fun_2 = lambda l: -fun(l)
    eps = 0.1  # 0.1
    mu_mid = (R[1]+R[0])/2
    mu_L = mu_mid-3
    mu_R = mu_mid +3
    mu1 = np.linspace(mu_L, R[0]-eps, n_points//3, endpoint=True)
    mu2 = np.linspace(R[0]+eps, R[1]-eps, n_points//3, endpoint=True)
    mu3 = np.linspace(R[1]+eps, mu_R, n_points//3, endpoint=True)
    mu = np.hstack((mu1, mu2, mu3))
    mu_ax1 = mu
    if X0[I[0]] == 0:
        mu_ax1 = np.hstack((np.linspace(mu_L, R[1]-eps, 2*(n_points//3), endpoint=True), mu3))
    elif X0[I[1]] == 0:
        mu_ax1 = np.hstack((mu1, np.linspace(R[0]+eps, mu_R, 2*(n_points//3), endpoint=True)))
    mu_ax1 = mu 
    x_mu = []
    f_mu = []
    df_mu = []
    norm_mu = []
    print('Test', x(R[0]+0.00000001))
    
    flag_degenerate = False
    if np.any(x0 == 0):
        flag_degenerate = True


    for i, m in enumerate(mu):
        _x = x(mu_ax1[i])
        x_mu.append(_x)
        f_mu.append(fun(m))
        df_mu.append(d_fun(m))
        norm_mu.append(np.linalg.norm(x(m)-x0))

        if m > 0:
            color = 'purple'
        else:
            color = 'orange'
        color = colormap(i)
        if i in [-1]:
            color = 'red'
            _s = '%0.2f' % m 
            ax1.text(x_mu[-1][0], x_mu[-1][1], _s, color=color)
        if not flag_degenerate:
            if i == 0:
                _s = r'$\mu \to -\infty$' 
            #    ax1.text(x_mu[-1][0], x_mu[-1][1], _s)
            if i == n_points//3-1:
                _s = r'$\mu \to \frac{-1}{\lambda_2}$' 
                ax1.text(x_mu[-1][0], x_mu[-1][1], _s, **text_params)
            if i == n_points//3:
                _s = r'$\mu \to \frac{-1}{\lambda_2}$' 
                ax1.text(x_mu[-1][0], x_mu[-1][1], _s, **text_params)
            if i == 2*n_points//3-1:
                _s = r'$\mu \to \frac{-1}{\lambda_1}$' 
                ax1.text(x_mu[-1][0], x_mu[-1][1], _s, **text_params)
            if i == 2*n_points//3:
                _s = r'$\mu \to \frac{-1}{\lambda_1}$' 
                ax1.text(x_mu[-1][0], x_mu[-1][1], _s, **text_params)
            if i == n_points-1:
                _s = r'$\mu \to \infty$' 
            #    ax1.text(x_mu[-1][0], x_mu[-1][1], _s)

        ax1.scatter(x_mu[-1][0], x_mu[-1][1], color=color, s=4)
        #ax2.scatter(m, fun(m), color=color)
    min_style = {'color': 'purple', 'marker': 'v', 'zorder': 2, 's': 12}
    max_style = {'color': 'purple', 'marker': 's', 'zorder': 2, 's': 12}
    min_style_2 = {'markeredgecolor': min_style['color'], 'markerfacecolor': min_style['color'], 'marker': min_style['marker'], 'zorder': min_style['zorder'], 'markersize': 6, 'color': 'w'}
    max_style_2 = {'markeredgecolor': max_style['color'], 'markerfacecolor': max_style['color'], 'marker': max_style['marker'], 'zorder': max_style['zorder'], 'markersize': 6, 'color': 'w'}
    legend_elements = [Line2D([0], [0], color='b', lw=2, label=r'$\mathcal{Q}(\Psi)$'),
                       Line2D([0], [0], label=r'$\mathbf{x}(\mu^*)$', **min_style_2),
                       Line2D([0], [0], label=r'$\mathbf{x}(\mu^{**})$', **max_style_2),
                       Line2D([0], [0], marker='x', color='w', label=r'$\mathbf{x}^0 = \mathbf{x}(0)$',
                              markeredgecolor='red', markersize=8, zorder=2)
                      ]
    if flag_degenerate:
        legend_elements.append(
                       Line2D([0], [0], color='w', label=r'$\mathbf{x}^\mathrm{d}$',
                              marker='o', markerfacecolor='green', markersize=8, zorder=2)
        )
    fig.tight_layout(pad=2.1)

    
#    ax1.text(0.4, -0.2, r'$\mu \to \pm \infty$', **text_params)
    ax1.set_xlabel(r'$x_1$')
    ax1.set_ylabel(r'$x_2$')
    xlim1 = [-2, 2]
    ax1.axis('equal')
    ax1.set_xlim(xlim1)
    ax1.set_ylim(xlim1)
    
    ax1.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(1, 0), prop=fontP)

    fig2, ax5 = plt.subplots()
    hexbins = ax5.hexbin([], [],
                 bins=20, gridsize=50, cmap=colormap)
    cb = fig.colorbar(hexbins, ax=ax1)
    cb.set_ticks([-0.1, 0.1]) # it's in percent so 10/100 = 0.1
    cb.ax.set_yticklabels([r'$\mu \to -\infty$', r'$\mu \to \infty$'])  # vertically oriented colorbar
    color='tab:blue'
    print(x0, X0)
    print(Q.eig)
    if np.all(x0 != 0):
        colored_line(mu1, f_mu[points[0]:points[1]], points[0], points[1], colormap, ax2, n_points, m=2)
        colored_line(mu2, f_mu[points[1]:points[2]], points[1], points[2], colormap, ax2, n_points, m=5)
        colored_line(mu3, f_mu[points[2]:points[3]], points[2], points[3], colormap, ax2, n_points, m=2)
    print(x0, I)
    print(x0[I[0]])
    if X0[I[0]] == 0:
        colored_line(np.hstack((mu1, mu2)), f_mu[points[0]:points[2]], points[0], points[2], colormap, ax2, n_points, m=1)
        colored_line(mu3, f_mu[points[2]:points[3]], points[2], points[3], colormap, ax2, n_points, m=1)
    elif X0[I[1]] == 0:
        colored_line(mu1, f_mu[points[0]:points[1]], points[0], points[1], colormap, ax2, n_points, m=1)
        colored_line(np.hstack((mu2, mu3)), f_mu[points[1]:points[3]], points[1], points[3], colormap, ax2, n_points, m=1)


    #ax2.set_ylim([-1, 4])
    #xlim = [-4, 4]  # -2, 2
    labels = [r'$\mu \to -\infty$', r'$\frac{-1}{\lambda_2}$', r'$\frac{-1}{\lambda_1}$', r'$0$', r'$\mu \to \infty$']

    asymptot_linestyle = {'linestyle': 'dashed', 'color': 'grey'}
    for j in range(Q.dim):
        if X0[I[j]] != 0:
            ax2.plot([R[j], R[j]], [min(f_mu), max(f_mu)], **asymptot_linestyle)
            ax3.plot([R[j], R[j]], [min(norm_mu), max(norm_mu)], **asymptot_linestyle)
            ax4.plot([R[j], R[j]], [min(df_mu), max(df_mu)], **asymptot_linestyle)
    xlim = ax2.get_xlim()
    ax2.plot([xlim[0], xlim[1]], [0, 0], color='red', alpha=0.5, zorder=1)
    ticks = [xlim[0], R[I[1]], R[I[0]], 0, xlim[1]]
    ax2.set_xticks(ticks)
    ax2.set_xticklabels(labels)
    ax3.set_xticks(ticks)
    ax3.set_xticklabels(labels)
    ax4.set_xticks(ticks)
    ax4.set_xticklabels(labels)
    ax2.set_xlabel(r'$\mu$')
    ax2.set_ylabel(r'$f(\mu)$')
    ax2.set_xlim(xlim)
    ax2.yaxis.set_ticks_position('right')
    #ax2.set_xlim(xlim)
    if np.all(x0 != 0):
        colored_line(mu1, norm_mu[points[0]:points[1]], points[0], points[1], colormap, ax3, n_points, m=2)
        colored_line(mu2, norm_mu[points[1]:points[2]], points[1], points[2], colormap, ax3, n_points, m=6)
        colored_line(mu3, norm_mu[points[2]:points[3]], points[2], points[3], colormap, ax3, n_points, m=2)
    if X0[I[0]] == 0:
        colored_line(np.hstack((mu1, mu2)), norm_mu[points[0]:points[2]], points[0], points[2], colormap, ax3, n_points, m=1)
        colored_line(mu3, norm_mu[points[2]:points[3]], points[2], points[3], colormap, ax3, n_points, m=1)
    elif X0[I[1]] == 0:
        colored_line(mu1, norm_mu[points[0]:points[1]], points[0], points[1], colormap, ax3, n_points, m=1)
        colored_line(np.hstack((mu2, mu3)), norm_mu[points[1]:points[3]], points[1], points[3], colormap, ax3, n_points, m=1)

    ax3.set_xlabel(r'$\mu$')
    ax3.set_ylabel(r'$||\mathbf{x}^0 - \mathbf{x}(\mu)||_2$')
    ax3.set_xlim(xlim)
    #ax3.set_ylim([0, 1.95])
    if np.all(x0 != 0):
        colored_line(mu1, df_mu[points[0]:points[1]], points[0], points[1], colormap, ax4, n_points, m=2)
        colored_line(mu2, df_mu[points[1]:points[2]], points[1], points[2], colormap, ax4, n_points, m=50)
        colored_line(mu3, df_mu[points[2]:points[3]], points[2], points[3], colormap, ax4, n_points, m=2)
    print('\n\n DF \n\n')
    print(mu3)
    if X0[I[0]] == 0:
        colored_line(mu3, df_mu[points[2]:points[3]], points[2], points[3], colormap, ax4, n_points, m=1)
        colored_line(np.hstack((mu1, mu2)), df_mu[points[0]:points[2]], points[0], points[2], colormap, ax4, n_points, m=1)
    elif X0[I[1]] == 0:
        colored_line(mu1, df_mu[points[0]:points[1]], points[0], points[1], colormap, ax4, n_points, m=1)
        colored_line(np.hstack((mu2, mu3)), df_mu[points[1]:points[3]], points[1], points[3], colormap, ax4, n_points, m=1)


    ## Asymptot
    a = []
    print(x0, x0)
    a0 = Q._get_asymptot_value(fun, x0_std, j=1, i=0)
    a1 = Q._get_asymptot_value(fun, x0_std, j=0, i=1)
    if np.any(Q.V != np.eye(Q.dim)) and True:
        a0_old = a0
        a0 = a1
        a1 = a0_old
    print('a0', a0)
    print('a1', a1)
    if not flag_degenerate:
        ax1.plot([a0, a0], [xlim1[0]-1, xlim1[1]+1], linestyle='dotted', color='grey')
        ax1.plot([xlim[0], xlim[1]], [a1, a1], linestyle='dotted', color='grey')
    flag_d = False
    print(xd)
    for _xd in xd:
        ax1.scatter(_xd[0], _xd[1], color='green', zorder=2)
        _norm = np.linalg.norm(_xd - x0)
        ax3.plot([xlim[0], xlim[1]], [_norm+0.1, _norm+0.1], color='green')
        x_text = xlim[1] + (R[1] - xlim[1])/3*2
        ax3.text(x_text, _norm+0.2, r'$||\mathbf{x}^0 - \mathbf{x}^\mathrm{d}||_2$', color='green')
        if x0[0] == 0:
            ax1.plot([0, _xd[0]], [_xd[1], _xd[1]], color='grey', zorder=0)
        else:
            ax1.plot([_xd[0], _xd[0]], [0, _xd[1]], color='grey', zorder=0)
    if len(xd) == 0 and flag_degenerate:
        if x0[0] == 0:
            _s = x0[1]/(1+Q.eig[1]/Q.eig[0])
            ax1.plot([-1, 1], [_s, _s], color='grey', zorder=0)
        else:
            _s = x0[0]/(1+Q.eig[0]/Q.eig[1])
            ax1.plot([_s, _s], [-1, 1], color='grey', zorder=0)

    if False:
        for i in range(Q.dim):
            if x0[i] == 0:
                if i == 1:
                    # j1 = 0
                    # j2 = 1
                    # ax1.plot([0, 0], [xlim[0]+2, xlim[1]-2], color='grey', zorder=0)
                    # ax1.scatter([0, 0], [-np.sqrt(abs((1-0**2*Q.eig[j1])/Q.eig[j2])), np.sqrt(abs((1-0**2*Q.eig[j1])/Q.eig[j2]))], color='green')
                    mu = -1/Q.eig[1]
                    _x = x0[0] / (1+mu*Q.eig[0])
                    print('eig', Q.eig, x0, _x)
                    ylim1 = ax1.get_ylim()
                    ylim1 = [ylim1[0], ylim1[1]]
                    _y = ylim1[1]
                    flag_d = False
                    if (1-Q.eig[0]*_x**2)/Q.eig[1]> 0:
                        flag_d = True
                        _y = np.sqrt( (1-Q.eig[0]*_x**2)/Q.eig[1])
                        ax1.scatter([_x, _x], [-_y, _y], color='green', zorder=2)
                        _d_1 = np.array([_x, _y])
                        _d_2 = np.array([_x, _y])
                        _norm = [np.linalg.norm(_d_1 - x0), np.linalg.norm(_d_2 - x0)]
                        ax3.plot([xlim[0], xlim[1]], [_norm[0]+0.1, _norm[0]+0.1], color='green')
                    ax1.text(_x+0.1, _y/2, '$d$')
                    x_text = xlim[1] + (R[1] - xlim[1])/3*2
                    if not flag_d:
                        _y = ylim1[1]
                    ax1.plot([_x, _x], [-_y, _y], color='grey', zorder=0)
                else:
                    #j1 = 1
                    #j2 = 0
                    #ax1.plot([xlim1[0], xlim1[1]], [0, 0], color='grey', zorder=0)
                    #ax1.scatter([-np.sqrt((1-0**2*Q.eig[j1])/Q.eig[j2]), np.sqrt((1-0**2*Q.eig[j1])/Q.eig[j2])], [0, 0], color='green')
                    mu = -1/Q.eig[0]
                    _x = x0[1] / (1+mu*Q.eig[1])
                    _y = xlim1[1]
                    flag_d = False
                    print(x0, x0[1])
                    if (1-Q.eig[1]*_x**2)/Q.eig[0] >0:
                        flag_d = True
                        _y = np.sqrt( (1-Q.eig[1]*_x**2)/Q.eig[0])
                        ax1.scatter([-_y, _y], [_x, _x], color='green', zorder=2)
                        ax1.text(-_y-0.5, _x, '$d$')
                    
                    ax1.plot([xlim1[0], xlim1[1]], [_x, _x], color='grey', zorder=0)
                    _d_1 = np.array([-_y, _x])
                    _d_2 = np.array([_y, _x])
                    _norm = [np.linalg.norm(_d_1 - x0), np.linalg.norm(_d_2 - x0)]
                    x_text = xlim[0] + (R[0] - xlim[0])/2
                    ax3.plot([xlim[0], xlim[1]], [_norm[0], _norm[0]], color='green')
                if flag_d:
                    ax3.text(x_text, _norm[0]+0.2, r'$||\mathbf{x}^0 - \mathbf{x}^\mathrm{d}||_2$', color='green')




    print('a =', a)

    ax4.set_xlabel(r'$\mu$')
    ax4.set_ylabel(r'$f^\prime(\mu)$')
    ax4.yaxis.set_ticks_position('right')
    ax4.set_xlim(xlim)
    #ax4.set_ylim([-50, 50])
    ax1.scatter(x0[0], x0[1], color='red', marker='x')
    if x_min is not None:
        ax1.scatter(x_min[0], x_min[1], **min_style)
        ax2.scatter(mu_min, fun(mu_min), **min_style)
        ax3.scatter(mu_min, norm(mu_min), **min_style)
        ax4.scatter(mu_min, d_fun(mu_min), **min_style)
        ax1.scatter(x_max[0], x_max[1], **max_style)
        ax2.scatter(mu_max, fun(mu_max), **max_style)
        ax3.scatter(mu_max, norm(mu_max), **max_style)
        ax4.scatter(mu_max, d_fun(mu_max), **max_style)
    plt.close(fig2)
    fig.savefig('tmp/changes_mu/x_trajectories_mu.png')
    fig.savefig('tmp/changes_mu/x_trajectories_mu.pdf')
    plt.show()


def run_compare_alg(dim):
    n_iter = 100  # should be 100
    alg_proj = get_alg_proj()
    exp_distances = {alg: np.zeros(n_iter) for alg in alg_proj}
    exp_iterations = {alg: np.zeros(n_iter) for alg in alg_proj}
    exp_times = {alg: np.zeros(n_iter) for alg in alg_proj}
    exp_devs = {alg: np.zeros(n_iter) for alg in alg_proj}
    exp_total_times = {alg: np.zeros(n_iter) for alg in alg_proj}
     
    for k in range(n_iter):
        print("\n\n ********** \n Current dimension is %s \n **********\n\n" % (dim))
        print("\n At %s percent \n " % (k/n_iter*100))
        exp_distance, exp_iteration, exp_time, exp_dev, exp_total_time = compare_alg(dim)
        for alg in alg_proj:
            exp_distances[alg][k] = exp_distance[alg]
            exp_iterations[alg][k] = exp_iteration[alg]
            exp_times[alg][k] = exp_time[alg]
            exp_devs[alg][k] = exp_dev[alg]
            exp_total_times[alg][k] = exp_total_time[alg]
    df_distance = pd.DataFrame(data=exp_distances)
    
    df_out = pd.DataFrame(columns=df_distance.columns)

    
    df_distance.replace([np.inf, -np.inf], np.nan, inplace=True)
    max_dist = max(df_distance.max())
    df_out.loc['timeout'] = df_distance.isna().sum()
    #df_out.loc['mean-distance'] = df_out.loc['mean-distance'].replace
    df_distance.replace(np.nan, max_dist, inplace=True)
    print('df_distance', df_distance)
    df_time = pd.DataFrame(data=exp_times)
    df_total_time = pd.DataFrame(data=exp_total_times)
    df_iteration = pd.DataFrame(data=exp_iterations)
    df_deviation = pd.DataFrame(data=exp_devs)
    flag_plot = False
    if flag_plot:
        sns.set_style("whitegrid")
        bplot=sns.boxplot(data=df_distance, 
                         width=0.5,
                         palette="colorblind")
        bplot=sns.stripplot(data=df_distance, 
                           jitter=True,
                           alpha=0.5,
                           marker='o', 
                           color='black')
        plt.tight_layout()
        bplot.set_ylabel(r'$||\mathbf{x}_{\textrm{f}}-\mathbf{x}_0||_2$')
        plt.show()
        ax_distance = df_distance.boxplot(return_type='axes')

        ax_distance.set_ylabel(r'$||\mathbf{x}_{\textrm{f}}-\mathbf{x}_0||_2$')
        plt.show()
        ax_time = df_time.boxplot(return_type='axes')
        ax_time.set_ylabel('Execution Time')
        plt.show()
    df_out.loc['mean-distance'] = df_distance.mean()
    df_out.loc['mean-time'] = df_time.mean()
    df_out.loc['mean-iteration'] = df_iteration.mean()
    df_out.loc['mean-deviation'] = df_deviation.mean()
    df_out.loc['median-distance'] = df_distance.median()
    df_out.loc['median-time'] = df_time.median()
    df_out.loc['median-iteration'] = df_iteration.median()
    df_out.loc['median-deviation'] = df_deviation.median()
    df_out.loc['max-distance'] = df_distance.max()
    df_out.loc['max-time'] = df_time.max()
    df_out.loc['max-iteration'] = df_iteration.max()
    df_out.loc['max-deviation'] = df_deviation.max()
    df_out.loc['min-distance'] = df_distance.min()
    df_out.loc['min-time'] = df_time.min()
    df_out.loc['min-iteration'] = df_iteration.min()
    df_out.loc['min-deviation'] = df_deviation.min()
    df_out.loc['mean-total-time'] = df_total_time.mean()
    df_out.loc['median-total-time'] = df_total_time.median()
    df_out.loc['max-total-time'] = df_total_time.max()
    df_out.loc['min-total-time'] = df_total_time.min()
    print(df_out)
    return df_out

def get_alg_proj():
    alg_names = ['douglas-rachford', 'dykstra', 'alternate-projection']
    alg_names = ['douglas-rachford', 'dykstra', 'alternate-projection', 'IPOPT']
    alg_names = ['IPOPT', 'douglas-rachford', 'alternate-projection']
    alg_names = []
    alg_names = ['douglas-rachford-feasibility']
    alg_names = ['alternate-projection', 'douglas-rachford', 'douglas-rachford-feasibility', 'IPOPT']
    alg_quasi = []
    alg_quasi = ['alternate-projection']
    alg_proj = [(k, 'exact') for k in alg_names]
    for alg in alg_quasi:
        alg_proj.append((alg, 'quasi'))
      #  alg_proj.append((alg, 'quasi-dir'))
        alg_proj.append((alg, 'current-grad'))
    #alg_proj = [("alternate-projection", "quasi-dir")]
    return alg_proj

def compare_alg(dim):
    print('Start compare_alg')
    param = {}
    _A = np.random.randn(dim, dim)+2*np.eye(dim)
    #_A = scipy.sparse.random(dim, dim, density=0.01)
    #_A = _A.tocsr()
    B = (_A + _A.T)/2
    l, D = np.linalg.eig(B)
    l_shift = min(l)
    B = B + 2* l_shift * np.eye(dim)

    param['A'] =  B   #_lamb = np.sort(-(np.random.rand(dim)-2))
    #_lamb = np.sort((np.random.rand(dim)))+2
    #_lamb = np.ones(dim)
    #_lamb[-1] = -2
    #param['A'] = np.diag(_lamb)
    param['b'] = np.random.randn(dim)
    #param['b'] = np.zeros(dim)
    param['c'] = np.random.randn(1)[0]-1
    #param['c'] = -1
    if is_empty(param):
        return compare_alg(dim)
    
    param['projection_type'] = 'exact'
    tic = time.time()
    Q = Quadric(param)
    toc_eigenvalue = time.time() - tic

    print(Q.type)
    x_min, x_max, x_feas = get_feas_ranges(Q, scale=1)  # 100 shift
    param['x_min'] = x_min
    param['x_max'] = x_max


    B = Box(x_min, x_max)
    x0 = x_feas + np.random.rand(dim) * (x_max - x_min)/2
    x0 = x_feas + (x_min - x_feas) * abs(np.random.rand(1)[0])
    x0 = np.random.rand(dim)/100
    x0 = 10* (np.random.rand(dim)-0.5) * (x_max - x_min) + x_min
    x0 = (np.random.rand(dim)) * (x_max - x_min) + x_min
    
    flag_test_pathological = False
    if flag_test_pathological:
        param['A'] = np.array([[2.3123, 0.4019], [0.4019, -1.2517]])
        param['b'] = np.array([1.01394, 1.91])
        param['c'] = -1.19
        x_min = np.array([-0.74, 0.71])
        x_max = np.array([0.9671, 0.73])
        x_min = np.array([-0.74, 0.5])
        x_max = np.array([0.9671, 1])
        Q = Quadric(param)
        B = Box(x_min, x_max)
        x0 = np.array([-0.598, 0.75])


    print('Param are', param)
    #print('x_feas is', x_feas)
    
    flag_plot = True
    if flag_plot and Q.dim == 2:
        Om = Omega(B, Q, x_feas)

        fig, ax = Om.plot(tight_layout=True)
        ax.scatter(x_feas[0], x_feas[1], label=r'$x_{feas}$')
        ax.scatter(x0[0], x0[1], label=r'x^0')

#    ax1.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(1, 0), prop=fontP)
        plt.show()
        

    alg_proj = get_alg_proj()
    
    exp_time = {alg: 0 for alg in alg_proj}
    exp_total_time = {alg: 0 for alg in alg_proj}
    exp_distance = {alg: 0 for alg in alg_proj}
    exp_iteration = {alg: 0 for alg in alg_proj}
    exp_dev = {alg: 0 for alg in alg_proj}
    for alg in alg_proj:
        plt.close()
        print('Ici')
        print(alg, alg[0])
        param_alg = Param_alg(alg_name=alg[0], dim=dim)
        param['alg'] = param_alg
        param['projection_type'] = alg[1]
        param['flag_restart'] = True

        Q.projection_type = alg[1]
        Om = Omega(B, Q, x_feas)
        Om.Q.need_std = False
        tic = time.time()
        if alg[0] == "IPOPT":
            #print(param)
            #print(Om.Q.A)
            write_data_for_ipopt(Om, x0)
            os.system('julia proj_ipopt.jl')
            x_julia = np.loadtxt("tmp/julia/x_julia.csv", delimiter=",")
            iterates = [x_julia]
            df_julia = pd.read_csv("tmp/julia/df_julia.csv")
            print(x_julia, df_julia)
        else:
            iterates, param = project(Om.B, Om.Q, x0, param)
            if not Om.is_feasible(iterates[-1]) and Om.Q.dim <= 3:
                fig, ax = Om.plot(tight_layout=True)
                plot_iterates(np.array(iterates), ax, fig)
                ax.scatter(iterates[-1][0], iterates[-1][1], color='red', s=50, zorder=2)
                print(alg)
                #plt.show()
                #raise
            if alg[1] not in ["quasi", "current-grad"] or Om.Q.need_std:
                print(alg)
                print('Adding time of eigenvalue decomposition')
                tic = tic - toc_eigenvalue
            if param['output']['n_rebranching'] * param['output']['n_convert'] * param['output']['n_resort_exact_proj'] != 0:
                print('Rebranching is', param['output']['n_rebranching'])
                print('Resorting is', param['output']['n_resort_exact_proj'])
                print('Converting is', param['output']['n_convert'])

                pass
                #plt.show()
                #raise



        toc = time.time() - tic
        if Om.dim <= 3:
            print('alg is %s ', alg)
            fig, ax = Om.plot(tight_layout=True)
            plot_iterates(np.array(iterates), ax, fig)
            print(x0)
            print('show')
            #circle1 = plt.Circle(x0, np.linalg.norm(x0-iterates[-1]), edgecolor='red', facecolor='None')
            #ax.add_patch(circle1)
            #plt.show()
            #plt.savefig(os.path.join('tmp', alg[0]))
        exp_time[alg] = toc
        exp_total_time[alg] = exp_time[alg]
        exp_iteration[alg] = len(iterates)
        exp_dev[alg] = abs(Om.Q.evaluate_point(iterates[-1]))
        if alg[0] == "IPOPT":
            exp_iteration[alg] = df_julia['iter'][0]
            exp_time[alg] = df_julia['ipopt_time'][0]
            exp_total_time[alg] = df_julia['total_time'][0]
        if Om.is_feasible(iterates[-1]):
            exp_distance[alg] = np.linalg.norm(iterates[-1] - x0)
        else:
            print(alg)
            print('Infeasible point')
            exp_distance[alg] = np.inf
        box_c = Om.B.center
        box_bottom_L = Om.B.x_min
        dist = np.linalg.norm(iterates[-1]-box_bottom_L)

        #c = plt.Circle(iterates[-1], dist, color='red', alpha=0.1)
        if flag_test_pathological:
            c = plt.Circle(box_bottom_L, dist, color='red', alpha=0.1)
            ax.scatter(iterates[-1][0], iterates[-1][1], color='red', zorder=2)
            #ax.add_artist(c)
            fig.tight_layout(pad=0.05)
            #fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
            ax.scatter(box_c[0], box_c[1], color='green')
            ax.legend()
            ax.axis('equal')
            ax.axis('off')
            ax.xaxis.set_ticks([])
            ax.yaxis.set_ticks([])
            ax.legend(loc='lower right', bbox_to_anchor= (1, 0))
            fig.savefig(os.path.join('tmp', 'pathological_' + str(alg) + '.pdf'))
            ax.get_legend().remove()
            fig.savefig(os.path.join('tmp', 'pathological_' + str(alg) + '_no_legend' +  '.pdf'))
            #plot_alg_convergence(ax2, x0, iterates)
                #raise

            plt.show()
        plt.close()
    return exp_distance, exp_iteration, exp_time, exp_dev, exp_total_time

def dist(x1, x2):
    if x1 is None or x2 is None:
        return np.inf
    return np.linalg.norm(x1-x2)


def is_empty(param):
    A = -param['A']/param['c']
    b = -param['b']/param['c']
    c = -1
    eig, _ = np.linalg.eig(A)
    p = np.sum(eig > 0)
    return p == 0

def write_data_for_ipopt(Om, x0):
    data_to_write = {}
    data_ipopt_path = os.path.join('data', 'data_ipopt')
    data_to_write['A.csv'] = Om.Q.A
    data_to_write['b.csv'] = Om.Q.b
    data_to_write['x_max.csv'] = Om.B.x_max
    data_to_write['x_min.csv'] = Om.B.x_min
    data_to_write['x0.csv'] = x0
    for _, file_name in enumerate(data_to_write):
        np.savetxt(os.path.join(data_ipopt_path, file_name), data_to_write[file_name], delimiter=",")

    f = open(os.path.join(data_ipopt_path, 'c.csv'), "w")
    print(Om.Q.c)
    f.write(str(Om.Q.c))

def test_when_no_point():
    param = {}
    _A = np.zeros((2, 2))
    _A[0, 0] = 2
    _A[1, 1] = -1
    param['A'] = _A
    dim, _ = _A.shape
    #_lamb = np.sort(-(np.random.rand(dim)-2))
    #_lamb = np.ones(dim)
    #_lamb[-1] = -2
    #param['A'] = np.diag(_lamb)
    param['b'] = 0*np.random.randn(dim)
    #param['b'] = np.zeros(dim)
    param['c'] = 0*np.random.randn(1)[0]-1
    param['projection_type'] = 'current-grad'  # quasi exact quasi-dir
    Q = Quadric(param)
    k_iter = 1000
    for k in range(k_iter):
        x0 = np.random.rand(Q.dim)*1
        x = Q.project(x0)
        if False:
            plt.close()
            fig = plt.figure(1)
            ax = fig.add_subplot()
            Q.plot(ax, fig)
            ax.scatter(x0[0], x0[1], color='green')
            ax.scatter(x[0], x[1], color='red')
            plt.show()

def test_example_1():

    param = {}
    _A = np.zeros((2, 2))
    _A[0, 0] = 2
    _A[1, 1] = 2
    param['A'] = _A/2
    dim, _ = _A.shape
    param['b'] = np.array([0, 0])
    param['c'] = -1
    param['projection_type']  = 'exact'
    Q = Quadric(param)
    x0 = np.array([0, 0])
    x = Q.project(x0)
    print('Projection')
    x_article = Q.project_sosa(x0)
    print('x_article', x_article)
    raise
    print('Distance is ', np.linalg.norm(x-x0))
    print('x', x)
    print('Feasibility is ', Q.is_feasible(x_article))
    print('Distance is ', np.linalg.norm(x_article-x0))

def test_example_2():

    param = {}
    _A = -np.ones((2, 2))
    _A[0, 0] = 1
    _A[1, 1] = 2
    param['A'] = _A/2
    dim, _ = _A.shape
    param['b'] = np.array([0, -2])
    param['c'] = -4
    param['projection_type']  = 'exact'
    Q = Quadric(param)
    x0 = np.array([0, 0])
    x = Q.project(x0)
    x_article = np.array([2.82, 0])
    print('Projection')
    x_article_2 = Q.project_sosa(x0)
    print('x_article', x_article)
    print('x_article 2', x_article_2)
    raise
    print('Distance is ', np.linalg.norm(x-x0))
    print('x', x)
    print('Feasibility is ', Q.is_feasible(x_article))
    print('Distance is ', np.linalg.norm(x_article-x0))


def test_example_8():

    param = {}
    _A = np.zeros((2, 2))
    _A[0, 0] = 1
    _A[1, 1] = -1
    print('_A', _A)
    param['A'] = _A/2
    dim, _ = _A.shape
    param['b'] = np.array([0, 0])
    param['c'] = -20
    param['projection_type']  = 'exact'
    Q = Quadric(param)
    x0 = np.array([-3, -3])
    x = Q.project(x0)
    x_article = np.array([-6.6164,-1.9433])
    print('Distance is ', np.linalg.norm(x-x0))
    print('x', x)
    print('Feasibility x_artoc;e is ', Q.is_feasible(x_article))
    print('Feasibility of x is ', Q.is_feasible(x))
    print('Distance is x', np.linalg.norm(x-x0))
    print('Distance is article', np.linalg.norm(x_article-x0))
    x0 = np.array([-8, 2])
    x = Q.project(x0)
    x_article = np.array([-6.779, 2.4402])
    x_article_2 = Q.project_sosa(x0)
    print('x_article', x_article)
    print('x_article 2', x_article_2)
    raise

    print('Distance is ', np.linalg.norm(x-x0))
    print('x', x)
    print('Feasibility x_artoc;e is ', Q.is_feasible(x_article))
    print('Feasibility of x is ', Q.is_feasible(x))
    print('Distance is x', np.linalg.norm(x-x0))
    print('Distance is article', np.linalg.norm(x_article-x0))

def test_example_11():
    param = {}
    _Q = np.array([
        [0.5, 0.2887, 0.7887, -0.2113],
        [0.5, 0.2887, -0.2113, 0.7887],
        [0.5, 0.2887, -0.5774, -0.5774],
        [0.5, -0.8660, 0, 0]
    ])
    _M = np.zeros((4, 4))
    _M[0, 0] = 1
    _M[-1, -1] = -2
    _A = _Q.T @ _M @ _Q
    param['A'] = _A / 2

    x0 = np.zeros(4)
    param['b'] = x0
    x0[0] = 1
    x0[2] = 1
    param['c'] = 2

    param['projection_type']  = 'exact'
    Q = Quadric(param)
    x = Q.project(x0)
    x_article = np.array([-0.73, 0.75, -0.28, -0.02])
    print('Distance is ', np.linalg.norm(x-x0))
    print('x', x)
    print('Feasibility is ', Q.is_feasible(x_article))
    print('Feasibility is ', Q.is_feasible(x))
    print('Distance is ', np.linalg.norm(x_article-x0))
    print(_M)


    

if __name__ == "__main__":
    print('Launching test')
    test_example_2()
    #test_mu_ellipse()
    #run_compare_alg(dim=2000)
    #test_when_no_point() 
    #compare_alg(3)
    #test_exact_proj_quadric_2()
    #test_ellipsoid()
    #test_run_compare_alg()
    run_compare_alg_dim()
    #test_run_project_2D()
    #test_run_project_3D()
    #test_run_project_n_D(3)
    #plt.show()
    #test_exact_proj()
    #test_compare_proj()
    #test_omega()
    #test_run_project_2D()
    #test_run_project_3D()
    #test_run_project_n_D()
    #test_run_compare_alg()
    #run_compare_alg_dim()
    #test_exact_proj_quadric_2()

    #plt.show()
    #for i in range(100):
    #test_run_project_n_D(dim=2)
    #plot_comparison()
    #test_data(_str_data='data_15_bis')
    #for i in range(100):
    #for i in range(10):
    #test_omega()
    #test_data()
    #test_data(flag_show=True)
