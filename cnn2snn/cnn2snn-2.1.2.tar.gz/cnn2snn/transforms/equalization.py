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
"""Equalization tools for Keras/CNN2SNN Sequential models.

   These transformations take models with heterogeneities in their weights or
   biases that are identified as harmful for the model quantization of for their
   conversion to akida. They produce models with reduced heterogeneities, yet
   returning nearly identical results.
"""

import numpy as np
import keras

from .clone import clone_model_with_weights


def _is_fused(layer):
    return isinstance(layer, keras.layers.SeparableConv2D)


def _get_unique_source_layer(layer):
    if len(layer.inbound_nodes) != 1:
        return None
    return layer.inbound_nodes[0].inbound_layers


def _is_scalable(layer):
    scalable_layers = (keras.layers.Conv2D, keras.layers.SeparableConv2D,
                       keras.layers.Dense)
    return isinstance(layer, scalable_layers)


def _is_neutral(layer):
    neutral_layers = (keras.layers.MaxPooling2D, keras.layers.GlobalAvgPool2D)
    if isinstance(layer, neutral_layers):
        return True
    # ReLU is neutral only if it is zero-centered and unlimited
    return (isinstance(layer, keras.layers.ReLU) and layer.threshold == 0 and
            layer.max_value is None)


def _identify_scalable_layer_pairs(model):
    scalable_pairs = {}
    for destination_layer in model.layers:
        # First, identify a scalable destination layer
        if _is_scalable(destination_layer):
            source_layer = _get_unique_source_layer(destination_layer)
            # Climb model until we find another scalable layer
            while source_layer is not None and not _is_scalable(source_layer):
                if _is_neutral(source_layer):
                    # This layer can be safely ignored
                    source_layer = _get_unique_source_layer(source_layer)
                else:
                    # An incompatible layer got in the way: abort search
                    source_layer = None
            if source_layer is not None:
                # We found a valid pair of scalable layers
                scalable_pairs[source_layer] = destination_layer
    return scalable_pairs


def _get_filter_max_values(layer):
    if isinstance(layer, keras.layers.Conv2D):
        # Layer "weights" are filters, biases
        filters = layer.get_weights()[0]
        # Filters are HWCN, i.e. the filter index is the last dimension
        return np.amax(np.abs(filters), axis=(0, 1, 2))
    if isinstance(layer, keras.layers.SeparableConv2D):
        # Layer "weights" are depthwise filters, pointwise filters, biases
        # We are only interested in rescaling pointwise filters
        filters = layer.get_weights()[1]
        # Pointwise filters are HWCN, i.e. the filter index is the last dimension
        return np.amax(np.abs(filters), axis=(0, 1, 2))
    if isinstance(layer, keras.layers.Dense):
        # Layer "weights" are filters, biases
        filters = layer.get_weights()[0]
        # Filters are CN, i.e. the filter index is the last dimension
        return np.amax(np.abs(filters), axis=0)
    return None


def _get_channel_max_values(layer):
    if isinstance(layer, keras.layers.Conv2D):
        # Layer "weights" are filters, biases
        filters = layer.get_weights()[0]
        # Filters are HWCN, i.e. the channel index is the third dimension
        return np.amax(np.abs(filters), axis=(0, 1, 3))
    if isinstance(layer, keras.layers.SeparableConv2D):
        # Layer "weights" are depthwise filters, pointwise filters, biases
        dw_filters = layer.get_weights()[0]
        # Depthwise filters are HWCN, i.e. channel index is the third dimension
        return np.amax(np.abs(dw_filters), axis=(0, 1, 3))
    if isinstance(layer, keras.layers.Dense):
        # Layer "weights" are filters, biases
        filters = layer.get_weights()[0]
        # Filters are CN, i.e. the channel index is the first dimension
        return np.amax(np.abs(filters), axis=1)
    return None


def _get_optimal_scales(source_max, destination_max):
    if source_max.shape[0] != destination_max.shape[0]:
        raise ValueError("Incompatible source and destination for equalization")
    # By default, do not rescale
    scales = np.ones(source_max.shape, dtype=np.float32)
    for i in range(source_max.shape[0]):
        if destination_max[i] > 0:
            # Apply the formula from equation (11) in paragraph 4.1
            # From "Data-Free Quantization Through Weight Equalization and Bias
            # Correction"
            # Markus Nagel, Mart van Baalen, Tijmen Blankevoort, Max Welling
            # https://arxiv.org/abs/1906.04721
            scales[i] = np.sqrt(source_max[i] / destination_max[i])
    return scales


def _get_optimal_fused_layer_scales(layer):
    source_max = _get_channel_max_values(layer)
    pw_filters = layer.get_weights()[1]
    # Pointwise filters are HWCN, i.e. channel index is the third dimension
    destination_max = np.amax(np.abs(pw_filters), axis=(0, 1, 3))
    return _get_optimal_scales(source_max, destination_max)


def _rescale_fused_layer(layer, scales):
    weights = layer.get_weights()
    if isinstance(layer, keras.layers.SeparableConv2D):
        # Layer "weights" are depthwise filters, pointwise filters, biases
        dw_filters = weights[0]
        pw_filters = weights[1]
        # Divide dw_filters and multiply pw_filters by the same scale
        for i in range(scales.shape[0]):
            dw_filters[:, :, i, :] = dw_filters[:, :, i, :] / scales[i]
            pw_filters[:, :, i, :] = pw_filters[:, :, i, :] * scales[i]
        weights[0] = dw_filters
        weights[1] = pw_filters
        # Update layer weights
        layer.set_weights(weights)


