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
"""Conversion of a Keras/CNN2SNN model into an Akida model"""

import os
import tensorflow as tf
from keras import Sequential
from .model_generator import generate_model
from .transforms import sequentialize, syncretize
from .compatibility_checks import check_sequential_compatibility


def _sync_and_check_model(model, input_is_image):
    # Make sure the model is sequential
    seq_model = sequentialize(model)

    # For now, we support only models with a single branch
    if not isinstance(seq_model, Sequential):
        raise RuntimeError(
            "The model contains more than one sequential branch.")

    # Transform model to prepare conversion: change the order of layers,
    # fold BN, freeze quantizers, remove useless layers.
    sync_model = syncretize(seq_model)

    # Check model compatibility
    check_sequential_compatibility(sync_model, input_is_image)

    return sync_model


def convert(model, file_path=None, input_scaling=None, input_is_image=True):
    """Converts a Keras quantized model to an Akida one.

    After quantizing a Keras model with :func:`cnn2snn.quantize`, it can be
    converted to an Akida model. By default, the conversion expects that the
    Akida model takes 8-bit images as inputs. ``input_scaling`` defines how the
    images have been rescaled to be fed into the Keras model (see note below).

    If inputs are spikes, you can set ``input_is_image=False``. In this case,
    Akida inputs are then expected to be integers between 0 and 15.

    Note:
        The relationship between Keras and Akida inputs is defined as::

            input_akida = input_scaling[0] * input_keras + input_scaling[1].

        If a :class:`tf.keras.layers.Rescaling`
        layer is present as first layer of the model, ``input_scaling`` must
        be None: the :class:`Rescaling` parameters will be used to compute the
        input scaling.

    Examples:

        >>> # Convert a quantized Keras model with Keras inputs as images
        >>> # rescaled between -1 and 1
        >>> inputs_akida = images.astype('uint8')
        >>> inputs_keras = (images.astype('float32') - 128) / 128
        >>> model_akida = cnn2snn.convert(model_keras, input_scaling=(128, 128))
        >>> model_akida.evaluate(inputs_akida)

        >>> # Convert a quantized Keras model with Keras inputs as spikes and
        >>> # input scaling of (2.5, 0). Akida spikes must be integers between
        >>> # 0 and 15
        >>> inputs_akida = spikes.astype('uint8')
        >>> inputs_keras = spikes.astype('float32') / 2.5
        >>> model_akida = cnn2snn.convert(model_keras, input_scaling=(2.5, 0))
        >>> model_akida.evaluate(inputs_akida)

        >>> # Convert and directly save the Akida model to fbz file.
        >>> cnn2snn.convert(model_keras, 'model_akida.fbz')

    Args:
        model (:obj:`tf.keras.Model`): a tf.keras model
        file_path (str, optional): destination for the akida model.
            (Default value = None)
        input_scaling (2 elements tuple, optional): value of the input scaling.
            (Default value = None)
        input_is_image (bool, optional): True if input is an image (3-D 8-bit
            input with 1 or 3 channels) followed by QuantizedConv2D. Akida model
            input will be InputConvolutional. If False, Akida model input will
            be InputData. (Default value = True)

    Returns:
        :obj:`akida.Model`: an Akida model.

    Raises:
        ValueError: If ``input_scaling[0]`` is null or negative.
        ValueError: If a :class:`Rescaling` layer is present and
            ``input_scaling`` is not None.
        SystemError: If Tensorflow is not run in eager mode.
    """

    if not tf.executing_eagerly():
        raise SystemError("Tensorflow eager execution is disabled. "
                          "It is required to convert Keras weights to Akida.")

    # Check Keras Rescaling layer to replace the input_scaling
    rescaling_input_scaling = _get_rescaling_layer_params(model)
    if rescaling_input_scaling is not None and input_scaling is not None:
        raise ValueError("If a Rescaling layer is present in the model, "
                         "'input_scaling' argument must be None. Receives "
                         f"{input_scaling}.")

    input_scaling = rescaling_input_scaling or input_scaling or (1, 0)

    if input_scaling[0] <= 0:
        raise ValueError("The scale factor 'input_scaling[0]' must be strictly"
                         f" positive. Receives: input_scaling={input_scaling}")

    # Prepare model for conversion and check its compatibility
    sync_model = _sync_and_check_model(model, input_is_image)

    # Generate Akida model with converted weights/thresholds
    ak_model = generate_model(sync_model, input_scaling, input_is_image)

    # Save model if file_path is given
    if file_path:
        # Create directories
        dir_name, base_name = os.path.split(file_path)
        if base_name:
            file_root, file_ext = os.path.splitext(base_name)
            if not file_ext:
                file_ext = '.fbz'
        else:
            file_root = model.name
            file_ext = '.fbz'

        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        save_path = os.path.join(dir_name, file_root + file_ext)
        ak_model.save(save_path)

    return ak_model


