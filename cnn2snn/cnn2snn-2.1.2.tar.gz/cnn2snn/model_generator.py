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
"""Parsing functions to generate an Akida model from a Keras model.
"""

from keras import Sequential
import keras.layers as layers
from akida import (Model, Convolutional, FullyConnected, SeparableConvolutional,
                   InputData, InputConvolutional, Padding, PoolType, LayerType)
from . import quantization_layers as qlayers
from .weights_ops import set_layer_variables


def _get_padding(str_padding):
    if str_padding == 'same':
        return Padding.Same
    return Padding.Valid


def _parse_input_data(layer, params):
    if len(layer.input_shape) == 2:
        params["input_shape"] = (1, 1, int(layer.input_shape[1]))

    else:
        params["input_shape"] = (int(layer.input_shape[2]),
                                 int(layer.input_shape[1]),
                                 int(layer.input_shape[3]))
    params['name'] = layer.name + "_input"


def _parse_input_conv(layer, params, input_shift):
    if not isinstance(layer, qlayers.QuantizedConv2D):
        raise TypeError(f"First layer {layer.name} must be QuantizedConv2D "
                        "when input_is_image=True. Received layer of type "
                        f"{layer.__class__.__name__}")
    params["input_shape"] = (int(layer.input_shape[2]),
                             int(layer.input_shape[1]),
                             int(layer.input_shape[3]))
    params["padding"] = _get_padding(layer.padding)
    params["kernel_size"] = (layer.kernel_size[1], layer.kernel_size[0])
    params["filters"] = int(layer.kernel.shape[3])
    params["weights_bits"] = layer.quantizer.bitwidth
    params["kernel_stride"] = (layer.strides[1], layer.strides[0])
    params["name"] = layer.name
    params["padding_value"] = int(input_shift)


def _parse_conv(layer, params):
    if not isinstance(layer, qlayers.QuantizedConv2D):
        raise TypeError(f"Layer {layer.name} was expected to be "
                        "QuantizedConv2D")
    params["padding"] = _get_padding(layer.padding)
    params["kernel_size"] = (layer.kernel_size[1], layer.kernel_size[0])
    params["filters"] = int(layer.kernel.shape[3])
    params["weights_bits"] = layer.quantizer.bitwidth
    params["kernel_stride"] = (layer.strides[1], layer.strides[0])
    params["name"] = layer.name


def _parse_separable_conv(layer, params):
    if not isinstance(layer, qlayers.QuantizedSeparableConv2D):
        raise TypeError(f"Layer {layer.name} was expected to be "
                        "QuantizedSeparableConv2D")
    if layer.quantizer_dw.bitwidth != layer.quantizer.bitwidth:
        raise ValueError(f"Quantized layer {layer.name} must have the same "
                         f"bitwidth for depthwise and pointwise quantizers.")
    params["padding"] = _get_padding(layer.padding)
    params["kernel_size"] = (layer.kernel_size[1], layer.kernel_size[0])
    # filters is set to the number of filters of the depthwise
    params["filters"] = int(layer.pointwise_kernel.shape[3])
    params["weights_bits"] = layer.quantizer.bitwidth
    params["kernel_stride"] = (layer.strides[1], layer.strides[0])
    params["name"] = layer.name


def _parse_dense(layer, params):
    if not isinstance(layer, qlayers.QuantizedDense):
        raise TypeError(f"Layer {layer.name} was expected to be "
                        "QuantizedDense")
    params["units"] = layer.units
    params["weights_bits"] = layer.quantizer.bitwidth
    params["name"] = layer.name


def _parse_max_pooling(layer, params):
    if not isinstance(layer, layers.MaxPooling2D):
        raise TypeError(f"Layer {layer.name} was expected to be MaxPooling2D")
    params["pool_type"] = PoolType.Max
    params["pool_size"] = (layer.pool_size[1], layer.pool_size[0])
    params["pool_stride"] = (layer.strides[1], layer.strides[0])


def _parse_global_average_pooling(layer, params):
    if not isinstance(layer, layers.GlobalAveragePooling2D):
        raise TypeError(f"Layer {layer.name} was expected to be "
                        "GlobalAveragePooling2D")
    params["pool_type"] = PoolType.Average


