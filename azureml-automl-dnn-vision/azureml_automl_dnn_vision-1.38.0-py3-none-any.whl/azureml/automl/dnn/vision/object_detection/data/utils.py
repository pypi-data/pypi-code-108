# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper classes and functions for creating operating with datasets and dataloaders."""

import torch

from typing import Optional, Tuple

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from azureml.automl.dnn.vision.common.utils import _save_image_df, _save_image_lf
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.object_detection.data import datasets
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import \
    CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from azureml.core import Run

logger = get_logger(__name__)


def read_aml_dataset(dataset_id, validation_dataset_id, split_ratio, ignore_data_errors, output_dir,
                     master_process, use_bg_label, dataset_class=datasets.AmlDatasetObjectDetection,
                     settings=None, download_files=False, masks_required=False,
                     tile_grid_size=None, tile_overlap_ratio=None):
    """Read the training and validation datasets from AML datasets.

    :param dataset_id: Training dataset id
    :type dataset_id: str
    :param validation_dataset_id: Validation dataset id
    :type dataset_id: str
    :param split_ratio: split ratio of dataset to use for validation if no validation dataset is defined.
    :type split_ratio: float
    :param ignore_data_errors: boolean flag on whether to ignore input data errors
    :type ignore_data_errors: bool
    :param output_dir: where to save train and val files
    :type output_dir: str
    :param master_process: boolean flag indicating whether current process is master or not.
    :type master_process: bool
    :param use_bg_label: flag to indicate if dataset should include the --bg-- label
    :type use_bg_label: bool
    :param dataset_class: the class to use to instantiate the dataset
    :type dataset_class: Class
    :param settings: dictionary of settings to be passed to the dataset
    :type settings: dict
    :param download_files: flag to indicate if files should be downloaded. Assumption is that aml dataset
                           files are already downloaded to local path by a call to download_required_files()
    :type download_files: bool
    :param masks_required: If masks information is required
    :type masks_required: bool
    :param tile_grid_size: The grid size to split the image into, if tiling is enabled. None, otherwise
    :type tile_grid_size: Tuple[int, int]
    :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
                               None, if tile_grid_size is None
    :type tile_overlap_ratio: float
    :return: Training dataset and validation dataset
    :rtype: Tuple of form (AmlDatasetObjectDetection, AmlDatasetObjectDetection)
    """
    ws = Run.get_context().experiment.workspace

    if validation_dataset_id is not None:
        training_dataset = dataset_class(dataset_id=dataset_id, is_train=True,
                                         ignore_data_errors=ignore_data_errors,
                                         workspace=ws, download_files=download_files,
                                         settings=settings, use_bg_label=use_bg_label,
                                         masks_required=masks_required, tile_overlap_ratio=tile_overlap_ratio,
                                         tile_grid_size=tile_grid_size)
        validation_dataset = dataset_class(dataset_id=validation_dataset_id, is_train=False,
                                           ignore_data_errors=ignore_data_errors,
                                           workspace=ws, download_files=download_files,
                                           settings=settings, use_bg_label=use_bg_label,
                                           masks_required=masks_required, tile_overlap_ratio=tile_overlap_ratio,
                                           tile_grid_size=tile_grid_size)
        if master_process:
            _save_image_df(train_df=training_dataset.get_images_df(),
                           val_df=validation_dataset.get_images_df(),
                           output_dir=output_dir)

    else:
        dataset = dataset_class(dataset_id=dataset_id, is_train=True,
                                ignore_data_errors=ignore_data_errors,
                                workspace=ws, download_files=download_files,
                                settings=settings, use_bg_label=use_bg_label,
                                masks_required=masks_required, tile_overlap_ratio=tile_overlap_ratio,
                                tile_grid_size=tile_grid_size)
        training_dataset, validation_dataset = dataset.train_val_split(split_ratio)
        if master_process:
            _save_image_df(train_df=dataset.get_images_df(), train_index=training_dataset._indices,
                           val_index=validation_dataset._indices, output_dir=output_dir)

    return training_dataset, validation_dataset


