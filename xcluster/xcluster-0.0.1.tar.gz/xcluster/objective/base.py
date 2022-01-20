# Copyright 2021 Baihan Lin
#
# Licensed under the GNU General Public License, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.gnu.org/licenses/gpl-3.0.en.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base class of objective functions
"""

from abc import abstractmethod

class BaseObjective(object):
    
    def __init__(self, **kwargs):
        """[summary]
        """
        self.model = kwargs.get('model', None)
        pass
    
    @abstractmethod
    def update_model(self, model):
        self.model = model
        
    @abstractmethod
    def get_loss(self, X, Y=None):
        """[summary]

        Args:
            X ([type]): [description]
            Y ([type], optional): [description]. Defaults to None.
        """
        raise NotImplementedError

    @abstractmethod
    def get_loss_history(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return None
    
    @abstractmethod
    def save_loss_history(self, file_path=None):
        """[summary]

        Args:
            file_path ([type], optional): [description]. Defaults to None.
        """

    
    