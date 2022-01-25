# Copyright 1993-2021 NVIDIA Corporation.  All rights reserved.
#
# NOTICE TO LICENSEE:
#
# This source code and/or documentation ("Licensed Deliverables") are
# subject to NVIDIA intellectual property rights under U.S. and
# international Copyright laws.
#
# These Licensed Deliverables contained herein is PROPRIETARY and
# CONFIDENTIAL to NVIDIA and is being provided under the terms and
# conditions of a form of NVIDIA software license agreement by and
# between NVIDIA and Licensee ("License Agreement") or electronically
# accepted by Licensee.  Notwithstanding any terms or conditions to
# the contrary in the License Agreement, reproduction or disclosure
# of the Licensed Deliverables to any third party without the express
# written consent of NVIDIA is prohibited.
#
# NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
# LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
# SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  IT IS
# PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
# NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
# DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
# NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
# NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
# LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
# SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THESE LICENSED DELIVERABLES.
#
# U.S. Government End Users.  These Licensed Deliverables are a
# "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
# 1995), consisting of "commercial computer software" and "commercial
# computer software documentation" as such terms are used in 48
# C.F.R. 12.212 (SEPT 1995) and is provided to the U.S. Government
# only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
# 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
# U.S. Government End Users acquire the Licensed Deliverables with
# only those rights set forth herein.
#
# Any use of the Licensed Deliverables in individual and commercial
# software must include, in the user documentation and internal
# comments to the code, the above Disclaimer and U.S. Government End
# Users Notice.

import ctypes
import glob
import os
import warnings


def try_load(library):
    try:
        ctypes.CDLL(library)
    except OSError:
        pass


# Try loading all packaged libraries
# CURDIR = os.path.realpath(os.path.dirname(__file__))
# for lib in glob.iglob(os.path.join(CURDIR, "*.so*")):
#     try_load(lib)

import trtpy.init_default as trtpy
# from .tensorrt import *

package_name = f"{trtpy.select_nvbinary_version}.{trtpy.python_version_module_name}.tensorrt"
m = __import__(package_name, globals(), locals(), ["*"])
trtpy.update_module_variables(locals(), m)

# __version__ = "8.0.1.6"


# Provides Python's `with` syntax
def common_enter(this):
    warnings.warn("Context managers for TensorRT types are deprecated. "
                  "Memory will be freed automatically when the reference count reaches 0.",
                  DeprecationWarning)
    return this


def common_exit(this, exc_type, exc_value, traceback):
    """
    Context managers are deprecated and have no effect. Objects are automatically freed when
    the reference count reaches 0.
    """
    pass


# Logger does not have a destructor.
ILogger.__enter__ = common_enter
ILogger.__exit__ = lambda this, exc_type, exc_value, traceback : None

Builder.__enter__ = common_enter
Builder.__exit__ = common_exit

ICudaEngine.__enter__ = common_enter
ICudaEngine.__exit__ = common_exit

IExecutionContext.__enter__ = common_enter
IExecutionContext.__exit__ = common_exit

Runtime.__enter__ = common_enter
Runtime.__exit__ = common_exit

INetworkDefinition.__enter__ = common_enter
INetworkDefinition.__exit__ = common_exit

UffParser.__enter__ = common_enter
UffParser.__exit__ = common_exit

CaffeParser.__enter__ = common_enter
CaffeParser.__exit__ = common_exit

OnnxParser.__enter__ = common_enter
OnnxParser.__exit__ = common_exit

IHostMemory.__enter__ = common_enter
IHostMemory.__exit__ = common_exit

Refitter.__enter__ = common_enter
Refitter.__exit__ = common_exit

IBuilderConfig.__enter__ = common_enter
IBuilderConfig.__exit__ = common_exit


# Computes the volume of an iterable.
def volume(iterable):
    """
    Computes the volume of an iterable.

    :arg iterable: Any python iterable, including a :class:`Dims` object.

    :returns: The volume of the iterable. This will return 1 for empty iterables, as a scalar has an empty shape and the volume of a tensor with empty shape is 1.
    """
    vol = 1
    for elem in iterable:
        vol *= elem
    return vol


# Converts a TensorRT datatype to the equivalent numpy type.
def nptype(trt_type):
    '''
    Returns the numpy-equivalent of a TensorRT :class:`DataType` .

    :arg trt_type: The TensorRT data type to convert.

    :returns: The equivalent numpy type.
    '''
    import numpy as np
    mapping = {
        float32: np.float32,
        float16: np.float16,
        int8: np.int8,
        int32: np.int32,
        bool: np.bool,
    }
    if trt_type in mapping:
        return mapping[trt_type]
    raise TypeError("Could not resolve TensorRT datatype to an equivalent numpy datatype.")


# Add a numpy-like itemsize property to the datatype.
def _itemsize(trt_type):
    '''
    Returns the size in bytes of this :class:`DataType` .

    :arg trt_type: The TensorRT data type.

    :returns: The size of the type.
    '''
    mapping = {
        float32: 4,
        float16: 2,
        int8: 1,
        int32: 4,
        bool: 1,
    }
    if trt_type in mapping:
        return mapping[trt_type]

DataType.itemsize = property(lambda this: _itemsize(this))
