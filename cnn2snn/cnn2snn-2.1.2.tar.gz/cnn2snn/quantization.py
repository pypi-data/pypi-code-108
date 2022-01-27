# ******************************************************************************
# Copyright 2020 Brainchip Holdings Ltd.
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
"""Model quantization API"""

import tensorflow as tf
from keras.models import clone_model
from keras.layers import Conv2D, SeparableConv2D, Dense, ReLU, Layer

from .quantization_ops import MaxQuantizer, MaxPerAxisQuantizer
from .quantization_layers import (QuantizedConv2D, QuantizedSeparableConv2D,
                                  QuantizedDense, ActivationDiscreteRelu,
                                  QuantizedActivation)
from .transforms import (sequentialize, invert_batchnorm_pooling,
                         fold_batchnorm, normalize_separable_layer)
from .cnn2snn_objects import cnn2snn_objects

keras_neural_layers = (Conv2D, SeparableConv2D, Dense)
cnn2snn_neural_layers = (QuantizedConv2D, QuantizedSeparableConv2D,
                         QuantizedDense)
supported_neural_layers = keras_neural_layers + cnn2snn_neural_layers


def quantize(model,
             weight_quantization=0,
             activ_quantization=0,
             input_weight_quantization=None,
             fold_BN=True,
             quantizer_function=None):
    """Converts a standard sequential Keras model to a CNN2SNN Keras quantized
    model, compatible for Akida conversion.

    This function returns a Keras model where the standard neural layers
    (Conv2D, SeparableConv2D, Dense) and the ReLU activations are replaced with
    CNN2SNN quantized layers (QuantizedConv2D, QuantizedSeparableConv2D,
    QuantizedDense, ActivationDiscreteRelu).

    Several transformations are applied to the model:
    - the order of MaxPool and BatchNormalization layers are inverted so that
    BatchNormalization always happens first,
    - the batch normalization layers are folded into the previous layers.

    This new model can be either directly converted to akida, or first
    retrained for a few epochs to recover any accuracy loss.

    Args:
        model (tf.keras.Model): a standard Keras model
        weight_quantization (int): sets all weights in the model to have
            a particular quantization bitwidth except for the weights in the
            first layer.

            * '0' implements floating point 32-bit weights.
            * '2' through '8' implements n-bit weights where n is from 2-8 bits.
        activ_quantization (int): sets all activations in the model to have a
            particular activation quantization bitwidth.

            * '0' implements floating point 32-bit activations.
            * '1' through '8' implements n-bit weights where n is from 1-8 bits.
        input_weight_quantization (int): sets weight quantization in the first
            layer. Defaults to weight_quantization value.

            * 'None' implements the same bitwidth as the other weights.
            * '0' implements floating point 32-bit weights.
            * '2' through '8' implements n-bit weights where n is from 2-8 bits.
        fold_BN (bool): enable folding batch normalization layers with their
             corresponding neural layer.
        quantizer_function (function): callable that takes as argument the layer
            instance to be quantized and the corresponding default quantizer and
            returns the quantizer to use.

    Returns:
        tf.keras.Model: a quantized Keras model
    """

    # Overrides input weight quantization if None
    if input_weight_quantization is None:
        input_weight_quantization = weight_quantization

    if fold_BN:
        # Identify sequential branches
        seq_model = sequentialize(model)
        # Invert batch normalization and pooling
        model_t = invert_batchnorm_pooling(seq_model)
        # Fold batch norm layers with corresponding neural layers
        model_t = fold_batchnorm(model_t)
    else:
        # Keep original model without transformation
        model_t = model

    # Convert neural layers and ReLU to CNN2SNN quantized layers
    first_neural_layer = True

    def replace_layer(layer):
        nonlocal first_neural_layer
        if isinstance(layer, (ReLU, QuantizedActivation)):
            return _quantize_activation_layer(layer, activ_quantization)
        if type(layer) in supported_neural_layers:
            if first_neural_layer:
                bitwidth = input_weight_quantization
                first_neural_layer = False
            else:
                bitwidth = weight_quantization
            return _convert_to_quantized_layer(layer, bitwidth,
                                               quantizer_function)
        return layer.__class__.from_config(layer.get_config())

    with tf.keras.utils.custom_object_scope(cnn2snn_objects):
        new_model = clone_model(model_t, clone_function=replace_layer)
    new_model.set_weights(model_t.get_weights())

    return new_model


