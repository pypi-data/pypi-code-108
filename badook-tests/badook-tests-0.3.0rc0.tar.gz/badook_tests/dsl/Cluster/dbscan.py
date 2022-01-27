from __future__ import annotations
from badook_tests.dsl.summary import Summary
from badook_tests.dsl.checks import Calculation


class DBSCAN(Summary):
    """
    DBSCAN Clustering: https://en.wikipedia.org/wiki/DBSCAN
    """

    def __init__(self, features: list, name: str, eps=0.5, min_samples=5, metric='euclidean',
                 metric_params=None, algorithm='auto', leaf_size=30, p=None, n_jobs=None):
        super().__init__(features, name)
        self.method = 'dbscan'
        self.type = 'Cluster'
        self.params = {'eps': eps, 'min_samples': min_samples, 'metric': metric,
                       'metric_params': metric_params, 'algorithm': algorithm,
                       'leaf_size': leaf_size, 'p': p, 'n_jobs': n_jobs}

    @property
    def clusters_count(self):
        return Calculation(self.data, 'clusters_count', self._ctx)

    @property
    def noise_count(self):
        return Calculation(self.data, 'noise_count', self._ctx)

    @property
    def silhouette_score(self):
        return Calculation(self.data, 'silhouette_score', self._ctx)

    @property
    def clusters(self):
        return Clusters(self.data, 'cluster', self._ctx)


class Clusters(Summary):
    """
    A subclass to hold the output of the clusters
    """

    def __init__(self, data, name, _ctx):
        self.data = data
        self.name = name
        self._ctx = _ctx

    @property
    def member_count(self):
        return Calculation(self.data, self.name + '_member_count', self._ctx)

    @property
    def core_count(self):
        return Calculation(self.data, self.name + '_membcore_counter_count', self._ctx)

    @property
    def border_count(self):
        return Calculation(self.data, self.name + '_border_count', self._ctx)
