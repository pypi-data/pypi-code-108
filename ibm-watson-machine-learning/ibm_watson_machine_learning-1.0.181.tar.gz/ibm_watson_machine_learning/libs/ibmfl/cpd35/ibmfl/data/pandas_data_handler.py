#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import abc
import logging

from ibmfl.data.data_handler import DataHandler

logger = logging.getLogger(__name__)


class PandasDataHandler(DataHandler):
    """
    Base class to load and pre-process data.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None

    @abc.abstractmethod
    def get_data(self):
        """
        Read data and return as Pandas data frame.

        :return: A dataset structure
        :rtype: `pandas.core.frame.DataFrame`
        """

    @abc.abstractmethod
    def get_dataset_info(self, **kwargs):
        """
        Read and extract data information

        :return: some information about the dataset (i.e. a dictionary that contains the list of features)
        :rtype: `dict`
        """
        raise NotImplemented

    def get_min(self, dp_flag=False, **kwargs):
        """
        Assuming the dataset is loaded as type `pandas.DataFrame`, and
        has shape(num_samples, num_features).

        :param dp_flag: Flag for differential private answer. By default is \
        set to False.
        :type dp_flag: `boolean`
        :param kwargs: Dictionary of differential privacy arguments \
        for computing the minimum value of each feature across all samples, \
        e.g., epsilon and delta, etc.
        :type kwargs: `dict`
        :return: A vector of shape (1, num_features) stores the minimum value \
        of each feature across all samples.
        :rtype: `pandas.Series` where each entry matches the original type \
        of the corresponding feature.
        """
        train_data, (_) = self.get_data()

        if not dp_flag:
            logger.info('Calculating minimum values.')
            min_vec = train_data.min(axis=0)
            # TODO dp minimum calculation
        return min_vec