def quantize_layer(model, target_layer, bitwidth, quantizer_function=None):
    """Quantizes a specific layer with the given bitwidth.

    This function returns a Keras model where the target layer is quantized.
    All other layers are preserved.
    If the target layer is a native Keras layer (Conv2D, SeparableConv2D, Dense,
    ReLU), it is replaced by a CNN2SNN quantized layer (QuantizedConv2D,
    QuantizedSeparableConv2D, QuantizedDense, ActivationDiscreteRelu). If
    the target layer is an already quantized layer, only the bitwidth is
    modified.

    Examples:

        >>> # Quantize a layer of a native Keras model
        >>> model = tf.keras.Sequential([
        ...     tf.keras.layers.Dense(5, input_shape=(3,)),
        ...     tf.keras.layers.Softmax()])
        >>> model_quantized = cnn2snn.quantize_layer(model,
        ...                                          target_layer=0,
        ...                                          bitwidth=4)
        >>> assert isinstance(model_quantized.layers[0], cnn2snn.QuantizedDense)
        >>> print(model_quantized.layers[0].quantizer.bitwidth)
        4

        >>> # Quantize a layer of an an already quantized layer
        >>> model_quantized = cnn2snn.quantize_layer(model_quantized,
        ...                                          target_layer=0, bitwidth=2)
        >>> print(model_quantized.layers[0].quantizer.bitwidth)
        2

    Args:
        model (tf.keras.Model): a standard Keras model
        target_layer: a standard or quantized Keras layer to be
            converted, or the index or name of the target layer.
        bitwidth (int): the desired quantization bitwidth. If zero, no
            quantization will be applied.
        quantizer_function (function): callable that takes as argument the layer
            instance to be quantized and the corresponding default quantizer and
            returns the quantizer to use.

    Returns:
        tf.keras.Model: a quantized Keras model

    Raises:
        ValueError: In case of invalid target layer
        ValueError: If bitwidth is not greater than zero
    """

    if not bitwidth > 0:
        raise ValueError("Only bitwidth greater than zero is supported. "
                         f"Receives bitwidth {bitwidth}.")

    if isinstance(target_layer, int):
        layer_to_quantize = model.layers[target_layer]
    elif isinstance(target_layer, str):
        layer_to_quantize = model.get_layer(target_layer)
    elif isinstance(target_layer, Layer):
        layer_to_quantize = target_layer
    else:
        raise ValueError("Target layer argument is not recognized")

    def replace_layer(layer):
        if layer == layer_to_quantize:
            if isinstance(layer, (ReLU, QuantizedActivation)):
                return _quantize_activation_layer(layer, bitwidth)
            if type(layer) in supported_neural_layers:
                return _convert_to_quantized_layer(layer, bitwidth,
                                                   quantizer_function)
            return layer.__class__.from_config(layer.get_config())
        return layer.__class__.from_config(layer.get_config())

    with tf.keras.utils.custom_object_scope(cnn2snn_objects):
        new_model = clone_model(model, clone_function=replace_layer)
    new_model.set_weights(model.get_weights())

    return new_model


