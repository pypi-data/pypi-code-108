#!/usr/bin/env python3

import copy
import imageio
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy
from scipy.optimize import root_scalar, minimize_scalar, minimize
from scipy.sparse.linalg import spsolve
import time
import warnings
from shutil import copyfile
from itertools import product, combinations
from gurobipy import Model, quicksum, GRB

plt.rcParams.update({
    "text.usetex": True,
    "font.size": 16,
})
CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']


global old_lambda
old_lambda = 0

global eps_p
eps_p = pow(10, -6)
global eps_dev
eps_dev = pow(10, -6)


class NoFeasibleDirection(Exception):
    pass


    def quasi_project(self, x, xi, param=None):
            if xi is None or self.projection_type == 'quasi-farthest':  # should not happened
                xi = x-self.d


            print('Quasi_project')
            #print(xi)
            if np.all(x == self.d):
                xi = np.zeros(self.dim)
                xi[0] = 0.00001
                print('coucou')
            Q = self
            #print(Q.A, Q.b, Q.c, Q.d)
            a1 = xi.T @ Q.A @ xi
            a2 = 2 * (x.T @ Q.A @ xi) + Q.b.T @ xi
            a3 = x.T @ Q.A @ x + Q.b.T @ x + Q.c
            delta = a2**2 - 4*a1*a3
            if delta < 0:
                print('Negative delta, it seems impossible to find intersections.')
                print('Dimension', Q.dim)
                Q.need_std = True # if we resort to the true projection, we have to account for the fact that we should have to compute the eigenvalue decomposition
                Q.projection_type = 'exact'
                if param is not None:
                    param['output']['n_resort_exact_proj'] += 1
                fig, ax = get_fig_ax(Q.dim)
                print('Type is ', Q.type)
                #plt.show()
                if Q.dim <= 3 and False:
                    Q.plot(ax, fig)
                    #x = Q.to_non_standardized(x)
                    ax.scatter(x[0], x[1], marker='x', color=CB_color_cycle[1],
                               label=r'$\mathbf{x}^0$')
                    ax.set_xlabel('$x_1$')
                    ax.set_ylabel('$x_2$')
                    if self.dim == 3:
                        ax.set_zlabel('$x_3$')
                        ax.set_zticks([])
                    ax.set_xticks([])
                    ax.set_yticks([])
                    plt.tight_layout()
                    print('xi =', xi)
                    print('x =', x)
                    plt.scatter(x[0], x[1])
                    #y = x + xi
                    #plt.plot([x[0], y[0]], [x[1], y[1]])
                    plt.show()
                warnings.warn('Negative delta, it seems impossible to find intersections.')
                return self.project(x, forced_projection='exact')
                #raise ValueError('Negative delta, it seems impossible to find intersections.')

            betas = (-a2 + np.array([1, -1]).T * np.sqrt(delta).T) / (2.0*a1)
            betas = betas.reshape((2, 1))
            ind = np.argmin(np.abs(betas))
            q = x + betas[ind] * xi
            
            q0 = x + betas[0] * xi
            q1 = x + betas[1] * xi
            if np.linalg.norm(q0 - x) < np.linalg.norm(q1-x) and not self.projection_type == 'quasi-farthest':
                q = q0
            else:
                
                q = q1

            if self.projection_type == 'quasi-dir' :
                self.xi = self.get_tangent_plane(q) 
            assert q.T @ Q.A @ q + Q.b.T @ q + Q.c <= eps_dev * Q.dim, ' psi(p) = %s, ep_s = %s' % (q.T @ Q.A @ q + Q.b.T @ q + Q.c, eps_dev)

            return q

    def project(self, x, forced_projection=None, param=None):
        if self.is_feasible(x):
            return x
        x_std = self.to_standardized(x)
        if forced_projection is None:
            projection_type = self.projection_type
        else:
            projection_type = forced_projection
        print('\n Projection using %s \n' % projection_type)
        if projection_type in ['quasi', 'quasi-dir', 'current-grad']:
            Q = self
            if projection_type == 'current-grad':
                print('Getting xi')
                xi = Q.get_tangent_plane(x, forced=True)
                print('xi = ', xi)
                
                #print('xi is ', xi)
            elif self.xi is None:
                xi = x - Q.d
            else:
                xi = self.xi
            return Q.quasi_project(x, xi, param)

        elif projection_type == 'exact':
            if self.alg_exact_projection == 'dichotomy':
                #print('A', self.A, x)
                mu_dich, x_proj = self._get_lambda_dichotomy(x)
                if not self.is_feasible(x_proj):
                    # relaunch with better precision rerun
                    print('\n\n Convert (nearly feasible) solution to feasible')
                    #self.xi = self.get_tangent_plane(x_proj, forced=True) 
                    x_proj = self.project(x_proj, forced_projection='current-grad')
                    if param is not None:
                        param['output']['n_convert'] += 1
                    print(self.is_feasible(x_proj))
                    if not self.is_feasible(x_proj):
                        x_proj = self.project(x_proj, forced_projection='quasi')

                return x_proj
            elif self.alg_exact_projection == 'GD':
                return self._get_lambda_GD(x)
            else:
                raise ValueError('Invalid argument, the algorithm for the exact projection should be either "dichotomy" or "GD" and is currently %s' % self.alg_exact_projection)


    def plot(self, ax, fig, save=False, show=False):
        dim = np.size(self.A, 1)
        assert dim <= 3, 'Sorry, I can not represent easily > 3D spaces...'
        m = 1000
        quadric_color = 'royalblue'
        flag_hyperboloid = np.any(self.eig < 0)

        
        T = np.linspace(-np.pi, np.pi, m)
        T2 = T/2
        x = np.zeros_like(T)
        y = np.zeros_like(T)
        gamma = (np.sqrt(abs(self.c+self.d.T @ self.A @ self.d + self.b.T @ self.d)))
        if dim == 2:
            x = np.zeros_like(T)
            y = np.zeros_like(T)

            for i, t in enumerate(T):
                if flag_hyperboloid:
                    t = t/4 # otherwise we plot too much of the quadric...
                    v = self.d + (self.V @ np.array([self.axes[0] / np.cos(t),
                                                           -self.axes[1] * np.tan(t)])) * gamma
                    v2 = self.d + (self.V @ np.array([self.axes[0] / np.cos(t+np.pi),
                                                           -self.axes[1] * np.tan(t+np.pi)])) * gamma
                    x[i//2], y[i//2] = (v[0], v[1])
                    x[i//2 + m//2], y[i//2 + m//2] =(v2[0], v2[1])
                else:
                    v = self.d + (self.V @ np.array([self.axes[0] * np.cos(t),
                                                           self.axes[1] * np.sin(t)])) * gamma 
                 #   v = np.array([self.axes[0]*np.cos(t), self.axes[1] * np.sin(t)])
                    x[i], y[i] = (v[0], v[1])
            if flag_hyperboloid:
                ax.plot(x[:m//2], y[:m//2], color=quadric_color, zorder=1, label=r'$\mathcal{Q}$')
                ax.plot(x[m//2:], y[m//2:], color=quadric_color, zorder=1)
            else:
                ax.plot(x, y, color=quadric_color, label=r'$\mathcal{Q}$', zorder=1)
            ax.scatter(self.d[0], self.d[1], color=quadric_color, label=r'$\mathbf{d}$')
        elif dim == 3:
            m1 = 40
            m2 = 20
            print('type is', self.type)
            ax.scatter(self.d[0], self.d[1], self.d[2], color=quadric_color, label=r'$\mathbf{d}$')
            if self.type == 'one_sheet_hyperboloid':
                t, s = np.mgrid[0:2*np.pi:m1 * 1j, -1:1:m2 * 1j]
                u_x = self.axes[0] * np.cos(t) * np.sqrt(1+s**2)
                u_y = self.axes[1] * np.sin(t) * np.sqrt(1+s**2)
                u_z = self.axes[2] * s
                U_vec = np.tile(self.d, (m1*m2, 1)).T +  self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                surf = ax.plot_surface(x, y, z, color=quadric_color, alpha=0.3, label=r'$\mathcal{Q}$')
                surf._facecolors2d = surf._facecolors3d
                surf._edgecolors2d = surf._edgecolors3d
                ax.plot_wireframe(x, y, z, color=quadric_color, alpha=0.7)

            
            elif self.type == 'two_sheets_hyperboloid':
               
                t, s1 = np.mgrid[0:2*np.pi:m1 * 1j, 0:np.pi/2-1:m2//2 * 1j]
                _, s2 = np.mgrid[0:2*np.pi:m1 * 1j, np.pi/2+1:np.pi:m2//2 * 1j]
                s = np.hstack((s1, s2))
                t = np.hstack((t, t))
                u_x = self.axes[0] / np.cos(s)
                u_y = self.axes[1] * np.cos(t) * np.tan(s)
                u_z = self.axes[2] * np.sin(t) * np.tan(s)
                U_vec = np.tile(self.d, (m1*m2, 1)).T +  self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
            #    U_vec = np.tile(self.d, (m1*m2, 1)).T +  np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten()))
                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                print(x.shape)
                x1 = x[:, :m2//2]
                y1 = y[:, :m2//2]
                z1 = z[:, :m2//2]
                x2 = x[:, m2//2:]
                y2 = y[:, m2//2:]
                z2 = z[:, m2//2:]
                surf = ax.plot_surface(x1, y1, z1, color=quadric_color, alpha=0.3, label=r'$\mathcal{Q}$')
                surf._facecolors2d = surf._facecolors3d
                surf._edgecolors2d = surf._edgecolors3d
                ax.plot_wireframe(x1, y1, z1, color=quadric_color, alpha=0.7)
                surf2 = ax.plot_surface(x2, y2, z2, color=quadric_color, alpha=0.3)
                ax.plot_wireframe(x2, y2, z2, color=quadric_color, alpha=0.7)
                surf2._facecolors2d = surf._facecolors3d
                surf2._edgecolors2d = surf._edgecolors3d

            else:
                t, s = np.mgrid[0:2*np.pi:m1 * 1j, 0:np.pi:m2 * 1j]
                u_x = self.axes[0] * np.cos(t) * np.sin(s)
                u_y = self.axes[1] * np.sin(t) * np.sin(s)
                u_z = self.axes[2] * np.cos(s)
                U_vec = np.tile(self.d, (m1*m2, 1)).T +  self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
                # U_vec = np.tile(self.d, (m1*m2, 1)).T +  np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten()))  
    

                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                print(x)
                print('Here 1')
                surf = ax.plot_surface(x, y, z, color=quadric_color, alpha=0.3)
                surf._facecolors2d = surf._facecolors3d
                surf._edgecolors2d = surf._edgecolors3d
                print('Here 2')
                ax.plot_wireframe(x, y, z, color=quadric_color, alpha=0.7)
            #self.ranges = [(np.min(x), np.max(x)), (np.min(y), np.max(y)), (np.min(z), np.max(z))]
            print('Here 3')
        if show:
            plt.show()
        if save:
            fig.savefig('tmp/fig.png')

    def plot_planes(self, ax, fig):
        x = np.linspace(self.ranges[0][0], self.ranges[0][1])
        y = np.linspace(self.ranges[1][0], self.ranges[1][1])

    def scatter(self, ax, x, options=None):
        if self.dim == 2:
            ax.scatter(x[0], x[1], **options)
        elif self.dim == 3:
            ax.scatter(x[0], x[1], x[2], **options)
        else:
            print('Dimension is too large to plot point')


    def _get_x0(self, fun, x_L, x_R):
        max_k = 100
        shift = -1
        bound = x_R
        sign_0 = np.sign(fun(0))
        if fun(0) < 0:
            shift = 1
            bound = x_L
        

        k = 1
        x0 = 0
        while k < max_k and np.sign(fun(x0)) == sign_0:
            x0 = bound + shift * abs(bound)/pow(2, k)
            k += 1
        if k == max_k:
            t = np.linspace(x_L-10, x_R+10, 1000)
            plt.plot(t, fun(t))
            plt.savefig('wtf.png')
            print('\n\n strange behavior')
            #raise ValueError('Max number of iteration reached')
        return x0
    

    def _get_interval(self, fun, x0):
        # TODO
        """
            Actually the asymptot in -1/lambda_j where x_j^0 = 0 disappear... Hence I should look around -1/lambda_i where i is the max eigenvalue such that x_i != 0 AND WITH A PROBLEM UNDER THE STANDARD FORM !!!! 
        """

        eps = 0.000000001
        extrema = np.sort(-1 / self.eig)
        extrema = extrema + eps
        interval_dichotomy = []
        n_extrema = len(extrema)

        if np.all(abs(x0) < eps_p):
            return []

        def _get_right_value(_x_R):
            _shift = 1
            n_iter = 30
            while fun(_x_R) > 0 and n_iter <100:
                _x_R = _x_R + _shift
                _shift = 10*_shift
                n_iter += 1
            return _x_R

        #print('extrema', extrema)
        #print('eig', self.eig)
        if extrema[-1] < 0: # Ellipsoid case
            for i, x0_i in enumerate(x0):
                print('check x0', i, x0_i)
                if abs(x0_i) > eps_p/1000:
                    x_L = -1/self.eig[i]
                    _x_R = -1/self.eig[i]+0.0001
                    if fun(_x_R) < 0:
                        return [[x_L, _x_R]]
                    else:
                        x_R = _get_right_value(_x_R)
                    print('right value', x_R)
                    return [[-1/self.eig[i], x_R]] # TODO not robust
        n_mid = np.where(extrema > 0)[0][0]
        extrema_mid = extrema[n_mid]
        #print('hu',extrema_mid, extrema[n_mid-1], extrema)
        #print(self.A, self.V)
        
        if np.sign(fun(extrema[n_mid-1])) == np.sign(fun(extrema[n_mid]-2*eps)):
            print(extrema, extrema_mid)
            print([fun(e) for e in extrema])
            print('x0', x0)
            print('x0 std', self.to_standardized(x0))
            warnings.warn('No valid interval')
            return []
        interval_dichotomy = []
        i = 0
        while len(interval_dichotomy) == 0 and i < n_mid:

            x_s = extrema[n_mid-i-1]
            x_f = extrema[n_mid+i]
        
            if np.sign(fun(x_s)) != np.sign(fun(x_f)):
                print('c')
                interval_dichotomy.append([x_s, x_f])
                return interval_dichotomy
                print("len", len(interval_dichotomy))
            i += 1
        return interval_dichotomy
        

    def _get_all_intervals(self, fun):
        eps = 0.001
        extrema = np.sort(-1 / self.eig)
        extrema = extrema + eps
        shift = max(extrema[-1] - extrema[0], 2000)
        x_s = extrema[0] - shift
        x_f = extrema[-1] + shift
        extrema = np.append(extrema, x_f)
        interval_dichotomy = []
        sign = np.sign(fun(x_s))
        x_L = x_s
        for x_R in extrema:
            print('Testing interval [%s, %s]' % (x_L, x_R))
            print('Fun value is [%s, %s]' % (fun(x_L), fun(x_R)))
            assert np.sign(fun(x_R)) != 0, 'we should not find any root'
            print('Sign are', np.sign(fun(x_L)), np.sign(fun(x_R)))
            if np.sign(fun(x_R)) != np.sign(fun(x_L)):
                print('Function change of sign!')
                # We found an interval over which fun changes of sign
                interval_dichotomy.append([x_L, x_R])
                sign = not sign
            x_L = x_R




        return interval_dichotomy

    def _get_lambda_dichotomy(self, x0, flag_max=False, flag_all=False, return_xd=False, mu_0=None):
        x0_std = self.to_standardized(x0)
        flag_degenerated = np.any(abs(x0_std) < eps_p)
        I = np.eye(self.dim)
        E = np.ones(self.dim)
        L = np.diag(self.L)
        inv_I_lA = lambda l: self.U @ np.diag(1/(np.ones(self.dim)+l*np.diag(self.L))) @ self.U.T
        inv_I_lA = lambda l: self.U @ np.diag(1/(E+l*L)) @ self.U.T
        inv_I_lA = lambda l:  np.diag(1/(E+l*L))
        inv_I_lA_2 = lambda l: np.dot(np.dot(self.U, np.diag(1/(E+l*L))), self.U.T)

        def x_2(l):
            return inv_I_lA_2(l) @ (x0 - 0.5*l*self.b)

        def x_std(l):
            return inv_I_lA(l) @ x0_std

        def x(l):
            return self.to_non_standardized(x_std(l))

        def fun(l):
            _sum = 0
            for i in range(self.dim):
                _sum += self.eig[i] * (x0_std[i]/(1+l*self.eig[i]))**2
            return _sum -1
        

        def fun_2(l):
            _xx = x(l)
            return _xx.T @ self.A @ _xx + self.b.T @ _xx + self.c - 1



        def psi_std(_xx):
            return _xx.T @ self.A_std @ _xx - 1

        def psi(_xx):
            return _xx.T @ self.A @ _xx + self.b.T @ _xx + self.c 

        fun_2 = lambda l: -fun(l)
        #assert psi(x0) < 0, 'point should be inside the quadric' 
        def d_fun_2(l):
            _inv_I_lA = inv_I_lA(l)

            out = (2*self.A @ x(l)+self.b).T @ (- _inv_I_lA @ self.A @ _inv_I_lA @ (x0 -0.5*l*self.b) - 0.5 * _inv_I_lA @ self.b)
            return out
        def d_fun(l):
            _sum = 0
            for i in range(self.dim):
                _sum += -2* (self.eig[i] * x0_std[i])**2 / (1+l*self.eig[i])**3
            return _sum 
        def d2_fun(l):
            _sum = 0
            for i in range(self.dim):
                _sum += 6* (self.eig[i]**3 * x0_std[i]**2) / (1+l*self.eig[i])**4
            return _sum 
        eps = 0.0
        bounds= (-max(1/self.eig)-eps, -min(1/self.eig)+eps)
        #print('bounds ', bounds)
        #max_value = minimize(fun_2, 0) # TODO use previous as starting point?
        #print('1/Eig of A', 1/self.eig)
        #print(np.linalg.eig(l0*self.A)[0])
        #print('Check moore', np.linalg.pinv(self.A) @ self.A @ self.b - self.b)
        #print('Check derivative', d_fun(l0))
        #print('maximum is %s with value %s ' % (l0, fun(l0)))

        #_x0  = 0

        flag_converged = False
        i=0
        _flag_plot = False
        
        #dichotomy_intervals = self._get_all_interval(fun)
        if flag_all : # TODO TO CHANGE
            dichotomy_interval = self._get_all_intervals(fun)
        else:
            dichotomy_interval = self._get_interval(fun, x0_std)
        print('End get interval')
        print('Dichotomy interval are', dichotomy_interval)

        flag_add_interval = False
        if flag_add_interval:
            max_value = minimize_scalar(fun_2, bounds=bounds, method='bounded')
            min_value = minimize_scalar(fun, bounds=bounds, method='bounded')
            l0 = max_value.x
            l1 = min_value.x

            for l in [l0, l1]:
                if np.sign(fun(l-eps)) != np.sign(fun(l)):
                    dichotomy_interval.append((l-eps, l))
                    print('\n\nAdding from max!\n\n')

        print('Dichotomy interval are', dichotomy_interval)
        if len(dichotomy_interval) == 0:

            _flag_plot = False
            print(self.A, self.b, self.c, self.d)
            print('r = ', np.linalg.matrix_rank(self.A))
            print(self.eig)
            print('x0_std', x0_std)
            print('\n\nWarning: no dichotomy interval found!!!\n\n')
        
        if _flag_plot:
            t = np.linspace(bounds[0]-100, bounds[1]+100, 1000)
            f = np.zeros_like(t)
            df = np.zeros_like(t)
            for (i, _t) in enumerate(t):
                f[i] = fun(_t)
                df[i] = d_fun(_t)
            fig, ax = plt.subplots()
            ax.plot(t, f)
            ax.set_xlabel(r'$\lambda$')
            ax.set_ylabel(r'$f(\lambda)$')
            # plt.plot(t, df)
            plt.show()
            if self.dim <= 3:
                fig, ax = plt.subplots()
                self.plot(ax, fig)
                ax.scatter(x0[0], x0[1], marker='x')
                plt.show()
        roots = []


        #TODO TEST Newton to remove
        flag_newton = True
        if flag_newton == True and len(dichotomy_interval) > 0 and not flag_all:
            print(dichotomy_interval)
            if self.is_ellipsoid:
                interval = dichotomy_interval[-1]
            else:
                interval = [I for I in dichotomy_interval if I[0]*I[1] < 0][0]
            print(interval)
            e_1, e_2 = interval
            f0 = fun(0)
            df0 = d_fun(0)
            d2f0 = d2_fun(0)
            print('f(0)', fun(0))
            print('df(0)', d_fun(0))
            print('d2 f(0)', d2_fun(0))

            eps_N = pow(10, -10)

            if interval[0] == interval[1]:
                interval[1] = interval[1] + 1000  # TODO TO clean
                print('THIS IS A TEST')
                #time.sleep(10)
                #plt.show()
            if mu_0 is None:
                mu_s = 0
                sol = my_newton(fun, d_fun, mu_s, interval=interval)
                print('\n\nNewton from mu_s = %s with f(\mu_s) = %s' %  (mu_s, fun(mu_s)))
                print(sol)
            else:
                print('\n\n\n **********  Need to rerun newton ********** \n\n\n')

                sol = root_scalar(fun, fprime=d_fun, x0=mu_0, method='newton', xtol=eps_N, rtol=eps_N, maxiter=100)
                print(sol)
                



            if not sol.converged:
                mu_s2 = self._get_x0(fun, e_1, e_2)  # OK
                print('\n\nNewton from mu_s = %s with f(\mu_s) = %s' %  (mu_s2, fun(mu_s2)))
                sol = my_newton(fun, d_fun, mu_s2, interval=interval)
                print('SOL', sol)
                if not sol.converged:
                    print('Using bracket?')
                    sol = root_scalar(fun, bracket=[e_1, e_2])

                print('d2f  (mu^*) =', d2_fun(sol.root))
                print('Interval = ]%s, %s[' % (e_1, e_2))
                print(sol.root, fun(sol.root))
            print('Sol from 0', sol)
            print('Interval = ]%s, %s[' % (e_1, e_2))
            print(sol.root, fun(sol.root))
            print('Breakdanc')
            if self.is_feasible(x(sol.root)):
                roots.append(sol.root)
            else:
                roots.append(sol.root)
                warnings.warn('Root not feasible')
        if flag_all:
            for I in dichotomy_interval:
                x_L, x_R = I
                print('Interval is [%s, %s] for f [%s, %s]' % (x_L, x_R, fun(x_L), fun(x_R)))
                print('Optimizing')
                global old_lambda
                print('Old lambda =', old_lambda)
                #print('[x_L, x_R] = [%s, %s] and [f(x_L), f(x_R)] = [%s, %s]' % (x_L, x_R, fun(x_L), fun(x_R)))
                tic = time.time()
                print('Type is ', self.type)
                #print('x0', x0)
                #print('x0_std', x0_std)
                sol = root_scalar(fun, bracket=[x_L, x_R])
                print('Elsapse', time.time() - tic)
                print(sol.root)
                old_lambda = sol.root
                #print('x0', x0)

                print('End Optimizing', sol.root, np.linalg.norm(x0-x(sol.root)))
                print(fun(sol.root))
                if abs(fun(sol.root)) < 0.0001:
                    print('Found a root on interval %s', I)
                    #print('x0', x0)
                    #print('x0', x0_std)
                    #print('d', self.d)
                    if self.is_feasible(x(sol.root)):
                        roots.append(sol.root)
                    else:
                        warnings.warn('Root not feasible')
                        raise
                else:
                    print('No valid root')
        print('Getting d solution')
        lambda_bar = np.unique(self.eig)
        xd = []
        #print('x0', x0)
        #print('x0 std', x0_std)
        if flag_degenerated:
            print('Degenerated!')
            for k, _l in enumerate(lambda_bar):
                K_k = [i for i in range(self.dim) if (abs(self.eig[i] - _l) < eps_p and abs(x0_std[i]) < eps_p)]
                if len(K_k)>=1:
                    _sum = [self.eig[j] * (x0_std[j]/(1-self.eig[j]/_l))**2 for j in range(self.dim) if abs(self.eig[j] - _l) > 0]
                    sqr_arg = (1 - sum(_sum))/_l
                    if sqr_arg > 0:
                        print('K_k', K_k)
                        print('There are d solution!')
                        _xdk_std = np.zeros(self.dim)
                        for i in range(self.dim):
                            if i not in K_k:
                                _xdk_std[i] = x0_std[i] / (1 - self.eig[i]/_l)
                            elif i == K_k[0]:
                                
                                _xdk_std[i] = np.sqrt(sqr_arg)

                        _xdk = self.to_non_standardized(_xdk_std)
                        xd.append(_xdk)
                        #fig, ax = get_fig_ax(self.dim)
                        #self.plot(ax, fig)
                        #ax.scatter(_xdk[0], _xdk[1])
                        d_std = self.to_standardized(self.d)
                        #print('d_std', d_std)
                        #print('d', self.to_non_standardized(d_std))
                        #ax.axis('equal')
                        #plt.show()
                        #assert self.is_feasible(_xdk)


        #print('Roots lambdq are', roots)
        print('bla')

        best_norm = np.inf
        if flag_max:
            best_norm = - np.inf
        best_x = None
        best_l = None
        best_dichotomy_interval = None
        for r, I in zip(roots, dichotomy_interval):
            _x = x(r)
            print("Testing if the point belongs to the quadric %s: %s" % (self.type, self.is_feasible(_x)))
            _norm = np.linalg.norm(_x-x0)
            #plt.scatter(_x[0], _x[1], _x[2], color='red')
            print("Computing the norm:", _norm)
            if _norm < best_norm and not flag_max:
                best_x = _x
                best_l = r
                best_norm = _norm
                best_dichotomy_interval = dichotomy_interval
            if _norm > best_norm and flag_max:
                best_x = _x
                best_l = r
                best_norm = _norm
                best_dichotomy_interval = dichotomy_interval

        for _xd in xd:
            _norm = np.linalg.norm(_xd - x0)
            if _norm < best_norm and not flag_max and not return_xd:
                best_x = _xd
                best_norm = _norm
        print('Best norm is', best_norm)
        print('Best lambda is', best_l)
        print('Best interval is', best_dichotomy_interval)

        #sol_R = root_f, x0=l1_L, fprime=d_fun, method='newton')
        #plt.show()
        #sol_L = root_scalar(fun, x0=l1_L, fprime=d_fun, method='newton')
        if return_xd:
            return best_l, best_x, xd
        else:
            return best_l, best_x 
    
    def _get_lambda_GD(self, x0):
        pass
        #TODO
    
    def _run_double_side_dichotomy(self):
        pass

class Box:
    def __init__(self, x_min, x_max):
        self.dim = len(x_min)
        self.x_min = x_min
        self.x_max = x_max
        assert np.all(x_min < x_max), 'x_min should be < than x_max !'
        self.center = x_min + 0.5*(x_max-x_min)
        self.R = self.x_max - self.x_min

    def is_feasible(self, x):
        flag = np.all(np.logical_and(x >= self.x_min-eps_p, x <= self.x_max+eps_p))
        print('Feasibility box is', flag)
        if not flag:
            _sum = 0
            for i, _x in enumerate(x):
                if _x < self.x_min[i]:
                    _sum += self.x_min[i] - _x
                elif _x > self.x_max[i]:
                    _sum += _x - self.x_max[i]
            print('Box deviation is', _sum)



        return flag

    def plot(self, ax, fig, show=False, save=False, color='b'):
        #ax.set_aspect("equal")
        box_color = CB_color_cycle[2]
        if self.dim == 2:
            ax.hlines([self.x_min[1], self.x_max[1]], self.x_min[0], self.x_max[0], color=box_color, label=r'$\mathcal{B}$')
            ax.vlines([self.x_min[0], self.x_max[0]], self.x_min[1], self.x_max[1], color=box_color)
        elif self.dim == 3:
            r1 = [self.x_min[0], self.x_max[0]]
            r2 = [self.x_min[1], self.x_max[1]]
            r3 = [self.x_min[2], self.x_max[2]]
            for s, e in combinations(np.array(list(product(r1, r2, r3))), 2):
                if np.linalg.norm(s-e) in [self.x_max[0]-self.x_min[0], self.x_max[1] - self.x_min[1], self.x_max[2] - self.x_min[2]]:
                    myplot = ax.plot3D(*zip(s, e), color=box_color)
            myplot[0].set_label(r'$\mathcal{B}$')
        if show:
            plt.show()
        if save:
            fig.savefig('tmp/fig.png')

    def project(self, x):
        q = copy.copy(x)
        for i in range(self.dim):
            if x[i] < self.x_min[i]:
                q[i] = self.x_min[i]
            elif x[i] > self.x_max[i]:
                q[i] = self.x_max[i]
        return q

class Variable:
    def __init__(self):
        pass

class Omega:
    def __init__(self, B, Q, x_feas):
        self.Q = copy.deepcopy(Q)
        self.B = copy.deepcopy(B)
        self.dim = self.Q.dim
        self.x_feas = x_feas
        #self.n, self.c_lower, self.c_upper = self.get_planes_relax()
    

    def get_mod(self):
        mod = Model()
        mod.Params.NonConvex = 2
        Q = self.Q
        B = self.B
        var = {}
        var['p'] = mod.addVars(Q.dim, lb=B.x_min, ub=B.x_max, name='p')
        p = var['p']
        mod.addConstr(
            quicksum(p[i]*p[j]*Q.A[i, j] for (i, j) in product(range(Q.dim), range(Q.dim)))
            + quicksum(p[i]*Q.b[i] for i in range(Q.dim))
            + Q.c
            == 0, name = 'Balance')
        return mod, var


    def is_feasible(self, x):
        print('Is on quadric (%s): %s' % (self.Q.type,  self.Q.is_feasible(x)))
        print('Is in box', self.B.is_feasible(x))
        # print('Is in box', self.B.is_feasible(x), x, self.B.x_min, self.B.x_max)
        return self.Q.is_feasible(x) and self.B.is_feasible(x)

    def plot(self, flag_show=False, tight_layout=True):
        assert self.dim in [2, 3], 'I can only plot for 2D or 3D'
        fig = plt.figure()
        if self.dim == 2:
            ax = fig.add_subplot()
        elif self.dim == 3:
            ax = fig.add_subplot(projection='3d')
        if self.dim in [2, 3]:
            self.Q.plot(ax, fig, show=False)
            self.B.plot(ax, fig)
        if tight_layout:
            R = self.B.R/2

            ax.set_xlim(self.B.x_min[0]-R[0], self.B.x_max[0]+R[0])
            ax.set_ylim(self.B.x_min[1]-R[1], self.B.x_max[1]+R[1])
            if self.dim == 3:
                ax.set_zlim(self.B.x_min[2]-R[1], self.B.x_max[2]+R[1])

        if flag_show:
            plt.show()

        return fig, ax

    def print_info(self):
        print("\n\n ********** Information about feasible set ***********")
        print("Dimension is %s" % (self.dim))
        print("Type of quadric is %s" % (self.Q.type))
        print(self.Q.A)
        print('Min ranges', self.B.x_min)
        print('Max ranges', self.B.x_max)
        print("**********\n\n")

    def reduce_box(self):
        mod, var = self.get_mod()
        p = var['p']
        for i in range(self.dim):
            mod.setObjective(p[i], GRB.MAXIMIZE)
            mod.optimize()
            new_x_min = mod.getAttr('ObjVal')
            print('Checkk', new_x_min, self.B.x_min[i])
            self.B.x_max[i] = mod.getAttr('ObjVal')
            mod.setObjective(p[i], GRB.MINIMIZE)
            mod.optimize()
            self.B.x_min[i] = mod.getAttr('ObjVal')
            mod.dispose()
    
    def set_planes_relax(self):
        self.n, self.c_lower, self.c_upper = self.get_planes_relax()

    def transform_B(self):
        x_max = (self.Q.V.T @ (self.B.x_max - self.Q.d)) / np.sqrt(abs(self.Q.gamma))
        x_min = (self.Q.V.T @ (self.B.x_min - self.Q.d)) / np.sqrt(abs(self.Q.gamma))
        if np.any(x_max < x_min):
            raise ValueError('Bug to be fixed')
        self.B.x_max = x_max
        self.B.x_min = x_min


    def get_planes_relax(self):
        p0 = self.x_feas
        assert self.is_feasible(p0), 'x_feas is not feasible'
        n = self.Q.get_tangent_plane(self.x_feas)

        n_normed = n / np.linalg.norm(n)
        mod, var = self.get_mod()
        mod.Params.timelimit = 300
        p = var['p']
        if self.Q.is_ellipsoid:
            y_upper = p0
            c_upper = - n.T @ y_upper
        else:
            mod.setObjective(quicksum(
                    n_normed[i] * (p[i] - p0[i]) for i in range(self.Q.dim)
                ), GRB.MAXIMIZE)
            mod.update()
            mod.optimize()
            scalar_product = mod.getAttr('ObjVal')
            y_upper = p0 + n_normed*scalar_product
            c_upper = - n.T @ y_upper
        mod.setObjective(quicksum(
                n_normed[i] * (p[i] - p0[i]) for i in range(self.Q.dim)
            ), GRB.MINIMIZE)
        mod.update()
        mod.optimize()
        scalar_product = mod.getAttr('ObjVal')
        y_lower = p0 + n_normed * scalar_product
        c_lower = - n.T @ y_lower
        print('c are', c_upper, c_lower)
        mod.dispose()
        return n, c_lower, c_upper

    def get_point_in_relaxation(self):
        #print('A', self.Q.A)
        mod = Model()
        mod.Params.timelimit = 30
        p = mod.addVars(self.Q.dim, lb=self.B.x_min, ub=self.B.x_max, name='p')
        mod.addConstr(quicksum(
            p[i] * self.n[i] for i in range(self.dim))
            >=- self.c_lower, name = 'lower plane')
        mod.addConstr(quicksum(
            -p[i] * self.n[i] for i in range(self.dim))
            >= self.c_upper, name = 'upper plane')
        mod.setObjective(1)
        mod.optimize()
        #print(self.Q.eig)
        #fig, ax = get_fig_ax(self.Q.dim)
        #self.plot_planes_relax(ax, fig)
        #print('x_feas', self.x_feas)
        #print('Feasibility', self.is_feasible(self.x_feas))
        #print(self.Q.A, self.Q.eig, np.linalg.eig(self.Q.A)[0])
        #ax.scatter(self.x_feas[0], self.x_feas[1])
        #self.plot(ax, fig)
        #plt.show()
        x_out =  gurobi_sol_to_np(mod.getAttr('x', p))
        mod.dispose()
        return x_out

    def plot_planes_relax(self, ax, fig):
        m = 100
        t = np.linspace(-250, 250, m)
        v = copy.copy(self.n)
        v[0] = 1/v[0]
        v[1] = -1/v[1]
        #assert v @ self.n <= 0.000001
        z_lower = (- self.c_lower - self.n[0]*t)/self.n[1]
        z_upper = (-self.c_upper - self.n[0]*t)/self.n[1]
        ax.plot(t, z_lower, '--', linewidth=2)
        ax.plot(t, z_upper, 'r--', linewidth=2)
        

def get_fig_ax(dim=2, label='test'):
    fig = plt.figure(1)
    if dim == 2:
        ax = fig.add_subplot()
    else:
        ax = fig.add_subplot(projection='3d')
    return fig, ax
    
def get_omega(param, Q=None):
    if Q is None:
        Q = Quadric(param)
    else:
        Q.projection_type = param['projection_type']

    p0 = Q.d
    #p0[1] = 1
    x_feas = Q.project(p0)
    x_min = param['x_min']
    x_max = param['x_max']

    assert np.all(x_max > x_min), 'Bug to be fixed'
    B = Box(x_min, x_max)

    k = 0
    k_max = 300
    while not B.is_feasible(x_feas) and k < 300:
        p0 = x_min + np.random.rand(Q.dim) * (x_max - x_min)
        #print(Q.A, Q.b, Q.c, Q.d)

        #fig, ax = get_fig_ax(Q.dim)
        #Q.plot(ax, fig)
        #ax.scatter(p0[0], p0[1], p0[2])
        #plt.show()
        #print('p0', p0)
        #print(Q.to_non_standardized(p0))
        #print(x_min, x_max)
        x_feas = Q.project(p0, forced_projection='exact')
        #print('p0', p0)
        #print('x_feas', x_feas)
        #print('x_feas_s', Q.to_standardized(x_feas))
        print(k)
        k += 1
    if k == k_max:
        print(Q.eig)
        print('k=', k)
        raise ValueError('Problem is not feasible')
    return  Omega(B, Q, x_feas)

def box_proj(B, x):
    q = copy.copy(x)
    for i in range(B.dim):
        if x[i] < B.x_min[i]:
            q[i] = B.x_min[i]
        elif x[i] > B.x_max[i]:
            q[i] = B.x_max[i]

    return q

def exact_proj(B, Q, x):
    mod = Model()
    mod.Params.NonConvex = 2
    mod.Params.mipgap = 0.0001
    mod.Params.FeasibilityTol = eps_p/10
    mod.Params.timelimit = 600
    # mod.Params.solutionlimit = 1
    p = mod.addVars(Q.dim, lb=B.x_min, ub=B.x_max, name='p')
    mod.addConstr(
        quicksum(p[i]*p[j]*Q.A[i, j] for (i, j) in product(range(Q.dim), range(Q.dim)))
        + quicksum(p[i]*Q.b[i] for i in range(Q.dim))
        + Q.c
        == 0, name = 'balance')
    mod.setObjective(
        quicksum((x[i] - p[i])*(x[i]-p[i]) for i in range(Q.dim))
    )
    mod.write('model.lp')
    mod.update()
    mod.optimize()
    print('Optimization status is', mod.status)
    if mod.status in [3, 7, 8, 9]:
        print('Hellllllo sunshine')
        x_proj = None
    else:
        x_proj = gurobi_sol_to_np(mod.getAttr('x', p))
    mod.dispose()

    return x_proj

def gurobi_sol_to_np(x):
    x_np = np.array(list(x.values()))
    return x_np

def plot_iterates(iterates_np, ax, fig, options={'marker': 'x', 'color': CB_color_cycle[1], 'zorder': 1}):
    print('Here shape', iterates_np.shape)
    dim = np.size(iterates_np, 1)
    if dim == 2:
        ax.plot(iterates_np[:, 0], iterates_np[:, 1], color=options['color'], zorder=1)
        ax.scatter(iterates_np[-1, 0], iterates_np[-1, 1], color = 'red', zorder=2, label='Final iterate')
        if iterates_np.shape[0] == 1:
            if options['color'] == 'red':
                ax.scatter(iterates_np[:, 0], iterates_np[:, 1], marker=options['marker'], color = options['color'], zorder=2, label='Final iterate')
            else:
                ax.scatter(iterates_np[:, 0], iterates_np[:, 1], marker=options['marker'], color = options['color'], zorder=2, label=r'$\mathbf{x}^k$')


        else:
            ax.scatter(iterates_np[:, 0], iterates_np[:, 1], marker=options['marker'], color = options['color'], zorder=2, label=r'$\mathbf{x}^k, \mathbf{y}^k$')
        ax.scatter(iterates_np[0, 0], iterates_np[0, 1], color = 'black', marker='s', zorder=2, label=r'$\mathbf{x}^0$')
    elif dim == 3:
        ax.plot(iterates_np[:, 0], iterates_np[:, 1], iterates_np[:, 2], linestyle='dashed', color=options['color'])
        ax.scatter(iterates_np[0, 0], iterates_np[0, 1], iterates_np[0, 2], linestyle='dashed', color='black', marker='s', label=r'$\mathbf{x}^0$')
        ax.scatter(iterates_np[0, 0], iterates_np[0, 1], iterates_np[0, 2], linestyle='dashed', color=options['color'], marker='x', label=r'$\mathbf{x}^k, \mathbf{y}^k$')
        ax.scatter(iterates_np[-1, 0], iterates_np[-1, 1], iterates_np[-1, 2], linestyle='dashed', color='red', label=r'Final iterate')
        if iterates_np.shape[0] == 1:
            if options['color'] == 'red':
                ax.scatter(iterates_np[:, 0], iterates_np[:, 1], iterates_np[:, 2], marker=options['marker'], color = options['color'], label='Final iterate')
            else:
                ax.scatter(iterates_np[:, 0], iterates_np[:, 1], iterates_np[:, 2], marker=options['marker'], color = options['color'], label=r'$\mathbf{x}^k$')
        else:
            ax.scatter(iterates_np[:, 0], iterates_np[:, 1], iterates_np[:, 2], marker=options['marker'], color = options['color'])


def is_feasible(B, Q, x):
    print('Is on quadric (%s): %s' % (Q.type,  Q.is_feasible(x)))
    print('Is in box', B.is_feasible(x))
#    print('Is in box', B.is_feasible(x), x, B.x_min, B.x_max)
    return Q.is_feasible(x) and B.is_feasible(x)

def run_project(param, ranges=None, gif_name='iterates.gif', gif='iterates'):
    print('Run project')
    plt.clf()
    Q = Quadric(param)
    dim = np.size(Q.A, 1)
    fig = plt.figure(1)
    if dim == 2:
        ax = fig.add_subplot()
    else:
        ax = fig.add_subplot(projection='3d')
        ax.view_init(elev=26., azim=130)
        #ax.set_zlabel('$x_3$')
        ax.set_zticks([])
    Q.plot(ax, fig)
    if ranges is None:
        x_min, x_max, x_feas = get_feas_ranges(Q)
    else:
        x_min, x_max, x_feas = ranges
    B = Box(x_min, x_max)
    #B.plot(ax, fig)
    param['x_min'] = x_min
    param['x_max'] = x_max
    Om = get_omega(param, Q=Q)
    print('Initializing random point and start iterating')
    x0 = (np.random.rand(dim)-0.5)*2

    fig.tight_layout()
    #ax.set_xlabel('$x_1$')
    #ax.set_ylabel('$x_2$')
    ax.set_xticks([])
    ax.set_yticks([])
    if Q.dim == 3 and gif == '3D_final':
        ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        plt.axis('off')


    iterates, _ = project(B, Q, x0, param)
    iterates_np = np.array(iterates)
    #print(iterates_np)
    if gif == 'iterates':
        for i, x in enumerate(iterates):
            _iterates_np = iterates_np[:i+1, :]
            plot_iterates(_iterates_np, ax, fig)
            #ax.legend([])
            fig.savefig('tmp/gif/' + str(i) + '.png')
        plot_iterates(np.reshape(_iterates_np[-1, :], (-1, dim)), ax, fig,
                      options={'marker': 'o', 'color': 'red', 'zorder': 2})
        #ax.legend()
        if is_feasible(B, Q, _iterates_np[-1]):
        #    plt.scatter(_iterates_np[-1, 0], _iterates_np[-1, 1], marker='o', color='red', zorder=10)
            fig.savefig('tmp/gif/' + str(i) + '.png')
        else:
            plt.show()
    elif gif == '3D_final' and Q.dim == 3:
        azims = np.arange(1, 360, 2)
        print(azims)
        #plt.legend()
        plot_iterates(iterates_np, ax, fig)
        plot_iterates(np.reshape(iterates_np[-1, :], (-1, dim)), ax, fig,
                      options={'marker': 'o', 'color': 'red', 'zorder': 2})
        for i, azim in enumerate(azims):
            print(i, azim)
            ax.view_init(elev=26, azim=azim)
            fig.savefig('tmp/gif/' + str(i) + '.png')

    plt.savefig('tmp/fig.png')
    get_gif(iterates_np, gif_name=gif_name)
    

def get_gif(iterates_np, gif_name='out.gif'):
    images = []
   # n_images = len([name for name in os.listfile('tmp/gif/') if os.path.isfile(name)])
    #print(os.listdir('tmp/gif'))
    n_images = 0
    for path in os.listdir('tmp/gif'):
        name = os.path.join('tmp/gif', path)
        if os.path.isfile(name):
            n_images += 1
    filenames = ['tmp/gif/' + str(i) + '.png' for i in range(n_images)]

    #copyfile(filenames[-1], 'tmp/test.png')
    for filename in filenames:
        images.append(imageio.imread(filename))
        os.remove(filename)
    imageio.mimsave('tmp/'+gif_name, images)  # fps=25 for projection 

def get_feas_ranges(Q, scale=None):
    p0 = Q.V[:, 0]
    if scale is None:
        scale = np.mean(np.abs(np.diag(Q.A))) * 0.3 # 10

    x_n = abs(np.random.rand(Q.dim)*scale)
    x_m = abs(np.random.rand(Q.dim)*scale)
    _flag = True
    i = Q.dim-1
    while _flag and i in range(0, Q.dim):
        _flag = False
        p0 = Q.V[i, :]
        p0 = Q.d+np.random.rand(Q.dim)*0.1
        i -= 1
        try:
            x_feas = Q.project(p0)
        except ValueError:
            raise
            print("Catch ValueError")
            print("i = %s" % i)
            _flag = True
        if _flag and Q.dim == i:
            raise NoFeasibleDirection
        
    
    x_min = x_feas - x_n
    x_max = x_feas + x_m



    return x_min, x_max, x_feas

def project(B, Q, x0, param):
    str_output = ['x', 'nit', 'success', 'maxcv', 'nfev', 'fun', 'n_convert',
                  'n_rebranching', 'n_resort_exact_proj', 'message', 'status']
    output = {str_o: 0 for str_o in str_output}
    param['output'] = output
    k = 0
    n_iter = 300 # should be1000
    count = 0
    x = [x0]
    D = B.x_max - B.x_min
    B_new = copy.deepcopy(B)
    Q.xi = None
    #B_new.x_min = B.x_min + D/10
    #B_new.x_max = B.x_max - D/10
    print('Starting projection')
    alg_name = param['alg'].alg_name
    flag_double = False
    if alg_name == 'alternate-projection' and flag_double:
        n_iter = n_iter*2
    _x = x0
    while not is_feasible(B, Q, x[k]) and k < n_iter:
        print('k =', k)
        if alg_name == 'alternate-projection':    
            new_x = alternate_projection(B, Q, x[k], param)
        elif alg_name == 'dykstra':
            new_x = dykstra(B, Q, x[k], param['alg'])
        elif alg_name == 'douglas-rachford':
            new_x = douglas_rachford(B, Q, x[k])
        elif alg_name == 'douglas-rachford-feasibility':
            _x, new_x = douglas_rachford(B, Q, x[k], gamma=0.1)
            #print('\n\nNew x is %s \n\n' % new_x)
        else:
            raise ValueError('Invalid algorithm name %s' % alg_name)
        flag_alternate, count = check_alternate(x, count)
        if k == n_iter // 2:
                #_projection_type = Q.projection_type
                print('Changing of branch! v2')
                #Q.projection_type = 'quasi-farthest'
                #param['output']['n_rebranching'] += 1
                #new_x = Q.quasi_project(new_x, None)
                #print(new_x)
                if abs(Q.evaluate_point(new_x)) <= eps_dev*10:
                    print('Breaking')
                    break
                #Q.projection_type = _projection_type
                if param['flag_restart']:
                    new_x = Q.change_branch(new_x, B, param)
                #fig, ax = get_fig_ax(Q.dim)
                print('New x', new_x)
                #ax.scatter(new_x[0], new_x[1], color='red', s=50)
                #fig, ax = get_fig_ax(Q.dim)
                #Q.plot(ax, fig)
                #B.plot(ax, fig)
                #plot_iterates(np.array(x), ax, fig)
                #plt.show()
        elif flag_alternate:
            count = 0
            if alg_name =='alternate-projection' and Q.projection_type == 'quasi' and param['flag_restart']: #could simpyl use true projection?
                _projection_type = Q.projection_type
                Q.projection_type = 'exact'
                new_x = alternate_projection(B, Q, x[k], param)
            else:
                print('Changing of branch!')
                #fig, ax = get_fig_ax(Q.dim)
                if param['flag_restart']:
                    new_x = Q.change_branch(new_x, B, param)
                else:
                    break
                print('New x', new_x)
                #ax.scatter(new_x[0], new_x[1], color='red', s=50)
                #Q.plot(ax, fig)
                #B.plot(ax, fig)
                #plot_iterates(np.array(x), ax, fig)
                #plt.show()

        k+=1
        param['alg'].increment_k()
        x.append(new_x)

        if Q.projection_type == 'current-grad' and False:
            plt.close()
            fig, ax = get_fig_ax(Q.dim)
            ax.axis('equal')
            
            Q.plot(ax, fig)
            B.plot(ax, fig)
            plot_iterates(np.array(x), ax, fig)
            xi = Q.get_tangent_plane(x[-1], forced=True)
            d1 = new_x + 0.1*xi
            d2 = new_x - 0.1*xi
            ax.plot([d1[0], d2[0]], [d1[1], d2[1]], linestyle='dashed', color='red')

            plt.show()
            

            
    if k == n_iter:
        print('Max number of iteration reached')
        print(alg_name)
        output['success'] = False
    str_output = ['x', 'nit', 'success', 'maxcv', 'nfev', 'fun', 
                  'n_rebranching', 'n_resort_exact_proj', 'message', 'status']
    #print(param)
    if alg_name == 'alternate-projection' and flag_double:
        k = k/2
    param['output']['x'] = new_x 
    param['output']['nit'] = k

        #raise
    #print('Final x is', x[-1])
    print('Nbre iteration is', k)
    print('Feasibility of x is', is_feasible(B, Q, x[-1]))
    return x, param


def check_alternate(x, count):
    count += 1
    if count < 100:
        return False, count
    #return np.linalg.norm(x[-1] -x[-3]) < 0.001
    flag_alternate = np.linalg.norm(x[-1]-x[-3]) < pow(10, -12)
    print('1 is', flag_alternate)
    flag_alternate = flag_alternate or np.linalg.norm(x[-1]-x[-2]) < pow(10, -12)
    print('Alternating is', flag_alternate)
    return flag_alternate, count

def alternate_projection(B, Q, xk, param):
    k = param['alg'].k
    y = Q.project(xk, param=param)
    new_x = B.project(y)

    return new_x


def dykstra(B, Q, x, param):
    b = Q.project(param.a + param.q)
    param.q = param.a + param.q - b
    param.a = B.project(b + x)
    x_proj = b + x - param.a
    return b

def douglas_rachford(B, Q, x, gamma=None):
    if gamma is None:
        y = Q.project(x)
        _b = 2 * y - x
        x_proj = B.project(_b) + x - y
        return x_proj
    else:

        y = 1/(1+gamma) * (x + gamma*B.project(x))
        z = Q.project(2*y-x)
        print('Feasibilityz z is ', Q.is_feasible(z))
        #print(z, y)
        return x + (z - y), z

def my_newton(fun, fprime, x0, interval=None):
    class Output:
        def __init__(self):
            self.converged = False
            self.message = ''
            self.iteration = 0
            self.root = None
            self.fx = None
            self.dfx = None
            self.rtol = float('inf')
            self.xtol = float('inf')
        def __str__(self):
            output_str = f"""
            converged: {self.converged} \n
            iterations: {self.iteration} \n
            root: {self.root} \n
            message: {self.message} \n
            fx: {self.fx} \n
            dfx: {self.dfx} \n"""
            return output_str
        def is_in_interval(self, interval):
            if interval[0] == interval[1]:
                return True

            if self.root is None or interval is None:
                return True
            else:
                return self.root >= interval[0] and self.root <= interval[1]

    output = Output()
    iteration_max = 100
    eps_rtol = pow(10, -10)
    eps_xtol = pow(10, -14)
    x = x0
    new_x = x
    while (output.iteration < iteration_max and output.rtol > eps_rtol and 
           output.xtol > eps_xtol and output.is_in_interval(interval)):
        print('Interval', interval, x)
        print('Interval', output.is_in_interval(interval))
        output.fx = fun(x)
        output.dfx = fprime(x)
        new_x = x - output.fx/output.dfx
        print('x,new_x', x, new_x)
        output.xtol = abs(x-new_x)
        x = new_x
        output.root = new_x
        output.rtol = abs(output.fx)
        output.iteration += 1
    output.converged = False
    if output.iteration == iteration_max:
        output.message = "max number of iteration reached"
        
    elif output.rtol <= eps_rtol:
        output.message = "converged"
        output.converged = True
    elif output.xtol <= eps_xtol:
        output.message = "weak improvement, stopping the alg early. You may want to check the value of the derivative around the root"
    elif not output.is_in_interval(interval):
        output.message = "Point is outside the interval of research"

    output.iteration += 1
    return output


def plot_alg_convergence(ax, x0, iterates):
    n_iter = len(iterates)
    iterations = np.arange(n_iter)
    dists = np.ones_like(iterations)
    for i, x in enumerate(iterates):
        dists[i] = np.linalg.norm(x-iterates[-1])
    #print('dists', iterates)
    ax.plot(iterations, dists)

class Param_alg:
    def __init__(self, alg_name, dim=0):
        self.alg_name = alg_name
        self.dim = dim
        self.__set_attributes__()

    def __set_attributes__(self):
        self.k = 0
        if self.alg_name == 'alternate-projection':
            pass
        elif self.alg_name == 'dykstra':
            self.a = np.zeros(self.dim)
            self.q = np.zeros(self.dim)

    def increment_k(self):
        self.k += 1

    def __str__(self):
        return "alg_name: %s" % self.alg_name

