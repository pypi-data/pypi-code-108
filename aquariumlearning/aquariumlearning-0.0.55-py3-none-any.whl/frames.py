"""frames.py
============
The base frame and update frame classes.
"""

import datetime
import json
import numbers
from io import IOBase
from tempfile import NamedTemporaryFile
import pyarrow as pa
import numpy as np
import pandas as pd
import re
from typing import Any, Optional, Union, Callable, List, Dict, Tuple, Set, IO, cast
from typing_extensions import Protocol, TypedDict

from .util import (
    ALL_CAMERA_MODELS,
    ALL_ORIENTATION_KEYS,
    ALL_POSITION_KEYS,
    CAMERA_MODELS,
    DEFAULT_SENSOR_ID,
    ResizeMode,
    _is_one_gb_available,
    assert_and_get_valid_iso_date,
    assert_valid_name,
    add_object_user_attrs,
    create_temp_directory,
    is_valid_float,
    is_valid_number,
    mark_temp_directory_complete,
    TYPE_PRIMITIVE_TO_STRING_MAP,
    USER_METADATA_SEQUENCE,
    USER_METADATA_PRIMITIVE_TYPES,
    USER_METADATA_MODE_TYPES,
    SUPPORTED_USER_METADATA_TYPES,
    POLYGON_VERTICES_KEYS,
    POSITION_KEYS,
    ORIENTATION_KEYS,
    KEYPOINT_KEYS,
    MAX_FRAMES_PER_BATCH,
    GtLabelEntryDict,
    FrameEmbeddingDict,
    CropEmbeddingDict,
    LabelType,
    LabelFrameSummary,
    InferenceFrameSummary,
    UpdateType,
)

from .labels import GTLabelSet, InferenceLabelSet

# TODO: optional types aren't supported in python, so we should avoid it
# TODO: Give these explicit, concrete typing
CoordinateFrameDict = Dict[str, Any]
SensorDataDict = Dict[str, Any]
GeoDataDict = Dict[str, Any]
UserMetadataEntry = Tuple[
    str,
    SUPPORTED_USER_METADATA_TYPES,
    USER_METADATA_PRIMITIVE_TYPES,
    USER_METADATA_MODE_TYPES,
]


