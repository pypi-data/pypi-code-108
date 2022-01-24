# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Any, List
from argparse import ArgumentParser
from .util import _is_bool, _convert_string_to_bool


def add_preprocessor_parameters(parser: ArgumentParser) -> None:
    """Add model preprocessor parameters."""
    parser.add_argument(make_arg("preprocessor_name"), type=str,
                        help="",
                        default="StandardScaler")
    parser.add_argument(make_arg("with_std"), type=str,
                        help="",
                        default=None)
    parser.add_argument(make_arg("with_mean"), type=str,
                        help="",
                        default=None)
    parser.add_argument(make_arg("with_centering"), type=str,
                        help="",
                        default=None)
    parser.add_argument(make_arg("with_scaling"), type=str,
                        help="",
                        default=None)


def make_arg(arg_name: str) -> str:
    """append dashes"""
    return f"--{arg_name}"


def clean_arg(arg_name: str) -> str:
    """Clean argument to lstrip dashes"""
    return arg_name.lstrip('-')


def clean_args(args: List[str]) -> List[str]:
    """Clean arguments to lstrip dashes"""
    new_args = []  # type: List[str]
    for arg in args:
        new_args.append(clean_arg(arg))
    return new_args


def process_models_args(model_args: Dict[str, str]) -> Dict[str, Any]:
    """Process model arguments into proper type.

    :parameter
        model_args: all model arguments in str format
    :returns
        converted model parameters with correct type
    """
    result_args = {}  # type: Dict[str, Any]
    for k, v in model_args.items():
        print("model_argument {} with value {}".format(k, v))
        if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
            result_args[k] = int(v)
        elif v.isalnum() and _is_bool(v):
            result_args[k] = _convert_string_to_bool(v)
        elif v.isalnum():
            result_args[k] = v
        else:
            try:
                result_args[k] = float(v)
            except ValueError:
                result_args[k] = v
    return result_args
