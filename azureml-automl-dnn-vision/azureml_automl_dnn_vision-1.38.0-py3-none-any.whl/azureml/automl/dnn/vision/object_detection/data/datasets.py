# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Classes and functions to ingest data for object detection."""
import copy
import json
import os
import numpy as np
import time
import torch
from typing import Any, Dict, DefaultDict, Optional, List, Tuple

from collections import defaultdict
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from azureml.automl.core.shared import logging_utilities
from azureml.automl.dnn.vision.common.aml_dataset_base_wrapper import AmlDatasetBaseWrapper
from azureml.automl.dnn.vision.common.constants import TrainingCommonSettings
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.tiling_utils import validate_tiling_settings
from azureml.automl.dnn.vision.common.utils import _validate_image_exists
from azureml.automl.dnn.vision.object_detection.common.augmentations \
    import transform as augmentations_transform
from azureml.automl.dnn.vision.object_detection.common.constants \
    import DatasetFieldLabels, PredefinedLiterals
from azureml.automl.dnn.vision.object_detection.common.masktools import decode_rle_masks_as_binary_mask
from azureml.automl.dnn.vision.object_detection.common.tiling_helper import generate_tiles_annotations
from azureml.automl.dnn.vision.object_detection.data.object_annotation import ObjectAnnotation
from azureml.automl.dnn.vision.common.tiling_dataset_element import TilingDatasetElement
from azureml.core import Dataset as AmlDataset
from typing import TypeVar
from torchvision.transforms import transforms

logger = get_logger(__name__)

T_co = TypeVar('T_co', covariant=True)


