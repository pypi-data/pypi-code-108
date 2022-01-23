"""
This file implements the Relief variants in Python
and calls the c++ libraries.
"""

import numpy as np
from enum import Enum

from . import _c_relief as _c_r
from .utils import Metric, _validate_metric


class Variant(Enum):
    RELIEF = 0
    RELIEFK = 1
    RELIEFF = 2


class ReliefBase:
    """
    The base relief class.
    """

    def __init__(
            self, n_iter, n_neighbors=5, n_jobs=4, metric=Metric.EUCLIDEAN):
        """
        Parameters
        __________

        n_iter: int
            Number of iterations (samples) to run for
        n_jobs: int
            Number of threads
        n_neighbors: int
            Number of samples that determine a neighborhood
        metric: enum, int
            Metric to use for computing distances
        """
        self._n_iter = int(n_iter)
        self._n_neighbors = int(n_neighbors)
        self._n_jobs = int(n_jobs)
        self._metric = metric
        self._metric_value = _validate_metric(metric)

        self._relief = None

    def __repr__(self):
        return f"ReliefBase({self.n_iter}, {self.n_neighbors}, {self.n_jobs}, {self.metric})"

    def __str__(self):
        return f"ReliefBase({self.n_iter}, {self.n_neighbors}, {self.n_jobs}, {self.metric})"

    @property
    def n_iter(self):
        return self._n_iter

    @property
    def n_neighbors(self):
        return self._n_neighbors

    @property
    def n_jobs(self):
        return self._n_jobs

    @property
    def metric(self):
        return self.metric

    def fit(self, X, y):
        """
        Parameters
        __________

        X: np.ndarray, shape (n_samples, n_features)
        y: np.ndarray, shape (n_samples,)
        """
        X = np.array(X)
        y = np.array(y)
        return _c_r._Relief_fit(self._relief, X, y)

    def transform(self, X):
        """
        Parameters
        __________

        X: np.ndarray, shape (n_samples, n_features)

        Returns
        _______

        np.ndarray, shape (n_samples, n_features)
            The data matrix X with its features reordered so that
            the first feature has the highest score, and so on.
        """
        X = np.array(X)
        return _c_r._Relief_transform(self._relief, X)

    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)

    @property
    def scores(self):
        return _c_r._Relief_get_scores(self._relief)


class Relief(ReliefBase):
    """
    The vanilla Relief algorithm.

    For every iteration, it picks a random sample (without replacement)
    and finds its `n_neighbors` nearest hits and `n_neighbors` nearest misses
    as measured by `metric`. For each class, a neighbor is randomly picked
    and is used to update the scores for every weight.
    The diff function is weight(x, nh) = (x - nh)**2 and the scores are
    updated as scores[w] = scores[w] - weight(x, nh) + weight(x, nm)
    where nh = near hit and nm = near miss.

    If the labels are not binary, then the nearest miss is computed as
    the nearest point belonging to any other class.
    """

    def __init__(
            self, n_iter, n_neighbors=5, n_jobs=4, metric=Metric.EUCLIDEAN):
        super().__init__(n_iter, n_neighbors, n_jobs, metric)
        self._relief = _c_r._new_Relief(
            n_iter, n_jobs, n_neighbors, self._metric_value,
            Variant.RELIEF.value)


class ReliefK(ReliefBase):
    """
    The vanilla Relief algorithm where instead of picking a random
    point from the neighbors, it averages the updates for every point
    in the neighborhood.
    """

    def __init__(
            self, n_iter, n_neighbors=5, n_jobs=4, metric=Metric.EUCLIDEAN):
        super().__init__(n_iter, n_neighbors, n_jobs, metric)
        self._relief = _c_r._new_Relief(
            n_iter, n_jobs, n_neighbors, self._metric_value,
            Variant.RELIEFK.value)


class ReliefF(ReliefBase):
    """
    The ReliefF algorithm.

    For multiclass problems. Given a sample point, find its nearest
    neighbor for every class and averages the update weights.
    The updates are weighted according to the prior probabilities
    of each class.
    """

    def __init__(
            self, n_iter, n_jobs=4, metric=Metric.EUCLIDEAN):
        super().__init__(n_iter, 0, n_jobs, metric)
        self._relief = _c_r._new_Relief(
            n_iter, n_jobs, 0, self._metric_value,
            Variant.RELIEFF.value)
