"""
    Basic learner for active learning.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 15/12/2021
"""
from abc import ABC, abstractmethod


class BaseLearner(ABC):
    """
    Learner: the basic class for learning process.
    """

    @abstractmethod
    def learn(self, data_x, data_y, n_epoch, batch_size, **kwargs):
        pass

    @abstractmethod
    def infer(self, data, batch_size):
        pass

    @abstractmethod
    def infer_proba(self, data, batch_size, n_drop):
        pass
