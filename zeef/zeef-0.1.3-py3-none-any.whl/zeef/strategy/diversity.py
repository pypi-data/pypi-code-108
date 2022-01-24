"""
    Diversity based sampling methods.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 05/01/2022
"""
from .base import Strategy
from ..util import flatten_data

# tests
import torch


class CoreSet(Strategy):
    """
    CoreSet Sampling Method.
    TODO: Complete Feature
    """

    def __init__(self, dataset, learner, embedding_func=None):
        super(CoreSet, self).__init__(dataset, learner)
        if embedding_func:
            self.embedding_func = embedding_func
        else:
            self.embedding_func = flatten_data

        # tests
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def query(self, n):
        self.check_query_availability(n)
        unlabeled_data = self.data_host.get_unlabeled_data()
        labeled_data, _ = self.data_host.get_labeled_data()
        unlabeled_ids = self.data_host.get_unlabeled_ids()

        unlabeled_embeddings = self.embedding_func(unlabeled_data).to(self.device)
        labeled_embeddings = self.embedding_func(labeled_data).to(self.device)

        m = unlabeled_embeddings.shape[0]
        if labeled_embeddings.shape[0] == 0:
            min_dist = torch.tile(float("inf"), m)
        else:
            dist_ctr = torch.cdist(unlabeled_embeddings, labeled_embeddings, p=2)
            min_dist = torch.min(dist_ctr, dim=1)[0]

        idxs = []

        for i in range(n):
            idx = torch.argmax(min_dist)
            idxs.append(idx.item())
            dist_new_ctr = torch.cdist(unlabeled_embeddings, unlabeled_embeddings[[idx], :])
            min_dist = torch.minimum(min_dist, dist_new_ctr[:, 0])

        return idxs


class KMeansDiverse(Strategy):
    """
    KMeans Diverse Batch Sampling Method.
    TODO: Complete Feature
    """

    def __init__(self, dataset, learner):
        super(KMeansDiverse, self).__init__(dataset, learner)

    def query(self, n):
        self.check_query_availability(n)
        return []
