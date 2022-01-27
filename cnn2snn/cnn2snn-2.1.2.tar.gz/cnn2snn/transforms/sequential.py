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
"""Transformation utilities for Keras/CNN2SNN Sequential models.
"""

from keras import Model, Sequential, Input
from keras.layers import ReLU, Dropout, Concatenate, InputLayer, MaxPool2D

from ..quantization_layers import QuantizedActivation
from .clone import (clone_model_with_weights, clone_layer,
                    clone_layer_and_add_to_model)
from .batch_normalization import invert_batchnorm_pooling, fold_batchnorm


def sequential_remove_useless_layers(model):
    """Removes useless layers in a Sequential model.

    Useless layers are:
    - Dropout

    Args:
        model (:obj:`tf.keras.Model`): a Sequential Keras model.
    Returns:
        :obj:`tf.keras.Model`: a Sequential Keras model.
    """

    _raise_error_if_model_not_sequential(model)

    useless_layers = (Dropout,)

    new_model = Sequential()
    new_model.add(Input(model.input_shape[1:]))
    for layer in model.layers:
        if isinstance(layer, useless_layers):
            continue
        clone_layer_and_add_to_model(layer, new_model)

    return new_model


def sequential_invert_pooling_activation(model):
    """Invert activation and MaxPool2D layer in a Sequential model to have
    MaxPool2D before the activation.

    Having activation->MaxPool2D or MaxPool2D->activation is equivalent only if
    the activation is increasing (ok for ReLU and QuantizedActivation).
    Note that GlobalAvgPool2D cannot be inverted with an activation because
    there is no equivalence between activation->GAP and GAP->activation.

    Args:
        model (:obj:`tf.keras.Model`): a Sequential Keras model.
    Returns:
        :obj:`tf.keras.Model`: a Sequential Keras model.
    """

    _raise_error_if_model_not_sequential(model)

    new_model = Sequential()
    new_model.add(Input(model.input_shape[1:]))
    i = 0
    while i < len(model.layers) - 1:
        layer = model.layers[i]
        next_layer = model.layers[i + 1]
        if (isinstance(layer, (ReLU, QuantizedActivation)) and
                isinstance(next_layer, MaxPool2D)):
            clone_layer_and_add_to_model(next_layer, new_model)
            clone_layer_and_add_to_model(layer, new_model)
            i = i + 2
        else:
            clone_layer_and_add_to_model(layer, new_model)
            i = i + 1

    if i < len(model.layers):
        clone_layer_and_add_to_model(model.layers[-1], new_model)

    return new_model


def _raise_error_if_model_not_sequential(model):
    """Raises a ValueError if model is not a Sequential Keras model.
    """
    if not isinstance(model, Sequential):
        raise ValueError(f"Model is expected to be Sequential. Receives type "
                         f"{model.__class__.__name__}.")


def _check_layers_data_format(model):
    """Asserts that all layers in the model are 'channels_last'.
    Args:
        model (tf.keras.model): the Keras model to check.
    """

    # Error if 'data_format' is 'channels_first'
    for layer in model.layers:
        if hasattr(layer, 'data_format'):
            if layer.data_format == "channels_first":
                raise RuntimeError("Unsupported data format 'channels_first' "
                                   f"in layer '{layer.name}'.")


def _check_model_input_output(model):
    """Asserts that model inputs/outputs are supported for conversion.
    The Keras model must have only one input layer and one output layer. The
    input shape must 4-D (N, H, W, C).

    Args:
        model (tf.keras.model): the Keras model to check.
    """

    # Error if multiple inputs
    if len(model.input_names) > 1:
        raise RuntimeError("Model must have only one input layer. Receives "
                           f"inputs {model.input_names}.")

    # Error if multiple outputs
    if len(model.output_names) != 1:
        raise RuntimeError("Model must have only one output layer. Receives"
                           f"outputs {model.output_names}.")

    # Error if input shape is not 4D, i.e. (N, H, W, C)
    if len(model.input_shape) not in (2, 4):
        raise RuntimeError(
            "Input shape of model must be 2-D or 4-D (batch size + 1-D or 3-D "
            f"tensors). Receives input shape {model.input_shape}.")


