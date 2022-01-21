"""labels.py
============
The label set classes.
"""

import datetime
import json
from io import IOBase, BytesIO
from tempfile import NamedTemporaryFile
import pyarrow as pa
import numpy as np
import pandas as pd
from typing import Any, Optional, Union, Callable, List, Dict, Tuple, Set, IO, cast
from typing_extensions import Literal
from uuid import uuid4
from .util import is_valid_number, is_valid_float

HAS_PILLOW = False
try:
    from PIL import Image  # type: ignore

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


from .util import (
    DEFAULT_SENSOR_ID,
    _is_one_gb_available,
    add_object_user_attrs,
    assert_valid_name,
    create_temp_directory,
    mark_temp_directory_complete,
    POLYGON_VERTICES_KEYS,
    KEYPOINT_KEYS,
    MAX_FRAMES_PER_BATCH,
    InferenceEntryDict,
    FrameEmbeddingDict,
    CropEmbeddingDict,
    LabelType,
    InferenceFrameSummary,
    LabelFrameSummary,
    BaseLabelEntryDict,
    BaseLabelAssetDict,
    ResizeMode,
)

CustomMetricsEntry = Union[float, List[List[Union[float, int]]]]
CropType = Literal["GT", "Inference"]


class BaseLabelSet:
    """A frame containing inferences from an experiment.

    Args:
        frame_id (str): A unique id for this frame.
    """

    # TODO: Is this the most pythonic pattern?
    frame_id: str
    crop_type: CropType
    label_data: List[BaseLabelEntryDict]
    label_assets: List[BaseLabelAssetDict]
    _label_ids_set: Set[str]
    crop_embeddings: List[CropEmbeddingDict]
    _seen_label_class_ids: Set[int]
    reuse_latest_embedding: bool
    crop_embedding_dim: Optional[int]

    def __init__(
        self,
        *,
        frame_id: str,
        crop_type: CropType,
        reuse_latest_embedding: Optional[bool] = False,
    ) -> None:
        if not isinstance(frame_id, str):
            raise Exception("frame ids must be strings")

        if "/" in frame_id:
            raise Exception("frame ids cannot contain slashes (/)")

        self.frame_id = frame_id
        self.crop_type = crop_type
        self.label_data = []
        self.label_assets = []
        self.crop_embeddings = []
        self._label_ids_set = set()
        self._seen_label_class_ids = set()
        self.reuse_latest_embedding = (
            False if reuse_latest_embedding is None else reuse_latest_embedding
        )
        self.crop_embedding_dim = None

    def add_crop_embedding(
        self, *, label_id: str, embedding: List[float], model_id: str = ""
    ) -> None:
        """Add a per inference crop embedding

        Args:
            label_id (str): [description]
            embedding (List[float]): A vector of floats between length 0 and 12,000.
            model_id (str, optional): The model id used to generate these embeddings. Defaults to "".
        """
        if not embedding or len(embedding) > 12000:
            raise Exception("Length of embeddings should be between 0 and 12,000")

        if not self.crop_embedding_dim:
            self.crop_embedding_dim = len(embedding)
        elif self.crop_embedding_dim != len(embedding):
            raise Exception(
                f"Length of embeddings must be the same, existing embeddings are of dimension {self.crop_embedding_dim} but new embedding has dimension {len(embedding)}"
            )

        # TODO: check label id present
        self.crop_embeddings.append(
            {
                "uuid": label_id,
                "embedding": embedding,
                "model_id": model_id,
                "date_generated": str(datetime.datetime.now()),
            }
        )
        self.reuse_latest_embedding = False

    def _all_label_classes(self) -> List[str]:
        return list(
            set(
                [data["label"] for data in self.label_data if data["label"] != "__mask"]
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert this label set into a dictionary representation.

        Returns:
            dict: dictified frame
        """
        row = {
            "task_id": self.frame_id,
            "label_data": [
                {
                    **cast(Dict[str, Any], label),
                    "reuse_latest_embedding": self.reuse_latest_embedding,
                }
                for label in self.label_data
            ],
            "type": self.crop_type,
        }

        return row

    def _to_summary(self) -> LabelFrameSummary:
        """Converts this frame to a lightweight summary dict for internal cataloging

        Returns:
            dict: lightweight summaried frame
        """
        label_counts: Dict[LabelType, int] = {}
        for label in self.label_data:
            if not label_counts.get(label["label_type"]):
                label_counts[label["label_type"]] = 0
            label_counts[label["label_type"]] += 1

        return {
            "frame_id": self.frame_id,
            "label_counts": label_counts,
        }

    # Handle confidence
    def add_2d_line_segment(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        classification: str,
        x1: Union[int, float],
        y1: Union[int, float],
        x2: Union[int, float],
        y2: Union[int, float],
        confidence: Optional[float] = None,
        iscrowd: Optional[bool] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a 2D line segment.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            x1 (int or float): The x-coord of the first vertex in pixels
            y1 (int or float): The x-coord of the first vertex in pixels
            x2 (int or float): The x-coord of the first vertex in pixels
            y2 (int or float): The x-coord of the first vertex in pixels
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        for coord in [x1, y1, x2, y2]:
            if not is_valid_number(coord):
                raise Exception("all line segment coordinates must be valid int/float")

        attrs = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}

        if confidence is not None:
            if not is_valid_float(confidence):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        if iscrowd is not None:
            attrs["iscrowd"] = iscrowd

        if links is not None:
            for k, v in links.items():
                if "link__" not in k:
                    k = "link__" + k
                attrs[k] = v

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "LINE_SEGMENT_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_2d_bbox(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        classification: str,
        top: Union[int, float],
        left: Union[int, float],
        width: Union[int, float],
        height: Union[int, float],
        confidence: Optional[float] = None,
        area: Optional[float] = None,
        iscrowd: Optional[bool] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a 2D bounding box.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            top (int or float): The top of the box in pixels
            left (int or float): The left of the box in pixels
            width (int or float): The width of the box in pixels
            height (int or float): The height of the box in pixels
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            area (float, optional): The area of the image.
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        for dim in [top, left, width, height]:
            if not is_valid_number(dim):
                raise Exception("all bounding box dimensions must be valid int/float")

        attrs = {
            "top": top,
            "left": left,
            "width": width,
            "height": height,
        }

        if confidence is not None:
            if not is_valid_float(confidence):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        if iscrowd is not None:
            attrs["iscrowd"] = iscrowd
        # TODO: This is mostly legacy for vergesense
        if area is not None:
            if not is_valid_float(area):
                raise Exception("area must be floats")
            if area < 0.0:
                raise Exception("area must be positive")
            attrs["area"] = area

        if links is not None:
            for k, v in links.items():
                if "link__" not in k:
                    k = "link__" + k
                attrs[k] = v

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "BBOX_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_text_token(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        index: int,
        token: str,
        classification: str,
        visible: bool,
        confidence: Optional[float] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a label for a text token.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            index (int): the index of this token in the text
            token (str): the text content of this token
            classification (str): the classification string
            visible (bool): is this a visible token in the text
            confidence (float): confidence of prediction
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """
        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {
            "index": index,
            "token": token,
            "visible": visible,
        }

        if confidence is not None:
            if not is_valid_float(confidence):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "TEXT_TOKEN",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_3d_cuboid(
        self,
        *,
        label_id: str,
        classification: str,
        position: List[float],
        dimensions: List[float],
        rotation: List[float],
        confidence: Optional[float] = None,
        iscrowd: Optional[bool] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, Any]] = None,
        coord_frame_id: Optional[str] = None,
    ) -> None:
        """Add an inference for a 3D cuboid.

        Args:
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            position (list of float): the position of the center of the cuboid
            dimensions (list of float): the dimensions of the cuboid
            rotation (list of float): the local rotation of the cuboid, represented as an xyzw quaternion.
            confidence (float): confidence of prediction
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
            links (dict, optional): Links between labels. Defaults to None.
            coord_frame_id (str, optional): Coordinate frame id. Defaults to 'world'
        """
        if coord_frame_id is None:
            coord_frame_id = "world"

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs: Dict[str, Any] = {
            "pos_x": position[0],
            "pos_y": position[1],
            "pos_z": position[2],
            "dim_x": dimensions[0],
            "dim_y": dimensions[1],
            "dim_z": dimensions[2],
            "rot_x": rotation[0],
            "rot_y": rotation[1],
            "rot_z": rotation[2],
            "rot_w": rotation[3],
        }

        for k, v in attrs.items():
            if not is_valid_float(v):
                raise Exception(k + " must be valid float")

        if confidence is not None:
            if not is_valid_float(confidence):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        if iscrowd is not None:
            attrs["iscrowd"] = iscrowd

        add_object_user_attrs(attrs, user_attrs)

        if links is not None:
            for k, v in links.items():
                if "link__" not in k:
                    k = "link__" + k
                attrs[k] = v

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "CUBOID_3D",
                "label": classification,
                "label_coordinate_frame": coord_frame_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_2d_keypoints(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        classification: str,
        keypoints: List[Dict[KEYPOINT_KEYS, Union[int, float, str]]],
        confidence: Optional[float] = None,
        top: Optional[Union[int, float]] = None,
        left: Optional[Union[int, float]] = None,
        width: Optional[Union[int, float]] = None,
        height: Optional[Union[int, float]] = None,
        polygons: Optional[
            List[Dict[POLYGON_VERTICES_KEYS, List[Tuple[Union[int, float]]]]]
        ] = None,
        center: Optional[List[Union[int, float]]] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an inference for a 2D keypoints task.

        A keypoint is a dictionary of the form:
            'x': x-coordinate in pixels
            'y': y-coordinate in pixels
            'name': string name of the keypoint

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            keypoints (list of dicts): The keypoints of this detection
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            top (int or float, optional): The top of the bounding box in pixels. Defaults to None.
            left (int or float, optional): The left of the bounding box in pixels. Defaults to None.
            width (int or float, optional): The width of the bounding box in pixels. Defaults to None.
            height (int or float, optional): The height of the bounding box in pixels. Defaults to None.
            polygons (list of dicts, optional): The polygon geometry. Defaults to None.
            center (list of ints or floats, optional): The center point of the polygon instance. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        keypoint_names_set = set()
        for keypoint in keypoints:
            x = keypoint["x"]
            y = keypoint["y"]
            name = keypoint["name"]
            if not is_valid_number(x):
                raise Exception("keypoint x coordinate must be valid int/float")
            if not is_valid_number(y):
                raise Exception("keypoint y coordinate must be valid int/float")
            if not isinstance(name, str) or len(name) == 0:
                raise Exception("keypoint name must be non-zero length string")
            if name in keypoint_names_set:
                raise Exception("keypoint names must be unique within a label")
            keypoint_names_set.add(name)

        attrs: Dict[str, Any] = {
            "keypoints": keypoints,
        }

        if (
            top is not None
            and left is not None
            and width is not None
            and height is not None
        ):
            for dim in [top, left, width, height]:
                if not is_valid_number(dim):
                    raise Exception(
                        "all bounding box dimensions must be valid int/float"
                    )
            attrs["top"] = top
            attrs["left"] = left
            attrs["width"] = width
            attrs["height"] = height

        if polygons:
            for polygon in polygons:
                for vertex in polygon["vertices"]:
                    for num in vertex:
                        if not is_valid_number(num):
                            raise Exception(
                                "all polygon vertex coordinates must be valid int/float"
                            )
            attrs["polygons"] = polygons

        if center is not None:
            for num in center:
                if not is_valid_number(num):
                    raise Exception(
                        "polygon center coordinates must be valid int/float"
                    )
            attrs["center"] = center

        if confidence is not None:
            if not is_valid_float(confidence):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "KEYPOINTS_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_2d_polygon_list(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        classification: str,
        polygons: List[Dict[POLYGON_VERTICES_KEYS, List[Tuple[Union[int, float]]]]],
        confidence: Optional[float] = None,
        center: Optional[List[Union[int, float]]] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an inference for a 2D polygon list instance segmentation task.

        Polygons are dictionaries of the form:
            'vertices': List of (x, y) vertices (e.g. [[x1,y1], [x2,y2], ...])
                The polygon does not need to be closed with (x1, y1).
                As an example, a bounding box in polygon representation would look like:

                .. code-block::

                    {
                        'vertices': [
                            [left, top],
                            [left + width, top],
                            [left + width, top + height],
                            [left, top + height]
                        ]
                    }


        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            polygons (list of dicts): The polygon geometry
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            center (list of ints or floats, optional): The center point of the instance
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        for polygon in polygons:
            for vertex in polygon["vertices"]:
                for num in vertex:
                    if not is_valid_number(num):
                        raise Exception(
                            "all polygon vertex coordinates must be valid int/float"
                        )

        if center is not None:
            for num in center:
                if not is_valid_number(num):
                    raise Exception(
                        "polygon center coordinates must be valid int/float"
                    )

        attrs: Dict[str, Any] = {"polygons": polygons, "center": center}

        if confidence is not None:
            if not is_valid_float(confidence):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "POLYGON_LIST_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    # TODO: Do we want to expect column major or row major?
    def add_2d_semseg(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        mask_url: Optional[str] = None,
        mask_data: Optional[Any] = None,
        resize_mode: Optional[ResizeMode] = None,
    ) -> None:
        """
        Add an inference for 2D semseg. These should provide either a mask_url or a mask_data.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            mask_url (str, optional): URL to the pixel mask png.
            mask_data (ndarray, optional): ndarray of pixel mask data, shape [height, width]
            resize_mode (ResizeMode, optional): if the mask is a different size from the base image, define how to display it
                "fill": stretch the mask to fit the base image dimensions
                None: no change
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if mask_data is None and mask_url is None:
            raise Exception("Please provide either a mask_data or a mask_url")

        if mask_url is not None:
            self.label_data.append(
                {
                    "uuid": label_id,
                    "linked_labels": [],
                    "label": "__mask",
                    "label_coordinate_frame": sensor_id,
                    "label_type": "SEMANTIC_LABEL_URL_2D",
                    "attributes": {"url": mask_url, "resize_mode": resize_mode},
                }
            )
            self._label_ids_set.add(label_id)

        elif mask_data is not None:
            if not HAS_PILLOW:
                raise Exception(
                    "To use mask_data, please install with additional image dependencies using `pip install aquariumlearning[img]`"
                )

            if not isinstance(mask_data, (np.ndarray, np.generic)):
                raise Exception("mask_data must be a numpy ndarray")

            if not np.issubdtype(mask_data.dtype, np.integer):
                raise Exception("mask_data must have an integer dtype")

            if len(mask_data.shape) != 2:
                raise Exception(
                    "mask_data must be a 2d ndarray of shape [height, width]"
                )

            # TODO: Validate
            # TODO: Is png encoding too slow? Would something like pycocotools RLE be better?
            unique_label_ids = np.unique(mask_data)
            for v in unique_label_ids:
                self._seen_label_class_ids.add(cast(int, v))

            # Compress to a png for later usage, and immediate compression
            png_img = Image.fromarray(mask_data.astype("uint8"))
            png_io = BytesIO()
            png_img.save(
                png_io, format="PNG", compress_level=6
            )  # 0-9, defualt is 6, we favor slightly faster
            png_io.seek(0)
            png_bytes = png_io.read()

            asset_uuid = str(uuid4())
            self.label_assets.append(
                {"uuid": asset_uuid, "asset_type": "SEMSEG_MASK", "value": png_bytes}
            )

            self.label_data.append(
                {
                    "uuid": label_id,
                    "linked_labels": [],
                    "label": "__mask",
                    "label_coordinate_frame": sensor_id,
                    "label_type": "SEMANTIC_LABEL_ASSET_2D",
                    "attributes": {
                        "asset_uuid": asset_uuid,
                        "resize_mode": resize_mode,
                    },
                }
            )
            self._label_ids_set.add(label_id)

    # TODO: Do we want to expect column major or row major?
    def add_2d_instance_seg(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        mask_url: Optional[str] = None,
        mask_data: Optional[Any] = None,
        instance_mapping: List[Dict[str, Any]],
        resize_mode: Optional[ResizeMode] = None,
    ) -> None:
        """
        Add an label for 2D instance segmentation. These should provide either a mask_url or a mask_data, and a instance mapping.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            mask_url (str, optional): URL to the pixel mask png.
            mask_data (ndarray, optional): ndarray of pixel mask data, shape [height, width]
            instance_mapping (List[Dict]): a list of instances present in the mask,
                each is a numeric `id`, string `classification`, and optional dict of additional attributes.
                As an example of one instance:
                .. code-block::
                        {
                            'id': 1,
                            'classification': "Person",
                            'attributes': {
                                'is_standing': false,
                            }
                        }
            resize_mode (ResizeMode, optional): if the mask is a different size from the base image, define how to display it
                "fill": stretch the mask to fit the base image dimensions
                None: no change
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if mask_data is None and mask_url is None:
            raise Exception("Please provide either a mask_data or a mask_url")

        for instance_info in instance_mapping:
            attrs = instance_info.get("attributes")
            if attrs is None:
                attrs = {}
            attrs["id"] = instance_info.get("id")
            attrs["resize_mode"] = resize_mode
            self.label_data.append(
                {
                    "uuid": label_id + "_" + str(instance_info.get("id")),
                    "linked_labels": [],
                    "label": instance_info.get("classification", ""),
                    "label_coordinate_frame": sensor_id,
                    "label_type": "INSTANCE_LABEL_2D",
                    "attributes": attrs,
                }
            )

        if mask_url is not None:
            self.label_data.append(
                {
                    "uuid": label_id,
                    "linked_labels": [],
                    "label": "__mask",
                    "label_coordinate_frame": sensor_id,
                    "label_type": "INSTANCE_LABEL_URL_2D",
                    "attributes": {"url": mask_url, "resize_mode": resize_mode},
                }
            )
            self._label_ids_set.add(label_id)

        elif mask_data is not None:
            if not HAS_PILLOW:
                raise Exception(
                    "To use mask_data, please install with additional image dependencies using `pip install aquariumlearning[img]`"
                )

            if not isinstance(mask_data, (np.ndarray, np.generic)):
                raise Exception("mask_data must be a numpy ndarray")

            if not np.issubdtype(mask_data.dtype, np.integer):
                raise Exception("mask_data must have an integer dtype")

            if len(mask_data.shape) != 2:
                raise Exception(
                    "mask_data must be a 2d ndarray of shape [height, width]"
                )

            # TODO: Validate
            # TODO: Is png encoding too slow? Would something like pycocotools RLE be better?
            unique_label_ids = np.unique(mask_data)
            for v in unique_label_ids:
                self._seen_label_class_ids.add(cast(int, v))

            # Compress to a png for later usage, and immediate compression
            png_img = Image.fromarray(mask_data.astype("uint8"))
            png_io = BytesIO()
            png_img.save(
                png_io, format="PNG", compress_level=6
            )  # 0-9, defualt is 6, we favor slightly faster
            png_io.seek(0)
            png_bytes = png_io.read()

            asset_uuid = str(uuid4())
            self.label_assets.append(
                {
                    "uuid": asset_uuid,
                    "asset_type": "INSTANCE_SEG_MASK",
                    "value": png_bytes,
                }
            )

            self.label_data.append(
                {
                    "uuid": label_id,
                    "linked_labels": [],
                    "label": "__mask",
                    "label_coordinate_frame": sensor_id,
                    "label_type": "INSTANCE_LABEL_ASSET_2D",
                    "attributes": {
                        "asset_uuid": asset_uuid,
                        "resize_mode": resize_mode,
                    },
                }
            )
            self._label_ids_set.add(label_id)

    def add_2d_classification(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        classification: str,
        confidence: Optional[float] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        secondary_labels: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an inference for 2D classification.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {}

        if confidence is not None:
            if not is_valid_float(confidence):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        if secondary_labels is not None:
            for k, v in secondary_labels.items():
                attrs[k] = v

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "CLASSIFICATION_2D",
                "label": classification,
                "label_coordinate_frame": sensor_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)

    def add_3d_classification(
        self,
        *,
        label_id: str,
        classification: str,
        confidence: Optional[float] = None,
        coord_frame_id: Optional[str] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a label for 3D classification.

        Args:
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            confidence (float): The confidence between 0.0 and 1.0 of the prediction
            coord_frame_id (optional, str): The coordinate frame id.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """

        if coord_frame_id is None:
            coord_frame_id = "world"

        if not isinstance(label_id, str):
            raise Exception("label ids must be strings")
        if "/" in label_id:
            raise Exception("label ids cannot contain slashes (/)")

        if not isinstance(classification, str):
            raise Exception("classifications must be strings")

        attrs = {}

        if confidence is not None:
            if not is_valid_float(confidence):
                raise Exception("confidence must be floats")
            if confidence < 0.0 or confidence > 1.0:
                raise Exception("confidence must be between 0.0 and 1.0")

            attrs["confidence"] = confidence

        add_object_user_attrs(attrs, user_attrs)

        self.label_data.append(
            {
                "uuid": label_id,
                "linked_labels": [],
                "label_type": "CLASSIFICATION_3D",
                "label": classification,
                "label_coordinate_frame": coord_frame_id,
                "attributes": attrs,
            }
        )
        self._label_ids_set.add(label_id)


class InferenceLabelSet(BaseLabelSet):
    custom_metrics: Dict[str, CustomMetricsEntry]
    visualization_assets: Dict[str, str]
    user_metadata: Dict[str, Any]
    reuse_latest_embedding: bool

    def __init__(
        self, *, frame_id: str, reuse_latest_embedding: Optional[bool] = False
    ) -> None:
        super().__init__(
            frame_id=frame_id,
            crop_type="Inference",
            reuse_latest_embedding=reuse_latest_embedding,
        )
        self.custom_metrics = {}
        self.visualization_assets = {}
        self.user_metadata = {}
        self.reuse_latest_embedding = (
            False if reuse_latest_embedding is None else reuse_latest_embedding
        )

    def add_custom_metric(self, name: str, value: CustomMetricsEntry) -> None:
        """Add a custom metric for a given inference frame.

        Args:
            name (str): The name of the custom metric being added. Must match one of the custom_metrics already defined by the corresponding Project.
            value (Union[float, List[List[Union[int, float]]]]): The value of the custom metric (either a float or 2d list of floats/integers).
        """
        if not (
            is_valid_float(value)
            or (
                isinstance(value, list)
                and all(all(is_valid_number(y) for y in x) for x in value)
            )
        ):
            raise Exception(
                "Custom metrics values must be either a float, or a 2D list of floats/integers."
            )

        self.custom_metrics[name] = value

    def add_visualization_asset(self, image_id: str, image_url: str) -> None:
        self.visualization_assets[image_id] = image_url

    def add_user_metadata(
        self,
        key: str,
        val: Union[str, int, float, bool],
    ) -> None:
        """Add a user provided metadata field.

        The types of these metadata fields will be infered and they'll be made
        available in the app for querying and metrics.

        Args:
            key (str): The key for your metadata field
            val (Union[str, int, float, bool]): value
            val_type (Literal["str", "int", "float", "bool"], optional): type of val as string. Defaults to None.
        """
        assert_valid_name(key)
        # Validates that neither val or type is None
        self.user_metadata[key] = val

    def to_dict(self) -> Dict[str, Any]:
        row = super().to_dict()

        row["custom_metrics"] = self.custom_metrics
        row["inference_metadata"] = {
            "visualization_assets": self.visualization_assets,
        }
        row["inference_data"] = row["label_data"]
        row["reuse_latest_embedding"] = self.reuse_latest_embedding
        del row["label_data"]

        row["inference_metadata"]["user_metadata"] = self.user_metadata

        return row

    def _to_summary(self) -> InferenceFrameSummary:
        """Converts this frame to a lightweight summary dict for internal cataloging

        Returns:
            dict: lightweight summaried frame
        """
        result: Any = super()._to_summary()
        result["custom_metrics_names"] = list(self.custom_metrics.keys())
        return result


class GTLabelSet(BaseLabelSet):
    def __init__(
        self, *, frame_id: str, reuse_latest_embedding: Optional[bool] = False
    ) -> None:
        super().__init__(
            frame_id=frame_id,
            crop_type="GT",
            reuse_latest_embedding=reuse_latest_embedding,
        )


class UpdateGTLabelSet(GTLabelSet):
    is_snapshot: bool

    def __init__(self, *, frame_id: str, is_snapshot: Optional[bool] = True) -> None:
        super().__init__(frame_id=frame_id)
        self.is_snapshot = True

    def to_dict(self) -> Dict[str, Any]:
        if self.is_snapshot:
            return super().to_dict()
        else:
            raise Exception("Not Implemented")


class UpdateInferenceLabelSet(InferenceLabelSet):
    is_snapshot: bool

    def __init__(self, *, frame_id: str, is_snapshot: Optional[bool] = True) -> None:
        super().__init__(frame_id=frame_id)
        self.is_snapshot = True

    def to_dict(self) -> Dict[str, Any]:
        if self.is_snapshot:
            return super().to_dict()
        else:
            raise Exception("Not Implemented")


# class Frame:

# class LabeledFrame:


# class FrameEmbedding:

# class CropEmbedding:
