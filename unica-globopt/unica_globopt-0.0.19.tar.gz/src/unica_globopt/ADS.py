from .nn_utils import *
from . import active_subspaces as ac
import matplotlib.pyplot as plt
import os
import scipy
import matplotlib.tri as tri
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import pickle


class ADS:
    """
    A utility class for creating Active Design Subspaces using a NeuralNet and a Dataset objects

    Attributes
    ----------
    dataset : Dataset
        a Dataset object containing the dataset employed for training the NeuralNet
    network : NeuralNet
        a NeuralNet object which must have been trained
    bounds : np.array
        an array containing the lower and upper boundaries of each input
    n_pts : int
        the number of points to be used for the construction of the ADS. If lower than
        dataset.n_samples, it defaults to dataset.n_samples
    n_dims : int
        the number of dimensions desired for the ADS
    """

    def __init__(self, dataset, network, bounds, n_pts=2000, n_dims=-1):
        self.dataset = dataset
        self.network = network
        self.bounds = bounds
        self.n_pts = n_pts

        if n_dims < 0:
            self.n_dims = self.dataset.n_params
        else:
            self.n_dims = n_dims

        self.x = None
        self.qoi = None
        self.gradients = None

        self.x_normed = None
        self.grad_normed = None

        self.figures = os.path.join(os.getcwd(), 'figures')

        self.ss = ac.subspaces.Subspaces()
        self.W1 = None

    def define_evaluations_random(self):
        added_points = self.n_pts - self.dataset.n_samples

        # adding remaining points uniformely distributed in the design space
        if added_points > 0:
            x = np.array([]).reshape(added_points, 0)
            for i in range(self.dataset.n_params):
                x = np.hstack(
                    (x, vectorize_random(np.linspace(self.bounds[i, 0], self.bounds[i, 1],
                                                     num=added_points,
                                                     dtype=float))))

            x = np.vstack((x, np.array(self.dataset.x)))

        else:
            x = np.array(self.dataset.x)

        self.x = x

    def define_evaluations_by_corners(self, xc_normed, ret=False):
        """xc_normed should be the HD corner points in the [-1, 1] range"""

        xc = (xc_normed + 1) * (self.bounds[:, 1] - self.bounds[:, 0]) / 2 + self.bounds[:, 0]

        n_corners = xc.shape[0]  # number of corner points
        nsp = int(self.n_pts / n_corners)  # number of samples to take in each direction

        x = np.array([]).reshape(0, self.dataset.n_params)
        for corner in xc:
            norm = np.linalg.norm(corner)
            corner /= norm
            vals = np.linspace(0, norm, nsp + 1)
            vals = np.delete(vals, 0)  # deleting first value since it will be 0
            for val in vals:
                x = np.vstack((x, vectorize(corner * val).T))

        # adding dataset samples
        x = np.vstack((x, np.array(self.dataset.x)))
        if ret:
            return x
        else:
            self.x = x

    def evaluate_x(self):
        print('evaluating points')
        xpred = self.dataset.norm_x(pd.DataFrame(self.x, columns=self.dataset.x.columns))
        self.qoi = self.dataset.ret_qoi(self.network.predict(xpred))

    def compute_gradients(self):
        print('computing gradients')
        gcomp = GradientComputation(dataset=self.dataset, network=self.network, step=0.1)
        self.gradients = gcomp.central_diff(self.x)

    def normalise(self):
        # ADS requires inputs normalised in the range [-1,1]. So inputs, and gradients must be normalised
        self.x_normed = 2. * (self.x - self.bounds[:, 0]) / (self.bounds[:, 1] - self.bounds[:, 0]) - 1.0

        # Gradients were evaluated as df/dx. We need the gradients as df/dx_normed.
        # We need to multiply them by dx/dx_normed
        self.grad_normed = self.gradients * (self.bounds[:, 1] - self.bounds[:, 0]) / 2.0

    def compute(self, to_corners=False):

        self.define_evaluations_random()
        self.evaluate_x()
        self.compute_gradients()
        self.normalise()

        self.ss.compute(df=self.grad_normed, nboot=500)
        self.W1 = self.ss.eigenvecs[:, :self.n_dims]

        # corners
        if to_corners:
            print ('Calculating corner points')
            y, xc_normed = self.get_corners()
            self.define_evaluations_by_corners(xc_normed)
            print('Infilling corners')
            self.evaluate_x()
            print('Calcularing gradients')
            self.compute_gradients()
            self.normalise()

            self.ss.compute(df=self.grad_normed, nboot=500)
            self.W1 = self.ss.eigenvecs[:, :self.n_dims]

    def get_corners(self):
        """
        Computes the vertices of the zonotope

        Returns
        -------
        y : ndarray
            nzv-by-n matrix that contains the zonotope vertices
        x : ndarray
            nzv-by-m matrix that contains the corners of the m-dimensional hypercube
            that map to the zonotope vertices
        """
        print ('Calculating corners')
        y, x = ac.domains.zonotope_vertices(self.W1)
        return y, x

    def plot(self, key=None, **kwargs):

        ret = kwargs.get('ret')
        if ret is None:
            ret = False
        else:
            ret = ret

        if not os.path.exists(self.figures):
            os.mkdir(self.figures)

        fig, ax = plt.subplots()

        if key == 'eigs':
            ids = np.arange(1, self.dataset.n_params + 1, 1)
            ax.plot(ids, self.ss.eigenvals.flatten(), marker='o', linewidth=1.5, mfc='none')
            ax.set_yscale('log')
            ax.set_xlabel('ID')
            ax.set_ylabel('Eigenvalue ID')
            ax.set_title('C matrix Eigenvalue Decay')
        elif key == 'cumsum':
            limit = kwargs.get('limit')
            cumsum = np.array([np.sum(self.ss.eigenvals[:i + 1]) * 100 / np.sum(self.ss.eigenvals) for i in
                               range(self.dataset.n_params)])
            ids = np.arange(1, self.dataset.n_params + 1, 1)
            ax.plot(ids[:limit], cumsum[:limit], marker='o', linewidth=1.5, mfc='none')
            ax.set_xlabel('ID')
            ax.set_ylabel('Energy (%)')
            ax.set_title('C matrix Cumulative Energy')

        elif key == 'zonotope':
            show_boundary = kwargs.get('show_boundary')
            show_samples = kwargs.get('show_samples')
            interp = kwargs.get('interp')
            show_evaluations = kwargs.get('show_evaluations')
            levels = kwargs.get('levels')
            to_corners = kwargs.get('to_corners')
            add_points = kwargs.get('add_points')

            if show_boundary is None:
                show_boundary = False
            if show_samples is None:
                show_samples = False
            if show_evaluations is None:
                show_evaluations = False
            if to_corners is None:
                to_corners = False
            if interp is None:
                interp = 'linear'
            if levels is None:
                levels = 10

            # forcing matrix W1 to be the first 2 eigenvectors of C
            W1 = self.ss.eigenvecs[:, :2]

            if to_corners:
                y, xc_normed = ac.domains.zonotope_vertices(W1)
                x_eval = self.define_evaluations_by_corners(xc_normed, ret=True)
                x_eval_normed = self.dataset.norm_x(pd.DataFrame(x_eval, columns=self.dataset.x.columns))
                qoi = self.dataset.ret_qoi(self.network.predict(x_eval_normed))
                y = self.forward_map(x_eval)
            else:
                qoi = self.qoi
                y = self.x_normed.dot(W1)

            u1_i = np.linspace(min(y[:, 0]), max(y[:, 0]), 1500)
            u2_i = np.linspace(min(y[:, 1]), max(y[:, 1]), 1500)

            triang = tri.Triangulation(y[:, 0], y[:, 1])
            if interp == 'cubic':
                interpolator = tri.CubicTriInterpolator(triang, qoi)
            else:
                interpolator = tri.LinearTriInterpolator(triang, qoi)

            U1, U2 = np.meshgrid(u1_i, u2_i)
            QOI = interpolator(U1, U2)

            plt.contourf(U1, U2, QOI, levels)
            ax.set_xlabel('$\mathbf{U_{1}}$')
            ax.set_ylabel('$\mathbf{U_{2}}$')
            plt.colorbar()
            ax.set_title('%s along $\mathbf{U_{1}}$ and $\mathbf{U_{2}}$' % self.dataset.qoi_label)

            if show_boundary:
                y, x = ac.domains.zonotope_vertices(W1)
                u1_sorted, u2_sorted = self.sort_xy(y[:, 0], y[:, 1])
                u1_sorted = np.append(u1_sorted, u1_sorted[0])
                u2_sorted = np.append(u2_sorted, u2_sorted[0])
                ax.plot(u1_sorted, u2_sorted, c='k', lw=1, marker='*', markersize=5)

            if show_samples:
                if not show_evaluations:
                    y = self.forward_map(self.dataset.x)
                    ax.scatter(y[:, 0], y[:, 1], c=self.dataset.qoi.values, edgecolors='k')
            if show_evaluations:
                y = self.forward_map(self.x)
                ax.scatter(y[:, 0], y[:, 1], c=self.qoi, edgecolors='k')

            if add_points is not None:
                if 'points' not in add_points.keys():
                    print('cannot display added points. No points found')
                else:
                    show_points = True
                if 'marker' in add_points.keys() or 'm' in add_points.keys():
                    if 'marker' in add_points.keys():
                        marker = add_points['marker']
                    else:
                        marker = add_points['m']
                else:
                    marker = 's'
                if 'color' in add_points.keys() or 'c' in add_points.keys():
                    if 'color' in add_points.keys():
                        color = add_points['color']
                    else:
                        color = add_points['c']
                else:
                    color = 'r'

                if show_points:
                    points = add_points['points']
                    y = self.forward_map(points)
                    if len(y.shape) == 1:
                        ax.scatter(y[0], y[1], facecolors='none', edgecolors=color, marker=marker)
                    else:
                        ax.scatter(y[:, 0], y[:, 1], facecolors='none', edgecolors=color, marker=marker)

        elif key == 'contribution':

            fig, ax = plt.subplots(figsize=(8, 16))

            dp_names = kwargs.get('names')
            if dp_names is None:
                dp_names = list(self.dataset.x.columns)
            var = kwargs.get('var')
            if var is None:
                var = self.W1[:, 0]
            mode = kwargs.get('mode')
            if mode is None:
                mode = 'abs'
            if mode == 'abs':
                var = np.abs(var)
                idx = np.argsort(var)[::-1]
                label = 'Coefficient Magnitude'
            else:
                idx = np.argsort(var)
                label = 'Coefficient Value'

            sorted_names = np.array(dp_names)[idx]
            sorted_var = var[idx]
            ticks = np.arange(self.dataset.n_params)
            ax.barh(ticks, sorted_var, align='center', alpha=0.5)
            ax.set_yticks(ticks)
            ax.set_ylim([-1.5, self.dataset.n_params - 0.5])
            ax.set_yticklabels(sorted_names, fontsize=10)
            ax.set_xlabel(label)
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.tick_params(axis='y', direction='inout')
            ax.tick_params(axis='x', which='major', direction='inout')
            ax.tick_params(axis='x', which='minor', direction='in')
            # Hide the right and top spines
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

        if key == 'eigs' or key == 'cumsum':
            ax.grid(color='black', lw=0.25)
            ax.tick_params(direction='in', which='both')
            ax.xaxis.set_major_locator(MaxNLocator(8))
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.xaxis.set_ticks_position('both')
            ax.yaxis.set_ticks_position('both')

        if ret:
            return fig, ax
        else:	
            plt.savefig('%s/%s.png' % (self.figures, key))

    def sort_xy(self, x, y):
        x0 = np.mean(x)
        y0 = np.mean(y)
        r = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
        angles = np.where((y - y0) > 0, np.arccos((x - x0) / r), 2 * np.pi - np.arccos((x - x0) / r))
        mask = np.argsort(angles)
        x_sorted = x[mask]
        y_sorted = y[mask]
        return x_sorted, y_sorted

    def save_data(self, name='ADS'):
        w1 = pd.DataFrame(self.ss.eigenvecs[:, :self.n_dims], columns=['e%s' % a for a in range(1, self.n_dims + 1)])
        w1.to_csv('%s_W1.csv' % name, index=False)
        np.savetxt('%s_eigs.dat' % name, self.ss.eigenvals)

    def map_input_data(self, fout='ADS_dataset'):

        y = self.forward_map(self.dataset.x)
        # x_normed = 2. * (self.dataset.x - self.bounds[:, 0]) / (self.bounds[:, 1] - self.bounds[:, 0]) - 1.0
        # y = np.array(x_normed).dot(self.W1) # must be done with the normalised inputs in [-1,1] range, since ADS is based on this!
        df = pd.DataFrame(y, columns=['y%s' % i for i in range(1, self.n_dims + 1)])
        df[self.dataset.qoi_label] = self.dataset.qoi
        if '.csv' not in fout:
            fout += '.csv'
        df.to_csv(fout)

    def forward_map(self, x):
        """performs the forward map for x.
        First it normalises x in the [-1,1] range since ADS is based on this
        Then it computes the dot product"""

        x_normed = 2. * (x - self.bounds[:, 0]) / (self.bounds[:, 1] - self.bounds[:, 0]) - 1.0

        if len(x_normed.shape) == 1:
            # x is a 1d array
            if len(x_normed) != self.dataset.n_params:
                raise ValueError('Dimensionality of x not correct')
            else:
                y = self.W1.T.dot(x_normed)
        else:
            if x_normed.shape[1] != self.dataset.n_params:
                raise ValueError('Dimensionality of x not correct')
            else:
                y = np.array(x_normed).dot(self.W1)

        return y

    def save(self, fout='ADS'):
        self.network = None
        if '.ads' not in fout:
            fout += '.ads'
        with open(fout, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def load(fin='ADS.ads'):
        with open(fin, 'rb') as inps:
            return pickle.load(inps)