def _check_layer_inbounds(model):
    """Asserts that all layers in the model have only one inbound node and
    inbound layer (except for input layers and Concatenate layers).
    """
    for layer in model.layers:
        if len(layer.inbound_nodes) != 1:
            raise RuntimeError("Layers must have only one inbound node. "
                               f"Receives layer {layer.name} with "
                               f"{len(layer.inbound_nodes)} nodes.")

        if (layer.inbound_nodes[0].is_input or isinstance(layer, Concatenate)):
            continue

        num_inbound_layers = len(layer.inbound_nodes[0].parent_nodes)
        if num_inbound_layers != 1:
            raise RuntimeError(f"Layer {layer.name} must have only one inbound "
                               f"layer. Receives {num_inbound_layers}.")


def _check_concat_layer_compatibility(layer, inbound_layers):
    """Checks that the Concatenate layer is compatible for conversion:

    - A Concatenate layer axis parameter must be equal to -1.
    - A Concatenate layer must have exactly two inbound layers.

    Args:
        layer (:obj:`tf.keras.Layer`): a Keras Concatenate layer.
        inbound_layers (list): the inbound layers of the Concatenate layer.
    """

    if layer.axis != -1:
        raise RuntimeError(f"The Concatenate layer '{layer.name}' must have "
                           f"axis=-1. Receives axis={layer.axis}.")

    if len(inbound_layers) != 2:
        inbound_names = [l.name for l in inbound_layers]
        raise RuntimeError(f"The Concatenate layer '{layer.name}' must have "
                           f"exactly two inbound layers. Receives inbound "
                           f"layers {inbound_names}.")


def sequentialize(model):
    """Transform a Model into Sequential sub-models and Concatenate layers.

    This function returns an equivalent model where all linear branches are
    replaced by a Sequential sub-model.

    Args:
        model (:obj:`tf.keras.Model`): a Keras model

    Returns:
        :obj:`tf.keras.Model`: a Keras model with Sequential sub-models
    """

    # Clone model to avoid shared layers
    model_clone = clone_model_with_weights(model)

    _check_layers_data_format(model_clone)
    _check_model_input_output(model_clone)
    _check_layer_inbounds(model_clone)

    if isinstance(model_clone, Sequential):
        return model_clone

    def parse_layer(layer, visited_layers, current_branch, output_tensors):
        """Go through a TensorFlow/Keras graph by recursively looking at
        outbound layers.

        Each linear branch is detected and converted to a Sequential sub-model.
        A linear branch ends if:
          - the current layer has multiple outbounds (split connections)
          - the current layer has no outbound (output layer of the model)
          - the next layer is a Concatenate layer
        """

        if layer in visited_layers:
            raise RuntimeError(f"Layer {layer.name} already visited.")

        # Do not visit this layer if all inbound layers were not visited yet
        # (e.g. for Concatenate inbounds)
        # pylint: disable=duplicate-code
        inbound_layers = [n.layer for n in layer.inbound_nodes[0].parent_nodes]
        if set(inbound_layers).difference(visited_layers):
            return
        visited_layers.append(layer)

        # Skip input layer but store its output tensor for graph connection
        if isinstance(layer, InputLayer):
            output_tensors[layer] = layer.output
        # Add layer to graph if layer is Concatenate
        elif isinstance(layer, Concatenate):
            _check_concat_layer_compatibility(layer, inbound_layers)
            # Get input tensors of Concatenate layer
            concat_input_tensors = [output_tensors[l] for l in inbound_layers]
            # Add Concatenate layer to the graph
            output_tensors[layer] = layer(concat_input_tensors)

        else:
            # Add current layer to current branch
            current_branch.append(layer)

            # End current branch and add it to the graph if:
            # - current layer has multiple outbounds (split connections)
            # - current layer has no outbound (output layer of the model)
            # - next layer is Concatenate
            if (len(layer.outbound_nodes) != 1 or
                    isinstance(layer.outbound_nodes[0].layer, Concatenate)):

                parent_nodes = current_branch[0].inbound_nodes[0].parent_nodes
                input_tensor = output_tensors[parent_nodes[0].layer]

                # Create sub-model for current branch and add it to the graph
                submodel = Sequential(current_branch)
                output_tensors[layer] = submodel(input_tensor)
                current_branch.clear()

        # Go to next layer
        for next_layer in [node.layer for node in layer.outbound_nodes]:
            parse_layer(next_layer, visited_layers, current_branch,
                        output_tensors)

    # Go through model layers to detect Sequential branches
    input_layer = model_clone.get_layer(model_clone.input_names[0])
    output_layer = model_clone.get_layer(model_clone.output_names[0])
    output_tensors = {}
    parse_layer(input_layer,
                visited_layers=[],
                current_branch=[],
                output_tensors=output_tensors)

    # Create new model with Sequential sub-models
    model_cut = Model(model_clone.input, output_tensors[output_layer])

    # Clone model to avoid shared layers
    model_cut = clone_model_with_weights(model_cut)

    # Sanity check: the first layer should always be an InputLayer
    if not isinstance(model_cut.layers[0], InputLayer):
        raise ValueError("Incompatible model")
    # Subsequent layers are either Concatenate or Sequential
    for layer in model_cut.layers[1:]:
        if not isinstance(layer, (Concatenate, Sequential)):
            raise ValueError("Incompatible model")

    # If the Model contains a single branch, return it
    if len(model_cut.layers) == 2:
        return model_cut.layers[1]

    return model_cut


