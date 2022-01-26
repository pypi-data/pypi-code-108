from collections import OrderedDict
from typing import Any, Tuple

import numpy as np

from .types.field import FieldType


def orjson_serialize_default_handler(obj: Any) -> str:
    """Default callback for orjson dumps.

    Supports pandas Timestamp type.

    Args:
        obj: Object to serialize

    Returns:
        Serialized object
    """
    # This supports serializing pandas the Timestamp type
    if hasattr(obj, "isoformat"):
        return obj.isoformat()

    # As recommended by orjson, we raise TypeError to indicate this
    # function can't serialize the object
    raise TypeError()


def generate_features_schema_from_shape(features_shape: Tuple) -> OrderedDict:
    """Return features schema to use in version creation from ndarray shape.

    Args:
        features_shape (Tuple): the shape of the features array.

    Returns:
        OrderedDict: The object to pass to features in the version schema.
    """
    features_schema = OrderedDict()
    for i in range(np.prod(features_shape)):
        features_schema[f"X{i}"] = FieldType.NUMERIC.value

    return features_schema