class CommonObjectDetectionDataset:
    """Common object detection dataset"""

    def __init__(self, is_train: bool = False, prob: float = 0.5, ignore_data_errors: bool = True,
                 transform: transforms = None, use_bg_label: bool = True, label_compute_func: Any = None,
                 settings: Optional[Dict[str, Any]] = None, masks_required: bool = False,
                 tile_grid_size: Optional[Tuple[int, int]] = None, tile_overlap_ratio: Optional[float] = None) -> None:
        """
        :param is_train: which mode (training, inference) is the network in?
        :type is_train: bool
        :param prob: target probability of randomness for each augmentation method
        :type prob: float
        :param ignore_data_errors: boolean flag on whether to ignore input data errors
        :type ignore_data_errors: bool
        :param transform: function to apply for data transformation
        :type transform: function that gets 2 parameters: image tensor and targets tensor
        :param use_bg_label: flag to indicate if we use incluse the --bg-- label
        :type use_bg_label: bool
        :param label_compute_func: function to use when computing labels
        :type label_compute_func: func
        :param settings: additional settings to be used in the dataset
        :type settings: dict
        :param masks_required: If masks information is required
        :type masks_required: bool
        :param tile_grid_size: The grid size to split the image into, if tiling is enabled. None, otherwise
        :type tile_grid_size: Tuple[int, int]
        :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
                                   None, if tile_grid_size is None
        :type tile_overlap_ratio: float
        """
        self._is_train = is_train
        self._prob = prob
        self._ignore_data_errors = ignore_data_errors
        self._transform = transform
        self._use_bg_label = use_bg_label
        self._label_compute_func = label_compute_func
        self._settings = settings
        validate_tiling_settings(tile_grid_size, tile_overlap_ratio)
        self._tile_grid_size = tile_grid_size
        self._tile_overlap_ratio = tile_overlap_ratio

        self._image_urls: List[str] = []
        self._annotations: DefaultDict[str, Any] = defaultdict(list)
        self._image_tiles: DefaultDict[str, Any] = defaultdict(list)
        self._tile_annotations: DefaultDict[TilingDatasetElement, Any] = defaultdict(list)
        self._object_classes: List[str] = []
        self._class_to_index_map: Dict[str, Any] = {}
        self._labels = None
        # when self is a subset of a dataset, self._indices is not None
        self._indices = None
        self._masks_required = masks_required

    def __len__(self):
        """Get number of records in dataset

        :return: Number of records
        :rtype: int
        """
        if self._indices is not None:
            return len(self._indices)
        else:
            return len(self._image_urls)

    def get_image(self, image_url, tile, index):
        """Get image.

        :param image_url: Image Url
        :type image_url: str
        :param tile: Image Tile
        :type tile: Tile
        :param index: Index of the image in image_urls (Note: This parameter is not used here
                      but is required for yolo datasets)
        :type index: int
        :return: Image, bounding box information, and image information, with form:
                 -Image: Torch tensor
                 -Labels: Dictionary with keys "boxes" and "labels", where boxes is a list of lists of
                          pixel coordinates, and "labels" is a list of integers with the class of each bounding box,
                          and optionally masks if there are masks in the image annotations
                 -Image Information: is a dictionary with the image url, image width and height,
                                     and a list of areas of the different bounding boxes
        :rtype: Tuple of form (Torch Tensor, Dictionary, Dictionary)
        """
        from azureml.automl.dnn.vision.common.utils import _read_image
        image = _read_image(self._ignore_data_errors, image_url, tile=tile)
        if image is None:
            return None, {}, {}

        if tile is not None:
            annotations = self._tile_annotations[TilingDatasetElement(image_url, tile)]
        else:
            annotations = self._annotations[image_url]

        height = image.height
        width = image.width

        bounding_boxes = []
        classes = []
        iscrowd = []
        raw_masks = []

        for annotation in annotations:
            self._fill_missing_fields_annotation(annotation, height=height, width=width)
            bounding_boxes.append(annotation.bounding_box)
            annotation_index = self._class_to_index_map[annotation.label]
            classes.append(annotation_index)
            iscrowd.append(annotation.iscrowd)

            # Convert masks to tensors if they are present
            if annotation.rle_masks is not None:
                mask = decode_rle_masks_as_binary_mask(annotation.rle_masks)
                raw_masks.append(torch.as_tensor(mask, dtype=torch.uint8))

        # if no valid masks, return None to skip this image.
        masks = None
        if raw_masks:
            masks = torch.stack(raw_masks)
        elif self._masks_required:
            logger.warning("(train: {}) No valid masks for image.".format(self._is_train))
            return None, {}, {}

        boxes = torch.as_tensor(bounding_boxes, dtype=torch.float32)
        labels = torch.as_tensor(classes, dtype=torch.int64)

        original_width = width
        original_height = height

        # data augmentations
        image, boxes, areas, height, width, masks = augmentations_transform(
            image, boxes, self._is_train, self._prob, self._transform, masks)

        # validate bounding boxes after transform
        # if no valid bbox left, return None to skip this image, other pass only valid ones
        boxes, labels, iscrowd, areas, masks = \
            self._filter_invalid_bounding_boxes(boxes, labels, iscrowd, areas, masks)
        if not boxes.shape[0]:
            logger.warning("(train: {}) No valid bbox for image after transform.".format(self._is_train))
            return None, {}, {}

        training_labels = {"boxes": boxes,
                           "labels": labels}

        # Only include masks if they have been computed
        if masks is not None:
            training_labels["masks"] = masks

        image_info = {"areas": areas, "iscrowd": iscrowd, "filename": image_url,
                      "height": height, "width": width, "original_height": original_height,
                      "original_width": original_width}

        if tile is not None:
            # the default_collate function used in PredictionDataset has issues with None values in item
            # returned by dataset. See __getitem__() function in PredictionDataset for more info.
            # Even though the collate function for this dataset has no issues,
            # adding tile only when it is not None to keep it consistent with PredictionDataset.
            image_info.update({"tile": tile})

        return (image, training_labels, image_info)

    @staticmethod
    def _fill_missing_fields_annotation(annotation, height=None, width=None):
        """Fills object annotation in place

        :param annotation: annotation object
        :type annotation: azureml.automl.dnn.vision.object_detection.data.datasets.ObjectAnnotation
        :param height: image height in pixels
        :type height: int
        :param width: image width in pixels
        :type width: int
        """
        if height is None or width is None:
            raise AutoMLVisionDataException("width or height cannot be None", has_pii=False)

        if annotation.missing_properties:
            annotation.fill_box_properties(width=width, height=height)

    @staticmethod
    def _filter_invalid_bounding_boxes(boxes, labels, iscrowd, areas, masks=None):
        """validate bbox w/ condition of (x_min < x_max and y_min < y_max)
        and return the valid boxes and corresponding labels, iscrowd and areas.

        :param boxes: Tensor containing bounding box co-ordinates in (x_min, y_min, x_max, y_max) format.
        :type boxes: torch.Tensor of shape (N, 4)
        :param labels: Bounding box labels.
        :type labels: torch.Tensor of shape (N)
        :param iscrowd: iscrowd values for the bounding boxes.
        :type iscrowd: List
        :param areas: Bounding box areas.
        :type areas: List
        :param masks (optional): Tensor containing mask data
        :type masks (optional): Tensor
        :return: Valid bounding boxes and corresponding labels, iscrowd and areas.
        :rtype: tensor, tensor, List, List
        """
        is_valid = (boxes[:, 0] < boxes[:, 2]) * (boxes[:, 1] < boxes[:, 3])
        valid_boxes = boxes[is_valid, :]
        valid_labels = labels[is_valid]
        iscrowd = torch.as_tensor(iscrowd, dtype=torch.int8)
        valid_iscrowd = iscrowd[is_valid].tolist()
        valid_areas = torch.as_tensor(areas, dtype=torch.float32)
        valid_areas_list = valid_areas[is_valid].tolist()

        valid_masks = None
        if masks is not None:
            valid_masks = masks[is_valid]

        return valid_boxes, valid_labels, valid_iscrowd, valid_areas_list, valid_masks

    @property
    def num_classes(self):
        """Get number of classes in dataset

        :return: Number of classes in dataset
        :rtype: int
        """
        return len(self._object_classes)

    @property
    def classes(self):
        """Get list of classes in dataset

        :return: List of classses
        :rtype: List of strings
        """
        return self._object_classes

    @property
    def transform(self):
        """The post augmentation transform.

        :return: the transform function
        :rtype: function that gets 2 parameters: image tensor and targets tensor
        """
        return self._transform

    @transform.setter
    def transform(self, value):
        """The post augmentation transform.

        :return: the transform function
        :rtype: function that gets 2 parameters: image tensor and targets tensor
        """
        self._transform = value

    def label_to_index_map(self, label):
        """Get mapping from class name to numeric
        class index.

        :param label: Class name
        :type label: str
        :return: Numeric class index
        :rtype: int
        """
        return self._class_to_index_map[label]

    def index_to_label(self, index):
        """Get the class name associated with numeric index

        :param index: Numeric class index
        :type index: int
        :return: Class name
        :rtype: str
        """
        return self._object_classes[index]

    def train_val_split(self, valid_portion=TrainingCommonSettings.DEFAULT_SPLIT_RATIO):
        """Splits a dataset into two datasets, one for training and and for validation.

        :param valid_portion: (optional) Portion of dataset to use for validation.
        :type valid_portion: Float between 0.0 and 1.0
        :return: Training dataset and validation dataset
        :rtype: Tuple of (Trainining, Validation) datasets of the same type as current object
        """
        number_of_samples = len(self._image_urls)
        indices = np.arange(number_of_samples)
        if number_of_samples == 1:
            logger.warning("Only one data point provided, will use this for both training and validation.")
            training_indices = indices
            validation_indices = indices
        else:
            training_indices, validation_indices = train_test_split(indices, test_size=valid_portion)

        train_dataset = copy.deepcopy(self)
        train_dataset._indices = training_indices

        validation_dataset = copy.deepcopy(self)
        validation_dataset._indices = validation_indices
        validation_dataset._is_train = False

        return train_dataset, validation_dataset

    def reset_classes(self, classes):
        """Update dataset wrapper with a list of new classes

        :param classes: classes
        :type classes: string list
        """
        self._object_classes = sorted(classes, reverse=False)
        self._class_to_index_map = {object_class: i for
                                    i, object_class in
                                    enumerate(self._object_classes)}

    def collate_function(self, batch):
        """Collate function for the dataset"""
        return tuple(zip(*batch))

    @staticmethod
    def _prepare_images_and_labels(image_urls, annotations, object_classes, use_bg_label, label_compute_func):
        object_classes = list(object_classes)
        if use_bg_label:
            object_classes = [PredefinedLiterals.BG_LABEL] + object_classes
        # "-" is smaller than capital letter
        object_classes = sorted(object_classes, reverse=False)  # make sure --bg-- is mapped to zero index
        # Use sorted to make sure all workers get the same order of data in distributed training/validation
        image_urls = sorted(image_urls)
        class_to_index_map = {object_class: i for
                              i, object_class in
                              enumerate(object_classes)}
        labels = None
        if label_compute_func is not None:
            labels = label_compute_func(image_urls, annotations, class_to_index_map)

        return object_classes, image_urls, class_to_index_map, labels

    def _get_real_index(self, index):
        if self._indices is not None:
            if index >= len(self._indices):
                raise IndexError
            return self._indices[index]
        else:
            if index >= len(self._image_urls):
                raise IndexError
        return index

    def pad(self, padding_factor):
        """Pad the dataset so that its length can be evenly divided by padding_factor

        :param padding_factor: padding factor
        :type padding_factor: int
        """
        from azureml.automl.dnn.vision.common.utils import _pad
        if self._indices is not None:
            self._indices = _pad(self._indices, padding_factor)
        else:
            self._image_urls = _pad(self._image_urls, padding_factor)

    def prepare_image_targets_for_eval(self, image_targets, height, width):
        """ Convert image_targets (part of output of __getitem__) to a format suitable for calculating
        eval metrics.

        :param image_targets: Targets for an image (part of output of __getitem__)
        :type image_targets: dict
        :param height: image height in pixels
        :type height: int
        :param width: image width in pixesl
        :type width: int
        :return: Dictionary containing boxes, labels and optionally masks.
        :rtype: dict
        """
        return image_targets

    def get_image_url_at_index(self, index):
        """Get the image_url at an index.

        :param index: Index
        :type index: Int
        :return: Image url
        :rtype: str
        """
        index = self._get_real_index(index)
        return self._image_urls[index]

    def get_image_tiles(self, image_url):
        """Get tiles for an image.

        :param image_url: Image Url
        :type image_url: str
        :return: List of image tiles
        :rtype: List[TilingDatasetElement]
        """
        return self._image_tiles[image_url]

    def _generate_tile_elements(self):
        """ Generate tiles and corresponding annotations.
        """
        if self._tile_grid_size is None or self._tile_overlap_ratio is None:
            return

        from azureml.automl.dnn.vision.common.utils import _read_image_dimensions

        tiling_start = time.time()
        logger.info("Generating tiles for all images using grid size: {} and overlap ratio: {}".format(
                    self._tile_grid_size, self._tile_overlap_ratio))

        for index in range(len(self)):
            image_url = self.get_image_url_at_index(index)
            image_annotations = self._annotations[image_url]
            image_tiles = []

            image_size = _read_image_dimensions(self._ignore_data_errors, image_url)
            if image_size is not None:
                tile_annotations = generate_tiles_annotations(image_annotations,
                                                              self._tile_grid_size, self._tile_overlap_ratio,
                                                              image_size)
                for tile, per_tile_annotations in tile_annotations.items():
                    if per_tile_annotations:  # not empty
                        image_tile = TilingDatasetElement(image_url, tile)
                        image_tiles.append(image_tile)
                        self._tile_annotations[image_tile] = \
                            [ObjectAnnotation(item) for item in per_tile_annotations]

            self._image_tiles[image_url] = image_tiles

        logger.info("Generated tiles in {} sec".format(time.time() - tiling_start))

    def supports_tiling(self):
        """Check if the dataset supports tiling.

        :return: Supports tiling or not
        :rtype: bool
        """
        return self._tile_grid_size is not None