def _get_optimal_cross_layer_scales(source_layer, destination_layer):
    source_max = _get_filter_max_values(source_layer)
    destination_max = _get_channel_max_values(destination_layer)
    return _get_optimal_scales(source_max, destination_max)


def _rescale_source_layer(layer, scales):
    assert _is_scalable(layer)
    weights = layer.get_weights()
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.Dense)):
        # Layer "weights" are filters, biases
        filters = weights[0]
        biases = weights[1]
    elif isinstance(layer, keras.layers.SeparableConv2D):
        # Layer "weights" are depthwise filters, pointwise filters, biases
        filters = weights[1]
        biases = weights[2]
    # Divide filters by scales (broadcast on the filters last dimension)
    scaled_weights = filters / scales
    # Divide biases by scales (element-wise)
    scaled_biases = biases / scales
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.Dense)):
        weights[0] = scaled_weights
        weights[1] = scaled_biases
    elif isinstance(layer, keras.layers.SeparableConv2D):
        weights[1] = scaled_weights
        weights[2] = scaled_biases
    # Update layer weights
    layer.set_weights(weights)


def _rescale_destination_layer(layer, scales):
    weights = layer.get_weights()
    # Extract filters (resp. depthwise filters)
    filters = weights[0]
    if isinstance(layer, (keras.layers.Conv2D, keras.layers.SeparableConv2D)):
        # Mutiply each channel (third dimension) by scale
        for i in range(scales.shape[0]):
            filters[:, :, i, :] = filters[:, :, i, :] * scales[i]
    elif isinstance(layer, keras.layers.Dense):
        # Mutiply each channel (first dimension) by scale
        for i in range(scales.shape[0]):
            filters[i, :] = filters[i, :] * scales[i]
    # Update layer weights
    weights[0] = filters
    layer.set_weights(weights)


def _adjust_fused_layer_weights(layer):
    scales = _get_optimal_fused_layer_scales(layer)
    _rescale_fused_layer(layer, scales)


def _adjust_consecutive_layer_weights(source_layer, destination_layer):
    scales = _get_optimal_cross_layer_scales(source_layer, destination_layer)
    _rescale_source_layer(source_layer, scales)
    _rescale_destination_layer(destination_layer, scales)


def cross_layer_scaling(model):
    """Equalize weights between neural layers.

    This is an implementation of "Cross-layer range equalization", described
    in paragraph 4.1 of "Data-Free Quantization Through Weight Equalization
    and Bias Correction".
    Markus Nagel, Mart van Baalen, Tijmen Blankevoort, Max Welling
    https://arxiv.org/abs/1906.04721
    
    Args:
        model (:obj:`tf.keras.Model`): a Keras model.

    Returns:
        :obj:`tf.keras.Model`: a new Keras model with normalized depthwise
        weights in SeparableConv2D layers.
    """
    # Clone model
    new_model = clone_model_with_weights(model)

    # Identify scalable pairs
    scalable_pairs = _identify_scalable_layer_pairs(new_model)

    # Rescale layer weights
    for source_layer in new_model.layers:
        if _is_fused(source_layer):
            _adjust_fused_layer_weights(source_layer)
        if source_layer in scalable_pairs:
            destination_layer = scalable_pairs[source_layer]
            _adjust_consecutive_layer_weights(source_layer, destination_layer)

    return new_model


def _get_homogeneity_rate(layer):
    filter_max = _get_filter_max_values(layer)
    if filter_max is None:
        return None
    global_max = np.max(filter_max)
    # Evaluate the relative score of each filter
    filter_rate = filter_max / global_max
    return np.mean(filter_rate)


def weights_homogeneity(model):
    """Give an estimation of the homogeneity of layer weights

    For each Conv or Dense layer in the model, this compares the ranges of
    the weights for each filter with the range of the tensor.
    The score for each filter is expressed as an homogeneity rate (1 is the
    maximum), and the layer homogeneity rate is the mean of all filter rates.

    Args:
        model (:obj:`tf.keras.Model`): a Keras model.
    Returns:
        dict: rates indexed by layer names.
    """
    scores = {}
    for layer in model.layers:
        score = _get_homogeneity_rate(layer)
        if score is not None:
            scores[layer.name] = score
    return scores


def normalize_separable_layer(layer):
    """This normalizes the depthwise weights of a SeparableConv2D.

       In order to limit the quantization error when using a per-tensor
       quantization of depthwise weights, this rescales all depthwise weights
       to fit within the [-1, 1] range.
       To preserve the output of the layer, each depthwise kernel is rescaled
       independently to the [-1, 1] interval by dividing all weights by the
       absolute maximum value, and inversely, all pointwise filters 'looking'
       at these kernels are multiplied by the same value.

    Args:
        layer (:obj:`tf.keras.layers.SeparableConv2D`): a Keras SeparableConv2D
        layer.
    """
    if not isinstance(layer, keras.layers.SeparableConv2D):
        raise ValueError("The layer is not a SeparableConv2D")
    # Get maximum ranges per channel
    dw_max = _get_channel_max_values(layer)
    # Rescale depthwise to [-1, 1] and adjust pointwise accordingly
    _rescale_fused_layer(layer, dw_max)


def normalize_separable_model(model):
    """This normalizes the depthwise weights of all SeparableConv2D in a Model.
    
    Args:
        model (:obj:`tf.keras.Model`): a Keras model.

    Returns:
        :obj:`tf.keras.Model`: a new Keras model with normalized depthwise
        weights in SeparableConv2D layers.
    """
    # Clone model
    new_model = clone_model_with_weights(model)

    # Normalize SeparableConv2D depthwise weights
    for layer in new_model.layers:
        if isinstance(layer, keras.layers.SeparableConv2D):
            normalize_separable_layer(layer)

    return new_model
