#!/usr/bin/env python
# ******************************************************************************
# Copyright 2021 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
"""
Custom tf.keras.constraint.Constraint object to limit weights minimum value.
"""

import tensorflow as tf

from keras.constraints import Constraint


class MinValueConstraint(Constraint):
    """ Constraint that ensures that weights values are not below a minimum
    value.

    Args:
        min_value: the minimum desired value for the weights
    """

    def __init__(self, min_value=1e-2):
        self.min_value = min_value

    def __call__(self, w):
        return tf.clip_by_value(w, self.min_value, tf.float32.max)

    def get_config(self):
        return {'min_value': self.min_value}
