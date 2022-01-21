"""dataset.py
============
The dataset and dataset frame classes.
"""

import datetime
import json
from io import IOBase
from tempfile import NamedTemporaryFile
import pyarrow as pa
import numpy as np
import pandas as pd
import re
from typing import Any, Optional, Union, Callable, List, Dict, Tuple, Set, IO, cast
from typing_extensions import Protocol, TypedDict

from .util import (
    ResizeMode,
    UpdateType,
    _is_one_gb_available,
    assert_valid_name,
    add_object_user_attrs,
    create_temp_directory,
    mark_temp_directory_complete,
    TYPE_PRIMITIVE_TO_STRING_MAP,
    USER_METADATA_PRIMITIVE,
    POLYGON_VERTICES_KEYS,
    POSITION_KEYS,
    ORIENTATION_KEYS,
    KEYPOINT_KEYS,
    MAX_FRAMES_PER_BATCH,
    DEFAULT_SENSOR_ID,
    GtLabelEntryDict,
    FrameEmbeddingDict,
    CropEmbeddingDict,
    LabelType,
    LabelFrameSummary,
    DUMMY_FRAME_EMBEDDING,
)
from .frames import BaseFrame
from .labels import GTLabelSet, InferenceLabelSet


class GTFrameWithEmbeddings(Protocol):
    embedding: FrameEmbeddingDict
    _labels: GTLabelSet


