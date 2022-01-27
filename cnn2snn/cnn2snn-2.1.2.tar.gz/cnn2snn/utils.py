#!/usr/bin/env python
# ******************************************************************************
# Copyright 2019 Brainchip Holdings Ltd.
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
"""Various utility methods
"""
from keras.models import load_model
from .cnn2snn_objects import cnn2snn_objects


def load_quantized_model(filepath, custom_objects=None, compile_model=True):
    """Loads a quantized model saved in TF or HDF5 format.

    If the model was compiled and trained before saving, its training state
    will be loaded as well.
    This function is a wrapper of `tf.keras.models.load_model`.

    Args:
        filepath (string): path to the saved model.
        custom_objects (dict): optional dictionary mapping names (strings) to
            custom classes or functions to be considered during deserialization.
        compile_model (bool): whether to compile the model after loading.

    Returns:
        :obj:`keras.Model`: a Keras model instance.
    """
    if custom_objects is None:
        custom_objects = {}
    all_objects = {**custom_objects, **cnn2snn_objects}
    return load_model(filepath, all_objects, compile_model)
