"""
    The basic data management class for both pool and stream based AL methods.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 05/12/2021
"""
from abc import ABC, abstractmethod


class DataHost(ABC):
    """
    The base class for both data pool and data channel.
    """

    def __init__(self, transform=None):
        self.transform = transform

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def get_transform_data(self):
        pass

    @abstractmethod
    def get_unlabeled_data(self, transformed=False):
        pass

    @abstractmethod
    def get_unlabeled_ids(self):
        pass

    @abstractmethod
    def label(self, x, y):
        pass

    @abstractmethod
    def get_labeled_data(self, transformed=False):
        pass

    @abstractmethod
    def get_labeled_ids(self):
        pass

    @abstractmethod
    def get_size(self):
        pass