class LabeledFrame(BaseFrame):
    """A labeled frame for a dataset.

    Args:
        frame_id (str): A unique id for this frame.
        date_captured (str, optional): ISO formatted datetime string. Defaults to None.
        device_id (str, optional): The device that generated this frame. Defaults to None.
    """

    _labels: GTLabelSet

    def __init__(
        self,
        *,
        frame_id: str,
        date_captured: Optional[str] = None,
        device_id: Optional[str] = None,
        reuse_latest_embedding: Optional[bool] = False,
        update_type: UpdateType = "ADD",
    ) -> None:
        super(LabeledFrame, self).__init__(
            frame_id=frame_id,
            date_captured=date_captured,
            device_id=device_id,
            reuse_latest_embedding=reuse_latest_embedding,
            update_type=update_type,
        )

        self._labels = GTLabelSet(
            frame_id=frame_id, reuse_latest_embedding=reuse_latest_embedding
        )

    def _all_label_classes(self) -> List[str]:
        return self._labels._all_label_classes()

    def validate_and_backfill_crop_embeddings(self) -> bool:
        """Determines if there are frame embeddings but not Crop embeddings
        Backfills crop embeddings if Frame embeddings exist
        Returns True if backfill was necessary

        Returns:
            bool: returns if backfill on frame was necessary
        """

        # Handle case where Frame embedding is still None
        if not self.embedding:
            return False

        if len(self._labels.crop_embeddings) > 0:
            return False

        return_flag = False

        for label in self._labels.label_data:
            if label.get("label_type", "") in [
                "CLASSIFICATION_2D",
                "CLASSIFICATION_3D",
            ]:
                return False
            label_id = label["uuid"]

            self.add_crop_embedding(
                label_id=label_id, embedding=[0.0, 0.0, 0.0], model_id="crop_default"
            )
            return_flag = True
        return return_flag

    def add_crop_embedding(
        self, *, label_id: str, embedding: List[float], model_id: str = ""
    ) -> None:
        """Add a per label crop embedding

        Args:
            label_id (str): [description]
            embedding (List[float]): A vector of floats between length 0 and 12,000.
            model_id (str, optional): The model id used to generate these embeddings. Defaults to "".
        """
        self._labels.add_crop_embedding(
            label_id=label_id, embedding=embedding, model_id=model_id
        )

    # TODO: Better datamodel for embeddings, make it more first class
    def add_embedding(
        self,
        *,
        embedding: List[float],
        crop_embeddings: Optional[List[CropEmbeddingDict]] = None,
        model_id: str = "",
    ) -> None:
        """DEPRECATED! PLEASE USE add_frame_embedding and add_crop_embedding
        Add an embedding to this frame, and optionally to crops/labels within it.

        If provided, "crop_embeddings" is a list of dicts of the form:
            'uuid': the label id for the crop/label
            'embedding': a vector of floats between length 0 and 12,000.

        Args:
            embedding (list of floats): A vector of floats between length 0 and 12,000.
            crop_embeddings (list of dicts, optional): A list of dictionaries representing crop embeddings. Defaults to None.
            model_id (str, optional): The model id used to generate these embeddings. Defaults to "".
        """
        raise Exception("This method has been deprecated!")

    def add_label_text_token(
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
            confidence (float, optional): (Unlabeled Datasets Only) The confidence between 0.0 and 1.0 of the proposed label.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """
        self._labels.add_text_token(
            sensor_id=sensor_id,
            label_id=label_id,
            index=index,
            token=token,
            classification=classification,
            visible=visible,
            confidence=confidence,
            user_attrs=user_attrs,
        )

    # TODO: Dedupe code between here and inferences
    def add_label_3d_cuboid(
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
        """Add a label for a 3D cuboid.

        Args:
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            position (list of float): the position of the center of the cuboid
            dimensions (list of float): the dimensions of the cuboid
            rotation (list of float): the local rotation of the cuboid, represented as an xyzw quaternion.
            confidence (float, optional): (Unlabeled Datasets Only) The confidence between 0.0 and 1.0 of the proposed label.
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
            links (dict, optional): Links between labels. Defaults to None.
            coord_frame_id (str, optional): Coordinate frame id. Defaults to 'world'
        """
        if (
            coord_frame_id
            and coord_frame_id != "world"
            and not self._coord_frame_exists(coord_frame_id)
        ):
            raise Exception(f"Coordinate frame {coord_frame_id} does not exist.")

        self._labels.add_3d_cuboid(
            label_id=label_id,
            classification=classification,
            position=position,
            dimensions=dimensions,
            rotation=rotation,
            confidence=confidence,
            iscrowd=iscrowd,
            user_attrs=user_attrs,
            links=links,
            coord_frame_id=coord_frame_id,
        )

    def add_label_2d_bbox(
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
        iscrowd: Optional[bool] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a label for a 2D bounding box.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            top (int or float): The top of the box in pixels
            left (int or float): The left of the box in pixels
            width (int or float): The width of the box in pixels
            height (int or float): The height of the box in pixels
            confidence (float, optional): (Unlabeled Datasets Only) The confidence between 0.0 and 1.0 of the proposed label.
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
            links (dict, optional): Links between labels. Defaults to None.
        """
        self._labels.add_2d_bbox(
            sensor_id=sensor_id,
            label_id=label_id,
            classification=classification,
            top=top,
            left=left,
            width=width,
            height=height,
            confidence=confidence,
            area=None,
            iscrowd=iscrowd,
            user_attrs=user_attrs,
            links=links,
        )

    def add_label_2d_line_segment(
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
        """Add a label for a 2D line segment.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            x1 (int or float): The x-coord of the first vertex in pixels
            y1 (int or float): The x-coord of the first vertex in pixels
            x2 (int or float): The x-coord of the first vertex in pixels
            y2 (int or float): The x-coord of the first vertex in pixels
            confidence (float, optional): (Unlabeled Datasets Only) The confidence between 0.0 and 1.0 of the proposed label.
            iscrowd (bool, optional): Is this label marked as a crowd. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """
        self._labels.add_2d_line_segment(
            sensor_id=sensor_id,
            label_id=label_id,
            classification=classification,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            confidence=confidence,
            iscrowd=iscrowd,
            user_attrs=user_attrs,
            links=links,
        )

    def add_label_2d_keypoints(
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
        """Add a label for a 2D keypoints task.

        A keypoint is a dictionary of the form:
            'x': x-coordinate in pixels
            'y': y-coordinate in pixels
            'name': string name of the keypoint

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            keypoints (list of dicts): The keypoints of this detection
            confidence (float, optional): (Unlabeled Datasets Only) The confidence between 0.0 and 1.0 of the proposed label.
            top (int or float, optional): The top of the bounding box in pixels. Defaults to None.
            left (int or float, optional): The left of the bounding box in pixels. Defaults to None.
            width (int or float, optional): The width of the bounding box in pixels. Defaults to None.
            height (int or float, optional): The height of the bounding box in pixels. Defaults to None.
            polygons (list of dicts, optional): The polygon geometry. Defaults to None.
            center (list of ints or floats, optional): The center point of the polygon instance. Defaults to None.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """
        self._labels.add_2d_keypoints(
            sensor_id=sensor_id,
            label_id=label_id,
            classification=classification,
            keypoints=keypoints,
            confidence=confidence,
            top=top,
            left=left,
            width=width,
            height=height,
            polygons=polygons,
            center=center,
            user_attrs=user_attrs,
        )

    def add_label_2d_polygon_list(
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
        """Add a label for a 2D polygon list instance segmentation task.

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
            confidence (float, optional): (Unlabeled Datasets Only) The confidence between 0.0 and 1.0 of the proposed label.
            center (list of ints or floats, optional): The center point of the instance
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """
        self._labels.add_2d_polygon_list(
            sensor_id=sensor_id,
            label_id=label_id,
            classification=classification,
            polygons=polygons,
            confidence=confidence,
            center=center,
            user_attrs=user_attrs,
        )

    def add_label_2d_instance_seg(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        mask_url: Optional[str] = None,
        mask_data: Optional[Any] = None,
        instance_mapping: List[Dict[str, Any]],
        resize_mode: Optional[ResizeMode] = None,
    ) -> None:
        """Add a label for 2D instance segmentation.

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
        self._labels.add_2d_instance_seg(
            sensor_id=sensor_id,
            label_id=label_id,
            mask_url=mask_url,
            mask_data=mask_data,
            instance_mapping=instance_mapping,
            resize_mode=resize_mode,
        )

    def add_label_2d_semseg(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        mask_url: Optional[str] = None,
        mask_data: Optional[Any] = None,
        resize_mode: Optional[ResizeMode] = None,
    ) -> None:
        """Add a label for 2D semseg.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            mask_url (str, optional): URL to the pixel mask png.
            mask_data (ndarray, optional): ndarray of pixel mask data, shape [height, width]
            resize_mode (ResizeMode, optional): if the mask is a different size from the base image, define how to display it
                "fill": stretch the mask to fit the base image dimensions
                None: no change
        """
        self._labels.add_2d_semseg(
            sensor_id=sensor_id,
            label_id=label_id,
            mask_url=mask_url,
            mask_data=mask_data,
            resize_mode=resize_mode,
        )

    # TODO: handle secondary labels
    def add_label_2d_classification(
        self,
        *,
        sensor_id: str = DEFAULT_SENSOR_ID,
        label_id: str,
        classification: str,
        confidence: Optional[float] = None,
        secondary_labels: Optional[Dict[str, Any]] = None,
        user_attrs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a label for 2D classification.

        Args:
            sensor_id (str): ID of sensor that generates this datapoint. Must match base frame sensor_id. Do not use arg if not used in base frame.
            label_id (str): label_id which is unique across datasets and inferences.
            classification (str): the classification string
            confidence (float, optional): (Unlabeled Datasets Only) The confidence between 0.0 and 1.0 of the proposed label.
            secondary_labels (dict, optional): dictionary of secondary labels
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """
        self._labels.add_2d_classification(
            sensor_id=sensor_id,
            label_id=label_id,
            classification=classification,
            secondary_labels=secondary_labels,
            confidence=confidence,
            user_attrs=user_attrs,
        )

    def add_label_3d_classification(
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
            confidence (float, optional): (Unlabeled Datasets Only) The confidence between 0.0 and 1.0 of the proposed label.
            coord_frame_id (str, optional): The coordinate frame id.
            user_attrs (dict, optional): Any additional label-level metadata fields. Defaults to None.
        """
        if (
            coord_frame_id
            and coord_frame_id != "world"
            and not self._coord_frame_exists(coord_frame_id)
        ):
            raise Exception(f"Coordinate frame {coord_frame_id} does not exist.")

        self._labels.add_3d_classification(
            label_id=label_id,
            classification=classification,
            confidence=confidence,
            coord_frame_id=coord_frame_id,
            user_attrs=user_attrs,
        )

    def _to_summary(self) -> LabelFrameSummary:
        """Converts this frame to a lightweight summary dict for internal cataloging

        Returns:
            dict: lightweight summaried frame
        """
        return self._labels._to_summary()


class LabeledDataset:
    """A container used to construct a labeled dataset.

    Typical usage is to create a LabeledDataset, add multiple LabeledFrames to it,
    then serialize the frames to be submitted.
    """

    _frames: List[LabeledFrame]
    _frame_ids_set: Set[str]
    _label_ids_set: Set[str]
    _label_classes_set: Set[str]
    _label_class_ids_set: Set[int]
    _frame_summaries: List[LabelFrameSummary]
    _temp_frame_file_names: List[str]
    _temp_frame_asset_file_names: List[str]
    _temp_frame_embeddings_file_names: List[str]
    _temp_frame_file_names_streaming: List[str]
    _temp_frame_embeddings_file_names_streaming: List[str]
    _temp_crop_file_names_streaming: List[str]
    _temp_crop_embeddings_file_names_streaming: List[str]
    pipeline_mode: str
    backfilled_crops_flag: bool
    backfilled_frame_embs_flag: bool
    labels_with_confidence: bool
    crop_embedding_dim: Optional[int]
    frame_embedding_dim: Optional[int]
    sample_frame_embeddings: List[List[float]]
    sample_crop_embeddings: List[List[float]]

    def __init__(self, *, pipeline_mode: str = "BATCH") -> None:
        self._frames = []
        self._frame_ids_set = set()
        self._label_ids_set = set()
        self._label_classes_set = set()
        self._label_class_ids_set = set()
        self._frame_summaries = []
        current_time = datetime.datetime.now()
        self.temp_file_path = create_temp_directory()
        self._temp_frame_prefix = "al_{}_dataset_".format(
            current_time.strftime("%Y%m%d_%H%M%S_%f")
        )
        self._temp_frame_assets_prefix = "al_{}_dataset_".format(
            current_time.strftime("%Y%m%d_%H%M%S_%f")
        )
        self._temp_frame_embeddings_prefix = "al_{}_dataset_frame_embeddings_".format(
            current_time.strftime("%Y%m%d_%H%M%S_%f")
        )
        self._temp_crop_prefix = "al_{}_dataset_crops_".format(
            current_time.strftime("%Y%m%d_%H%M%S_%f")
        )
        self._temp_crop_embeddings_prefix = "al_{}_dataset_crop_embeddings_".format(
            current_time.strftime("%Y%m%d_%H%M%S_%f")
        )
        self._temp_frame_file_names = []
        self._temp_frame_embeddings_file_names = []
        self._temp_frame_asset_file_names = []

        self._temp_frame_file_names_streaming = []
        self._temp_frame_embeddings_file_names_streaming = []
        self._temp_crop_file_names_streaming = []
        self._temp_crop_embeddings_file_names_streaming = []
        self.pipeline_mode = pipeline_mode
        self.backfilled_crops_flag = False
        self.backfilled_frame_embs_flag = False
        self.crop_embedding_dim = None
        self.frame_embedding_dim = None
        self.sample_frame_embeddings = []
        self.sample_crop_embeddings = []
        self.labels_with_confidence = False

    def _cleanup_temp_dir(self) -> None:
        mark_temp_directory_complete(self.temp_file_path)

    def get_first_frame_dict(self) -> Dict[str, Any]:
        if self.pipeline_mode == "STREAMING":
            first_frame_file_name = self._temp_frame_file_names_streaming[0]
            first_crop_file_name = self._temp_crop_file_names_streaming[0]
            with open(first_frame_file_name, "r") as first_frame_file:
                with open(first_crop_file_name, "r") as first_crop_file:
                    first_frame_json = first_frame_file.readline().strip()
                    loaded_streaming: Dict[str, Any] = json.loads(first_frame_json)
                    first_crop_json = first_crop_file.readline().strip()
                    loaded_crop: Dict[str, Any] = json.loads(first_crop_json)
                    loaded_streaming["label_data"] = loaded_crop["label_data"]
                    return loaded_streaming
        else:
            first_frame_file_name = self._temp_frame_file_names[0]
            with open(first_frame_file_name, "r") as first_frame_file:
                first_frame_json = first_frame_file.readline().strip()
                loaded: Dict[str, Any] = json.loads(first_frame_json)
                return loaded

    def _check_labels_for_confidence(self, frame: LabeledFrame) -> None:
        """Checks if any GT labels have confidence and sets a flag if this is the case.
        (Only unlabeled dataset labels can have confidence values).
        """
        if self.labels_with_confidence:
            return

        for label in frame._labels.label_data:
            if label.get("attributes", {}).get("confidence") is not None:
                self.labels_with_confidence = True
                return

    def _save_rows_to_temp(
        self,
        file_name_prefix: str,
        writefunc: Callable[[IO[Any]], None],
        mode: str = "w",
    ) -> Optional[str]:
        """[summary]

        Args:
            file_name_prefix (str): prefix for the filename being saved
            writefunc ([filelike): function used to write data to the file opened

        Returns:
            str or None: path of file or none if nothing written
        """

        if not _is_one_gb_available():
            raise OSError(
                "Attempting to flush dataset to disk with less than 1 GB of available disk space. Exiting..."
            )

        data_rows_content = NamedTemporaryFile(
            mode=mode, delete=False, prefix=file_name_prefix, dir=self.temp_file_path
        )
        data_rows_content_path = data_rows_content.name
        writefunc(data_rows_content)

        # Nothing was written, return None
        if data_rows_content.tell() == 0:
            return None

        data_rows_content.seek(0)
        data_rows_content.close()
        return data_rows_content_path

    def _backfill_frame_embeddings_if_necessary(self) -> bool:
        """Determines if there are provided crop embeddings but no frame embeddings
        Backfills frame embeddings with dummy [0.0, 0.0, 0.0] if crop embeddings exist
        Returns True if backfill was necessary

        Returns:
            bool: returns if backfill on frame was necessary
        """
        if all([len(frame._labels.crop_embeddings) == 0 for frame in self._frames]):
            return False

        count = len([frame for frame in self._frames if frame.embedding is not None])
        if count != 0:
            return False

        for frame in self._frames:
            frame.add_frame_embedding(embedding=DUMMY_FRAME_EMBEDDING)

        return True

    def _flush_to_disk(self) -> None:
        """Writes the all the frames in the frame buffer to temp file on disk"""
        self.backfilled_frame_embs_flag = self._backfill_frame_embeddings_if_necessary()

        if self.pipeline_mode == "STREAMING":
            self._flush_to_disk_streaming()
        else:
            if len(self._frames) == 0:
                return
            frame_path = self._save_rows_to_temp(
                self._temp_frame_prefix, lambda x: self.write_to_file(x)
            )
            if frame_path:
                self._temp_frame_file_names.append(frame_path)
            embeddings_path = self._save_rows_to_temp(
                self._temp_frame_embeddings_prefix,
                lambda x: self.write_embeddings_to_file(x),
                mode="wb",
            )
            if embeddings_path:
                self._temp_frame_embeddings_file_names.append(embeddings_path)

            assets_path = self._save_rows_to_temp(
                self._temp_frame_assets_prefix,
                lambda x: self.write_label_assets_to_file(x),
                mode="wb",
            )
            if assets_path:
                self._temp_frame_asset_file_names.append(assets_path)

            self._frames = []

    def _flush_to_disk_streaming(self) -> None:
        """Writes the all the frames in the frame buffer to temp file on disk"""
        if len(self._frames) == 0:
            return
        frame_path = self._save_rows_to_temp(
            self._temp_frame_prefix, lambda x: self.write_frames_to_file_streaming(x)
        )
        crop_path = self._save_rows_to_temp(
            self._temp_crop_prefix, lambda x: self.write_labels_to_file_streaming(x)
        )
        if frame_path:
            self._temp_frame_file_names_streaming.append(frame_path)
        if crop_path:
            self._temp_crop_file_names_streaming.append(crop_path)

        frame_embeddings_path = self._save_rows_to_temp(
            self._temp_frame_embeddings_prefix,
            lambda x: self.write_frame_embeddings_to_file_streaming(x),
            mode="wb",
        )
        if frame_embeddings_path:
            self._temp_frame_embeddings_file_names_streaming.append(
                frame_embeddings_path
            )

        crop_embeddings_path = self._save_rows_to_temp(
            self._temp_crop_embeddings_prefix,
            lambda x: self.write_crop_embeddings_to_file_streaming(x),
            mode="wb",
        )
        if crop_embeddings_path:
            self._temp_crop_embeddings_file_names_streaming.append(crop_embeddings_path)

        assets_path = self._save_rows_to_temp(
            self._temp_frame_assets_prefix,
            lambda x: self.write_label_assets_to_file(x),
            mode="wb",
        )
        if assets_path:
            self._temp_frame_asset_file_names.append(assets_path)

        self._frames = []

    def _validate_frame(
        self, frame_summary: LabelFrameSummary, project_info: Dict[str, Any]
    ) -> None:
        """Validates single frame in set according to project constraints

        Args:
            frame_summary Dict[str, Any]: dictionary representation of a LabeledFrame's summary
            project_info Dict[str, Any]: metadata about the project being uploaded to
        """

        frame_id = frame_summary["frame_id"]
        primary_task = project_info.get("primary_task")

        # TODO: Should also check this for classification here.
        # 2D_SEMSEG frames may only have one label of type SEMANTIC_LABEL_URL_2D
        if primary_task == "2D_SEMSEG":
            label_counts = frame_summary["label_counts"]
            url_count = label_counts.get("SEMANTIC_LABEL_URL_2D", 0)
            assets_count = label_counts.get("SEMANTIC_LABEL_ASSET_2D", 0)
            if url_count + assets_count != 1:
                extra_labels = filter(
                    lambda x: x != "SEMANTIC_LABEL_URL_2D"
                    and x != "SEMANTIC_LABEL_ASSET_2D",
                    label_counts.keys(),
                )
                issue_text = (
                    "has no labels"
                    if not len(label_counts)
                    else f"has label types of {list(extra_labels)}"
                )
                raise Exception(
                    f"Frame {frame_id} {issue_text}. Dataset frames for 2D_SEMSEG projects must have exactly one 2d_semseg label"
                )

        if primary_task == "2D_INSTANCE_SEGMENTATION":
            label_counts = frame_summary["label_counts"]
            url_count = label_counts.get("INSTANCE_LABEL_URL_2D", 0)
            assets_count = label_counts.get("INSTANCE_LABEL_ASSET_2D", 0)
            if url_count + assets_count != 1:
                extra_labels = filter(
                    lambda x: x != "INSTANCE_LABEL_URL_2D"
                    and x != "INSTANCE_LABEL_ASSET_2D",
                    label_counts.keys(),
                )
                issue_text = (
                    "has no labels"
                    if not len(label_counts)
                    else f"has label types of {list(extra_labels)}"
                )
                raise Exception(
                    f"Frame {frame_id} {issue_text}. Dataset frames for 2D_INSTANCE_SEGMENTATION projects must have exactly one 2d_instance_seg label"
                )

    def _validate_frames(self, project_info: Dict[str, Any]) -> None:
        """Validates all frames in set according to project constraints

        Args:
            project_info Dict[str, Any]: metadata about the project being uploaded to
        """
        for frame_summary in self._frame_summaries:
            self._validate_frame(frame_summary, project_info)
        if self.backfilled_crops_flag:
            print(
                "WARNING: One or more Frames contained Frame Embeddings with Crops with no Crop Embeddings. All crops without Crop Embeddings have been backfilled with a default Embedding Vector"
            )
        if self.backfilled_frame_embs_flag:
            print(
                "WARNING: Crop Embeddings were provided but no Frame Embeddings were provided. All frames have backfilled with a default Frame Embedding Vector"
            )

    def add_frame(self, frame: LabeledFrame) -> None:
        """Add a LabeledFrame to this dataset.

        Args:
            frame (LabeledFrame): A LabeledFrame in this dataset.
        """
        if not isinstance(frame, LabeledFrame):
            raise Exception("Frame is not an LabeledFrame")

        if frame.frame_id in self._frame_ids_set:
            raise Exception("Attempted to add duplicate frame id.")

        duplicate_label_ids = frame._labels._label_ids_set & self._label_ids_set
        if duplicate_label_ids:
            raise Exception(
                f"Attempted to add duplicate label id(s): {duplicate_label_ids}"
            )

        self.backfilled_crops_flag = frame.validate_and_backfill_crop_embeddings()
        self._check_labels_for_confidence(frame)
        self._frames.append(frame)
        self._frame_ids_set.add(frame.frame_id)
        self._label_ids_set.update(frame._labels._label_ids_set)
        self._label_class_ids_set.update(frame._labels._seen_label_class_ids)
        self._label_classes_set.update(frame._all_label_classes())
        self._frame_summaries.append(frame._to_summary())

        if self.frame_embedding_dim is None:
            self.frame_embedding_dim = frame.frame_embedding_dim
        elif self.frame_embedding_dim != frame.frame_embedding_dim:
            raise Exception(
                f"Length of frame embeddings must be the same, existing embeddings are of dimension {self.frame_embedding_dim} but new embedding has dimension {frame.frame_embedding_dim}"
            )

        frame_embedding = (frame.embedding or {"embedding": None}).get("embedding")
        if frame_embedding and len(self.sample_frame_embeddings) < 5:
            self.sample_frame_embeddings.append(frame_embedding)

        if len(frame._labels._label_ids_set) > 0:
            if len(frame._labels.crop_embeddings) > 0 and len(
                frame._labels.crop_embeddings
            ) != len(frame._labels._label_ids_set):
                raise Exception(
                    f"Embeddings must be provided for all crops or no crops. Embeddings are provided for partial crops for frame {frame.frame_id}."
                )

            crop_embedding_dim = (
                frame._labels.crop_embedding_dim
                if frame._labels.crop_embedding_dim
                else -1
            )
            if self.crop_embedding_dim is None:
                self.crop_embedding_dim = crop_embedding_dim
            elif self.crop_embedding_dim != crop_embedding_dim:
                raise Exception(
                    f"Length of crop embeddings must be the same, existing embeddings are of dimension {self.crop_embedding_dim} but new embedding has dimension {crop_embedding_dim}"
                )

            if (
                len(frame._labels.crop_embeddings) > 0
                and len(self.sample_crop_embeddings) < 5
            ):
                remaining = 5 - len(self.sample_crop_embeddings)
                self.sample_crop_embeddings += [
                    x["embedding"] for x in frame._labels.crop_embeddings[0:remaining]
                ]

        if len(self._frames) >= MAX_FRAMES_PER_BATCH:
            self._flush_to_disk()

    def delete_frame(self, frame_id: str) -> None:
        """Delete a frame to this dataset.

        Args:
            frame_id: A frame_id in the dataset.
        """
        if frame_id in self._frame_ids_set:
            raise Exception("Attempted to add and delete the same frame id.")

        self._frames.append(
            LabeledFrame(
                frame_id=frame_id, reuse_latest_embedding=True, update_type="DELETE"
            )
        )
        self._frame_ids_set.add(frame_id)

        if len(self._frames) >= MAX_FRAMES_PER_BATCH:
            self._flush_to_disk()

    def write_to_file(self, filelike: IO[Any]) -> None:
        """Write the frame content to a text filelike object (File handle, StringIO, etc.)

        Args:
            filelike (filelike): The destination file-like to write to.
        """
        for frame in self._frames:
            if frame.update_type != "ADD":
                continue
            row = frame.to_dict()
            row["label_data"] = frame._labels.to_dict()["label_data"]
            filelike.write(json.dumps(row) + "\n")

    # TODO: Does this need a streaming equivalent?
    def write_label_assets_to_file(self, filelike: IO[Any]) -> None:
        """Write the frame's label assets to a text filelike object (File handle, StringIO, etc.)

        Args:
            filelike (filelike): The destination file-like to write to.
        """
        count = len(self._frames)
        with_label_assets_count = len(
            [frame for frame in self._frames if len(frame._labels.label_assets) > 0]
        )
        if with_label_assets_count == 0:
            return

        frame_ids = np.empty((count), dtype=object)
        label_assets = np.empty((count), dtype=object)

        for i, frame in enumerate(self._frames):
            frame_ids[i] = frame.frame_id
            label_assets[i] = frame._labels.label_assets

        df = pd.DataFrame(
            {"frame_ids": pd.Series(frame_ids), "label_assets": pd.Series(label_assets)}
        )

        arrow_data = pa.Table.from_pandas(df)
        writer = pa.ipc.new_file(filelike, arrow_data.schema, use_legacy_format=False)
        writer.write(arrow_data)
        writer.close()

    def write_embeddings_to_file(self, filelike: IO[Any]) -> None:
        """Write the frame's embeddings to a text filelike object (File handle, StringIO, etc.)

        Args:
            filelike (filelike): The destination file-like to write to.
        """
        count = len([frame for frame in self._frames if frame.embedding is not None])

        if count == 0:
            return

        if count != len(self._frames):
            raise Exception(
                "If any frames have user provided embeddings, all frames must have embeddings."
            )

        # TODO: Is there a pattern like type predicate functions we can use
        # to avoid error-prone inline manual casts like this?
        frames_with_embs = cast(List[GTFrameWithEmbeddings], self._frames)

        for frame in frames_with_embs:
            if frame._labels.crop_embeddings:
                break

        frame_ids = np.empty((count), dtype=object)
        frame_embeddings = np.empty((count), dtype=object)
        crop_ids = np.empty((count), dtype=object)
        crop_embeddings = np.empty((count), dtype=object)

        for i, frame in enumerate(frames_with_embs):
            frame_ids[i] = frame.embedding["task_id"]
            frame_embeddings[i] = frame.embedding["embedding"]
            crop_ids[i] = [x["uuid"] for x in frame._labels.crop_embeddings]
            crop_embeddings[i] = [x["embedding"] for x in frame._labels.crop_embeddings]

        df = pd.DataFrame(
            {
                "frame_ids": pd.Series(frame_ids),
                "frame_embeddings": pd.Series(frame_embeddings),
                "crop_ids": pd.Series(crop_ids),
                "crop_embeddings": pd.Series(crop_embeddings),
            }
        )

        arrow_data = pa.Table.from_pandas(df)
        writer = pa.ipc.new_file(filelike, arrow_data.schema, use_legacy_format=False)
        writer.write(arrow_data)
        writer.close()

    def write_frames_to_file_streaming(self, filelike: IO[Any]) -> None:
        """Write the frame content to a text filelike object (File handle, StringIO, etc.)

        Args:
            filelike (filelike): The destination file-like to write to.
        """
        for frame in self._frames:
            row = frame.to_dict()
            filelike.write(json.dumps(row) + "\n")

    def write_labels_to_file_streaming(self, filelike: IO[Any]) -> None:
        """Write the frame content to a text filelike object (File handle, StringIO, etc.)

        Args:
            filelike (filelike): The destination file-like to write to.
        """
        for frame in self._frames:
            row = frame._labels.to_dict()
            filelike.write(json.dumps(row) + "\n")

    def write_frame_embeddings_to_file_streaming(self, filelike: IO[Any]) -> None:
        """Write the frame's embeddings to a text filelike object (File handle, StringIO, etc.)

        Args:
            filelike (filelike): The destination file-like to write to.
        """

        count = len([frame for frame in self._frames if frame.embedding is not None])
        if count == 0:
            return

        if count != len(self._frames):
            raise Exception(
                "If any frames have user provided embeddings, all frames must have embeddings."
            )

        # TODO: Is there a pattern like type predicate functions we can use
        # to avoid error-prone inline manual casts like this?
        frames_with_embs = cast(List[GTFrameWithEmbeddings], self._frames)

        frame_ids = np.empty((count), dtype=object)
        frame_embeddings = np.empty((count), dtype=object)

        for i, frame in enumerate(frames_with_embs):
            frame_ids[i] = frame.embedding["task_id"]
            frame_embeddings[i] = frame.embedding["embedding"]

        df = pd.DataFrame(
            {
                "frame_ids": pd.Series(frame_ids),
                "frame_embeddings": pd.Series(frame_embeddings),
            }
        )

        arrow_data = pa.Table.from_pandas(df)
        writer = pa.ipc.new_file(filelike, arrow_data.schema, use_legacy_format=False)
        writer.write(arrow_data)
        writer.close()

    def write_crop_embeddings_to_file_streaming(self, filelike: IO[Any]) -> None:
        """Write the frame's embeddings to a text filelike object (File handle, StringIO, etc.)

        Args:
            filelike (filelike): The destination file-like to write to.
        """
        count = len([frame for frame in self._frames if frame.embedding is not None])

        if count == 0:
            return

        if count != len(self._frames):
            raise Exception(
                "If any frames have user provided embeddings, all frames must have embeddings."
            )

        # TODO: Is there a pattern like type predicate functions we can use
        # to avoid error-prone inline manual casts like this?
        frames_with_embs = cast(List[GTFrameWithEmbeddings], self._frames)

        # Get the first frame embedding dimension
        crop_ids = np.empty((count), dtype=object)
        crop_embeddings = np.empty((count), dtype=object)

        for i, frame in enumerate(frames_with_embs):
            crop_ids[i] = [x["uuid"] for x in frame._labels.crop_embeddings]
            crop_embeddings[i] = [x["embedding"] for x in frame._labels.crop_embeddings]

        df = pd.DataFrame(
            {
                "crop_ids": pd.Series(crop_ids),
                "crop_embeddings": pd.Series(crop_embeddings),
            }
        )

        arrow_data = pa.Table.from_pandas(df)
        writer = pa.ipc.new_file(filelike, arrow_data.schema, use_legacy_format=False)
        writer.write(arrow_data)
        writer.close()