class FileObjectDetectionDataset(CommonObjectDetectionDataset):
    """Wrapper for object detection dataset"""

    def __init__(self, annotations_file: Optional[str] = None, image_folder: str = ".", is_train: bool = False,
                 prob: float = 0.5, ignore_data_errors: bool = True, use_bg_label: bool = True,
                 label_compute_func: Any = None,
                 settings: Optional[Dict[str, Any]] = None, masks_required: bool = False,
                 tile_grid_size: Optional[Tuple[int, int]] = None,
                 tile_overlap_ratio: Optional[float] = None) -> None:
        """
        :param annotations_file: Annotations file
        :type annotations_file: str
        :param image_folder: target image path
        :type image_folder: str
        :param is_train: which mode (training, inferencing) is the network in?
        :type is_train: bool
        :param prob: target probability of random horizontal flipping
        :type prob: float
        :param ignore_data_errors: flag to indicate if image data errors should be ignored
        :type ignore_data_errors: bool
        :param use_bg_label: flag to indicate if we use incluse the --bg-- label
        :type use_bg_label: bool
        :param label_compute_func: function to use when computing labels
        :type label_compute_func: func
        :param settings: additional settings to be used in the dataset
        :type settings: dict
        :param masks_required: If masks information is required
        :type masks_required: bool
        :param tile_grid_size: The grid size to split the image into, if tiling is enabled. None, otherwise
        :type tile_grid_size: Tuple[int, int]
        :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
                                   None, if tile_grid_size is None
        :type tile_overlap_ratio: float
        """
        super().__init__(is_train=is_train, prob=prob, ignore_data_errors=ignore_data_errors,
                         use_bg_label=use_bg_label, label_compute_func=label_compute_func,
                         settings=settings, masks_required=masks_required,
                         tile_grid_size=tile_grid_size, tile_overlap_ratio=tile_overlap_ratio)

        if annotations_file is not None:
            annotations = self._read_annotations_file(annotations_file, ignore_data_errors=ignore_data_errors)
            self._init_dataset(annotations, image_folder,
                               ignore_data_errors=ignore_data_errors)

    def _init_dataset(self, annotations, image_folder, ignore_data_errors):

        image_urls = set()
        object_classes = set()

        if not annotations:
            raise AutoMLVisionDataException("No annotations to initialize datasets.", has_pii=False)
        for annotation in annotations:
            if (DatasetFieldLabels.IMAGE_URL not in annotation or DatasetFieldLabels.IMAGE_LABEL not in annotation):
                missing_required_fields_message = "Missing required fields in annotation"
                if ignore_data_errors:
                    logger.warning(missing_required_fields_message)
                    continue
                else:
                    raise AutoMLVisionDataException(missing_required_fields_message, has_pii=False)

            try:
                object_info = ObjectAnnotation(annotation[DatasetFieldLabels.IMAGE_LABEL], self._masks_required)
            except AutoMLVisionDataException as ex:
                if ignore_data_errors:
                    logging_utilities.log_traceback(ex, logger)
                    continue
                else:
                    raise

            if not object_info.valid:
                logger.warning("Invalid annotation. Skipping it.")
                continue

            image_url = os.path.join(image_folder, annotation[DatasetFieldLabels.IMAGE_URL])

            if not _validate_image_exists(image_url, ignore_data_errors):
                continue

            image_urls.add(image_url)
            self._annotations[image_url].append(object_info)
            object_classes.add(annotation[DatasetFieldLabels.IMAGE_LABEL][DatasetFieldLabels.CLASS_LABEL])

        if not image_urls:
            raise AutoMLVisionDataException("All annotations provided are ill-formed.", has_pii=False)

        self._object_classes, self._image_urls, self._class_to_index_map, self._labels = \
            self._prepare_images_and_labels(image_urls, self._annotations, object_classes,
                                            self._use_bg_label, self._label_compute_func)
        self._generate_tile_elements()

    @staticmethod
    def _read_annotations_file(annotations_file, ignore_data_errors=True):
        annotations = []
        line_no = 0
        with open(annotations_file, "r") as json_file:
            for line in json_file:
                try:
                    try:
                        line_no += 1
                        annotations.append(json.loads(line))
                    except json.JSONDecodeError:
                        raise AutoMLVisionDataException("Json decoding error in line no: {}".format(line_no),
                                                        has_pii=False)
                except AutoMLVisionDataException as ex:
                    if ignore_data_errors:
                        logging_utilities.log_traceback(ex, logger)
                    else:
                        raise

        return annotations


