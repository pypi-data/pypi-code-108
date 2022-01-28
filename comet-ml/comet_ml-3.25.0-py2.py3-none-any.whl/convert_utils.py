# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import inspect
import logging

from ._typing import Any, Dict, List, Number, Optional, Type
from .logging_messages import (
    INVALID_BOUNDING_BOX_3D,
    INVALID_BOUNDING_BOXES_3D,
    INVALID_CLOUD_POINTS_3D,
    INVALID_SINGLE_CLOUD_POINT_3D,
    INVALID_SINGLE_CLOUD_POINT_3D_LENGTH,
)
from .schemas import get_3d_boxes_validator

try:
    import pathlib
except ImportError:
    try:
        import pathlib2 as pathlib
    except ImportError:
        pathlib = None

LOGGER = logging.getLogger(__name__)


def convert_to_bytes(item):
    """
    Convert the item into bytes. The conversion may not
    be reversable.
    """
    if hasattr(item, "tobytes"):
        # Numpy arrays, etc.
        return item.tobytes()
    else:
        str_item = str(item)
        return str_item.encode(encoding="utf-8", errors="xmlcharrefreplace")


def convert_tensor_to_numpy(tensor):
    """
    Convert from various forms of pytorch tensors
    to numpy arrays.

    Note: torch tensors can have both "detach" and "numpy"
    methods, but numpy() alone will fail if tensor.requires_grad
    is True.
    """
    if hasattr(tensor, "detach"):  # pytorch tensor with attached gradient
        tensor = tensor.detach()

    if hasattr(tensor, "numpy"):  # pytorch tensor
        tensor = tensor.numpy()

    return tensor


def convert_to_scalar(user_data, dtype=None):
    # type: (Any, Optional[Type]) -> Any
    """
    Try to ensure that the given user_data is converted back to a
    Python scalar, and of proper type (if given).
    """
    # Fast-path for types and class, we currently does not apply any conversion
    # to classes
    if inspect.isclass(user_data):

        if dtype and not isinstance(user_data, dtype):
            raise TypeError("%r is not of type %r" % (user_data, dtype))

        return user_data

    # First try to convert tensorflow tensor to numpy objects
    try:
        if hasattr(user_data, "numpy"):
            user_data = user_data.numpy()
    except Exception:
        LOGGER.debug(
            "Failed to convert tensorflow tensor %r to numpy object",
            user_data,
            exc_info=True,
        )

    # Then try to convert numpy object to a Python scalar
    try:
        if hasattr(user_data, "item") and callable(user_data.item):
            user_data = user_data.item()
    except Exception:
        LOGGER.debug(
            "Failed to convert object %r to Python scalar",
            user_data,
            exc_info=True,
        )

    if dtype is not None and not isinstance(user_data, dtype):
        raise TypeError("%r is not of type %r" % (user_data, dtype))

    return user_data


def convert_to_list(items, dtype=None):
    # type: (Any, Any) -> List[Any]
    """
    Take an unknown item and convert to a list of scalars
    and ensure type is dtype, if given.
    """
    # First, convert it to numpy if possible:
    if hasattr(items, "numpy"):  # pytorch tensor
        items = convert_tensor_to_numpy(items)
    elif hasattr(items, "eval"):  # tensorflow tensor
        items = items.eval()

    # Next, handle numpy array:
    if hasattr(items, "tolist"):
        if len(items.shape) != 1:
            raise ValueError("list should be one dimensional")
        result = items.tolist()  # type: List[Any]
        return result
    else:
        # assume it is something with numbers in it:
        return [convert_to_scalar(item, dtype=dtype) for item in items]


def validate_single_3d_point(single_3d_point):
    # type: (Any) -> Optional[List[Number]]

    try:
        convert_point_list = convert_to_list(single_3d_point)
    except Exception:
        LOGGER.warning(
            INVALID_SINGLE_CLOUD_POINT_3D,
            single_3d_point,
            exc_info=True,
            extra={"show_traceback": True},
        )
        return None

    if len(convert_point_list) < 3:
        LOGGER.warning(INVALID_SINGLE_CLOUD_POINT_3D_LENGTH, single_3d_point)
        return None

    return convert_point_list


def validate_and_convert_3d_points(points):
    # type: (Any) -> List[List[Number]]
    if points is None:
        return []

    final_points = []

    try:
        for point in points:
            convert_point = validate_single_3d_point(point)

            if convert_point is not None:
                final_points.append(convert_point)
    except Exception:
        LOGGER.warning(
            INVALID_CLOUD_POINTS_3D,
            points,
            exc_info=True,
            extra={"show_traceback": True},
        )
        return []

    return final_points


def validate_single_3d_box(validator, box):
    # type: (Any, Any) -> Optional[Dict[str, Any]]
    try:
        # First reconstruct box with converted types
        converted_box = {
            "position": convert_to_list(box.get("position", [])),
            "size": {
                "height": convert_to_scalar(box.get("size", {}).get("height", None)),
                "width": convert_to_scalar(box.get("size", {}).get("width", None)),
                "depth": convert_to_scalar(box.get("size", {}).get("depth", None)),
            },
            "label": box.get("label", None),
        }

        # Optional fields
        box_rotation = box.get("rotation", None)
        if box_rotation is not None:
            converted_box.update(
                {
                    "rotation": {
                        "alpha": convert_to_scalar(box_rotation.get("alpha", None)),
                        "beta": convert_to_scalar(box_rotation.get("beta", None)),
                        "gamma": convert_to_scalar(box_rotation.get("gamma", None)),
                    }
                }
            )

        box_color = box.get("color", None)
        if box_color is not None:
            converted_box["color"] = convert_to_list(box_color)

        box_probability = box.get("probability", None)
        if box_probability is not None:
            converted_box["probability"] = convert_to_scalar(box_probability)

        box_class = box.get("class", None)
        if box_class is not None:
            converted_box["class"] = box_class

        validator.validate(converted_box)
        return converted_box
    except Exception:
        LOGGER.warning(
            INVALID_BOUNDING_BOX_3D,
            box,
            exc_info=True,
            extra={"show_traceback": True},
        )

        return None


def validate_and_convert_3d_boxes(boxes):
    # type: (Any) -> List[Dict[str, Any]]
    if boxes is None:
        return []

    validator = get_3d_boxes_validator()
    final_boxes = []

    try:
        for box in boxes:
            converted_box = validate_single_3d_box(validator, box)

            if converted_box is not None:
                final_boxes.append(converted_box)
    except Exception:
        LOGGER.warning(
            INVALID_BOUNDING_BOXES_3D,
            boxes,
            exc_info=True,
            extra={"show_traceback": True},
        )

    return final_boxes


def convert_pathlib_path(user_input):
    # type: (Any) -> Any
    if pathlib is not None and isinstance(user_input, pathlib.Path):
        return str(user_input)

    return user_input
