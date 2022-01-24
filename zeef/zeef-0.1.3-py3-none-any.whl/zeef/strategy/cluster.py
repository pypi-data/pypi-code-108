"""
    Cluster based sampling methods.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 08/12/2021
"""

import numpy as np
from sklearn.cluster import KMeans

from .base import Strategy


class KMeansSampling(Strategy):
    """
    KMeans Cluster Sampling Method.
    """

    def __init__(self, dataset, learner):
        """
        @param dataset: the input dataset.
        @param learner: the learning agent (oracle).
        """
        super(KMeansSampling, self).__init__(dataset, learner)

    def query(self, n):
        self.check_query_availability(n)
        features = self.data_host.get_unlabeled_data(transformed=True)
        unlabeled_ids = self.data_host.get_unlabeled_ids()
        kmeans = KMeans(n_clusters=n)
        kmeans.fit(features)
        distance = kmeans.transform(features)
        query_ids = np.argmin(distance, axis=0)
        return unlabeled_ids[query_ids]


class KCenterGreedy(Strategy):
    """
    KCenter Greedy Sampling Method.
    """

    def __init__(self, dataset, learner):
        """
        @param dataset: the input dataset.
        @param learner: the learning agent (oracle).
        """
        super(KCenterGreedy, self).__init__(dataset, learner)

    def query(self, n):
        labeled_masks = np.zeros(self.data_host.get_size(), dtype=bool)
        labeled_masks[np.array(list(self.data_host.get_labeled_ids()))] = True
        labeled_ids = labeled_masks.copy()
        features = np.array(self.data_host.get_transform_data())
        dist_mat = np.matmul(features, features.transpose())
        sq = np.array(dist_mat.diagonal()).reshape(self.data_host.get_size(), 1)
        dist_mat *= -2
        dist_mat += sq
        dist_mat += sq.transpose()
        dist_mat = np.sqrt(dist_mat)
        mat = dist_mat[~labeled_masks, :][:, labeled_masks]

        for i in range(n):
            mat_min = np.min(mat, axis=1)
            q_idx_ = mat_min.argmax()
            q_idx = np.arange(self.data_host.get_size())[~labeled_masks][q_idx_]
            labeled_masks[q_idx] = True
            mat = np.delete(mat, q_idx_, 0)
            mat = np.append(mat, dist_mat[~labeled_masks, q_idx][:, None], axis=1)

        return np.arange(self.data_host.get_size())[(labeled_ids ^ labeled_masks)]