def syncretize(model):
    """Align all linear branches of a Model with akida layer sequences.

    The input model must be composed of Sequential submodels and Concatenate
    layers. This function will apply transformations on every Sequential
    submodel and returns an equivalent functional model with akida compatible
    sequences of layers.

    Args:
        model (:obj:`tf.keras.Model`): a Keras model with Sequential submodels.

    Returns:
        :obj:`tf.keras.Model`: a Keras model with akida-compatible Sequential
            submodels.
    """

    def syncretize_sequential(submodel):
        submodel = sequential_remove_useless_layers(submodel)
        submodel = sequential_invert_pooling_activation(submodel)
        submodel = invert_batchnorm_pooling(submodel)
        submodel = fold_batchnorm(submodel)
        return submodel

    if isinstance(model, Sequential):
        return syncretize_sequential(model)

    def parse_submodel(layer, visited_layers, output_tensors):
        if layer in visited_layers:
            raise RuntimeError(f"Layer {layer.name} already visited.")

        # Do not visit this layer if all inbound layers were not visited yet
        # (e.g. for Concatenate inbounds)
        # pylint: disable=duplicate-code
        inbound_layers = [n.layer for n in layer.inbound_nodes[0].parent_nodes]
        if set(inbound_layers).difference(visited_layers):
            return
        visited_layers.append(layer)

        # Add layer to graph if layer is InputLayer or Concatenate
        if isinstance(layer, InputLayer):
            input_clone = clone_layer(layer)
            output_tensors[layer] = input_clone.output
        elif isinstance(layer, Concatenate):
            # Get input tensors of Concatenate layer
            concat_input_tensors = [output_tensors[l] for l in inbound_layers]
            # Add Concatenate layer to the graph
            concat_clone = clone_layer(layer)
            output_tensors[layer] = concat_clone(concat_input_tensors)
        elif isinstance(layer, Sequential):
            # Get input tensors of submodel
            parent_nodes = layer.inbound_nodes[0].parent_nodes
            input_tensor = output_tensors[parent_nodes[0].layer]
            # Transform submodel and add it to the graph
            new_submodel = syncretize_sequential(layer)
            output_tensors[layer] = new_submodel(input_tensor)
        else:
            # pylint: disable=duplicate-code
            raise RuntimeError(f"Layer {layer.name} of type "
                               f"{layer.__class__.__name__} is not supported "
                               f"here.")

        # Go to next layer
        for next_layer in [node.layer for node in layer.outbound_nodes]:
            parse_submodel(next_layer, visited_layers, output_tensors)

    # Go through model layers to transform Sequential branches
    input_layer = model.get_layer(model.input_names[0])
    output_tensors = {}
    parse_submodel(input_layer,
                   visited_layers=[],
                   output_tensors=output_tensors)

    # Create new model with transformed Sequential sub-models
    output_layer = model.get_layer(model.output_names[0])
    return Model(output_tensors[input_layer], output_tensors[output_layer])