def _create_akida_layer(layer_type, params):
    """Returns an Akida layer based on the input dictionary containing the
    parameters.

    """
    if layer_type == LayerType.InputData:
        layer_ak = InputData(**params)
    elif layer_type == LayerType.InputConvolutional:
        layer_ak = InputConvolutional(**params)
    elif layer_type == LayerType.Convolutional:
        layer_ak = Convolutional(**params)
    elif layer_type == LayerType.SeparableConvolutional:
        layer_ak = SeparableConvolutional(**params)
    elif layer_type == LayerType.FullyConnected:
        layer_ak = FullyConnected(**params)

    return layer_ak


def generate_model(model, input_scaling, input_is_image):
    """Generates an Akida model.

    This function creates an Akida model by parsing every Sequential branch of
    the input model: for each submodel, Akida layers are created sequentially
    and added to the Akida model. When coming across a Concatenate layer, an
    Akida Concat layer is added to the model with the corresponding input
    layers.

    Args:
        model (:obj:`tf.keras.Model`): a Keras model to convert.
        input_scaling (2-element tuple): the input factor and shift.
        input_is_image (bool): True if input is an image.

    Returns:
        :obj:`akida.Model`: the generated Akida model.

    """

    model_ak = Model()
    previous_layer_ak = None

    if not input_is_image:
        # Handle first akida layer as InputData and add it to the model
        params = {}
        _parse_input_data(model, params)
        layer_ak = InputData(**params)
        model_ak.add(layer_ak)
        previous_layer_ak = layer_ak

    if isinstance(model, Sequential):
        sequential_convert_to_akida_layers(model, model_ak, input_scaling,
                                           previous_layer_ak)
    return model_ak


def sequential_convert_to_akida_layers(model,
                                       model_ak,
                                       input_scaling,
                                       previous_layer_ak=None):
    """Converts a Sequential model into Akida layers.

    The Sequential model is converted into Akida layers that are directly added
    to the Akida model. The Akida weights and thresholds are also computed.

    The input Sequential model must have been transformed in advance: an Akida
    layer will start with a neural layer and ends with an activation layer
    (except) for the last Akida layer, with an optional pooling layer in
    between.

    Args:
        model (:obj:`tf.keras.Model`): a Keras Sequential model to convert.
        model_ak (:obj:`akida.Model`): the generated Akida model to fill.
        input_scaling (2-element tuple): the input factor and shift of the
            current submodel.
        previous_layer_ak (:obj:`akida.Layer`): the previous Akida layer in the
            model.

    Returns:
        :obj:`akida.Layer`: the last Akida layer of the converted sequence.
        tuple: the input scaling of the last layer, to be used by the next
            sequence to convert.
    """

    assert isinstance(model, Sequential)

    quantized_neural_layers = (qlayers.QuantizedConv2D,
                               qlayers.QuantizedSeparableConv2D,
                               qlayers.QuantizedDense)
    ignore_list = (layers.Flatten, layers.Reshape, layers.Activation,
                   layers.Softmax)

    next_layer_to_parse = 0
    layer_neural = layer_activation = layer_globalavgpool = layer_ak_type = None

    # If this sequence is the first of the functional model and there is no
    # previous Akida layer, we must handle it as InputConvolutional.
    layer_ak = previous_layer_ak
    if previous_layer_ak is None:
        # Handle first akida layer as InputConvolutional
        layer_ak_type = LayerType.InputConvolutional
        (layer_neural, params,
         next_layer_to_parse) = _handle_input_conv_layer(model, input_scaling)
        previous_layer_ak = []
    else:
        previous_layer_ak = [previous_layer_ak]

    for layer in model.layers[next_layer_to_parse:]:
        if isinstance(layer, quantized_neural_layers):
            layer_neural = layer
            layer_ak_type, params = _parse_neural_layer(layer)
            _check_weight_bitwidth(params['weights_bits'], layer.name)
        elif isinstance(layer, layers.MaxPool2D):
            _parse_max_pooling(layer, params)
        elif isinstance(layer, layers.GlobalAvgPool2D):
            layer_globalavgpool = layer
            _parse_global_average_pooling(layer, params)
        elif isinstance(layer, qlayers.QuantizedActivation):
            layer_activation = layer
            _check_activation_bitwidth(layer_activation)
            params['act_bits'] = layer_activation.bitwidth

            # An activation layer ends a block for an Akida layer : create
            # the corresponding Akida layer and set weights/thresholds
            layer_ak = _create_akida_layer(layer_ak_type, params)
            model_ak.add(layer_ak, previous_layer_ak)
            set_layer_variables(layer_ak, input_scaling, layer_neural,
                                layer_activation, layer_globalavgpool)

            # Refresh variables to start the next Akida layer
            input_scaling = (1 / layer_activation.step_height.numpy(), 0)
            layer_neural = layer_activation = layer_globalavgpool = layer_ak_type = None
            previous_layer_ak = [layer_ak]
        elif isinstance(layer, ignore_list):
            pass
        else:
            # If you got here, the layer is not supported: raise an error.
            raise RuntimeError(f"Layer {layer.name}: unsupported type "
                               f"{layer.__class__.__name__}.")

    # Handle last layer if there is no activation
    if layer_neural is not None:
        params["activation"] = False
        layer_ak = _create_akida_layer(layer_ak_type, params)
        model_ak.add(layer_ak, previous_layer_ak)
        set_layer_variables(layer_ak, input_scaling, layer_neural,
                            layer_activation, layer_globalavgpool)

    return layer_ak, input_scaling


