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
"""CNN2SNN toolkit to quantize and convert Keras models into Akida-compatible
models.
"""

from .utils import load_quantized_model

from .cnn2snn_objects import cnn2snn_objects
from .converter import convert, check_model_compatibility
from .quantization_ops import (StdWeightQuantizer, StdPerAxisQuantizer,
                               MaxQuantizer, MaxPerAxisQuantizer)
from .quantization_layers import (QuantizedConv2D, QuantizedDepthwiseConv2D,
                                  QuantizedDense, QuantizedSeparableConv2D,
                                  ActivationDiscreteRelu, QuantizedReLU,
                                  QuantizedActivation)
from .quantization import quantize, quantize_layer
