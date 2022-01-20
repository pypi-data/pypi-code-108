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
optimizer class of expectation–maximization (EM) algorithm
"""

from .base import BaseOptimizer

class EMOptimizer(BaseOptimizer):
    
    def __init__(self, **kwargs):
        """[summary]
        """
        threshold = kwargs.get('threshold', 1e-5)
    
    def optimize(self, **kwargs):
        """[summary]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError
    
    def optimize_step(self, **kwargs):
        """[summary]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError
    