def _convert_to_quantized_layer(layer, bitwidth, quantizer_function=None):
    """Quantizes a standard Keras layer (Conv2D, SeparableConv2D, Dense) or a
    CNN2SNN quantized layer (QuantizedConv2D, QuantizedSeparableConv2D,
    QuantizedDense) to a CNN2SNN quantized layer with given bitwidth.

    A native Keras layer will be converted to a quantized layer with a
    MaxPerAxisQuantizer if quantizer_function is not specified.

    Args:
        layer (tf.keras.Layer): a standard Keras (Conv2D, SeparableConv2D or
            Dense) or quantized (QuantizedConv2D, QuantizedSeparableConv2D,
            QuantizedDense) layer.
        bitwidth (int): the desired weight quantization bitwidth. If zero, the
            Keras neural layer will be returned as it is.
        quantizer_function (function): callable that takes as argument the layer
            instance to be quantized and the corresponding default quantizer and
            returns the quantizer to use.

    Returns:
        :obj:`keras.Layer`: a CNN2SNN quantized Keras layer

    Raises:
        ValueError: if a quantized layer is quantized with bitwidth 0.
    """
    config = layer.get_config()

    # Handle case where bitwidth=0
    if bitwidth == 0:
        if isinstance(layer, cnn2snn_neural_layers):
            raise ValueError(f"A quantized layer cannot be quantized with "
                             f"bitwidth 0. Receives layer {layer.name} of type "
                             f" {layer.__class__.__name__}.")
        return layer.__class__.from_config(config)

    # Set quantizer with expected bitwidth
    if not 'quantizer' in config:
        quantizer = MaxPerAxisQuantizer(bitwidth=bitwidth)
        if quantizer_function is not None:
            quantizer = quantizer_function(layer, quantizer)
        config['quantizer'] = quantizer
    else:
        config['quantizer']['config']['bitwidth'] = bitwidth

    # Function to handle unsupported arguments in config
    def pop_unsupported_args(class_type):
        for arg, default_value in class_type.unsupported_args.items():
            if (arg in config and config[arg] != default_value):
                raise RuntimeError(
                    f"Argument '{arg}' in layer '{layer.name}' is only "
                    f"supported with default value '{default_value}'. "
                    f"Receives '{config[arg]}'.")
            config.pop(arg, None)

    # Return quantized layer, based on the config
    if isinstance(layer, Conv2D):
        pop_unsupported_args(QuantizedConv2D)
        return QuantizedConv2D.from_config(config)

    if isinstance(layer, SeparableConv2D):
        if not 'quantizer_dw' in config:
            # Normalize depthwise weights (i.e. equalize kernel ranges)
            normalize_separable_layer(layer)
            quantizer = MaxQuantizer(bitwidth=bitwidth)
            if quantizer_function is not None:
                quantizer = quantizer_function(layer, quantizer)
            config['quantizer_dw'] = quantizer
        else:
            config['quantizer_dw']['config']['bitwidth'] = bitwidth
        pop_unsupported_args(QuantizedSeparableConv2D)
        return QuantizedSeparableConv2D.from_config(config)

    if isinstance(layer, Dense):
        pop_unsupported_args(QuantizedDense)
        return QuantizedDense.from_config(config)

    return None


def _quantize_activation_layer(layer, bitwidth):
    """Quantizes a Keras ReLU layer or a CNN2SNN quantized activation to the
    given bitwidth. A ReLU layer is converted to an ActivationDiscreteRelu
    layer.

    Args:
        layer (tf.keras.Layer): an activation layer (ReLU or CNN2SNN quantized
            activation)
        bitwidth (int): the desired quantization bitwidth. If zero, the ReLU
            layer will be returned as it is.

    Returns:
        :obj:`keras.Layer`: a CNN2SNN quantized Keras layer

    Raises:
        ValueError: if a quantized activation layer is quantized with
            bitwidth 0.
    """

    if bitwidth == 0:
        if isinstance(layer, QuantizedActivation):
            raise ValueError(f"A quantized activation cannot be quantized with "
                             f"bitwidth 0. Receives layer {layer.name} of type "
                             f" {layer.__class__.__name__}.")
        return layer.__class__.from_config(layer.get_config())

    if isinstance(layer, ReLU):
        return ActivationDiscreteRelu(bitwidth, name=layer.name)

    config = layer.get_config()
    config['bitwidth'] = bitwidth
    return layer.__class__.from_config(config)
