# Copyright Exafunction, Inc.

from enum import IntEnum
from typing import Sequence

import numpy as np

import exa._C as _C
from exa.common_pb.common_pb2 import DataType
from exa.common_pb.common_pb2 import TensorMetadata
from exa.common_pb.common_pb2 import ValueMetadata


class ValueCompressionType(IntEnum):
    """The format to use for compressing values on the wire."""

    UNCOMPRESSED = 0
    """ No compression """
    FLOAT_TO_UINT8_COMPRESSION = 1
    """
    Compress float32 values to uint8. Only valid if all the values are exactly
    integers from 0-255.
    """
    LZ4_COMPRESSION = 2
    """ Compress with LZ4 """


class Value:
    """
    Represents any Exafunction value. Exafunction values can be one of several
    types, such as byte arrays or tensors. Values can either exist locally,
    remotely or both. Methods in this class that convert an Exafunction value
    to a different Python type such as a NumPy array will automatically fetch
    remote values.
    """

    def __init__(self, c: _C.Value):
        self._c = c

    def _check_valid(self):
        if not self._c.is_valid():
            raise ValueError("Value is not valid (was the session closed?)")

    def clear(self):
        """Clear the value."""
        self._c = None

    def value_id(self) -> int:
        """
        Returns the value id.

        :return: The value id.
        """
        self._check_valid()
        return self._c.value_id()

    def bytes(self) -> bytes:
        """
        Returns the value as a bytes object.

        The underlying value must be an Exafunction Bytes value.

        :return: The bytes object.
        """
        self._check_valid()
        return bytes(self._c)

    def set_bytes(self, other: "__builtins__.bytes"):
        """
        Sets the value from a bytes object.

        The underlying value must be an Exafunction Bytes value.

        :param other: The bytes object.
        """
        self._check_valid()
        self.mutable_bytes_view()[:] = np.frombuffer(other, dtype=np.uint8)

    def bytes_view(self) -> np.ndarray:
        """
        Returns a view into the underlying value buffer as a read-only ndarray of bytes.

        :return: A read-only ndarray of bytes whose buffer is backed by this value's buffer.
        """
        self._check_valid()
        ret = self.mutable_bytes_view()
        ret.setflags(write=False)
        return ret

    # Return a mutable view into the underlying value buffer.
    def mutable_bytes_view(self) -> np.ndarray:
        """
        Returns a view into the underlying value buffer as a read-write ndarray of bytes.

        The underlying value must be mutable.

        :return: A read-write ndarray of bytes whose buffer is backed by this value's buffer.
        """
        self._check_valid()
        ret = np.frombuffer(self._c, dtype=np.uint8)
        return ret

    def is_gpu(self) -> bool:
        """
        Returns whether the value is stored on the GPU.

        :return: True if the value is stored on the GPU, False otherwise.
        """
        self._check_valid()
        return self._c.is_gpu()

    def is_local_valid(self) -> bool:
        """
        Returns whether a local copy of this value exists.

        :return: True if a local copy exists, False otherwise.
        """
        self._check_valid()
        return self._c.is_local_valid()

    def is_mutable(self) -> bool:
        """
        Returns whether the value is mutable.

        :return: True if the value is mutable, False otherwise.
        """
        self._check_valid()
        return self._c.is_mutable()

    def is_client_value(self) -> bool:
        """
        Returns whether the value is a client value.

        :return: True if the value is a client value, False otherwise.
        """
        self._check_valid()
        return self._c.is_client_value()

    def is_method_value(self) -> bool:
        """
        Returns whether the value is a method value.

        :return: True if the value is a method value, False otherwise.
        """
        self._check_valid()
        return self._c.is_method_value()

    def metadata(self) -> ValueMetadata:
        """
        Returns the metadata for the value.

        :return: The metadata
        """
        self._check_valid()
        m = ValueMetadata()
        m.ParseFromString(self._c.metadata())
        return m

    def set_metadata(self, v: ValueMetadata) -> None:
        """
        Sets the metadata for the value.

        :param v: The new metadata.
        """
        self._check_valid()
        self._c.set_metadata(v.SerializeToString())

    def is_tensor(self) -> bool:
        """
        Returns whether the value is a tensor.

        :return: True if the value is a tensor, False otherwise.
        """
        self._check_valid()
        return self._c.is_tensor()

    _NP_TO_PB_DTYPE = {
        np.dtype(np.float32): DataType.FLOAT32,
        np.dtype(np.float64): DataType.FLOAT64,
        np.dtype(np.int8): DataType.INT8,
        np.dtype(np.int16): DataType.INT16,
        np.dtype(np.int32): DataType.INT32,
        np.dtype(np.int64): DataType.INT64,
        np.dtype(np.uint8): DataType.UINT8,
        np.dtype(np.uint16): DataType.UINT16,
        np.dtype(np.uint32): DataType.UINT32,
        np.dtype(np.uint64): DataType.UINT64,
    }

    _PB_TO_NP_DTYPE = {v: k for k, v in _NP_TO_PB_DTYPE.items()}

    @classmethod
    def _get_tensor_metadata(cls, dtype, shape: Sequence[int], strides=None):
        m = ValueMetadata()
        m.size = np.prod(shape) * np.dtype(dtype).itemsize
        dtype = np.dtype(dtype)
        if dtype not in cls._NP_TO_PB_DTYPE:
            raise ValueError(f"invalid dtype {dtype}")
        m.tensor.dtype = cls._NP_TO_PB_DTYPE[dtype]
        if len(shape) == 0:
            raise ValueError("tensor must have at least 1 dimension")
        if any(s < 0 for s in shape):
            raise ValueError("tensor may not have negative sizes")
        m.tensor.shape.extend(shape)

        if strides is None:
            strides = [0] * len(shape)
            strides[-1] = dtype.itemsize
            for i in range(len(strides) - 1, 0, -1):
                strides[i - 1] = strides[i] * shape[i]
        m.tensor.strides.extend(strides)
        return m

    def numpy(self) -> np.ndarray:
        """
        Returns the value as a NumPy array.

        The value must be an Exafunction Tensor.  Note that this returns a
        read-only view into the same buffer as the underlying value. Therefore,
        it is important to keep a reference to the value to prevent the
        underlying buffer from getting garbage collected.

        If a copy is desired, the copy() method can be called on the returned
        array.

        :return: A read-only NumPy array backed by the same buffer as this value.
        """

        self._check_valid()
        m = self.metadata()
        if not m.HasField("tensor"):
            raise TypeError("Value is not a tensor, cannot convert to numpy")
        dtype = self._PB_TO_NP_DTYPE[m.tensor.dtype]
        buf = np.frombuffer(self._c, dtype=dtype)
        return np.lib.stride_tricks.as_strided(
            buf, shape=m.tensor.shape, strides=m.tensor.strides
        )

    def set_compression_type(self, compression_type: ValueCompressionType):
        """
        Sets the compression type for the value.

        :param compression_type: The compression type.
        """

        if not isinstance(compression_type, ValueCompressionType):
            raise TypeError("compression_type must be of type ValueCompressionType")
        self._c.set_compression_type(int(compression_type))
