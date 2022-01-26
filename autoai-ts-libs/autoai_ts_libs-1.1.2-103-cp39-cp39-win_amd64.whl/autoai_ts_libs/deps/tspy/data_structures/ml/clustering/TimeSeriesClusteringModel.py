#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

import abc

from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries


class TimeSeriesClusteringModel:
    __metaclass__ = abc.ABCMeta

    def __init__(self, tsc, j_model):
        self._tsc = tsc
        self._j_model = j_model
        _centroids = {}
        c = 0
        for j_centroid in self._j_model.centroids():
            _centroids[str(c)] = BoundTimeSeries(self._tsc, j_centroid)
            c = c + 1
        self._centroids = _centroids

    def score(self, observations, with_silhouette=False):
        """
        returns the scores of given observations

        """
        if with_silhouette is not True:
            return self._j_model.score(observations._j_observations)
        else:
            pair = self._j_model.scoreWithSilhouette(observations._j_observations)
            return pair.left(), pair.right()

    @property
    def intra_cluster_distances(self):
        return self._j_model.intraClusterDistances()

    @property
    def inter_cluster_distances(self):
        return self._j_model.interClusterDistances()

    @property
    def centroids(self):
        return self._centroids

    @property
    def silhouette_coefficients(self):
        return self._j_model.silhouetteCoefficients()

    @property
    def sum_squares(self):
        return self._j_model.sumSquares()

    @abc.abstractmethod
    def save(self, path):
        """Save this model"""
        return




