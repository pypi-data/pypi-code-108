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
"""Command-line interface"""

import argparse
import re
import os

from .converter import convert
from .quantization import quantize
from .utils import load_quantized_model
from .transforms import reshape


def quantize_model(model_path, wq, aq, iq, fold_BN):
    """Wrapper to quantize model"""
    model = load_quantized_model(model_path)
    if iq == -1:
        iq = wq
    model_q = quantize(model, wq, aq, iq, fold_BN)
    # Extract base name
    base_name = os.path.splitext(model_path)[0]
    # Cross-platform path may contain alpha characters, /, \ and :
    path_re = r"([\w/\\:~]+)"
    # Quantization suffix has a well-identified structure
    suffix_re = r"(_iq\d_wq\d_aq\d)"
    p = re.compile(path_re + suffix_re)
    # Look for an existing quantization suffix in the base name
    m = p.match(base_name)
    if m:
        # Only keep the actual base name (group(2) contains the suffix)
        base_name = m.group(1)
    out_path = f"{base_name}_iq{iq}_wq{wq}_aq{aq}.h5"
    model_q.save(out_path, include_optimizer=False)
    print(f"Model successfully quantized and saved as {out_path}.")


def convert_model(model_path, input_scaling, is_image):
    """Wrapper to convert model"""
    base_name = os.path.splitext(model_path)[0]
    q_model = load_quantized_model(model_path)
    ak_model = convert(q_model,
                       input_scaling=input_scaling,
                       input_is_image=is_image)
    out_path = f"{base_name}.fbz"
    ak_model.save(out_path)
    print(f"Model successfully converted and saved as {out_path}.")


def reshape_model(model_path, input_height, input_width):
    """Wrapper to reshape model"""
    # Load the original model file
    base_model = load_quantized_model(model_path)

    # Extract base name
    base_name = os.path.splitext(model_path)[0]

    model = reshape(base_model, input_height, input_width)

    out_path = f"{base_name}_{input_height}_{input_width}.h5"

    model.save(out_path)
    print(f"Model input successfully reshaped and saved as {out_path}.")


def main():
    """CNN2SNN command-line interface to quantize/convert/upgrade a model"""
    parser = argparse.ArgumentParser()
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("-m",
                               "--model",
                               type=str,
                               required=True,
                               help="The source model")
    sp = parser.add_subparsers(dest="action")
    q_parser = sp.add_parser("quantize",
                             parents=[parent_parser],
                             help="Quantize a Keras model")
    q_parser.add_argument("-wq",
                          "--weight_quantization",
                          type=int,
                          default=4,
                          help="The weight quantization")
    q_parser.add_argument("-aq",
                          "--activ_quantization",
                          type=int,
                          default=4,
                          help="The activations quantization")
    q_parser.add_argument("-iq",
                          "--input_weight_quantization",
                          type=int,
                          default=-1,
                          help="The first layer weight quantization (same as" \
                          " weight_quantization if omitted)")
    q_parser.add_argument("--no-fold-BN",
                          dest="fold_BN",
                          action='store_false',
                          help="If specified, do not fold BatchNormalization "
                          "layers before quantization")
    c_parser = sp.add_parser(
        "convert",
        parents=[parent_parser],
        help="Convert a quantized Keras model to an Akida model")
    c_parser.add_argument("-sc",
                          "--scale",
                          type=int,
                          default=None,
                          help="The scale factor applied on uint8 inputs.")
    c_parser.add_argument("-sh",
                          "--shift",
                          type=int,
                          default=None,
                          help="The shift applied on uint8 inputs.")
    c_parser.add_argument("--no-image-input",
                          action='store_true',
                          default=False,
                          help="If inputs are not 8-bit images")
    r_parser = sp.add_parser(
        "reshape",
        parents=[parent_parser],
        help="Reshape a (quantized) Keras model Input layer to a given size.")
    r_parser.add_argument("-ih",
                          "--input_height",
                          type=int,
                          default=None,
                          required=True,
                          help="The new input height.")
    r_parser.add_argument("-iw",
                          "--input_width",
                          type=int,
                          default=None,
                          required=True,
                          help="The new input width.")

    args = parser.parse_args()
    if args.action == "quantize":
        quantize_model(args.model, args.weight_quantization,
                       args.activ_quantization, args.input_weight_quantization,
                       args.fold_BN)
    if args.action == "convert":
        if args.scale is None or args.shift is None:
            input_scaling = None
        else:
            input_scaling = (args.scale, args.shift)
        convert_model(args.model, input_scaling, not args.no_image_input)
    if args.action == "reshape":
        reshape_model(args.model, args.input_height, args.input_width)
