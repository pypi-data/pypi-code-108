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
"""BatchNormalization transformations for Keras/CNN2SNN Sequential models.
"""

import numpy as np
import tensorflow as tf
from keras import Sequential, Input
from keras.layers import (Conv2D, SeparableConv2D, Dense, MaxPool2D,
                          GlobalAvgPool2D, BatchNormalization)

from ..quantization_ops import MaxPerAxisQuantizer, StdPerAxisQuantizer
from ..quantization_layers import (QuantizedConv2D, QuantizedSeparableConv2D,
                                   QuantizedDense)
from .clone import clone_layer, clone_layer_and_add_to_model


def invert_batchnorm_pooling(model):
    """Inverts pooling and BatchNormalization layers in a Sequential model to
    have BN layer before pooling.

    Having pool->BN or BN->pool is equivalent only if BN layer has no negative
    gammas.

    Args:
        model (:obj:`tf.keras.Model`): a Sequential Keras model.
    Returns:
        :obj:`tf.keras.Model`: a Sequential Keras model.
    """

    assert isinstance(model, Sequential)

    new_model = Sequential()
    new_model.add(Input(model.input_shape[1:]))
    i = 0
    while i < len(model.layers) - 1:
        layer = model.layers[i]
        next_layer = model.layers[i + 1]
        if (isinstance(layer, (MaxPool2D, GlobalAvgPool2D)) and
                isinstance(next_layer, BatchNormalization)):
            gammas = next_layer.get_weights()[0]
            if isinstance(layer, MaxPool2D) and np.any(gammas <= 0):
                # It is impossible to invert MaxPool->BN with gammas <= 0
                raise RuntimeError(f"There are {np.sum(gammas <= 0)} negative "
                                   "gammas in the batch norm layer "
                                   f"{next_layer.name}. Negative gammas are "
                                   "not supported.")
            # GlobalAveragePooling2D brings a change on axis for the batch norm.
            if isinstance(layer, GlobalAvgPool2D):
                bn_config = next_layer.get_config()
                bn_config['axis'] = [-1]
                bn_layer_clone = BatchNormalization.from_config(bn_config)
            else:
                bn_layer_clone = clone_layer(next_layer)
            new_model.add(bn_layer_clone)
            bn_layer_clone.set_weights(next_layer.get_weights())
            clone_layer_and_add_to_model(layer, new_model)
            i = i + 2
        else:
            clone_layer_and_add_to_model(layer, new_model)
            i = i + 1

    if i < len(model.layers):
        clone_layer_and_add_to_model(model.layers[-1], new_model)

    return new_model


def _compute_BN_folded_weights(neural_layer, bn_layer):
    """Computes the new weights of a neural layer after folding BN layer.

    Args:
        neural_layer (:obj:`tf.keras.Layer`): a neural layer where BN will be
            folded.
        bn_layer (:obj:`tf.keras.Layer`): the BatchNormalization layer to fold
            into the neural layer.
    Returns:
        list: a list of the new weights to set in the new folded neural layer.
        list: a list of positive scale factors introduced by the folding.

    """

    # Get kernel and bias weights of the neural layer
    if type(neural_layer) in (SeparableConv2D, QuantizedSeparableConv2D):
        kernel_position = 1
        bias_position = 2
    else:
        kernel_position = 0
        bias_position = 1
    weights = neural_layer.get_weights()
    kernel = weights[kernel_position]
    bias = weights[bias_position] if neural_layer.use_bias else 0

    # Get BN weights
    gamma, beta, mean, var = bn_layer.get_weights()
    scale_BN = gamma / np.sqrt(var + bn_layer.epsilon)

    # Compute new folded kernel and bias
    new_kernel = kernel * scale_BN
    new_bias = beta + (bias - mean) * scale_BN

    # Return all weights with modified ones
    new_weights = weights
    new_weights[kernel_position] = new_kernel
    if neural_layer.use_bias:
        new_weights[bias_position] = new_bias
    else:
        new_weights.insert(bias_position, new_bias)

    # Absolute value of scale_BN is returned because we no longer need its sign.
    # It is later used to rescale the scale factors which are always positive.
    return new_weights, np.abs(scale_BN)


def fold_batchnorm(model):
    """Folds BatchNormalization layers into the preceding neural layers of
    a Sequential model.

    Args:
        model (:obj:`tf.keras.Model`): a Sequential Keras model.
    Returns:
        :obj:`tf.keras.Model`: a Sequential Keras model.
    """

    assert isinstance(model, Sequential)

    quantized_layers = (QuantizedConv2D, QuantizedSeparableConv2D,
                        QuantizedDense)
    neural_layers = quantized_layers + (Conv2D, SeparableConv2D, Dense)

    new_model = Sequential()
    new_model.add(Input(model.input_shape[1:]))
    i = 0
    while i < len(model.layers) - 1:
        layer = model.layers[i]
        next_layer = model.layers[i + 1]
        if (isinstance(layer, neural_layers) and
                isinstance(next_layer, BatchNormalization)):

            # Check BN axis parameter
            if (len(next_layer.axis) != 1 or
                    next_layer.axis[0] != len(next_layer.input_shape) - 1):
                raise RuntimeError(f"The BatchNormalization layer "
                                   f"{next_layer.name} must be applied on the "
                                   f"last axis. Receives {next_layer.axis}.")

            # If the layer has been quantized, check quantizer
            if isinstance(layer, quantized_layers):
                if not isinstance(layer.quantizer,
                                  (MaxPerAxisQuantizer, StdPerAxisQuantizer)):
                    shift_for_sepconv = isinstance(layer,
                                                   QuantizedSeparableConv2D)
                    w = layer.get_weights()[0 + shift_for_sepconv]
                    scale_factors = layer.quantizer.scale_factor(tf.constant(w))
                    if tf.rank(scale_factors) != 1:
                        raise RuntimeError(
                            f"The BatchNormalization layer {next_layer.name} "
                            "can only be folded into a quantized layer that "
                            "uses a quantizer per axis.")

            # Add new neural layer with bias
            config = layer.get_config()
            config['use_bias'] = True
            new_layer = layer.__class__.from_config(config)
            new_model.add(new_layer)
            new_weights, scale_BN = _compute_BN_folded_weights(
                layer, next_layer)
            if np.any(scale_BN == 0):
                # Zero gammas are not supported: once folded, new kernel is zero
                raise RuntimeError(f"There are {np.sum(scale_BN == 0)} null "
                                   "gammas in the batch norm layer "
                                   f"{next_layer.name}. Null gammas are not "
                                   "supported.")
            new_layer.set_weights(new_weights)
            i = i + 2
        else:
            clone_layer_and_add_to_model(layer, new_model)
            i = i + 1

    if i < len(model.layers):
        clone_layer_and_add_to_model(model.layers[-1], new_model)

    return new_model
