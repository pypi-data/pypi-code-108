"""
    Data pool for pool-based query strategies.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 10/12/2021
"""

import numpy as np

from .base import DataHost


class Pool(DataHost):
    """
    Data Pool for pool-based query strategies.
    """

    def __init__(self, raw_data, transform=None):
        """
        @param raw_data: the raw data with no labels.
        @param process_func (optional): the pre-processing function to create the embeddings/features/processed data.
        You can also conduct the feature engineering outside this class.
        """
        super().__init__(transform)
        self.data = raw_data
        self.size = len(self.data)
        self.labels = [None] * len(self.data)
        self.labeled_ids = set()
        self.transform = transform
        if transform:
            self.features = transform(self.data)
        else:
            self.features = self.data

    def get_data(self):
        """
        Get all the available data (include both labeled and unlabeled) in the input type.
        @return: all the available data.
        """
        return self.data

    def get_transform_data(self):
        """
        Get all the available data (include both labeled and unlabeled) after processing.
        @return: all the processed data.
        """
        return self.features

    def get_data_by_ids(self, id_list):
        """
        Get the data points by giving a list of existing ids.
        :return: list of queried data objects.
        """
        return [self.data[i] for i in id_list]

    def get_label_by_ids(self, id_list):
        """
        Get the labels points by giving a list of existing ids.
        :return: list of queried label objects.
        """
        return [self.labels[i] for i in id_list]

    def get_unlabeled_data(self, transformed=False):
        """
        Get the unlabeled data.
        :return: a list (numpy array) of unlabeled data objects.
        """
        if transformed:
            return np.delete(self.features, list(self.labeled_ids), 0)
        else:
            return np.delete(self.data, list(self.labeled_ids), 0)

    def get_unlabeled_ids(self):
        """
        Get the unlabeled data ids, used for query in the unlabeled data pool.
        :return: a list (numpy array) contains all the unlabeled data ids.
        """
        return np.delete(range(self.size), list(self.labeled_ids))

    def label_by_ids(self, label_index_list, labels):
        """
        Label the data by given data ids, those ids should be existed in the given total
        data pool. The labels is a list of labels for corresponding indexed data points.

        :param label_index_list: a list of data ids.
        :param labels: a list of labels.
        :return: None
        """
        if len(label_index_list) == len(labels):
            self.labeled_ids.update(label_index_list)
            for i in range(len(label_index_list)):
                self.labels[label_index_list[i]] = labels[i]
        else:
            raise ValueError("the labeled data number should be the same as the corresponding labels.")

    def label_by_id(self, label_index, y):
        """
        Label single data point by indexing the data location.

        :param label_index: the index of the data point you want to label.
        :param y: the data label.
        :return: None
        """
        if label_index < self.size:
            self.labels[label_index] = y
            self.labeled_ids.update([label_index])
        else:
            raise ValueError("make sure the given index is available")

    def label(self, x, y):
        """
        Label the single data by querying the data object itself.

        :param x: The data object you want to label.
        :param y: the data label.
        :return: None
        """
        if x in self.data:
            for i in np.where(np.array(self.data) == x)[0]:
                self.labels[i] = y
        else:
            self.data = np.append(self.data, x)
            self.labels = np.append(self.labels, y)
            self.size = len(self.data)
        self.labeled_ids.update(np.where(np.array(self.data) == x)[0].tolist())

    def get_labeled_data(self, transformed=False):
        """
        Get all the labeled data objects, including the data and corresponding labels.
        :return: data, labels.
        """
        filter_ids = list(self.labeled_ids)
        labels = [self.labels[i] for i in filter_ids]
        if transformed:
            return [self.features[i] for i in filter_ids], labels
        else:
            return [self.data[i] for i in filter_ids], labels

    def get_labeled_ids(self):
        """
        Get the ids of all the labeled data in the pool.
        @return: a set of labeled ids.
        """
        return self.labeled_ids

    def get_size(self):
        """
        Get the pool size
        @return: the pool size number.
        """
        return self.size
