"""
    Random sampling methods.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 06/12/2021
"""

import numpy as np
from .base import Strategy


class RandomSampling(Strategy):
    """
    Randomly Selected the query samples.
    """

    def __init__(self, data_host, learner):
        super(RandomSampling, self).__init__(data_host, learner)

    def query(self, n):
        self.check_query_availability(n)
        return np.random.choice(list(self.data_host.get_unlabeled_ids()), n, replace=False)