def _get_rescaling_layer_params(model):
    """Computes the new input scaling retrieved from the Keras
    `Rescaling` layer.

    Keras Rescaling layer works as:

     input_k = scale * input_ak + offset

    CNN2SNN input scaling works as:

     input_ak = input_scaling[0] * input_k + input_scaling[1]

    Equivalence leads to:

     input_scaling[0] = 1 / scale
     input_scaling[1] = -offset / scale

    Args:
        model (:obj:`tf.keras.Model`): a tf.keras model.

    Returns:
        tuple: the new input scaling from the Rescaling layer or None if
            no Rescaling layer is at the beginning of the model.
    """

    Rescaling = tf.keras.layers.Rescaling
    for layer in model.layers[:2]:
        if isinstance(layer, Rescaling):
            return (1 / layer.scale, -layer.offset / layer.scale)
    return None


def check_model_compatibility(model, input_is_image=True):
    r"""Checks if a Keras model is compatible for cnn2snn conversion.

    This function doesn't convert the Keras model to an Akida model
    but only checks if the model design is compatible.

    Note that this function doesn't check if the quantization bitwidths (weights
    or activations) are supported by the Akida Execution Engine or by the Akida
    NSoC.

    **1. How to build a compatible Keras quantized model?**

    The following lines give details and constraints on how to build a Keras
    model compatible for the conversion to an Akida model.


    **2. General information about layers**

    An Akida layer must be seen as a block of Keras layers starting with a
    processing layer (Conv2D, SeparableConv2D,
    Dense). All blocks of Keras layers except the last block must have
    exactly one activation layer (ReLU or ActivationDiscreteRelu). Other
    optional layers can be present in a block such as a pooling layer or a
    batch normalization layer.
    Here are all the supported Keras layers for an Akida-compatible model:

    - Processing layers:

      - tf.keras Conv2D/SeparableConv2D/Dense
      - cnn2snn QuantizedConv2D/QuantizedSeparableConv2D/QuantizedDense

    - Activation layers:

      - tf.keras ReLU
      - cnn2snn ActivationDiscreteRelu
      - any increasing activation function (only for the last block of layers)
        such as softmax, sigmoid set as last layer. This layer must derive from
        tf.keras.layers.Activation, and it will be removed during conversion to
        an Akida model.

    - Pooling layers:

      - MaxPool2D
      - GlobalAvgPool2D

    - BatchNormalization
    - Dropout
    - Flatten
    - Input
    - Reshape

    Example of a block of Keras layers::

              ----------
              | Conv2D |
              ----------
                  ||
                  \/
        ----------------------
        | BatchNormalization |
        ----------------------
                  ||
                  \/
             -------------
             | MaxPool2D |
             -------------
                  ||
                  \/
       --------------------------
       | ActivationDiscreteRelu |
       --------------------------


    **3. Constraints about inputs**

    An Akida model can accept two types of inputs: sparse events or 8-bit
    images. Whatever the input type, the Keras inputs must respect the
    following relation:

        input_akida = scale * input_keras + shift

    where the Akida inputs must be positive integers, the input scale must be
    a float value and the input shift must be an integer. In other words,
    scale * input_keras must be integers.

    Depending on the input type:

    - if the inputs are events (sparse), the first layer of the Keras model can
      be any processing layer. The input shift must be zero.
    - if the inputs are images, the first layer must be a Conv2D
      layer.


    **4. Constraints about layers' parameters**

    To be Akida-compatible, the Keras layers must observe the following rules:

    - all layers with the 'data_format' parameter must be 'channels_last'
    - all processing quantized layers and ActivationDiscreteRelu must have a
      valid quantization bitwidth
    - a Dense layer must have an input shape of (N,) or (1, 1, N)
    - a BatchNormalization layer must have 'axis' set to -1 (default)
    - a BatchNormalization layer cannot have negative gammas
    - Reshape layers can only be used to transform a tensor of shape (N,) to a
      tensor of shape (1, 1, N), and vice-versa
    - only one pooling layer can be used in each block
    - a MaxPool2D layer must have the same 'padding' as the corresponding
      processing quantized layer

    **5. Constraints about the order of layers**

    To be Akida-compatible, the order of Keras layers must observe the following
    rules:

    - a block of Keras layers must start with a processing quantized layer
    - where present, a BatchNormalization/GlobalAvgPool2D layer must be placed
      before the activation
    - a Flatten layer can only be used before a Dense layer
    - an Activation layer other than ReLU can only be used in the last layer


    Args:
        model (:obj:`tf.keras.Model`): the model to check.
        input_is_image (bool, optional): True if input is an image (8-bit input
            with 1 or 3 channels) followed by QuantizedConv2D. Akida model
            input will be InputConvolutional. If False, Akida model input will
            be InputData. (Default value = True)
    """
    try:
        _sync_and_check_model(model, input_is_image)
        return True
    except RuntimeError as e:
        print(
            "The Keras quantized model is not compatible for a conversion "
            "to an Akida model:\n", str(e))
        return False