def _parse_neural_layer(layer):
    """Parses neural quantized layer and returns the params to create the
    corresponding Akida layer.

    Args:
        layer (:obj:`tf.keras.Layer`): a neural quantized layer to convert.

    Returns:
        :obj:`akida.LayerType`: the type of the future Akida layer
        dict: the parameters to create the future Akida layer
    """
    params = {}
    if isinstance(layer, qlayers.QuantizedConv2D):
        _parse_conv(layer, params)
        layer_ak_type = LayerType.Convolutional
    elif isinstance(layer, qlayers.QuantizedSeparableConv2D):
        _parse_separable_conv(layer, params)
        layer_ak_type = LayerType.SeparableConvolutional
    elif isinstance(layer, qlayers.QuantizedDense):
        _parse_dense(layer, params)
        layer_ak_type = LayerType.FullyConnected
    return layer_ak_type, params


def _handle_input_conv_layer(model, input_scaling):
    """Parses the first conv layer to create the future InputConvolutional Akida
    layer.

    This function also returns the layer after the first conv layer, which is
    the starting point for parsing the rest of the model. Note that a Sequential
    model with input_is_image=True (i.e. InputConvolutional) must start with a
    QuantizedConv2D layer with an optional Rescaling layer before.

    Args:
        model (:obj:`tf.keras.Model`): the Sequential model to parse.

    Returns:
        :obj:`tf.keras.Layer`: the first QuantizedConv2D layer.
        dict: the parameters to create the future Akida layer.
        int: the layer after the first conv layer.
    """

    next_neural_layer_id = 0
    # If next layer is Rescaling layer, skip it
    if isinstance(model.layers[next_neural_layer_id], layers.Rescaling):
        next_neural_layer_id += 1

    params = {}
    layer_neural = model.layers[next_neural_layer_id]
    _parse_input_conv(layer_neural, params, input_scaling[1])

    return layer_neural, params, next_neural_layer_id + 1


def _check_activation_bitwidth(layer):
    """Checks that activation bitwidth is either 1, 2 or 4.
    """

    if layer.bitwidth not in (1, 2, 4):
        raise ValueError("Activation bitwidth must be in (1, 2, 4). Receives "
                         f"bitwidth {layer.bitwidth} in layer '{layer.name}'.")


def _check_concat_input_bitwidths(layer, concat_input_layers):
    """Checks that inbound layers of a Concat layer have the same output
    bitwidth.

    Args:
        layer (:obj:`tf.keras.Layer`): the Keras Concatenate layer.
        concat_input_layers (list): Akida inbound layers of the Concat layer.
    """

    output_bitwidths = [l.parameters.act_bits for l in concat_input_layers]

    if len(set(output_bitwidths)) > 1:
        raise RuntimeError(
            f"Concatenate layer '{layer.name}' must have inbound layers with "
            f"the same activation bitwidth. Receives bitwidths "
            f"{output_bitwidths}.")


def _check_weight_bitwidth(bitwidth, layer_name):
    """Checks that weight bitwidth is supported by Akida: 2, 4 or 8 bits.
    """

    if bitwidth not in (2, 4, 8):
        raise ValueError("Weight bitwidth must be in (2, 4, 8). Receives "
                         f"bitwidth {bitwidth} in layer '{layer_name}'.")
