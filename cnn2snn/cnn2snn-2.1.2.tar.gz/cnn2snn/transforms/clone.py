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
"""Cloning helpers for Keras/CNN2SNN models.
"""

import tensorflow as tf
import keras

from ..cnn2snn_objects import cnn2snn_objects


def clone_model_with_weights(model, input_tensors=None):
    """Clones the model and copy weights into the cloned model.

    The cloned model is identical to the input model, but cloning removes the
    shared layers that can cause problems at inference.

    Args:
        model (:obj:`keras.Model`): a Sequential Keras model.
        input_tensors (list of Tensors or :obj:`keras.layers.InputLayer`, optional):
            to build the model upon. If not provided, new `Input` objects will
            be created.
    Returns:
        :obj:`keras.Model`: a Sequential Keras model.
    """

    with tf.keras.utils.custom_object_scope(cnn2snn_objects):
        model_clone = keras.models.clone_model(model, input_tensors)
    model_clone.set_weights(model.get_weights())
    return model_clone


def clone_layer(layer):
    """Clones the layer without copying its weights

    Args:
        layer (:obj:`keras.layers.Layer`): a Keras layer.
    Returns:
        :obj:`keras.layers.Layer`: a Keras layer.
    """
    with tf.keras.utils.custom_object_scope(cnn2snn_objects):
        return layer.__class__.from_config(layer.get_config())


def clone_layer_and_add_to_model(layer, model):
    """Clones the layer, add it to the model and copy its weights

    Args:
        layer (:obj:`keras.layers.Layer`): a Keras layer.
        model (:obj:`keras.Model`): a Sequential Keras model.
    Returns:
        :obj:`keras.Model`: a Keras layer.
    """
    layer_clone = clone_layer(layer)
    model.add(layer_clone)
    layer_clone.set_weights(layer.get_weights())
    return layer_clone
