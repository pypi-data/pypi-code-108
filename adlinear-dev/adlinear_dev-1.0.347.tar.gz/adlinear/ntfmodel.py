from .nmfmodel import NmfModel
from nmtf import NTF
from . import utilities as utl
import pandas as pd
import numpy as np


class NtfModel(NmfModel):
    def __init__(
        self,
        mat,
        ncomp,
        baseline=None,
        unfolded=True,
        nblocks=1,
        name="",
        use_hals=True,
        beta_loss="frobenius",
        leverage="standard",
        kernel="linear",
        regularization=None,
        tol=1e-6,
        max_iter=150,
        max_iter_mult=20,
        features_names=None,
        object_names=None,
    ):

        super().__init__(
            mat,
            ncomp=ncomp,
            name=name,
            use_hals=use_hals,
            beta_loss=beta_loss,
            leverage=leverage,
            kernel=kernel,
            tol=tol,
            max_iter=max_iter,
            max_iter_mult=max_iter_mult,
            regularization=regularization,
            features_names=None,
            object_names=None,
        )
        if object_names is None:
            object_names = []
        if features_names is None:
            features_names = []
        self._ncomp = ncomp
        self._baseline = baseline
        self._unfolded = unfolded
        self._hals = use_hals
        self._leverage = leverage
        self._nblocks = nblocks
        self._sparsity = 0
        # La matrice d'origine (n,c) remplie avec les moyennes
        self._origin_mat = None
        # La matrice (n, c)
        self._filledmat = None
        # la matrice [(n,c)(n,c)] <=> (2n, c) remplie par les moyennes par clusters
        self._unfolded_filledmat = None
        self._unfolded_unfilledmat = None

        if not unfolded:
            # cas d'une matrice "normale", non dépliée
            if nblocks == 2:
                # la matrice d'origine avant dépliage/duplication
                self._origin_mat = utl.fill_missing(mat, method="Median")
                self._unfolded_filledmat, self._baseline = utl.separate_along_median_by_cols(self._origin_mat)
                self._unfolded_unfilledmat, self._baseline = utl.separate_along_median_by_cols(mat)
            else:
                pass
        else:
            # cas où on a passé la matrice déjà dépliée avec sa baseline
            if nblocks == 2:
                self._origin_mat = utl.rebuild_median_separated_matrix(duplicated_mat=mat, med=baseline)
                self._unfolded_unfilledmat = mat

        if type(mat) is pd.DataFrame:
            self._objnames = list(mat.index)
            self._mat = mat
            self._nobj, self._nfeat = mat.shape
            self._nblocks = nblocks
            if self._unfolded:
                self._nfeat = int(self._nfeat / self._nblocks)
        else:
            # data provided as simple array
            self._nobj, self._nfeat = pd.DataFrame(mat).shape
            if self._unfolded:
                self._nfeat = int(self._nfeat / self._nblocks)
            self._fnames = (
                features_names
                if len(features_names) == self._nfeat
                else list(["F" + str(x) for x in range(1, self._nfeat + 1)])
            )
            self._objnames = (
                object_names
                if len(object_names) == self._nobj
                else list(["O" + str(x) for x in range(1, self._nobj + 1)])
            )
            self._mat = pd.DataFrame(mat, index=self._objnames, columns=self._fnames)

        self._filledmat = self._mat.copy()

        if self._nblocks == 2 and unfolded:
            # reconstituer les features d'origine
            # qui ont été fournies en double avec les suffixes + et -
            nf = int(len(mat.columns) / 2)
            self._fnames = self._fnames[0:nf]
            self._fnames = list([x.split("_+")[0] for x in self._fnames])
        if name == "":
            self._name = "NTF_" + str(self._ncomp) + "(O" + str(self._nobj) + ",F" + str(self._nfeat) + ")"
        else:
            self._name = name

        self._sortedmat = self._filledmat.copy()
        self._model = NTF(n_components=ncomp, fast_hals=use_hals, tol=self._tol, leverage=self._leverage)
        self._estimator = None
        self._predictor = None
        self._error = None
        self._volume = None

    def clone(self):
        model = NtfModel(
            mat=self._mat,
            ncomp=self._ncomp,
            name=self._name,
            use_hals=self._hals,
            beta_loss=self._beta_loss,
            leverage=self._leverage,
            kernel=self._kernel,
            baseline=self._baseline,
            unfolded=self._unfolded,
            nblocks=self._nblocks,
            tol=self._tol,
            max_iter=self._max_iter,
            max_iter_mult=self._max_iter_mult,
            regularization=self._regularization,
            features_names=self._fnames,
            object_names=self._objnames,
        )
        model.set_sparsity(self._sparsity)
        model.set_n_bootstrap(self._n_bootstrap)
        return model

    def set_ncomp(self, ncomp):
        self.__init__(
            mat=self._mat,
            ncomp=ncomp,
            name=self._name,
            use_hals=self._hals,
            beta_loss=self._beta_loss,
            leverage=self._leverage,
            kernel=self._kernel,
            baseline=self._baseline,
            unfolded=self._unfolded,
            nblocks=self._nblocks,
            tol=self._tol,
            max_iter=self._max_iter,
            max_iter_mult=self._max_iter_mult,
            regularization=self._regularization,
            features_names=self._fnames,
            object_names=self._objnames
        )
        if hasattr(self, "_estimator"):
            delattr(self, "_estimator")
        if hasattr(self, "_estimator"):
            delattr(self, "_predictor")

    @property
    def origin_mat(self):
        return self._origin_mat

    # def get_h_compression(self):
    #     if not self.is_ok():
    #         self.test_model()
    #     if "H" in self._estimator:
    #         h = self.get_h()
    #         feat_hhi = [hhi(h[col]) for col in h.columns]
    #         return float(self._ncomp) / self._nfeat * (1 + np.mean(feat_hhi) / self._nobj)
    #     else:
    #         return 0.0

    def get_precision(self, relative=True):
        if not self.is_ok():
            self.test_model()
        m_proxy = self.get_m_proxy()
        m_delta = self._origin_mat - m_proxy
        return utl.mean_square(m_delta) / utl.mean_square(self._origin_mat)

    def test_model(self, nfill_iters=1, verbose=True):

        nfill_iters = max(1, nfill_iters)
        for itrial in range(nfill_iters):
            if itrial == 0:
                self._filledmat = utl.fill_missing(self._unfolded_unfilledmat, method="median")
            else:
                w = self.get_w()
                h = self.get_h()
                self._filledmat = utl.fill_missing(self._unfolded_unfilledmat, method=None, fill_values=w @ h.T)
            self._estimator = self._model.fit_transform(
                self._filledmat.astype(float).values,
                n_blocks=self._nblocks,
                n_bootstrap=self._n_bootstrap,
                regularization=self._regularization,
                sparsity=self._sparsity,
            )
            self._predictor = self._model.predict(self._estimator)
            if verbose:
                print("Error: {0:.0f}%".format(self._estimator["diff"]))
        self._error = self.get_precision()
        self._volume = self._estimator["volume"]

    def get_h(self):
        if not self.is_ok():
            self.test_model()
        hmat = pd.DataFrame(
            index=self._fnames,
            columns=list(["V" + str(x) for x in range(1, self._ncomp + 1)]),
            data=self._predictor["H"],
        )
        return hmat

    def get_f(self):
        if not self.is_ok():
            self.test_model()
        fmat = pd.DataFrame(
            index=list(range(self._nblocks)),
            columns=list(["V" + str(x) for x in range(1, self._ncomp + 1)]),
            data=self._estimator["Q"],
        )
        return fmat

    def get_m_proxy(self):
        w = self.get_w()
        h = self.get_h()
        f = self.get_f()
        if self._nblocks == 2:  # and self._unfolded:
            f_plus = f.iloc[[0]]
            f_minus = f.iloc[[1]]
            f = pd.DataFrame(index=[0], data=f_plus.values - f_minus.values, columns=f.columns)
        hd = h * f.values
        whd = w @ hd.T
        whd += self._baseline.to_numpy()
        whd.index = self._origin_mat.index
        whd.columns = self._origin_mat.columns
        return whd

    def sort_features_by_cluster(self):
        feat_clust = pd.DataFrame(columns=self._fnames, index=[1000000])
        if not self.is_ok():
            self.test_model()
        for ic, col in enumerate(feat_clust.columns):
            feat_clust.loc[:, col] = self._predictor["HC"][ic]
        nf = int(self._nfeat)
        if self._nblocks == 2:
            pos_mat = pd.DataFrame(data=self._mat.iloc[:, 0:nf].values, columns=self._fnames, index=self._objnames)
            pos_mat_w_clust = pd.concat([pos_mat, feat_clust])
            pos_mat_w_clust = pos_mat_w_clust.sort_values(by=1000000, axis=1)

            neg_mat = pd.DataFrame(
                data=self._mat.iloc[:, nf: 2 * nf].values, columns=self._fnames, index=self._objnames
            )
            neg_mat_w_clust = pd.concat([neg_mat, feat_clust])
            neg_mat_w_clust = neg_mat_w_clust.loc[:, pos_mat_w_clust.columns]

            baseline = pd.DataFrame(index=pos_mat_w_clust.columns, data=self._baseline.loc[pos_mat_w_clust.columns]).T

            self._sortedmat = pos_mat_w_clust - neg_mat_w_clust
            self._sortedmat = self._sortedmat.add(baseline.values, axis="columns").drop(1000000, axis=0)
        return self