def read_file_dataset(image_folder, annotations_file, annotations_test_file, split_ratio,
                      ignore_data_errors, output_dir, master_process, use_bg_label,
                      dataset_class=datasets.FileObjectDetectionDataset,
                      settings=None, masks_required=False, tile_grid_size=None, tile_overlap_ratio=None):
    """Read the training and validation datasets from annotation files.

    :param image_folder: target image path
    :type image_folder: str
    :param annotations_file: Training annotations file
    :type annotations_file: str
    :param annotations_test_file: Validation annotations file
    :type annotations_test_file: str
    :param split_ratio: split ratio of dataset to use for validation if no validation dataset is defined.
    :type split_ratio: float
    :param ignore_data_errors: boolean flag on whether to ignore input data errors
    :type ignore_data_errors: bool
    :param output_dir: where to save train and val files
    :type output_dir: str
    :param master_process: boolean flag indicating whether current process is master or not.
    :type master_process: bool
    :param use_bg_label: flag to indicate if dataset should include the --bg-- label
    :type use_bg_label: bool
    :param dataset_class: the class to use to instanciate the dataset
    :type dataset_class: Class
    :param settings: dictionary of settings to be passed to the dataset
    :type settings: dict
    :param masks_required: If masks information is required
    :type masks_required: bool
    :param tile_grid_size: The grid size to split the image into, if tiling is enabled. None, otherwise
    :type tile_grid_size: Tuple[int, int]
    :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
                               None, if tile_grid_size is None
    :type tile_overlap_ratio: float
    :return: Training dataset and validation dataset
    :rtype: Tuple of form (FileObjectDetectionDataset, FileObjectDetectionDataset)
    """
    if annotations_file is None:
        raise AutoMLVisionDataException("labels_file needs to be specified", has_pii=False)

    if annotations_test_file:
        training_dataset = dataset_class(annotations_file, image_folder,
                                         is_train=True,
                                         ignore_data_errors=ignore_data_errors,
                                         settings=settings,
                                         use_bg_label=use_bg_label,
                                         masks_required=masks_required,
                                         tile_overlap_ratio=tile_overlap_ratio,
                                         tile_grid_size=tile_grid_size)
        validation_dataset = dataset_class(annotations_test_file,
                                           image_folder, is_train=False,
                                           ignore_data_errors=ignore_data_errors,
                                           settings=settings,
                                           use_bg_label=use_bg_label,
                                           masks_required=masks_required,
                                           tile_overlap_ratio=tile_overlap_ratio,
                                           tile_grid_size=tile_grid_size)
        if master_process:
            _save_image_lf(train_ds=annotations_file, val_ds=annotations_test_file, output_dir=output_dir)
    else:
        dataset = dataset_class(annotations_file, image_folder, is_train=True,
                                ignore_data_errors=ignore_data_errors,
                                settings=settings, use_bg_label=use_bg_label,
                                masks_required=masks_required,
                                tile_overlap_ratio=tile_overlap_ratio,
                                tile_grid_size=tile_grid_size)
        training_dataset, validation_dataset = dataset.train_val_split(split_ratio)
        if master_process:
            _save_image_lf(train_ds=training_dataset, val_ds=validation_dataset, output_dir=output_dir)

    return training_dataset, validation_dataset


def setup_dataset_wrappers(training_dataset: datasets.CommonObjectDetectionDataset,
                           validation_dataset: datasets.CommonObjectDetectionDataset,
                           tile_grid_size: Optional[Tuple[int, int]] = None) \
        -> Tuple[CommonObjectDetectionDatasetWrapper, CommonObjectDetectionDatasetWrapper]:
    """ Setup dataset wrappers.

    :param training_dataset: Training dataset
    :type training_dataset: CommonObjectDetectionDataset
    :param validation_dataset: Validation dataset
    :type validation_dataset: CommonObjectDetectionDataset
    :param tile_grid_size: The grid size to split the image into, if tiling is enabled. None, otherwise
    :type tile_grid_size: Optional[Tuple[int, int]]
    :return: Tuple of training dataset wrapper, validation dataset wrapper
    :rtype: Tuple of form [CommonObjectDetectionDatasetWrapper, CommonObjectDetectionDatasetWrapper]
    """
    dataset_processing_type = DatasetProcessingType.IMAGES
    if tile_grid_size is not None:
        dataset_processing_type = DatasetProcessingType.IMAGES_AND_TILES

    training_dataset_wrapper = CommonObjectDetectionDatasetWrapper(
        dataset=training_dataset, dataset_processing_type=dataset_processing_type)
    validation_dataset_wrapper = CommonObjectDetectionDatasetWrapper(
        dataset=validation_dataset, dataset_processing_type=dataset_processing_type)

    if tile_grid_size is not None:
        logger.info("After adding tiles, # train images: {}, # validation images: {}".format(
            len(training_dataset_wrapper), len(validation_dataset_wrapper)))

    return training_dataset_wrapper, validation_dataset_wrapper
