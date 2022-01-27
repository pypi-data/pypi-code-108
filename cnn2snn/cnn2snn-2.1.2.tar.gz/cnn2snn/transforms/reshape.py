#!/usr/bin/env python
# ******************************************************************************
# Copyright 2022 Brainchip Holdings Ltd.
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
"""Input layer size reshaping for Keras/CNN2SNN Sequential models.
"""

from keras import Sequential, Input

from .clone import clone_model_with_weights


def reshape(model_keras, input_height, input_width):
    """ Rescales the model by changing its input size.

    Args:
        model_keras (:obj:`tf.keras.Model`): Keras model to rescale
        input_height (int): desired model input height
        input_width (int): desired model input width

    Returns:
        keras.Model: the rescaled model
    """
    # The reshape function is restricted to Sequential models only
    assert isinstance(model_keras, Sequential)

    # Create the desired input
    input_shape = (input_height, input_width, model_keras.input.shape[-1])
    new_input = Input(input_shape)

    # Clone the model and replace input layer
    clone = clone_model_with_weights(model_keras, input_tensors=new_input)
    return clone
