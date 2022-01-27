import random
from sklearn.decomposition import PCA
from copy import copy
import pandas as pd
import numpy as np
from .utilities import hhi_1
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

import root_path


class PcaModel:

    def __init__(self,
                 mat,
                 ncomp: int,
                 name: str = '',
                 features_names=None,
                 object_names=None):
        """'
        Creates a PCA model

        Parameters
        ----------

        Return
        -------

        """

        if features_names is None:
            features_names = []
        if object_names is None:
            object_names = []
        self._ncomp: int = ncomp
        if hasattr(mat, 'values'):
            self._mat = mat.values
            self._nobj, self._nfeat = mat.values.shape
        else:
            self._mat = mat
            self._nobj, self._nfeat = mat.shape
        if hasattr(mat, 'columns'):
            self._fnames = list(mat.columns)
        else:
            self._fnames = features_names
        if hasattr(mat, 'index'):
            self._objnames = list(mat.index)
        else:
            self._objnames = object_names
        if name == '':
            self._name = 'PCA_' + str(self._ncomp) + \
                         '(O' + str(self._nobj) + \
                         ',F' + str(self._nfeat) + ')'
        else:
            self._name = name

        self._model = PCA(n_components=ncomp)
        self._estimator = None
        self._feature_clusters = None

    def is_ok(self):
        return hasattr(self._model, 'explained_variance_ratio_')

    def set_ncomp(self, ncomp):
        self.__init__(self._mat,
                      ncomp,
                      self._name)

    def test_model(self):
        self._model.fit(self._mat)
        self._estimator = self._model

    def get_sub_model(self, nb_excluded_obs=0.1):
        if type(nb_excluded_obs) is float:
            nb_excluded_obs = int(nb_excluded_obs * self._nobj)
        if nb_excluded_obs == 0:
            return copy(self)
        else:
            excl_obs = random.sample(list(range(self._nobj)), nb_excluded_obs)
            subindex = list(set(range(self._nobj)).difference(set(excl_obs)))
            submat = pd.DataFrame(self._mat).iloc[subindex]
            sub_model = PcaModel(submat, self._ncomp)
            return sub_model

    def get_feature_observations(self, col):
        if type(col) is int:
            return self._mat[col]
        else:
            return None

    def get_principal_component(self, icomp):
        if not self.is_ok():
            self.test_model()
        return self._model.components_[icomp]

    def get_proj_coeff(self, icol):
        if not self.is_ok():
            self.test_model()
        col = self.get_feature_observations(icol)
        coeffs = [np.dot(col, self.get_principal_component(icomp))
                  for icomp in range(self._ncomp)]
        return coeffs

    def get_feature_clusters(self):
        if not self.is_ok():
            self.test_model()
        self._feature_clusters = np.zeros(self._nfeat)
        for icol in range(self._nfeat):
            coeffs = self.get_proj_coeff(icol)
            imax = np.argmax(coeffs)
            self._feature_clusters[icol] = imax
            return self._feature_clusters

    def get_explained_variance_ratio(self):
        if not self.is_ok():
            self.test_model()
        return self._model.explained_variance_ratio_

    def get_explained_variance(self):
        if not self.is_ok():
            self.test_model()
        return self._model.explained_variance_

    def get_residual_variance(self):
        if not self.is_ok():
            self.test_model()
        total_var = pd.DataFrame(self._mat).var().sum()
        expl_var = self._model.explained_variance_.sum()
        return 1.0 - expl_var / total_var

    @staticmethod
    def get_stability():
        return 0.0

    @staticmethod
    def get_specific_cluster_contribution():
        return 0.0

    def get_precision(self):
        return self.get_residual_variance()

    def get_sparsity(self):
        if not self.is_ok():
            self.test_model()
            h = self._model.components_
            feat_hhi = [hhi_1(h[col]) for col in h.columns]
            return np.mean(feat_hhi) / self._ncomp
        else:
            return 0.0

    def get_dimension_score(self):
        if not self.is_ok():
            self.test_model()
        return self._ncomp / self._nfeat

    def get_ncomp(self):
        return self._ncomp

    def get_parsimony(self):
        return 0.5 * self.get_sparsity() + 0.5 * self.get_dimension_score()

    def get_interpretability(self):

        st = self.get_stability()
        pr = self.get_precision()
        pa = self.get_parsimony()
        return (st + pr + pa) / 3

    def get_score(self, x):
        if not self.is_ok():
            self.test_model()
        return self._model.score(x)

    def plot_cumulative_variance(self, path=None):
        '''
        Calcule et affiche le% de variance cumulative expliquée des facteurs
        :param path:
        :return:
        '''
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        expl_var = self.get_explained_variance_ratio().cumsum()
        ax.plot(expl_var * 100)
        ax.set_ylabel('Explained variance')
        xlabel = 'Components'
        ax.set_xlabel(xlabel)
        ax.set_title('Cumulative explained variance')
        ax.legend()
        if path is not None:
            plt.gcf().savefig(path)
        plt.show()

    def plot_components(self, listcomp=None, path=None):
        '''
        :param listcomp: list of components index
        :param path:
        :return:
        '''
        if listcomp is None:
            ncomp = self.get_ncomp()
            listcomp = range(ncomp)
        else:
            ncomp = len(listcomp)

        sz = len(self._model.components_[ncomp])
        cols = list(['C' + str(x) for x in range(ncomp)])
        df_spca = pd.DataFrame(index=list(range(sz)),
                               columns=cols)

        for icomp in listcomp:
            pca = pd.DataFrame(self._model.components_[icomp])
            spca = pd.DataFrame(index=list(range(sz)),
                                data=pca.sort_values(by=0, ascending=False).values)
            df_spca['C' + str(icomp)] = spca

        xa = df_spca.index

        fig, ax = plt.subplots(figsize=(8, 4))
        # ax.yaxis.set_major_locator(mtick.MultipleLocator(1.00))
        ax.yaxis.set_minor_locator(mtick.MultipleLocator(25))
        # ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_ylabel('Coefficient')
        xlabel = 'Components'

        xa = df_spca.index
        ax.plot(xa, df_spca['C0'] * 100, color='blue', linewidth=4, linestyle='-', label='C0')

        for icol in range(1, ncomp):
            ax.plot(xa, df_spca[df_spca.columns[icol]] * 100,
                    color='#4b0082', linewidth=2,
                    linestyle=':',
                    label='C' + str(icol))

        # ax.plot(df_spca*100)
        ax.set_xlabel(xlabel)
        ax.set_title('Sorted coefficients of first principal vectors')
        ax.legend()

        if path is not None:
            plt.gcf().savefig(path)
        plt.show()


def test_pca(mat, nc_pca, pictures_path, do_center=True):
    cmat = mat if not do_center else mat - mat.apply(np.nanmean, axis=0)
    mat_pca = PcaModel(cmat, nc_pca)
    mat_pca.plot_cumulative_variance(pictures_path / "cumulative_pca_variance.pdf")
    mat_pca.plot_components(listcomp=range(5), path=pictures_path / "cumulative_pca_variance.pdf")
