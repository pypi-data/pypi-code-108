"""
    Pool-based active learning strategy base class.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 07/12/2021
"""

from ..learner.base import BaseLearner
from ..data import DataHost


class Strategy:
    def __init__(self, data_host: DataHost, learner: BaseLearner):
        self.learner = learner
        self.data_host = data_host

    def check_query_availability(self, query_num):
        """
        Check the query number availability.
        @param query_num: the number of queried data.
        @return:
        """
        if query_num > self.data_host.get_size():
            raise ValueError(
                f"query size {query_num} should be no more than the unlabeled data size {self.data_host.get_size()}")

    def query(self, number):
        """
        The query function that calls the specific active learning strategy.
        :param number: the query number.
        :return: the data ids in a numpy array.
        """
        pass

    def query_object(self, number):
        """
        The query function that calls the specific active learning strategy.
        :param number: the query number.
        :return: the data points in a numpy array.
        """
        pass

    def learn(self, n_epoch=1, batch_size=1, **kwargs):
        """
        Train the model using all the labeled data.
        @return: None
        """
        self.learner.learn(*self.data_host.get_labeled_data(), n_epoch, batch_size=batch_size, **kwargs)

    def infer(self, data, batch_size=1, is_prob=False, n_drop=1):
        """
        Inference function by given request data.
        @param data: the inference raw data.
        @param batch_size: the inference batch_size.
        @param is_prob: is_prob: the return values or probabilities.
        @param n_drop: the number of dropout runs to use to generate MC samples (int, optional).
        @return: the inference results.
        """
        if is_prob:
            return self.learner.infer_proba(data, batch_size=batch_size, n_drop=n_drop)
        else:
            return self.learner.infer(data, batch_size=batch_size)
