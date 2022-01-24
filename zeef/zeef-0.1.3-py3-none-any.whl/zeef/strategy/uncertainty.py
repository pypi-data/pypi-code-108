"""
    Uncertainty based sampling methods.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 08/12/2021
"""
import numpy as np
from .base import Strategy


class LeastConfidence(Strategy):
    """
    Least Confidence Sampling.
    Reference: A Sequential Algorithm for Training Text Classifiers (1994).
    (https://arxiv.org/pdf/cmp-lg/9407020)
    """

    def __init__(self, data_host, learner, dropout=1):
        super(LeastConfidence, self).__init__(data_host, learner)
        self.dropout = dropout

    def query(self, n):
        self.check_query_availability(n)
        unlabeled_data = self.data_host.get_unlabeled_data()
        unlabeled_ids = self.data_host.get_unlabeled_ids()
        probs = self.infer(unlabeled_data, is_prob=True, n_drop=self.dropout)
        uncertainties = np.amax(probs, axis=1)
        return unlabeled_ids[uncertainties.argsort()[:n]]


class MarginConfidence(Strategy):
    """
    Margin of Confidence sampling
    Reference: Active Hidden Markov Models for Information Extraction (2001).
    (https://link.springer.com/chapter/10.1007/3-540-44816-0_31)
    """

    def __init__(self, data_host, learner, dropout=1):
        super(MarginConfidence, self).__init__(data_host, learner)
        self.dropout = dropout

    def query(self, n):
        self.check_query_availability(n)
        unlabeled_data = self.data_host.get_unlabeled_data()
        unlabeled_ids = self.data_host.get_unlabeled_ids()
        probs = self.infer(unlabeled_data, is_prob=True, n_drop=self.dropout)
        probs_sorted = -np.sort(-probs)
        difference_list = probs_sorted[:, 0] - probs_sorted[:, 1]
        return unlabeled_ids[difference_list.argsort()[:n]]


class RatioConfidence(Strategy):
    """
    Ratio of Confidence sampling
    Reference: Active learning literature survey. (https://minds.wisconsin.edu/handle/1793/60660)
    """

    def __init__(self, data_host, learner, dropout=1):
        super(RatioConfidence, self).__init__(data_host, learner)
        self.dropout = dropout

    def query(self, n):
        self.check_query_availability(n)
        unlabeled_data = self.data_host.get_unlabeled_data()
        unlabeled_ids = self.data_host.get_unlabeled_ids()
        probs = self.infer(unlabeled_data, is_prob=True, n_drop=self.dropout)
        probs_sorted = -np.sort(-probs)
        difference_list = probs_sorted[:, 0] / probs_sorted[:, 1]
        return unlabeled_ids[difference_list.argsort()[:n]]


class EntropySampling(Strategy):
    """
    Entropy Sampling.
    Reference: Active learning literature survey. (https://minds.wisconsin.edu/handle/1793/60660)
    """

    def __init__(self, data_host, learner, dropout=1):
        super(EntropySampling, self).__init__(data_host, learner)
        self.dropout = dropout

    def query(self, n):
        self.check_query_availability(n)
        unlabeled_data = self.data_host.get_unlabeled_data()
        unlabeled_ids = self.data_host.get_unlabeled_ids()
        predictions = self.infer(unlabeled_data, is_prob=True, n_drop=self.dropout)
        entropy = (predictions * np.log(predictions)).sum(1)
        return unlabeled_ids[entropy.argsort()[:n]]
