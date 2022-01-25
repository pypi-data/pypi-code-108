"""
Module to where data handler are implemented.
"""
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

from ibmfl.data.data_handler import DataHandler
from ibmfl.data.env_spec import EnvHandler


class EnvDataHandler(DataHandler):
    """
    Base class to load data and  environment for reinforcement learning.
    """

    @abc.abstractmethod
    def get_data(self, **kwargs):
        """
        Read train data and test data for reinforcement learning
        :return:
        """

    @abc.abstractmethod
    def get_env_class_ref(self) -> EnvHandler:
        """
           Get environment reference for RL trainer, the instance is created in
           model class as part of trainer initialization
        """
