# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class that contains all of the information associated with a single bounding box."""

import copy
from typing import Any, Dict, List, Optional

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.object_detection.common.constants import DatasetFieldLabels
from azureml.automl.dnn.vision.object_detection.common.masktools import convert_polygon_to_rle_masks


logger = get_logger(__name__)


class ObjectAnnotation:
    """Class that contains all of the information associated with
    a single bounding box."""

    def __init__(self, labels: Dict[str, Any], masks_required: bool = False) -> None:
        """
        :param labels: Information about the bounding box in the image,
                       must contain label, topX, topY, bottomX, bottomY.
        :type labels: dict
        :param masks_required: If masks information is required
        :type masks_required: bool
        """

        self._bounding_box: Optional[List[Any]] = None
        self._missing_properties = True
        self._label: Optional[str] = None
        self._area: Optional[float] = None
        self._iscrowd = 0

        self._width = None
        self._height = None

        self._masks_required = masks_required

        # Optional parameters required for instance segmentation
        self._normalized_mask_poly: Optional[List[Any]] = []
        self._mask_poly: List[Any] = []
        self._rle_masks = None

        self._init_labels(labels)
        self._valid = self._validate()

    @property
    def bounding_box(self):
        """Get bounding box coordinates

        :return: Bounding box in form [top, left, bottom, right] in pixel coordinates
        :rtype: typing.List[float]
        """
        return self._bounding_box

    @property
    def label(self):
        """Get bounding box classification

        :return: Classification for bounding box object
        :rtype: str
        """
        return self._label

    @property
    def area(self):
        """Get bounding box area

        :return: Area of bounding box
        :rtype: float
        """
        return self._area

    @property
    def iscrowd(self):
        """Get image is iscrowd

        :return: 0 for not crowd, 1 for crowd
        :rtype: int
        """
        return self._iscrowd

    @property
    def missing_properties(self):
        """Are the properties related to width, height, area been filled in."""
        return self._missing_properties

    @property
    def rle_masks(self):
        """Get the list of run-length encoded masks.

        :return: List of rle masks.
        :rtype: typing.List[dict]
        """
        return self._rle_masks

    @property
    def valid(self):
        """Get if annotation is valid

        :return: Valid or not
        :rtype: bool
        """
        return self._valid

    def _init_labels(self, labels):

        if not isinstance(labels, dict):
            raise AutoMLVisionDataException(
                "For Object Detection and Instance segmentation tasks, the label " +
                "column in the dataset should be a dictionary. Found type {}.".format(type(labels)),
                has_pii=False)
        # Optional load of mask for instance segmentation
        # copy normalized_mask_poly here since it might be modified in self._validate later
        # TODO: The variable below is used as both list and boolean. Should be fixed.
        self._normalized_mask_poly = copy.deepcopy(labels.get(DatasetFieldLabels.POLYGON, False))
        has_valid_normalized_mask_poly = self._normalized_mask_poly is not False  # type: ignore[comparison-overlap]

        has_valid_bounding_box = (DatasetFieldLabels.X_0_PERCENT in labels and DatasetFieldLabels.Y_0_PERCENT in
                                  labels and DatasetFieldLabels.X_1_PERCENT
                                  in labels and DatasetFieldLabels.Y_1_PERCENT in labels)

        has_valid_instance = has_valid_bounding_box or has_valid_normalized_mask_poly

        if DatasetFieldLabels.CLASS_LABEL not in labels or not has_valid_instance:
            raise AutoMLVisionDataException("Incomplete Record", has_pii=False)

        self._label = labels[DatasetFieldLabels.CLASS_LABEL]

        if DatasetFieldLabels.IS_CROWD in labels:
            self._iscrowd = int(labels[DatasetFieldLabels.IS_CROWD] in {"true", "True", "1", 1})

        if has_valid_normalized_mask_poly:
            self._update_box_percentages_from_normalized_mask_poly()
        else:
            try:
                self._x0_percentage = float(labels[DatasetFieldLabels.X_0_PERCENT])
                self._y0_percentage = float(labels[DatasetFieldLabels.Y_0_PERCENT])
                self._x1_percentage = float(labels[DatasetFieldLabels.X_1_PERCENT])
                self._y1_percentage = float(labels[DatasetFieldLabels.Y_1_PERCENT])
            except (TypeError, ValueError):
                raise AutoMLVisionDataException(
                    "Expected int or float types for box coordinates in labels dictionary, found invalid types",
                    has_pii=False)

        # TODO - change to always have the fill_box_properties method called
        # depending on the model, this will be overridden by fill_box_properties
        self._bounding_box = [self._label,
                              self._x0_percentage, self._y0_percentage,
                              self._x1_percentage, self._y1_percentage]

    def _update_box_percentages_from_normalized_mask_poly(self):
        """Update x0,x1,y0,y1 percentage from normalized mask poly """
        x_min_percent, x_max_percent, y_min_percent, y_max_percent = 101., -1., 101., -1.
        if self._normalized_mask_poly and self._normalized_mask_poly[0]:
            for segment in self._normalized_mask_poly:
                xs, ys = segment[::2], segment[1::2]
                if len(xs) != len(ys):
                    raise AutoMLVisionDataException(
                        "Invalid Polygon: should be equal numbers of Xs and Ys",
                        has_pii=False)
                x_min_percent = min(x_min_percent, min(xs))
                x_max_percent = max(x_max_percent, max(xs))
                y_min_percent = min(y_min_percent, min(ys))
                y_max_percent = max(y_max_percent, max(ys))

        self._x0_percentage = x_min_percent
        self._y0_percentage = y_min_percent
        self._x1_percentage = x_max_percent
        self._y1_percentage = y_max_percent

    def fill_box_properties(self, height, width):
        """Fills box properties that are computed from image's width and height.

        :param height: height in pixels
        :type height: int
        :param width: width in pixels
        :type width: int
        """
        self._bounding_box = [self._x0_percentage * width,
                              self._y0_percentage * height,
                              self._x1_percentage * width,
                              self._y1_percentage * height]

        self._area = (self._bounding_box[2] - self._bounding_box[0]) * \
                     (self._bounding_box[3] - self._bounding_box[1])

        if self._normalized_mask_poly:
            self._mask_poly = copy.deepcopy(self._normalized_mask_poly)
            for segment in self._mask_poly:
                segment[::2] = [x * width for x in segment[::2]]
                segment[1::2] = [y * height for y in segment[1::2]]

            self._rle_masks = convert_polygon_to_rle_masks(self._mask_poly,
                                                           height,
                                                           width)

        self._width = width
        self._height = height
        self._missing_properties = False

    def _validate(self):
        """Check if the annotation is a valid one.

        :return: Valid or not
        :rtype: bool
        """
        if self._normalized_mask_poly and self._normalized_mask_poly[0]:
            self._remove_invalid_segments_from_normalized_mask_poly()
            # Invalid if polygon is empty after removing invalid segments.
            if bool(self._normalized_mask_poly) is False:
                return False

        # Invalid if masks is required, and polygon is empty after removing invalid segments.
        if self._masks_required and bool(self._normalized_mask_poly) is False:
            return False

        # Validate bounding box percentage coordinates.
        normalized_bbox = [self._x0_percentage, self._y0_percentage,
                           self._x1_percentage, self._y1_percentage]
        valid_normalized_bbox = \
            all(entry >= 0.0 and entry <= 1.0 for entry in normalized_bbox) and \
            self._x0_percentage < self._x1_percentage and \
            self._y0_percentage < self._y1_percentage
        return valid_normalized_bbox

    def _remove_invalid_segments_from_normalized_mask_poly(self):
        """ Remove invalid segments from self._normalized_mask_poly and
            update bounding box percentage co-ordinates.
        """
        if self._normalized_mask_poly is None:
            return

        invalid_segment_indices = []
        for idx, segment in enumerate(self._normalized_mask_poly):
            if len(segment) < 5:
                # Remove invalid segments with number of polygon points < 5 to fix
                # the issue: TypeError (Argument 'bb' has incorrect type) in
                # pycocotools https://github.com/cocodataset/cocoapi/issues/139
                invalid_segment_indices.append(idx)
            elif any(entry < 0.0 or entry > 1.0 for entry in segment):
                # Remove invalid segments with percentage coordinates out of bounds
                invalid_segment_indices.append(idx)

        for idx in reversed(invalid_segment_indices):
            del self._normalized_mask_poly[idx]

        # Update bounding box percentage coordinates
        # if segments in normalized_mask_poly are removed.
        if invalid_segment_indices:
            logger.warning("Removed {} invalid segments from polygon.".format(len(invalid_segment_indices)))
            self._update_box_percentages_from_normalized_mask_poly()
            # depending on the model, this will be overridden by fill_box_properties
            self._bounding_box = [self._label,
                                  self._x0_percentage, self._y0_percentage,
                                  self._x1_percentage, self._y1_percentage]
