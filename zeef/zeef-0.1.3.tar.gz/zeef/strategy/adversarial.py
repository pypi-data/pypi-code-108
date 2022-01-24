"""
    Adversarial based sampling methods.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 28/12/2021
"""

from .base import Strategy


class AdversarialBIM(Strategy):
    """
    Adversarial Margin Sampling Method.
    Reference:
    @article{ducoffe2018adversarial,
          title={Adversarial active learning for deep networks: a margin based approach},
          author={Ducoffe, Melanie and Precioso, Frederic},
          journal={arXiv preprint arXiv:1802.09841},
          year={2018}
        }
    """

    def __init__(self, dataset, learner):
        super(AdversarialBIM, self).__init__(dataset, learner)

    def get_distance(self, x):
        return []

    def query(self, n):
        self.check_query_availability(n)
        unlabeled_data = self.data_host.get_unlabeled_data()
        unlabeled_ids = self.data_host.get_unlabeled_ids()
        return []


class AdversarialDFAL(Strategy):
    """
    DeepFool Active Learning (DFAL) Method.
    """

    def __init__(self, dataset, learner):
        super(AdversarialDFAL, self).__init__(dataset, learner)

    def get_distance(self, x):
        return []

    def query(self, n):
        self.check_query_availability(n)
        unlabeled_data = self.data_host.get_unlabeled_data()
        unlabeled_ids = self.data_host.get_unlabeled_ids()
        return []