class AmlDatasetObjectDetection(CommonObjectDetectionDataset, AmlDatasetBaseWrapper):
    """Wrapper for Aml labeled dataset for object detection dataset"""

    def __init__(self, dataset_id, is_train=False, prob=0.5,
                 workspace=None, ignore_data_errors=False, datasetclass=AmlDataset,
                 download_files=True, use_bg_label=True, label_compute_func=None,
                 settings=None, masks_required=False, tile_grid_size=None, tile_overlap_ratio=None):
        """
        :param dataset_id: dataset id
        :type dataset_id: str
        :param is_train: which mode (training, inferencing) is the network in?
        :type is_train: bool
        :param prob: target probability of random horizontal flipping
        :type prob: float
        :param ignore_data_errors: Setting this ignores and files in the labeled dataset that fail to download.
        :type ignore_data_errors: bool
        :param datasetclass: The source dataset class.
        :type datasetclass: class
        :param download_files: Flag to download files or not.
        :type download_files: bool
        :param use_bg_label: flag to indicate if we use incluse the --bg-- label
        :type use_bg_label: bool
        :param label_compute_func: function to use when computing labels
        :type label_compute_func: func
        :param settings: additional settings to be used in the dataset
        :type settings: dict
        :param masks_required: If masks information is required
        :type masks_required: bool
        :param tile_grid_size: The grid size to split the image into, if tiling is enabled. None, otherwise
        :type tile_grid_size: Tuple[int, int]
        :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
                                   None, if tile_grid_size is None
        :type tile_overlap_ratio: float
        """
        super().__init__(is_train=is_train, prob=prob, ignore_data_errors=ignore_data_errors,
                         use_bg_label=use_bg_label, label_compute_func=label_compute_func,
                         settings=settings, masks_required=masks_required, tile_grid_size=tile_grid_size,
                         tile_overlap_ratio=tile_overlap_ratio)

        self._dataset_helper = AmlDatasetHelper(dataset_id, workspace, ignore_data_errors,
                                                datasetclass,
                                                image_column_name=self.DATASET_IMAGE_COLUMN_NAME,
                                                download_files=download_files)
        self._label_column_name = self._dataset_helper.label_column_name
        images_df = self._dataset_helper.images_df

        self._init_dataset(images_df, ignore_data_errors=ignore_data_errors)

    def _init_dataset(self, images_df, ignore_data_errors=True):

        image_urls = set()
        object_classes = set()

        if self._label_column_name not in images_df:
            raise AutoMLVisionDataException("No labels found to initialize dataset.",
                                            has_pii=False)

        for index, label in enumerate(images_df[self._label_column_name]):

            image_url = self._dataset_helper.get_image_full_path(index)

            if not _validate_image_exists(image_url, ignore_data_errors):
                continue

            cur_img_object_infos = []
            cur_object_classes = set()

            try:
                for annotation in label:
                    object_info = ObjectAnnotation(annotation, self._masks_required)
                    if object_info.valid:
                        cur_img_object_infos.append(object_info)
                        cur_object_classes.add(annotation[DatasetFieldLabels.CLASS_LABEL])
            except AutoMLVisionDataException as ex:
                if ignore_data_errors:
                    logging_utilities.log_traceback(ex, logger)
                    continue
                else:
                    raise

            if not cur_img_object_infos:
                logger.warning("No valid annotations. Skipping image.")
                continue

            image_urls.add(image_url)
            self._annotations[image_url].extend(cur_img_object_infos)
            object_classes.update(cur_object_classes)

        if not image_urls:
            raise AutoMLVisionDataException("All annotations provided are ill-formed.", has_pii=False)

        self._object_classes, self._image_urls, self._class_to_index_map, self._labels = \
            self._prepare_images_and_labels(image_urls, self._annotations, object_classes,
                                            self._use_bg_label, self._label_compute_func)
        self._generate_tile_elements()

    def get_images_df(self):
        """Return images dataframe"""
        return self._dataset_helper.images_df
