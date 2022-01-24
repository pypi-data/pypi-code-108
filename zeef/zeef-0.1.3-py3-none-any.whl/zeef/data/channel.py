"""
    Data channel for stream-based query strategies.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 10/12/2021
"""

from .base import DataHost


class Channel(DataHost):
    """
    Data channel for stream-based query strategies.
    """

    def __init__(self, transform=None):
        super().__init__(transform)

    def get_data(self):
        pass

    def get_transform_data(self):
        pass

    def get_unlabeled_data(self, transformed=False):
        pass

    def get_unlabeled_ids(self):
        pass

    def label(self, x, y):
        pass

    def get_labeled_data(self, transformed=False):
        pass

    def get_labeled_ids(self):
        pass

    def get_size(self):
        return 1
