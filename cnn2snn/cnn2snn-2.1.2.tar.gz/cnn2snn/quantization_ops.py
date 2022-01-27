#!/usr/bin/env python
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
"""Weight quantizers API"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import
import keras.backend as K
import tensorflow as tf
from keras.layers import Layer


class WeightQuantizer(Layer):
    """The base class for all weight quantizers.

    This base class must be overloaded as well as the two functions `quantize`
    and `scale_factor`.

    Quantizers derived from this class must be symmetric uniform mid-tread
    quantizers, in order to be compatible with the conversion into an Akida
    model. Quantization is usually done in two steps:

    #. The weights must be first quantized on integer values in the
       range imposed by the bitwidth, e.g. from -7 to 7 for a 4-bit
       quantization.
    #. These integer weights are then reconstructed to float discretized
       values, in the range of the original weights. For example, 4-bit integer
       weights are reconstructed on a grid from -7*qstep to 7*qstep, where
       qstep is the quantization step size between two levels of the uniform
       grid.

    For a full explanation about mid-tread uniform quantization, one can take a
    look at `the Wikipedia page <https://en.wikipedia.org/wiki/Quantization_(signal_processing)#Example>`_.

    The `quantize` function takes as inputs the original weights and must
    return the reconstructed float values after quantization. The
    `scale_factor` function must return the factor used to transform the float
    reconstructed weights into the integer values obtained after step 1. In other
    words, given a set of float weights "w":

     quantize(w) * scale_factor(w) is a set of integer weights.

    The bitwidth defines the number of quantization levels on which the
    weights will be quantized. For instance, a 4-bit quantization gives
    integer values between -7 and 7. More generally, for a n-bit
    quantization, values are ranged from -kmax to kmax where kmax is
    (2^(n-1) - 1).

    Args:
        bitwidth (int): the quantization bitwidth.
    """

    def __init__(self, bitwidth, **kwargs):
        if bitwidth <= 1:
            raise ValueError(
                f"The quantization bitwidth should be higher than 1.\
                    Receives bitwidth {bitwidth}")

        self.bitwidth_ = int(bitwidth)
        self.kmax_ = (2.**(bitwidth - 1) - 1)
        super().__init__(**kwargs)

    def quantize(self, w):
        """Quantizes the specified weights Tensor.

        This function must return a tf.Tensor containing float weights
        discretized on a uniform grid based on the scale factor "sf".
        In other words, the discretized weights must be values among:
        -kmax/sf, ..., -2/sf, -1/sf, 0, 1/sf, 2/sf, ..., kmax/sf

        Args:
            w (:obj:`tensorflow.Tensor`): the weights Tensor to quantize.

        Returns:
            :obj:`tensorflow.Tensor`: a Tensor of quantized weights.

        """
        raise NotImplementedError()

    def scale_factor(self, w):
        """Evaluates the scale factor for the specified weights tf.Tensor.

        This function returns the scale factor to get the quantized integer
        weights from the reconstructed float weights. It is equal to the
        inverse of the quantization step size.

        The scale factor can be a scalar that is applied on the whole tensor
        of weights. It can also be a vector of length the number of filters,
        where each value applies to the weights of the corresponding output
        filter. This is called a per-axis quantization, as opposed to a
        per-tensor quantization. The number of filters is usually the last
        dimension of the weights tensor. More details are given
        `here <https://www.tensorflow.org/lite/performance/quantization_spec?hl=sv#per-axis_vs_per-tensor>`__

        Note that the `quantizer_dw` of a depthwise convolution in a
        QuantizedSeparableConv2D layer must imperatively return a scalar scale
        factor.

        Args:
          w (:obj:`tensorflow.Tensor`): the weights Tensor to quantize.

        Returns:
          :obj:`tensorflow.Tensor`: a Tensor containing a list of scalar values
                (1 or more).

        """
        raise NotImplementedError()

    @property
    def bitwidth(self):
        """Returns the bitwidth of the quantizer"""
        return self.bitwidth_

    def get_config(self):
        config = super().get_config()
        config.update({'bitwidth': self.bitwidth_})
        return config


class LinearWeightQuantizer(WeightQuantizer):
    """An abstract linear weight quantizer

    This abstract class proposes a linear symmetric and uniform quantization
    function. The "linear" term here means that there is no non-linear
    transformation of the weights before the uniform quantization.

    The `scale_factor` function must be overloaded.
    """

    def scale_factor(self, w):
        raise NotImplementedError()

    def quantize(self, w):
        """Linearly quantizes the input weights on a symmetric uniform grid
        based on the scale factor.

        The input weights are directly rounded to the closest discretized
        value, without any transformation on the input weights.

        The gradient is estimated using the Straight-Through Estimator (STE),
        i.e. the gradient is computed as if there were no quantization.
        """
        sf = self.scale_factor(w)
        return tf.clip_by_value(round_through(w * sf), -self.kmax_,
                                self.kmax_) / sf


class StdWeightQuantizer(LinearWeightQuantizer):
    """A uniform quantizer based on weights standard deviation.

    Quantizes the specified weights into 2^bitwidth-1 values centered on zero.
    E.g. with bitwidth = 4, 15 quantization levels: from -7 * qstep to 7 * qstep
    with qstep being the quantization step. The quantization step is defined by:

     qstep = threshold * std(W) / max_value

    with max_value being 2^(bitwidth-1) - 1. E.g with bitwidth = 4, max_value = 7.

    All values below or above threshold * std(W) are automatically assigned to
    the min (resp max) value.

    Args:
        threshold (int): the standard deviation multiplier used to exclude
            outliers.
        bitwidth (int): the quantizer bitwidth defining the number of
            quantized values.
    """

    def __init__(self, threshold=3, bitwidth=4, **kwargs):
        # Having a cast guarantees a check when the parameters are not numbers
        # (e.g.: None)
        self.threshold_ = float(threshold)
        # Initialize parent to store the bitwidth
        super().__init__(bitwidth, **kwargs)

    @staticmethod
    def sigma_(w):
        """Returns the standard deviation(s) of a set of weights"""
        return tf.math.reduce_std(w)

    @property
    def threshold(self):
        """Returns the threshold of the std quantizer"""
        return self.threshold_

    def scale_factor(self, w):
        sigma_scaled = self.sigma_(w) * self.threshold_
        return clip_scale_factor(self.kmax_ / sigma_scaled)

    def get_config(self):
        config = super().get_config()
        config.update({'threshold': self.threshold_})
        return config


class StdPerAxisQuantizer(StdWeightQuantizer):
    """A quantizer that relies on weights standard deviation per axis.

    Quantizes the specified weights into 2^bitwidth-1 values centered on zero.
    E.g. with bitwidth = 4, 15 quantization levels: from -7 * qstep to 7 * qstep
    with qstep being the quantization step. The quantization step is defined by:

     qstep = max_range / max_value

    with:

     - max_range = max(abs(W))
     - max_value = 2^(bitwidth-1) - 1. E.g with bitwidth = 4, max_value = 7.

    This is an evolution of the StdWeightQuantizer that defines the weights
    range per axis.

    The last dimension is used as axis, meaning that the scaling factor is a
    vector with as many values as "filters", or "neurons".

    Note: for a DepthwiseConv2D layer that has a single filter, this
    quantizer is strictly equivalent to the StdWeightQuantizer.

    """

    def sigma_(self, w):
        red_range = tf.range(tf.rank(w) - 1)
        return tf.math.reduce_std(w, red_range)


class MaxQuantizer(LinearWeightQuantizer):
    """A quantizer that relies on maximum range.

    Quantizes the specified weights into 2^bitwidth-1 values centered on zero.
    E.g. with bitwidth = 4, 15 quantization levels: from -7 * qstep to 7 * qstep
    with qstep being the quantization step. The quantization step is defined by:

     qstep = max_range / max_value

    with:

     - max_range = max(abs(W))
     - max_value = 2^(bitwidth-1) - 1. E.g with bitwidth = 4, max_value = 7.

    Args:
        bitwidth (int): the quantizer bitwidth defining the number of
            quantized values.

    """

    def __init__(self, bitwidth=4, **kwargs):
        # Initialize parent to store the bitwidth
        super().__init__(bitwidth, **kwargs)

    @staticmethod
    def max_range_(w):
        """Get the range on which the weights are quantized. This quantizer
        discretizes weights in the range:

         [-max(weights) ; max(weights)]
        """
        return tf.math.reduce_max(tf.math.abs(w))

    def scale_factor(self, w):
        return clip_scale_factor(self.kmax_ / self.max_range_(w))


class MaxPerAxisQuantizer(MaxQuantizer):
    """A quantizer that relies on maximum range per axis.

    Quantizes the specified weights into 2^bitwidth-1 values centered on zero.
    E.g. with bitwidth = 4, 15 quantization levels: from -7 * qstep to 7 * qstep
    with qstep being the quantization step. The quantization step is defined by:

     qstep = max_range / max_value

    with:

     - max_range = max(abs(W))
     - max_value = 2^(bitwidth-1) - 1. E.g with bitwidth = 4, max_value = 7.

    This is an evolution of the MaxQuantizer that defines the max_range per
    axis.

    The last dimension is used as axis, meaning that the scaling factor is a
    vector with as many values as "filters", or "neurons".

    Note: for a DepthwiseConv2D layer that has a single filter, this
    quantizer is strictly equivalent to the MaxQuantizer.

    """

    def max_range_(self, w):
        red_range = tf.range(tf.rank(w) - 1)
        return tf.math.reduce_max(tf.math.abs(w), red_range)


def get(identifier):
    """Returns the weight quantizer corresponding to the identifier.

    The 'identifier' input can take two types: either a weight quantizer
    instance, or a dictionary corresponding to the config serialization
    of a weight quantizer.

    Args:
        identifier (WeightQuantizer or dict): either a WeightQuantizer
            instance or a configuration dictionary to deserialize.

    Returns:
        :obj:`cnn2snn.WeightQuantizer`: a weight quantizer
    """
    if isinstance(identifier, WeightQuantizer):
        return identifier
    if isinstance(identifier, dict):
        return tf.keras.utils.deserialize_keras_object(
            identifier,
            custom_objects={
                'StdWeightQuantizer': StdWeightQuantizer,
                'StdPerAxisQuantizer': StdPerAxisQuantizer,
                'MaxQuantizer': MaxQuantizer,
                'MaxPerAxisQuantizer': MaxPerAxisQuantizer
            })

    raise ValueError(f"Could not interpret identifier {identifier} "
                     "for a weight quantizer object")


def round_through(x):
    """Element-wise rounding to the closest integer with full gradient propagation.
    A trick from [Sergey Ioffe](http://stackoverflow.com/a/36480182).

    """
    rounded = K.round(x)
    return x + K.stop_gradient(rounded - x)


def ceil_through(x):
    """Element-wise ceiling operation (to the closest greater integer) with
    full gradient propagation.

    """
    ceiling_value = tf.math.ceil(x)
    return x + K.stop_gradient(ceiling_value - x)


def clip_scale_factor(scale_factor):
    """ Clips scale factor(s) to 1000, in order to avoid very large scale
    factors and thus very large Akida thresholds after conversion.
    """
    return tf.clip_by_value(scale_factor, 0, 1e3)
