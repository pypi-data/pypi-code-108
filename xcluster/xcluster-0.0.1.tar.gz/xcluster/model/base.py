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
Base classes of model
"""

from abc import abstractmethod
import numpy as np
from typing import (
    Any,
    Dict,
    Optional,
)

class BaseModel(object):
    
    def __init__(self, seed: int=0, **kwargs: Optional[Dict[str, Any]]):
        self.seed = seed
        np.random.seed(self.seed)
        self.build(**kwargs)
        
    def fit(self, X, Y=None):
        """[summary]

        Args:
            X ([type]): [description]
            Y ([type], optional): [description]. Defaults to None.

        Raises:
            NotImplementedError: [description]
        """
        updated_params = self.optimizer.train(self.params, X, Y, self.objective)
        self._update_params(updated_params)

    @abstractmethod
    def build(self, **kwargs: Optional[Dict[str, Any]]):
        raise NotImplementedError

    @abstractmethod
    def predict(self, X):
        raise NotImplementedError
    
    @abstractmethod
    def _update_params(self, params: Dict[str, Any]):
        raise NotImplementedError


class PrototypeClustering(BaseModel):

    def __init__(self, seed: int=0, **kwargs: Optional[Dict[str, Any]]):
        BaseModel.__init__(self,seed=seed)
        self.build(**kwargs)

    def predict(self, X):
        """[summary]

        Args:
            X ([type]): [description]

        Returns:
            [type]: [description]
        """
        labels = self.compute_labels_from_prototypes(X, self.prototypes)
        return labels
    
    @abstractmethod
    def compute_labels_from_prototypes(self):
        raise NotImplementedError


class DensityClustering(BaseModel):

    def __init__(self, seed: int=0, **kwargs: Optional[Dict[str, Any]]):
        BaseModel.__init__(self,seed=seed)
        self.build(**kwargs)

    def build(self, **kwargs: Optional[Dict[str, Any]]):
        raise NotImplementedError
    
    def predict(self, X):
        raise NotImplementedError
    

class SpectralClustering(BaseModel):
    
    def __init__(self, seed: int=0, **kwargs: Optional[Dict[str, Any]]):
        BaseModel.__init__(self,seed=seed)
        self.build(**kwargs)

    def build(self, **kwargs: Optional[Dict[str, Any]]):
        raise NotImplementedError
    
    def predict(self, X):
        raise NotImplementedError
    
class AgglomerativeClustering(BaseModel):
    
    def __init__(self, seed: int=0, **kwargs: Optional[Dict[str, Any]]):
        BaseModel.__init__(self,seed=seed)
        self.build(**kwargs)

    def build(self, **kwargs: Optional[Dict[str, Any]]):
        raise NotImplementedError
        
    def predict(self, X):
        raise NotImplementedError
    
class DivisiveClustering(BaseModel):

    def __init__(self, seed: int=0, **kwargs: Optional[Dict[str, Any]]):
        BaseModel.__init__(self,seed=seed)
        self.build(**kwargs)

    def build(self, **kwargs: Optional[Dict[str, Any]]):
        raise NotImplementedError
        
    def predict(self, X):
        raise NotImplementedError