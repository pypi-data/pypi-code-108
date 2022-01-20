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
Base class of models.

usage:
m = Model()
...
m.fit(x, y)
y = a.predict(x)
...
"""

from abc import abstractmethod
import numpy as np

from typing import (
    Any,
    List,
    Dict,
    Optional,
)


class IOModel(object):
    """
    Base model with IO functions
    """

    def __init__(self, load: bool = False, fpath: Optional[str] = None):
        if load:
            self.load(fpath)

    def load(self, fpath: Optional[str] = None):
        """[summary]

        Args:
            fpath (Optional[str], optional): [description]. Defaults to None.

        Raises:
            NotImplementedError: [description]
        """
        # TODO
        raise NotImplementedError

    def save(self, fpath: Optional[str] = None):
        """[summary]

        Args:
            fpath (Optional[str], optional): [description]. Defaults to None.

        Raises:
            NotImplementedError: [description]
        """
        # TODO
        raise NotImplementedError


class Model(IOModel):
    """
    Base machine learning model class
    """

    def __init__(
        self,
        seed: int = 0,
        load: bool = False,
        name: Optional[str] = None,
        fpath: Optional[str] = None,
        **kwargs: Optional[Dict[str, Any]]
    ):
        IOModel.__init__(self, load=load, fpath=fpath)

        self.name = name
        self.seed = seed
        np.random.seed(seed)

        self.build(**kwargs)

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def fit(self):
        raise NotImplementedError

    @abstractmethod
    def predict(self):
        raise NotImplementedError


class SupervisedModel(Model):
    """
    Base supervised machine learning model class
    """
        
    @abstractmethod
    def transform_label(self):
        raise NotImplementedError


class UnsupervisedModel(Model):
    """
    Base unsupervised machine learning model class
    """
        
    @abstractmethod
    def embed(self):
        raise NotImplementedError
    
    
class SemisupervisedModel(Model):
    """
    Base semi-supervised machine learning model class
    """
        
    @abstractmethod
    def self_train(self):
        raise NotImplementedError
        
    @abstractmethod
    def label_propagate(self):
        raise NotImplementedError
    