# TODO: handle diffs?
class BaseFrame:
    """A labeled frame for a dataset.

    Args:
        frame_id (str): A unique id for this frame.
        date_captured (str, optional): ISO formatted datetime string. Defaults to None.
        device_id (str, optional): The device that generated this frame. Defaults to None.
    """

    device_id: str
    date_captured: str
    frame_id: str
    coordinate_frames: List[CoordinateFrameDict]
    sensor_data: List[SensorDataDict]
    geo_data: GeoDataDict
    user_metadata: List[UserMetadataEntry]
    _coord_frame_ids_set: Set[str]
    embedding: Optional[FrameEmbeddingDict]
    _label_ids_set: Set[str]
    reuse_latest_embedding: Optional[bool]
    frame_embedding_dim: int
    update_type: UpdateType

    def __init__(
        self,
        *,
        frame_id: str,
        date_captured: Optional[str] = None,
        device_id: Optional[str] = None,
        reuse_latest_embedding: Optional[bool] = False,
        update_type: UpdateType = "ADD",
    ) -> None:
        if not isinstance(frame_id, str):
            raise Exception("frame ids must be strings")

        if "/" in frame_id:
            raise Exception("frame ids cannot contain slashes (/)")

        self.frame_id = frame_id

        if date_captured is not None:
            self.date_captured = assert_and_get_valid_iso_date(date_captured)
        else:
            self.date_captured = str(datetime.datetime.now())

        if device_id is not None:
            self.device_id = device_id
        else:
            self.device_id = "default_device"

        self.coordinate_frames = []
        self.sensor_data = []
        self.geo_data = {}
        self.user_metadata = []
        self.embedding = None
        self.reuse_latest_embedding = reuse_latest_embedding
        self.frame_embedding_dim = -1

        self._coord_frame_ids_set = set()
        self._label_ids_set = set()
        self.update_type = update_type

    def _add_coordinate_frame(self, coord_frame_obj: Dict[str, str]) -> None:
        """Add coordinate frame to the dataset frame

        Args:
            coord_frame_obj (Dict[str, str]): takes in 'coordinate_frame_id', 'coordinate_frame_type' and optional 'coordinate_frame_metadata'(json dict)
        """
        self.coordinate_frames.append(coord_frame_obj)
        self._coord_frame_ids_set.add(coord_frame_obj["coordinate_frame_id"])

    def _coord_frame_exists(self, coord_frame_id: str) -> bool:
        """Check to see if the coord frame id is already part of the frame

        Args:
            coord_frame_id (str): The coord frame id to check for inclusion

        Returns:
            bool: whether or not the coord frame id is in the frame set
        """
        return coord_frame_id in self._coord_frame_ids_set

    def add_frame_embedding(
        self, *, embedding: List[float], model_id: str = ""
    ) -> None:
        """Add an embedding to this frame

        Args:
            embedding (List[float]): A vector of floats between length 0 and 12,000.
            model_id (str, optional): The model id used to generate these embeddings. Defaults to "".
        """
        if not embedding or len(embedding) > 12000:
            raise Exception("Length of embeddings should be between 0 and 12,000")

        for embedding_el in embedding:
            if not isinstance(embedding_el, numbers.Number):
                raise Exception(
                    f"Unexpectedly encountered a {type(embedding[0])} element. Only flat arrays of numbers are supported for embeddings."
                )

        if not self.embedding:
            self.frame_embedding_dim = len(embedding)
            self.embedding = {
                "task_id": self.frame_id,
                "model_id": model_id,
                "date_generated": str(datetime.datetime.now()),
                "embedding": embedding,
            }
            self.reuse_latest_embedding = False

    def add_user_metadata(
        self,
        key: str,
        val: Union[str, int, float, bool],
        val_type: Optional[USER_METADATA_PRIMITIVE_TYPES] = None,
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
        if val is None and val_type is None:
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata key {key} must provide "
                f"scalar value or expected type of scalar value if None"
            )
        # Validates that val has an accepted type
        if val is not None and type(val) not in TYPE_PRIMITIVE_TO_STRING_MAP:
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata Value {val} "
                f"not in accepted scalar value types {TYPE_PRIMITIVE_TO_STRING_MAP.values()}"
            )
        # Validates that val_type has an accepted type
        if val_type and val_type not in TYPE_PRIMITIVE_TO_STRING_MAP.values():
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata Value Type {val_type} "
                f"not in accepted scalar value types {TYPE_PRIMITIVE_TO_STRING_MAP.values()}"
            )

        # Sets val_type if it is not set
        if val_type is None:
            val_type = TYPE_PRIMITIVE_TO_STRING_MAP[type(val)]

        # If type is float, ensure that it is a valid float
        if val is not None and val_type == "float" and not is_valid_float(val):
            raise Exception(
                f"For frame_id {self.frame_id}, metadata key: {key}, value: {val}, "
                f"type is inferred as float but is not a valid float"
            )

        # Checks that inferred type matches what the user put in val_type
        if val is not None:
            for (
                primitive,
                type_string,
            ) in TYPE_PRIMITIVE_TO_STRING_MAP.items():
                if type(val) is primitive and val_type != type_string:
                    raise Exception(
                        f"For frame_id {self.frame_id}, metadata key: {key}, value: {val}, "
                        f"type is inferred as {type_string} but provided type was {val_type}"
                    )

        self.user_metadata.append((key, val, val_type, "scalar"))

    def add_user_metadata_list(
        self,
        key: str,
        val: USER_METADATA_SEQUENCE,
        list_elt_type: Optional[USER_METADATA_PRIMITIVE_TYPES] = None,
    ) -> None:
        """Add a user provided metadata list field.

        The types of these metadata fields will be infered and they'll be made
        available in the app for querying and metrics.

        Args:
            key (str): The key for your metadata field
            val (Union[List[int], List[str], List[bool], List[float], Tuple[int], Tuple[str], Tuple[bool], Tuple[float]]): value
            list_elt_type (Literal["str", "int", "float", "bool"], optional): type of list elements as string. Applies to all members of val. Defaults to None.
        """
        assert_valid_name(key)
        # Validates that neither val or type or mode is None
        if val is None and list_elt_type is None:
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata list key {key} must provide "
                f"list or expected type of list elements if None"
            )

        # Validates that val has an accepted type
        if val is not None:
            if type(val) not in (list, tuple):
                raise Exception(
                    f"For frame_id {self.frame_id}: User Metadata list value {val} "
                    f"is not in accepted sequence types list, tuple."
                )
            if len(val) == 0 and not list_elt_type:
                raise Exception(
                    f"For frame_id {self.frame_id}: User Metadata list value {val} "
                    f"is an empty {type(val).__name__}. "
                    "Please specify the expected scalar value type for its elements by passing a list_elt_type"
                )

            # validate that all elements in the list are the same primitive type, based on the first element
            if len(val) > 0:
                found_val_types = {type(el) for el in val}

                if len(found_val_types) > 1:
                    raise Exception(
                        f"For frame_id {self.frame_id}: User Metadata list value {val} "
                        f"has elements of invalid type. Expected all elements to be of the same type, found types of {found_val_types}"
                    )

                inferred_val_type = found_val_types.pop()
                if inferred_val_type not in TYPE_PRIMITIVE_TO_STRING_MAP:
                    raise Exception(
                        f"For frame_id {self.frame_id}: User Metadata list value {val} contains elements "
                        f"not in accepted scalar value types {TYPE_PRIMITIVE_TO_STRING_MAP.values()}"
                    )

        # Validates that list_elt_type has an accepted type
        if list_elt_type and list_elt_type not in TYPE_PRIMITIVE_TO_STRING_MAP.values():
            raise Exception(
                f"For frame_id {self.frame_id}: User Metadata list element type {list_elt_type} "
                f"not in accepted scalar value types {TYPE_PRIMITIVE_TO_STRING_MAP.values()}"
            )

        # Checks that inferred type matches what the user put in list_elt_type
        if list_elt_type is not None and val is not None and len(val) > 0:
            inferred_val_type = type(val[0])
            for (
                primitive,
                type_string,
            ) in TYPE_PRIMITIVE_TO_STRING_MAP.items():
                if inferred_val_type is primitive and list_elt_type != type_string:
                    raise Exception(
                        f"For frame_id {self.frame_id}, metadata key: {key}, value: {val}, "
                        f"element type is inferred as {type_string} but provided type was {list_elt_type}"
                    )

        # Sets list_elt_type if it is not set
        if list_elt_type is None:
            inferred_val_type = type(val[0])
            list_elt_type = TYPE_PRIMITIVE_TO_STRING_MAP[inferred_val_type]

        # If element type is float, ensure that all elements are valid floats
        if val is not None and list_elt_type == "float":
            for val_elt in val:
                if not is_valid_float(val_elt):
                    raise Exception(
                        f"For frame_id {self.frame_id}, metadata key: {key}, value: {val}, "
                        f"element type is inferred as float but is not a valid float"
                    )

        self.user_metadata.append((key, val, list_elt_type, "list"))

    def add_geo_latlong_data(self, lat: float, lon: float) -> None:
        """Add a user provided EPSG:4326 WGS84 lat long pair to each frame

        We expect these values to be floats

        Args:
            lat (float): lattitude of Geo Location
            lon (float): longitude of Geo Location
        """
        if not (isinstance(lat, float) and isinstance(lon, float)):
            raise Exception(
                f"Lattitude ({lat}) and Longitude ({lon}) must both be floats."
            )

        self.geo_data["geo_EPSG4326_lat"] = lat
        self.geo_data["geo_EPSG4326_lon"] = lon

    def add_point_cloud_pcd(
        self,
        *,
        sensor_id: str,
        pcd_url: str,
        coord_frame_id: Optional[str] = None,
        date_captured: Optional[str] = None,
        mirror_asset: Optional[bool] = False,
    ) -> None:
        """Add a point cloud sensor data point to this frame,
        contained in PCD format. ascii, binary, and binary_compressed formats are supported.
        Numeric values for the following column names are expected:
        x, y, z, intensity (optional), range (optional)

        Args:
            sensor_id (str): ID of sensor that generates this datapoint (optional if there is only 1 datapoint per frame)
            pcd_url (str): URL to PCD formated data
            coord_frame_id (Optional[str], optional): The coordinate frame id. Defaults to None.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
            mirror_asset (Optional[str]), optional): request this asset in this frame to be saved to Aquarium Storage. Useful for Short duration signed url assets.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        date_captured = assert_and_get_valid_iso_date(date_captured)

        if coord_frame_id is None:
            coord_frame_id = "world"

        data_urls = {
            "pcd_url": pcd_url,
        }

        if not self._coord_frame_exists(coord_frame_id):
            if coord_frame_id == "world":
                self._add_coordinate_frame(
                    {
                        "coordinate_frame_id": coord_frame_id,
                        "coordinate_frame_type": "WORLD",
                    }
                )
            else:
                raise Exception(
                    "Coordinate frame {} does not exist.".format(coord_frame_id)
                )

        self.sensor_data.append(
            {
                "coordinate_frame": coord_frame_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": {},
                "sensor_type": "POINTCLOUD_PCD_V0",
                "mirror_asset": mirror_asset,
            }
        )

    def add_point_cloud_bins(
        self,
        *,
        sensor_id: str,
        pointcloud_url: str = None,
        kitti_format_url: str = None,
        intensity_url: str = None,
        range_url: str = None,
        coord_frame_id: Optional[str] = None,
        date_captured: Optional[str] = None,
        mirror_asset: Optional[bool] = False,
    ) -> None:
        """Add a point cloud sensor data point to this frame, contained in dense binary files of
        little-endian values, similar to the raw format of KITTI lidar data. You can provide
        a combination of the following values, as long as at least either kitti_format_url or
        pointcloud_url are provided.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint (optional if there is only 1 datapoint per frame)
            pointcloud_url (Optional[str]): URL for the pointcloud: float32 [x1, y1, z1, x2, y2, z2, ...]
            kitti_format_url (Optional[str]): URL for the pointcloud + intensity: float32 [x1, y1, z1, i1, x2, y2, z2, i2, ...]
            intensity_url (Optional[str]): URL for the Intensity Pointcloud: unsigned int32 [i1, i2, ...]
            range_url (Optional[str]): URL for the Range Pointcloud: float32 [r1, r2, ...]
            coord_frame_id (Optional[str], optional): Id for the Coordinate Frame. Defaults to None.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
            mirror_asset (Optional[str]), optional): request this asset in this frame to be saved to Aquarium Storage. Useful for Short duration signed URL assets.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if pointcloud_url is None and kitti_format_url is None:
            raise Exception(
                "Either pointcloud_url or kitti_format_url must be provided."
            )

        if pointcloud_url is not None and kitti_format_url is not None:
            raise Exception(
                "Only one of pointcloud_url or kitti_format_url must be provided."
            )

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        date_captured = assert_and_get_valid_iso_date(date_captured)

        if coord_frame_id is None:
            coord_frame_id = "world"

        data_urls = {}
        if pointcloud_url is not None:
            data_urls["pointcloud_url"] = pointcloud_url
        if kitti_format_url is not None:
            data_urls["kitti_format_url"] = kitti_format_url
        if range_url is not None:
            data_urls["range_url"] = range_url
        if intensity_url is not None:
            data_urls["intensity_url"] = intensity_url

        if not self._coord_frame_exists(coord_frame_id):
            if coord_frame_id == "world":
                self._add_coordinate_frame(
                    {
                        "coordinate_frame_id": coord_frame_id,
                        "coordinate_frame_type": "WORLD",
                    }
                )
            else:
                raise Exception(
                    "Coordinate frame {} does not exist.".format(coord_frame_id)
                )

        self.sensor_data.append(
            {
                "coordinate_frame": coord_frame_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": {},
                "sensor_type": "POINTCLOUD_V0",
                "mirror_asset": mirror_asset,
            }
        )

    def add_obj(
        self,
        *,
        sensor_id: str,
        obj_url: str,
        coord_frame_id: Optional[str] = None,
        date_captured: Optional[str] = None,
        mirror_asset: Optional[bool] = False,
    ) -> None:
        """Add a .obj file to the frame for text based geometry

        Args:
            sensor_id (str): ID of sensor that generates this datapoint (optional if there is only 1 datapoint per frame)
            obj_url (str): URL to where the object is located
            coord_frame_id (Optional[str], optional): ID for the coordinate frame. Defaults to None.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
            mirror_asset (Optional[str]), optional): request this asset in this frame to be saved to Aquarium Storage. Useful for Short duration signed URL assets.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        date_captured = assert_and_get_valid_iso_date(date_captured)

        if coord_frame_id is None:
            coord_frame_id = "world"

        data_urls = {
            "obj_url": obj_url,
        }

        if not self._coord_frame_exists(coord_frame_id):
            self._add_coordinate_frame(
                {
                    "coordinate_frame_id": coord_frame_id,
                    "coordinate_frame_type": "WORLD",
                }
            )

        self.sensor_data.append(
            {
                "coordinate_frame": coord_frame_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": {},
                "sensor_type": "OBJ_V0",
                "mirror_asset": mirror_asset,
            }
        )

    def add_image(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        image_url: str,
        preview_url: Optional[str] = None,
        date_captured: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        coord_frame_id: Optional[str] = None,
        mirror_asset: Optional[bool] = False,
    ) -> None:
        """Add an image "sensor" data to this frame.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint (optional if there is only 1 datapoint per frame)
            image_url (str): The URL to load this image data.
            preview_url (Optional[str], optional): A URL to a compressed version of the image. It must be the same pixel dimensions as the original image. Defaults to None.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
            width (Optional[int], optional): The width of the image in pixels. Defaults to None.
            height (Optional[int], optional): The height of the image in pixels. Defaults to None.
            coord_frame_id (Optional[str], optional): Id for the Coordinate Frame (only accepts coordinate frames of type "IMAGE" or "IMAGE_PROJECTION"). Defaults to None.
            mirror_asset (Optional[str]), optional): request this asset in this frame to be saved to Aquarium Storage. Useful for Short duration signed URL assets.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        sensor_metadata = {}
        if width is not None:
            if not isinstance(width, int):
                raise Exception("width must be an int")
            sensor_metadata["width"] = width

        if height is not None:
            if not isinstance(height, int):
                raise Exception("height must be an int")
            sensor_metadata["height"] = height

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        date_captured = assert_and_get_valid_iso_date(date_captured)

        data_urls = {"image_url": image_url}
        if preview_url is not None:
            data_urls["preview_url"] = preview_url

        if coord_frame_id is None:
            coord_frame_id = sensor_id
            self._add_coordinate_frame(
                {
                    "coordinate_frame_id": coord_frame_id,
                    "coordinate_frame_type": "IMAGE",
                }
            )
        elif not self._coord_frame_exists(coord_frame_id):
            raise Exception(
                "Coordinate frame {} does not exist.".format(coord_frame_id)
            )

        for coordinate_frame in self.coordinate_frames:
            coord_type = coordinate_frame["coordinate_frame_type"]
            if (
                coordinate_frame["coordinate_frame_id"] == coord_frame_id
                and coord_type != "IMAGE"
                and coord_type != "IMAGE_PROJECTION"
            ):
                raise Exception(
                    'Coordinate frame {} is of type {} and must be either "IMAGE" or "IMAGE_PROJECTION".'.format(
                        coord_frame_id, coord_type
                    )
                )

        self.sensor_data.append(
            {
                "coordinate_frame": coord_frame_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": sensor_metadata,
                "sensor_type": "IMAGE_V0",
                "mirror_asset": mirror_asset,
            }
        )

    def add_image_overlay(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        overlay_id: str,
        image_url: str,
        date_captured: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        mirror_asset: Optional[bool] = False,
        resize_mode: Optional[ResizeMode] = None,
    ) -> None:
        """Add an image overlay for the given "sensor" to this frame.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint (optional if there is only 1 datapoint per frame)
            overlay_id (str): The id of this overlay.
            image_url (str): The URL to load this image data.
            date_captured (Optional[str], optional): ISO formatted date. Defaults to None.
            width (Optional[int], optional): The width of the image in pixels. Defaults to None.
            height (Optional[int], optional): The height of the image in pixels. Defaults to None.
            mirror_asset (Optional[str]), optional): request this asset in this frame to be saved to Aquarium Storage. Useful for Short duration signed URL assets.
            resize_mode (ResizeMode, optional): if the overlay is a different size from the base image, define how to display it
                "fill": stretch the overlay to fit the base image dimensions
                None: no change
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if not isinstance(overlay_id, str):
            raise Exception("overlay ids must be strings")

        sensor_metadata: Dict[str, Union[str, int]] = {
            "overlay_id": overlay_id,
            "resize_mode": str(resize_mode),
        }
        if width is not None:
            if not isinstance(width, int):
                raise Exception("width must be an int")
            sensor_metadata["width"] = width

        if height is not None:
            if not isinstance(height, int):
                raise Exception("height must be an int")
            sensor_metadata["height"] = height

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        date_captured = assert_and_get_valid_iso_date(date_captured)

        data_urls = {"image_url": image_url}

        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "IMAGE"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": sensor_metadata,
                "sensor_type": "IMAGE_OVERLAY_V0",
                "mirror_asset": mirror_asset,
            }
        )

    def add_audio(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        audio_url: str,
        date_captured: Optional[str] = None,
        mirror_asset: Optional[bool] = False,
    ) -> None:
        """Add an audio "sensor" data to this frame.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint (optional if there is only 1 datapoint per frame)
            audio_url (str): The URL to load this audio data (mp3, etc.).
            date_captured (str, optional): ISO formatted date. Defaults to None.
            mirror_asset (Optional[str]), optional): request this asset in this frame to be saved to Aquarium Storage. Useful for Short duration signed URL assets.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        sensor_metadata: Dict[str, Any] = {}
        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        date_captured = assert_and_get_valid_iso_date(date_captured)

        data_urls = {"audio_url": audio_url}

        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "AUDIO"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": sensor_metadata,
                "sensor_type": "AUDIO_V0",
                "mirror_asset": mirror_asset,
            }
        )

    def add_video(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        video_url: str,
        date_captured: Optional[str] = None,
        mirror_asset: Optional[bool] = False,
    ) -> None:
        """Add a video "sensor" data to this frame.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint (optional if there is only 1 datapoint per frame)
            video_url (str): The URL to load this video data (mp4, webm, etc.).
            date_captured (str, optional): ISO formatted date. Defaults to None.
            mirror_asset (Optional[str]), optional): request this asset in this frame to be saved to Aquarium Storage. Useful for Short duration signed URL assets.
        """
        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        sensor_metadata: Dict[str, Any] = {}
        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        date_captured = assert_and_get_valid_iso_date(date_captured)

        data_urls = {"video_url": video_url}

        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "VIDEO"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": sensor_metadata,
                "sensor_type": "VIDEO_V0",
                "mirror_asset": mirror_asset,
            }
        )

    def add_coordinate_frame_3d(
        self,
        *,
        coord_frame_id: str,
        position: Optional[Dict[POSITION_KEYS, Union[int, float]]] = None,
        orientation: Optional[Dict[ORIENTATION_KEYS, Union[int, float]]] = None,
        parent_frame_id: Optional[str] = None,
    ) -> None:
        """Add a 3D Coordinate Frame.

        Args:
            coord_frame_id (str): String identifier for this coordinate frame
            position (Optional[Dict[POSITION, Union[int, float]]], optional): Dict of the form {x, y, z}. Defaults to None.
            orientation (Optional[Dict[ORIENTATION, Union[int, float]]], optional): Quaternion rotation dict of the form {w, x, y, z}. Defaults to None.
            parent_frame_id (Optional[str], optional): String id of the parent coordinate frame. Defaults to None.
        """

        if not isinstance(coord_frame_id, str):
            raise Exception("coord_frame_id must be a string")

        if coord_frame_id == "world":
            raise Exception("coord_frame_id cannot be world")

        if self._coord_frame_exists(coord_frame_id):
            raise Exception("Coordinate frame already exists.")

        # If world doesn't exist, make the world coordinate frame
        if not self._coord_frame_exists("world"):
            self._add_coordinate_frame(
                {
                    "coordinate_frame_id": "world",
                    "coordinate_frame_type": "WORLD",
                }
            )

        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if type(position) is not dict:
            raise Exception("position improperly formatted")
        for position_key in ALL_POSITION_KEYS:
            if not is_valid_number(position[position_key]):
                raise Exception("position coordinates must be valid numbers")

        if orientation is None:
            orientation = {"w": 1, "x": 0, "y": 0, "z": 0}
        if type(orientation) is not dict:
            raise Exception("orientation improperly formatted")
        for orientation_key in ALL_ORIENTATION_KEYS:
            if not is_valid_number(orientation[orientation_key]):
                raise Exception("orientation coordinates must be valid numbers")

        if parent_frame_id is None:
            parent_frame_id = "world"

        if not isinstance(parent_frame_id, str):
            raise Exception("parent_frame_id must be a string or None.")

        metadata = {
            "position": position,
            "orientation": orientation,
            "parent_frame_id": parent_frame_id,
        }

        self._add_coordinate_frame(
            {
                "coordinate_frame_id": coord_frame_id,
                "coordinate_frame_type": "WORLD",
                "coordinate_frame_metadata": json.dumps(metadata),
            }
        )

    def add_coordinate_frame_2d(
        self,
        *,
        coord_frame_id: str,
        fx: Union[int, float],
        fy: Union[int, float],
        camera_model: Optional[CAMERA_MODELS] = None,
        position: Optional[Dict[POSITION_KEYS, Union[int, float]]] = None,
        orientation: Optional[Dict[ORIENTATION_KEYS, Union[int, float]]] = None,
        camera_matrix: Optional[List[List[Union[int, float]]]] = None,
        k1: Optional[Union[int, float]] = None,
        k2: Optional[Union[int, float]] = None,
        k3: Optional[Union[int, float]] = None,
        k4: Optional[Union[int, float]] = None,
        k5: Optional[Union[int, float]] = None,
        k6: Optional[Union[int, float]] = None,
        p1: Optional[Union[int, float]] = None,
        p2: Optional[Union[int, float]] = None,
        cx: Optional[Union[int, float]] = None,
        cy: Optional[Union[int, float]] = None,
        s1: Optional[Union[int, float]] = None,
        s2: Optional[Union[int, float]] = None,
        s3: Optional[Union[int, float]] = None,
        s4: Optional[Union[int, float]] = None,
        skew: Optional[Union[int, float]] = None,
        parent_frame_id: Optional[str] = None,
    ) -> None:
        """Add a 2D Coordinate Frame.

        Args:
            coord_frame_id (str): String identifier for this coordinate frame.
            fx (Union[int, float]): focal length x in pixels.
            fy (Union[int, float]): focal length y in pixels.
            camera_model (Optional[CAMERA_MODELS], optional): Either "fisheye" for the fisheye model, or "brown_conrady" for the pinhole model with Brown-Conrady distortion. Defaults to "brown_conrady".
            position (Optional[Dict[POSITION, Union[int, float]]], optional): Dict of the form {x, y, z}. Defaults to {x: 0, y: 0, z: 0}.
            orientation (Optional[Dict[ORIENTATION, Union[int, float]]], optional): Quaternion rotation dict of the form {w, x, y, z}. Defaults to {x: 0, y: 0, z: 0, w: 1}.
            camera_matrix (Optional[List[List[Union[int, float]]]], optional): 4x4 row major order camera matrix mapping 3d world space to camera space (x right, y down, z forward). Keep in mind, if you pass in the camera matrix it will stack on top of the position/orientation you pass in as well. This is only needed if you cannot properly represent your camera using the position/orientation parameters. Defaults to None.
            cx (Optional[Union[int, float]], optional): optical center pixel x coordinate. Defaults to x center of image.
            cy (Optional[Union[int, float]], optional): optical center pixel y coordinate. Defaults to y center of image.
            k1 (Optional[Union[int, float]], optional): k1 radial distortion coefficient (Brown-Conrady, fisheye). Defaults to 0.
            k2 (Optional[Union[int, float]], optional): k2 radial distortion coefficient (Brown-Conrady, fisheye). Defaults to 0.
            k3 (Optional[Union[int, float]], optional): k3 radial distortion coefficient (Brown-Conrady, fisheye). Defaults to 0.
            k4 (Optional[Union[int, float]], optional): k4 radial distortion coefficient (Brown-Conrady, fisheye). Defaults to 0.
            k5 (Optional[Union[int, float]], optional): k5 radial distortion coefficient (Brown-Conrady). Defaults to 0.
            k6 (Optional[Union[int, float]], optional): k6 radial distortion coefficient (Brown-Conrady). Defaults to 0.
            p1 (Optional[Union[int, float]], optional): p1 tangential distortion coefficient (Brown-Conrady). Defaults to 0.
            p2 (Optional[Union[int, float]], optional): p2 tangential distortion coefficient (Brown-Conrady). Defaults to 0.
            s1 (Optional[Union[int, float]], optional): s1 thin prism distortion coefficient (Brown-Conrady). Defaults to 0.
            s2 (Optional[Union[int, float]], optional): s2 thin prism distortion coefficient (Brown-Conrady). Defaults to 0.
            s3 (Optional[Union[int, float]], optional): s3 thin prism distortion coefficient (Brown-Conrady). Defaults to 0.
            s4 (Optional[Union[int, float]], optional): s4 thin prism distortion coefficient (Brown-Conrady). Defaults to 0.
            skew (Optional[Union[int, float]], optional): camera skew coefficient (fisheye). Defaults to 0.
            parent_frame_id (Optional[str], optional): String id of the parent coordinate frame. Defaults to None.
        """

        if not isinstance(coord_frame_id, str):
            raise Exception("coord_frame_id must be a string")

        if coord_frame_id == "world":
            raise Exception("coord_frame_id cannot be world")

        if self._coord_frame_exists(coord_frame_id):
            raise Exception("Coordinate frame already exists.")

        # If world doesn't exist, make the world coordinate frame
        if not self._coord_frame_exists("world"):
            self._add_coordinate_frame(
                {
                    "coordinate_frame_id": "world",
                    "coordinate_frame_type": "WORLD",
                }
            )

        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if type(position) is not dict:
            raise Exception("position improperly formatted")
        for position_key in ALL_POSITION_KEYS:
            if not is_valid_number(position[position_key]):
                raise Exception("position coordinates must be valid numbers")

        if orientation is None:
            orientation = {"w": 1, "x": 0, "y": 0, "z": 0}
        if type(orientation) is not dict:
            raise Exception("orientation improperly formatted")
        for orientation_key in ALL_ORIENTATION_KEYS:
            if not is_valid_number(orientation[orientation_key]):
                raise Exception("orientation coordinates must be valid numbers")

        if camera_matrix is not None:
            if type(camera_matrix) != list:
                raise Exception("camera matrix must be a python list of lists")
            if len(camera_matrix) != 4:
                raise Exception("camera matrix is not a properly formatted 4x4 matrix")
            for row in camera_matrix:
                if type(camera_matrix) != list:
                    raise Exception("camera matrix must be a python list of lists")
                if len(row) != 4:
                    raise Exception(
                        "camera matrix is not a properly formatted 4x4 matrix"
                    )
                for el in row:
                    if not is_valid_number(el):
                        raise Exception(
                            "element within camera matrix not a valid float/int"
                        )

        if parent_frame_id is None:
            parent_frame_id = "world"

        if not isinstance(parent_frame_id, str):
            raise Exception("parent_frame_id must be a string or None.")

        if not is_valid_number(fx) or not is_valid_number(fy):
            raise Exception("focal lengths are required and must be valid numbers")

        if fx == 0 or fy == 0:
            raise Exception("focal lengths cannot be 0")

        if camera_model is None:
            camera_model = "brown_conrady"

        if not isinstance(camera_model, str) or camera_model not in ALL_CAMERA_MODELS:
            raise Exception(
                "invalid camera model, valid values are {}".format(ALL_CAMERA_MODELS)
            )

        for coord in [k1, k2, k3, k4, k5, k6, p1, p2, cx, cy, s1, s2, s3, s4, skew]:
            if coord is not None and not is_valid_number(coord):
                raise Exception(
                    f"{coord} is not a valid 2D coordinate frame attribute. Must be float/int/None"
                )

        if (cx is None and cy is not None) or (cx is not None and cy is None):
            raise Exception("optical centers must both be None or both be numbers")
        if (cx is not None and cx <= 0) or (cy is not None and cy <= 0):
            raise Exception("optical centers must be greater than 0")

        metadata: Dict[str, Any] = {
            "fx": fx,
            "fy": fy,
            "camera_model": camera_model,
            "position": position,
            "orientation": orientation,
            "parent_frame_id": parent_frame_id,
        }

        if camera_matrix is not None:
            metadata["camera_matrix"] = camera_matrix
        if k1 is not None:
            metadata["k1"] = k1
        if k2 is not None:
            metadata["k2"] = k2
        if k3 is not None:
            metadata["k3"] = k3
        if k4 is not None:
            metadata["k4"] = k4
        if k5 is not None:
            metadata["k5"] = k5
        if k6 is not None:
            metadata["k6"] = k6
        if p1 is not None:
            metadata["p1"] = p1
        if p2 is not None:
            metadata["p2"] = p2
        if cx is not None:
            metadata["cx"] = cx
        if cy is not None:
            metadata["cy"] = cy
        if s1 is not None:
            metadata["s1"] = s1
        if s2 is not None:
            metadata["s2"] = s2
        if s3 is not None:
            metadata["s3"] = s3
        if s4 is not None:
            metadata["s4"] = s4
        if skew is not None:
            metadata["skew"] = skew

        self._add_coordinate_frame(
            {
                "coordinate_frame_id": coord_frame_id,
                "coordinate_frame_type": "IMAGE_PROJECTION",
                "coordinate_frame_metadata": json.dumps(metadata),
            }
        )

    def add_text(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        text: str,
        date_captured: Optional[str] = None,
    ) -> None:
        """Add a text "sensor" data to this frame.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint (optional if there is only 1 datapoint per frame)
            text (str): The text body.
            date_captured (str, optional): ISO formatted date. Defaults to None.
        """

        if not isinstance(sensor_id, str):
            raise Exception("sensor ids must be strings")

        if date_captured is None:
            date_captured = str(datetime.datetime.now())

        data_urls = {"text": text}
        self._add_coordinate_frame(
            {"coordinate_frame_id": sensor_id, "coordinate_frame_type": "TEXT"}
        )
        self.sensor_data.append(
            {
                "coordinate_frame": sensor_id,
                "data_urls": data_urls,
                "date_captured": date_captured,
                "sensor_id": sensor_id,
                "sensor_metadata": {},
                "sensor_type": "TEXT",
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert this frame into a dictionary representation.

        Returns:
            dict: dictified frame
        """
        row = {
            "task_id": self.frame_id,
            "date_captured": self.date_captured,
            "device_id": self.device_id,
            "coordinate_frames": self.coordinate_frames,
            "sensor_data": self.sensor_data,
            "geo_data": self.geo_data,
            "reuse_latest_embedding": self.reuse_latest_embedding,
        }
        user_metadata_types = {}
        user_metadata_modes = {}

        for k, v, vt, vm in self.user_metadata:
            namespaced = k
            if "user__" not in namespaced:
                namespaced = "user__" + namespaced
            # cast to BQ-serializable list if tuple
            row[namespaced] = list(v) if isinstance(v, tuple) else v
            user_metadata_types[namespaced] = vt
            user_metadata_modes[namespaced] = vm

        row["user_metadata_types"] = user_metadata_types
        row["user_metadata_modes"] = user_metadata_modes
        row["change"] = self.update_type
        return row


class UpdateFrame(BaseFrame):
    is_snapshot: bool

    def __init__(
        self,
        *,
        frame_id: str,
        update_type: UpdateType,
        is_snapshot: bool = True,
        date_captured: Optional[str] = None,
        device_id: Optional[str] = None,
    ):
        super().__init__(
            frame_id=frame_id, date_captured=date_captured, device_id=device_id
        )
        self.is_snapshot = is_snapshot

    def to_dict(self) -> Dict[str, Any]:
        """Convert this frame into a dictionary representation.

        Returns:
            dict: dictified frame
        """

        if self.is_snapshot:
            return super().to_dict()
        else:
            raise Exception("Not Implemented")
