# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#      https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""Module for serializing data."""
import json
from functools import reduce
from operator import mul
from typing import (
    Any,
    Dict,
    List,
    Union,
)

import numpy as np

from .data_types import (
    ComplexNumber,
    EllipsisDataType,
    FloatConstant,
    GraphDataType,
    NumpyArray,
    NumpyComplexNumber,
    NumpyScalar,
    OperationDataType,
    QuantumObject,
    SliceDataType,
    SparseMatrix,
)


class DataTypeMixin:  # pylint:disable=too-few-public-methods
    """Mixin class that defines the available data types in precedence order.
    To be used by the json encoder and decoder classes.
    """

    data_types = [
        NumpyArray(),
        NumpyComplexNumber(),
        NumpyScalar(),
        ComplexNumber(),
        OperationDataType(),
        GraphDataType(),
        SliceDataType(),
        EllipsisDataType(),
        SparseMatrix(),
        FloatConstant(),
        QuantumObject(),
    ]


class DataTypeDecoder(json.JSONDecoder, DataTypeMixin):
    """Represent DataTypeDecoder Model."""

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs
        )  # pylint:disable=method-hidden

    def object_hook(self, obj: Any) -> Any:
        """A function to check if any data type can be decoded.

        Parameters
        ----------
        obj : Any
            object to be examined.

        Returns
        -------
        Any
            a decode object.
        """
        for data_type in self.data_types:
            if data_type.can_decode(obj):
                return data_type.decode(obj)

        # otherwise decode as usual
        return obj


class DataTypeEncoder(json.JSONEncoder, DataTypeMixin):
    """
    Represent DataTypeEncoder Model.

    To be used with `json.dumps` (i.e.: `json.dumps(data, cls=DataTypeEncoder)`)
    to encode known objects that are not JSON serializable by the standard
    library.

    WARNING: the `DataTypeMixin` allow encoding/decoding of `FloatConstant`
    values (`inf`, `-inf` and `nan`). However, JSONEncoder.default will not
    engage with those values because floats are known types and will be encoded
    as their JavaScript constant equivalents Infinity, -Infinity and NaN. If the
    encoded data will be used on a strict JSON schema that doesn't accept
    JavaScript constants use `qctrlcommons.serializers.encode`.
    """

    def default(self, obj):  # pylint:disable=arguments-renamed, method-hidden
        # check if any data type can be encoded
        for data_type in self.data_types:
            if data_type.can_encode(obj):
                return data_type.encode(obj)

        # otherwise let the base class default method raise the TypeError
        super().default(obj)
        return None


def encode(data: Any) -> dict:
    """
    The data structure optionally containing complex types handled by
    DataTypeEncoder.

    Transforms the data structure into JSON Serializable values. Also encodes
    float constants (`inf`, `-inf`, `nan`) into custom data structure using the
    `parse_constant` option from `json.loads`.

    Parameters
    ----------
    data: Any
        data to be encoded.

    Returns
    -------
    dict
        the encoded dict.

    """
    return json.loads(
        json.dumps(data, cls=DataTypeEncoder),
        parse_constant=FloatConstant().parse_constant,
    )


def decode(data: Any) -> Any:
    """the data structure optionally containing objects handled
    by DataTypeDecoder.

    Parameters
    ----------
    data: Any
        object to be decoded.

    Returns
    -------
    Any
        the decoded data structure.

    """
    return json.loads(json.dumps(data), cls=DataTypeDecoder)


def read_complex(real: float = None, imag: float = None) -> complex:
    """
    Returns a `complex` parsed from the given GraphQL data.

    Parameters
    ----------
    real : float, optional
        The real part of the number. Defaults to 0 if omitted or ``None``.
    imag : float, optional
        The imaginary part of the number. Defaults to 0 if omitted or ``None``.

    Returns
    -------
    complex
        The parsed number.
    """
    return complex(real or 0, imag or 0)


def write_complex(value: Union[int, float, complex, np.number]) -> Dict[str, Any]:
    """
    Writes a complex number to a GraphQL-compatible dictionary.

    Parameters
    ----------
    value : numeric
        The number to write.

    Returns
    -------
    dict
        A GraphQL-compatible dictionary representing the given number.
    """
    real = np.real(value)
    imag = np.imag(value)

    result = {}
    if real != 0:
        result["real"] = float(real)
    if imag != 0:
        result["imag"] = float(imag)

    return result


def read_numpy_array(
    shape: List[int],
    sparse_entries: List[Dict[str, Any]] = None,
    dense_entries: Dict[str, List[Union[float, int]]] = None,
) -> np.ndarray:
    """
    Returns a NumPy array parsed from the given GraphQL data.

    Parameters
    ----------
    shape : List[int]
        The size of each dimension of the array.
    sparse_entries : List[Dict[str, Any]], optional
        The non-zero entries of the array. Each item of the list is a dict with entries
        "coordinates", which is a list of the coordinates of the entry, and "value", which is the
        complex value. Defaults to an empty list if omitted or ``None``.
    dense_entries : Dict[str, List[Union[float, int]]], optional
        The dict containing the "real" and "imag" lists to rebuild the array.
        Defaults to an empty dict if omitted or ``None``.

    Returns
    -------
    np.ndarray
        The array.
    """
    result = np.zeros(shape, dtype=complex)
    if dense_entries:
        element_count = reduce(mul, shape, 1)
        result = np.zeros(element_count, dtype=complex)

        if dense_entries.get("real"):
            result.real = dense_entries["real"]

        if dense_entries.get("imag"):
            result.imag = dense_entries["imag"]

        return result.reshape(shape)

    for entry in sparse_entries or []:
        result[tuple(entry["coordinates"])] = read_complex(**entry["value"])

    return result


def write_numpy_array(array: np.ndarray) -> Dict[str, Any]:
    """
    Writes a NumPy array to a GraphQL-compatible dictionary.

    Parameters
    ----------
    array : np.ndarray
        The NumPy array to write.

    Returns
    -------
    dict
        A GraphQL-compatible dictionary representing the given array. The entries are ordered in
        row-major order (i.e. with the last coordinate index varying fastest).
    """
    result = {
        "shape": list(array.shape),
    }
    if should_use_sparse(array):
        result["sparse_entries"] = numpy_to_sparse_array(array)
    else:
        result["dense_entries"] = numpy_to_dense_array(array)

    return result


def numpy_to_dense_array(array: np.ndarray) -> Dict[str, List[float]]:
    """
    Convert numpy array to dict using a dense strategy.
    """
    real = array.flatten().real
    imag = array.flatten().imag

    result = {}

    if real.any():
        result["real"] = real.tolist()

    if imag.any():
        result["imag"] = imag.tolist()

    return result


def numpy_to_sparse_array(array: np.ndarray) -> List[Dict[str, Any]]:
    """
    Convert numpy array to dict using a sparse strategy.
    """
    return [
        {
            # Note that we must cast the coordinates, which are initially NumPy integers, to raw
            # Python integers.
            "coordinates": [int(coordinate) for coordinate in coordinates],
            "value": write_complex(array[tuple(coordinates)]),
        }
        for coordinates in np.argwhere(array)
    ]


def should_use_sparse(array: np.ndarray) -> bool:
    """
    Checks whether an array can be most efficiently serialized as a sparse matrix.
    """

    if not array.shape:
        return False

    return sparse_array_approximate_size(array) < dense_array_approximate_size(array)


def dense_array_approximate_size(array: np.ndarray) -> int:
    """
    Calculate an approximate size for the dense array result.

    Expected serialized structure:

        {
            "shape": [2, 2],
            "dense_entries": {
                "real": [1, 0, 0, 1],
                "imag": [0, 0, 0, 0]
            }
        }
    """

    # array dtype
    is_int = array.dtype.kind == "i"  # non int add `.0` to all zeros
    is_complex = array.dtype.kind == "c"  # non int add `.0` to all zeros

    # count values
    non_zeros = np.nonzero(array)
    real_count = np.count_nonzero(np.real(array[non_zeros]))
    imag_count = np.count_nonzero(np.imag(array[non_zeros]))

    # defined dense array estimated schema sizes
    base_schema_chars = len('{"dense_entries": {}}')
    zero_entry_chars = len("0, " if is_int else "0.0, ")
    real_chars = len('"real": [], ')
    imag_chars = len('"imag": [], ' if is_complex else "")
    zero_array_size = array.size - real_count
    zero_array_size += array.size - imag_count if is_complex else 0
    trailing_comma = len(", ")

    dense_size = (
        base_schema_chars
        + real_chars
        + imag_chars
        - trailing_comma
        + (zero_entry_chars * zero_array_size)
    )

    return dense_size


def sparse_array_approximate_size(array: np.ndarray) -> int:
    """
    Calculate an approximate size for the sparse array result.

    Expected serialized structure:

        {
            "shape": [2, 2],
            "sparse_entries": [
                {
                    "coordinates": [0, 0],
                    "value": {"real": 1},
                },
                {
                    "coordinates": [1, 1],
                    "value": {"real": 1}
                }
            ]
        }

    """

    # count values
    non_zeros = np.nonzero(array)
    non_zero_count = non_zeros[0].size
    real_count = np.count_nonzero(np.real(array[non_zeros]))
    imag_count = np.count_nonzero(np.imag(array[non_zeros]))

    # defined sparse array estimated schema sizes
    base_schema_chars = len('{"sparse_entries": []}')
    entry_chars = len('{"coordinates": [, ], "value": {}}, ')
    real_chars = len('"real": ')
    imag_chars = len('"imag": ')
    trailing_comma = len(", ")

    coordinates = np.sum(
        [1 + np.floor(np.log10(np.maximum(val, 2))) for val in non_zeros]
    )
    sparse_size = (
        base_schema_chars
        + (entry_chars * non_zero_count)
        + coordinates
        + (real_chars * real_count - trailing_comma)
        + (imag_chars * imag_count - trailing_comma)
    )
    return sparse_size
