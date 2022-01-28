#!/usr/bin/env python3

import numpy as np
import scipy.sparse
import imageio
import matplotlib.pyplot as plt
from os import listdir, remove
from os.path import join, isfile

from utils import get_project_root, get_tmp_path, get_output_path, get_tmp_gif_path
import uuid

root = get_project_root()
tmp_path = get_tmp_path()
output_path = get_output_path()
tmp_gif_path = get_tmp_gif_path()

global eps_p
eps_p = pow(10, -10)
eps_dev = eps_p


class Quadric:
    """
        Define a quadric of the form

        x' A x + b' x + c = 0

        which can be reduced (via scaling and shifting) under the form

        z' A z = 1

        and x = z * gamma + d with d = - 0.5 A^{-1} b and
        gamma = sqrt(abs(c  + b' d + d'd)) \\in \\mathrm{R}

        This centred quadric can then be diagonalized, i.e., rotated by using the decomposition
        A = V L V' where L is diagonal matrix containing the eigenvalues and V the orthonormal
        matrix containing the associated eigenvectors.

        It follows that u' L u = 1 with u = V' z and therefore x = d + gamma * V u

    """
    class EmptyQuadric(Exception):

        def __str__(self):
            return 'Quadric appears to be empty'

    class InvalidArgument(Exception):

        def __init__(self, msg):
            self.msg = 'Invalid input arguments\n' + msg

        def __str__(self):
            return self.msg

    def __init__(self, param):
        #  assert param['c'] <= 0, 'c should be negative instead of %s ' % param['c']
        try:
            self.A = param['A']
            if not np.allclose(self.A, self.A.T):
                raise self.InvalidArgument('Matrix is not symmetric!')

            self.b = param['b']
            self.c = param['c']
        except KeyError:
            raise ValueError('Invalid parameters, please enter matrices (ndarray)\
                             A [n x n], b [n x 1] and a float c')
        self.d = np.linalg.solve(self.A, -self.b/2.0)
        self.dim = np.size(self.A, 0)
        if param.get('diagonalize') is not bool:
            self.is_standardized = True
        else:
            self.is_standardized = param['diagonalize']

        if self.is_standardized:
            self.eig, self.V = np.linalg.eig(self.A)
            self.idx = np.argsort(-self.eig)
            self.eig = self.eig[self.idx]
            indexes = np.unique(self.eig[self.idx], return_index=True)[1]
            self.eig_bar = [self.eig[idx] for idx in sorted(indexes)]
            self.poles_full = -1/self.eig
            self.poles_full_sorted = np.sort(self.poles_full)
            self.L = np.diag(self.eig)  # correctly sorted
            self.V = self.V[:, self.idx]
            self.standardize()
            self.axes = np.sign(self.eig) * 1/np.sqrt(abs(self.eig))
        self.set_type()
        self.xi = None

        self.gamma = self.c + self.b.T @ self.d + self.d.T @ self.A @ self.d
        self.is_empty = self.check_empty()
        if self.is_empty:
            raise self.EmptyQuadric

        if self.gamma > 0:  # and self.d.T @ self.A @ self.d < 0: TODO TOREVIE
            print('\n\nSwitching equality sign !\n\n')
            param['A'] = - param['A']
            param['b'] = - param['b']
            param['c'] = - param['c']
            self.__init__(param)

        assert self.dim > 1, 'one dimensional case is not yet supported'

    def change_branch(self, x, B, param):
        print('\n\nChanging of branch!\n\n')
        param['output']['n_rebranching'] += 1
        self.need_std = True
        if B.is_feasible(x):
            print('Via box')
            new_x = -x+2*B.center
            return new_x
        x_std = -self.to_standardized(x)
        new_x = self.to_non_standardized(x_std)

        return new_x

    def check_empty(self):
        if self.gamma < 0:
            p = np.sum(self.eig > 0)
        else:
            p = np.sum(self.eig < 0)
        return p == 0

    def standardize(self):
        self.A_std = self.L
        self.b_std = np.zeros(self.dim)
        self.c_std = -1
        self.d_std = np.zeros(self.dim)
        self.is_standardized = True

    def is_feasible(self, x):
        return abs(self.evaluate_point(x)) <= eps_dev

    def evaluate_point(self, x):
        if scipy.sparse.issparse(self.A):
            out = np.dot(self.A.dot(x), x) + np.dot(self.b, x) + self.c
        else:
            out = np.dot(np.dot(x, self.A), x) + np.dot(self.b, x) + self.c
        return out

    def is_in_quadric(self, x):
        return self.evaluate_point(x) <= 0

    def get_tangent_plane(self, x, forced=False):
        if not forced:
            assert self.is_feasible(x), 'Cannot compute tangent plane on infeasible points'
        Tp = 2 * self.A @ x + self.b
        return Tp

    def set_type(self):
        assert np.all(self.axes != 0), 'Quadric should be nondegenerated, i.e.,\
        A should be invertible.'
        if not self.is_standardized:
            self.type = 'unknown'
        elif self.dim == 2 and np.all(self.axes > 0):
            self.type = 'ellipse'
        elif self.dim == 2 and self.axes[0]*self.axes[1] < 0:
            self.type = 'hyperbole'
        elif np.all(self.axes > 0):
            self.type = 'ellipsoid'
        elif self.dim == 3 and np.prod(self.axes) > 0:
            self.type = 'two_sheets_hyperboloid'
        elif self.dim == 3 and np.prod(self.axes) < 0:
            self.type = 'one_sheet_hyperboloid'
        else:
            self.type = 'hyperboloid'

    def to_non_standardized(self, u):
        x = self.V @ (u * np.sqrt(abs(self.gamma))) + self.d
        return x

    def to_standardized(self, x):
        u = self.V.T @ (x-self.d) / np.sqrt(abs(self.gamma))

        return u

    def plot(self, *args, show=False, save=False):
        if args:
            fig = args[0]
            ax = args[1]
        else:
            fig, ax = get_fig_ax(self)

        dim = self.dim
        assert dim <= 3, 'Sorry, I can not represent easily > 3D spaces...'
        assert self.type != 'unknown', 'Diagonalize is none, impossible to know quadric type'
        m = 1000
        quadric_color = 'royalblue'
        flag_hyperboloid = np.any(self.eig < 0)

        T = np.linspace(-np.pi, np.pi, m)
        x = np.zeros_like(T)
        y = np.zeros_like(T)
        gamma = (np.sqrt(abs(self.c+self.d.T @ self.A @ self.d + self.b.T @ self.d)))
        if dim == 2:
            x = np.zeros_like(T)
            y = np.zeros_like(T)

            for i, t in enumerate(T):
                if flag_hyperboloid:
                    t = t/4  # otherwise we plot too much of the quadric...
                    v = self.d + (self.V @ np.array([self.axes[0] / np.cos(t),
                                                     -self.axes[1] * np.tan(t)])) * gamma
                    v2 = self.d + (self.V @ np.array([self.axes[0] / np.cos(t+np.pi),
                                                      -self.axes[1] * np.tan(t+np.pi)])) * gamma
                    x[i//2], y[i//2] = (v[0], v[1])
                    x[i//2 + m//2], y[i//2 + m//2] = (v2[0], v2[1])
                else:
                    v = self.d + (self.V @ np.array([self.axes[0] * np.cos(t),
                                                     self.axes[1] * np.sin(t)])) * gamma
                    #   v = np.array([self.axes[0]*np.cos(t), self.axes[1] * np.sin(t)])
                    x[i], y[i] = (v[0], v[1])
            if flag_hyperboloid:
                ax.plot(x[:m//2], y[:m//2], color=quadric_color, zorder=1,
                        label=r'$\mathcal{Q}$')
                ax.plot(x[m//2:], y[m//2:], color=quadric_color, zorder=1)
            else:
                ax.plot(x, y, color=quadric_color, label=r'$\mathcal{Q}$', zorder=1)
            ax.scatter(self.d[0], self.d[1], color=quadric_color, label=r'$\mathbf{d}$')
        elif dim == 3:
            m1 = 40
            m2 = 20
            ax.scatter(self.d[0], self.d[1], self.d[2],
                       color=quadric_color, label=r'$\mathbf{d}$')
            if self.type == 'one_sheet_hyperboloid':
                t, s = np.mgrid[0:2*np.pi:m1 * 1j, -1:1:m2 * 1j]
                u_x = self.axes[0] * np.cos(t) * np.sqrt(1+s**2)
                u_y = self.axes[1] * np.sin(t) * np.sqrt(1+s**2)
                u_z = self.axes[2] * s
                U_vec = np.tile(self.d, (m1*m2, 1)).T\
                    + self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                surf = ax.plot_surface(x, y, z, color=quadric_color,
                                       alpha=0.3, label=r'$\mathcal{Q}$')
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

                U_vec = np.tile(self.d, (m1*m2, 1)).T \
                    + self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
                #    U_vec = np.tile(self.d, (m1*m2, 1)).T
                #   +  np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten()))
                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                x1 = x[:, :m2//2]
                y1 = y[:, :m2//2]
                z1 = z[:, :m2//2]
                x2 = x[:, m2//2:]
                y2 = y[:, m2//2:]
                z2 = z[:, m2//2:]
                surf = ax.plot_surface(x1, y1, z1, color=quadric_color,
                                       alpha=0.3, label=r'$\mathcal{Q}$')
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
                U_vec = np.tile(self.d, (m1*m2, 1)).T\
                    + self.V @ np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten())) * gamma
                # U_vec = np.tile(self.d, (m1*m2, 1)).T
                # +  np.vstack((u_x.flatten(), u_y.flatten(), u_z.flatten()))

                x = np.reshape(U_vec[0, :], (m1, m2))
                y = np.reshape(U_vec[1, :], (m1, m2))
                z = np.reshape(U_vec[2, :], (m1, m2))
                surf = ax.plot_surface(x, y, z, color=quadric_color, alpha=0.3,
                                       label=r'$\mathcal{Q}$')
                surf._facecolors2d = surf._facecolors3d
                surf._edgecolors2d = surf._edgecolors3d
                ax.plot_wireframe(x, y, z, color=quadric_color, alpha=0.7)
            # self.ranges = [(np.min(x), np.max(x)), (np.min(y), np.max(y)),
            # (np.min(z), np.max(z))]
        plt.legend()
        if show:
            plt.show()
        if save:
            fig.savefig('tmp/fig.png')

        return fig, ax

    def get_gif(self, gif_path='out.gif', elev=25, step=2):
        assert self.dim == 3, f'Gif of quadric of dimension different than three is not supported.\
                Current dim = {self.dim}'
        azims = np.arange(1, 360, step)
        fig, ax = self.plot()
        seed = uuid.uuid4().hex
        seed_name = join(tmp_gif_path, seed)
        for i, azim in enumerate(azims):
            ax.view_init(elev=elev, azim=azim)
            file_name = seed_name + str(i) + '.png'
            fig.savefig(file_name)
        write_gif(tmp_gif_path, seed=seed, gif_name=gif_path)


def get_fig_ax(Q):
    fig = plt.figure()
    assert Q.dim in [2, 3], 'I can only plot 2 or 3D quadrics'
    if Q.dim == 2:
        ax = fig.add_subplot()
        ax.axis('equal')
        ax.set_aspect(1)
    else:
        ax = fig.add_subplot(projection='3d')
    return fig, ax


def write_gif(tmp_gif_path, seed='', gif_name='out.gif'):
    images = []
    n_images = 0
    for path in listdir(tmp_gif_path):
        name = join(tmp_gif_path, path)
        if isfile(name) and seed in name:
            n_images += 1
            filenames = [join(tmp_gif_path, seed + str(i) + '.png') for i in range(n_images)]

    for filename in filenames:
        images.append(imageio.imread(filename))
        remove(filename)
    imageio.mimsave(gif_name, images)  # fps=25 for projection
