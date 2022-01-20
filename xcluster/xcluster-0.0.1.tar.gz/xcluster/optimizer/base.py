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
Base class of optimizer
"""

from abc import abstractmethod
from xcluster import model as xc_model

class BaseOptimizer(object):
    
    def __init__(self):
        pass
    
    @abstractmethod
    def train(self):
        raise NotImplementedError
    
    @abstractmethod
    def train_step(self):
        raise NotImplementedError
    
    @abstractmethod
    def save(self):
        #TODO
        raise NotImplementedError
    
    @abstractmethod
    def load(self):
        #TODO
        raise NotImplementedError


class EMOptimizer(BaseOptimizer):

    def train(self, model: xc_model.BaseModel, X, Y, objective: ):
                params = self.optimizer.train(self, X, Y, self.objective)
