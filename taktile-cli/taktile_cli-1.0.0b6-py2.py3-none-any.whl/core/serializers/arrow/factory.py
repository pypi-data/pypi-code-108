from collections.abc import Sequence
from functools import singledispatch
from typing import Any, Type

import numpy
import pandas  # type: ignore
import pyarrow  # type: ignore

from tktl.core.exceptions import UnsupportedInputTypeException
from tktl.core.loggers import LOG
from tktl.core.serializers import arrow
from tktl.core.serializers.base import ObjectSerializer
from tktl.core.utils import DelayedLoader


def deserialize_arrow(model_input: pyarrow.Table):
    if b"CLS" not in model_input.schema.metadata:
        as_pandas = model_input.to_pandas()
        if len(as_pandas.columns) == 1:
            return as_pandas.squeeze()
        return as_pandas
    cls_name = model_input.schema.metadata[b"CLS"]
    func = getattr(getattr(arrow, cls_name.decode("utf-8")), "deserialize")
    return func(model_input)


@singledispatch
def serialize_arrow(model_input) -> pyarrow.Table:
    return arrow.BinarySerializer.serialize(model_input)


@serialize_arrow.register(Sequence)
def _sequence(model_input):
    return _do_serialize_with_fallback(
        arrow.SequenceSerializer, model_input=model_input
    )


@serialize_arrow.register(dict)
def _dict(model_input):
    return _do_serialize_with_fallback(
        arrow.SequenceSerializer, model_input=model_input
    )


@serialize_arrow.register(numpy.ndarray)
def _ndarry(model_input):
    return _do_serialize_with_fallback(arrow.ArraySerializer, model_input=model_input)


@serialize_arrow.register(pandas.DataFrame)
def _df(model_input):
    return _do_serialize_with_fallback(
        arrow.DataFrameSerializer, model_input=model_input
    )


@serialize_arrow.register(pandas.Series)
def _series(model_input):
    return _do_serialize_with_fallback(arrow.SeriesSerializer, model_input=model_input)


@serialize_arrow.register(DelayedLoader)
def _delayed_loaded_frame(model_input):
    return model_input


def _do_serialize_with_fallback(
    serializer_cls: Type[ObjectSerializer], model_input: Any
):
    try:
        return serializer_cls.serialize(value=model_input)
    except UnsupportedInputTypeException:
        LOG.warning(
            "Invalid serialization value, will use binary representation for object"
        )
    return arrow.BinarySerializer.serialize(model_input)
