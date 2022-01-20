import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from . import utilities as utl
from . import nmfmodel as nmf
from . import ntfmodel as ntf


class Clusterizer:

    def __init__(self,
                 method: str,
                 **kwargs):

        """

          Clusterizer.__init__:

          Parameters
          ----------

          method: a string in
          {
          "set_groups",     # user-defined clustering
          "kmeans",         # applies kmeans (given #groups) to the provided datafame
          "nmf.kmeans",     # applies kmeans to the W matrix from NMF factorization (given #components)
          "nmf.leverage",   # uses leverage-based clustering to the W matrix from NMF factorization (given #components)
          "snmf.kmeans",    # applies kmeans to the W matrix from SNMF factorization (given #components)
          "snmf.leverage"   # uses leverage-based clustering to the W matrix from SNMF factorization (given #components)
          }

          :returns:
          self
          """

        assert method in {"set_groups", "kmeans", "nmf.kmeans", "nmf.leverage", "snmf.kmeans", "snmf.leverage"}
        self._method = method
        self._kwargs = kwargs
        pass

    def __repr__(self):
        name = self._kwargs.get("name", "")
        kwargs = self._kwargs if name == "" else name
        return f"Clust_{self._method}_{kwargs}"

    def get_nbgroups(self):
        return self._kwargs.get("nb_groups", 2)

    def get_nbgroups(self):
        return int(self._kwargs.get("nb_groups", 2))

    def set_nbgroups(self, ng):
        self._kwargs.update(ng, "nb_groups")

    def apply(self,
              mat):
        """
          Clusterizer.apply
          Applies the object's method and parameters to a given matrix

          Parameters
          ----------
          mat: A data matrix

          :returns:
          a one-column dataframe with cluster attributions
        """
        kwargs = self._kwargs
        mat = pd.DataFrame(mat)
        method = self._method.lower()
        ngroups = kwargs.get("nb_groups", 2)
        groups = kwargs.get("groups", None)
        ncomp = kwargs.get("ncomp", ngroups)
        name = kwargs.get("name", "Cl_")
        if method == "set_groups":
            pd.testing.assert_index_equal(groups.index, mat.index)
            res = groups
        elif method == "kmeans":
            km = KMeans(n_clusters=ngroups)
            res = km.fit_predict(mat)
        elif method == "nmf.leverage":
            model = nmf.NmfModel(mat=mat, name=name, ncomp=ngroups,
                                 regularization="components", leverage="robust", max_iter=200)
            res = model.get_obs_leverage_clusters()
        elif method == "nmf.kmeans":
            model = nmf.NmfModel(mat=mat, name=name, ncomp=ncomp,
                                 regularization="components", leverage="robust", max_iter=200)
            res = model.get_obs_kmeans_clusters(ngroups=ngroups)
        elif method == "snmf.leverage":
            model = ntf.NtfModel(mat=mat, name=name, ncomp=ngroups, nblocks=2,
                                 regularization="components", leverage="robust", max_iter=200)
            res = model.get_obs_leverage_clusters()
        elif method == "snmf.kmeans":
            model = ntf.NtfModel(mat=mat, name=name, ncomp=ngroups, nblocks=2,
                                 regularization="components", leverage="robust", max_iter=200)
            res = model.get_obs_kmeans_clusters()
        else:
            res = None

        return None if res is None else pd.DataFrame(res)


def clusterizer_metrics(clst: Clusterizer, mat, ng):
    if clst is None:
        return None
    else:
        clst.set_nbgroups(ng)
        clusters = clst.apply(mat)
        return utl.clustering_caha_score(mat, clusters)


def clusterizer_optimize(clst: Clusterizer, mat, ngmin=2, ngmax=20):
    # Détermine le nb de composants optimal pour une clusterisation
    ngmax = max(ngmin, ngmax)
    df_metrics = pd.DataFrame(index=range(ngmin, ngmax+1), columns=["Score"])
    if clst is None:
        return None
    else:
        for ng in df_metrics.index:
            df_metrics.loc[ng, "Score"] = clusterizer_metrics(clst, mat, ng)
    score_opt = np.argmax(df_metrics["Score"])
    return score_opt, df_metrics
