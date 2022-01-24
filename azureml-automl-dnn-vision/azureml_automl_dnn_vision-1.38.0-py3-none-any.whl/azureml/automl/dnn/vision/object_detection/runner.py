# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Entry script that is invoked by the driver script from automl."""

import argparse
import ast
import os
import time
import torch

from typing import Any, Dict, List, Tuple

from azureml.core.run import Run
from azureml.automl.core.shared.constants import Tasks

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.artifacts_utils import load_from_pretrained_checkpoint
from azureml.automl.dnn.vision.common.constants import (
    SettingsLiterals, DistributedLiterals,
    DistributedParameters, TrainingLiterals as CommonTrainingLiterals
)
from azureml.automl.dnn.vision.common.trainer.lrschedule import setup_lr_scheduler
from azureml.automl.dnn.vision.common.trainer.optimize import setup_optimizer
from azureml.automl.dnn.vision.object_detection.common.constants import (
    training_settings_defaults, TrainingLiterals, ModelLiterals, ModelParameters,
    DataLoaderParameterLiterals, ValidationMetricType, safe_to_log_settings,
    ModelNames, CriterionNames, TilingLiterals
)
from azureml.automl.dnn.vision.object_detection.writers.score import _score_with_model
from azureml.automl.dnn.vision.object_detection_yolo import runner as yolo_runner

from .data import datasets, loaders
from .data.utils import read_aml_dataset, read_file_dataset, setup_dataset_wrappers
from .models import detection
from .models.object_detection_model_wrappers import ObjectDetectionModelFactory
from .models.instance_segmentation_model_wrappers import InstanceSegmentationModelFactory
from .trainer import criterion, train
from .common.object_detection_utils import score_validation_data
from ..common import distributed_utils
from ..common.data_utils import get_labels_files_paths_from_settings, validate_labels_files_paths
from ..common.exceptions import AutoMLVisionValidationException
from ..common.logging_utils import get_logger, clean_settings_for_logging
from ..common.parameters import add_task_agnostic_train_parameters
from ..common.system_meter import SystemMeter
from azureml.automl.dnn.vision.common.aml_dataset_base_wrapper import AmlDatasetBaseWrapper
from ..common.sku_validation import validate_gpu_sku

from typing import cast

azureml_run = Run.get_context()

logger = get_logger(__name__)


@utils._exception_handler
def run(automl_settings: Dict[str, Any]) -> None:
    """Invoke training by passing settings and write the resulting model.

    :param automl_settings: Dictionary with all training and model settings
    :type automl_settings: Dictionary
    """
    script_start_time = time.time()

    settings, unknown = _parse_argument_settings(automl_settings)

    # Temporary hack to expose yolo as a model_name setting
    model_name = settings.get(SettingsLiterals.MODEL_NAME, None)
    if model_name == ModelNames.YOLO_V5:
        yolo_runner.run(automl_settings)
        return

    utils._top_initialization(settings)

    task_type = settings.get(SettingsLiterals.TASK_TYPE, None)

    if not task_type:
        raise AutoMLVisionValidationException("Task type was not found in automl settings.",
                                              has_pii=False)
    utils._set_logging_parameters(task_type, settings)

    if unknown:
        logger.info("Got unknown args, will ignore them.")

    logger.info("Final settings (pii free): \n {}".format(clean_settings_for_logging(settings, safe_to_log_settings)))
    logger.info("Settings not logged (might contain pii): \n {}".format(settings.keys() - safe_to_log_settings))

    validate_labels_files_paths(settings)

    # Download required files before launching train_worker to avoid concurrency issues in distributed mode
    dataset_wrapper: AmlDatasetBaseWrapper = cast(AmlDatasetBaseWrapper, datasets.AmlDatasetObjectDetection)

    if task_type == Tasks.IMAGE_INSTANCE_SEGMENTATION:
        utils.download_required_files(settings, dataset_wrapper,
                                      InstanceSegmentationModelFactory())
    else:
        utils.download_required_files(settings, dataset_wrapper,
                                      ObjectDetectionModelFactory())

    # Decide to train in distributed mode or not based on gpu device count and distributed flag
    distributed = settings[DistributedLiterals.DISTRIBUTED]
    device_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
    if distributed and device_count > 1:
        logger.info("Starting distributed training with world_size: {}.".format(device_count))
        distributed_utils.update_settings_for_distributed_training(settings, device_count)
        # Launch multiple processes
        torch.multiprocessing.spawn(train_worker, args=(settings,), nprocs=device_count, join=True)
    else:
        if distributed:
            logger.warning("Distributed flag is {}, but is not supported as the device_count is {}. "
                           "Training using a single process and settings the flag to False"
                           .format(distributed, device_count))
            settings[DistributedLiterals.DISTRIBUTED] = False
        train_worker(0, settings)

    utils.log_script_duration(script_start_time, settings, azureml_run)


# Adding handler to log exceptions directly in the child process if using multigpu
@utils._exception_logger
def train_worker(rank: int, settings: Dict[str, Any]) -> None:
    """Invoke training on a single device and write the resulting model.

    :param rank: Rank of the process if invoked in distributed mode. 0 otherwise.
    :type rank: int
    :param settings: Dictionary with all training and model settings
    :type settings: Dict[str, Any]
    """
    distributed_utils.enable_distributed_logging(settings, rank)

    distributed = settings[DistributedLiterals.DISTRIBUTED]
    if distributed:
        distributed_utils.setup_distributed_training(rank, settings, logger)

    system_meter = SystemMeter(log_static_sys_info=True)
    system_meter.log_system_stats()

    model_name = settings[SettingsLiterals.MODEL_NAME]
    device = torch.device("cuda:" + str(rank)) if distributed else settings[SettingsLiterals.DEVICE]
    master_process = distributed_utils.master_process()
    validate_gpu_sku(device=device)

    utils.warn_for_cpu_devices(device, azureml_run)

    # Set dataloaders' num_workers
    num_workers = settings.get(SettingsLiterals.NUM_WORKERS, None)

    train_data_loader_settings = {
        DataLoaderParameterLiterals.BATCH_SIZE: settings[CommonTrainingLiterals.TRAINING_BATCH_SIZE],
        DataLoaderParameterLiterals.SHUFFLE: True,
        DataLoaderParameterLiterals.NUM_WORKERS: num_workers,
        DataLoaderParameterLiterals.DISTRIBUTED: distributed,
        DataLoaderParameterLiterals.DROP_LAST: False}

    validation_data_loader_settings = {
        DataLoaderParameterLiterals.BATCH_SIZE: settings[CommonTrainingLiterals.VALIDATION_BATCH_SIZE],
        DataLoaderParameterLiterals.SHUFFLE: False,
        DataLoaderParameterLiterals.NUM_WORKERS: num_workers,
        DataLoaderParameterLiterals.DISTRIBUTED: distributed,
        DataLoaderParameterLiterals.DROP_LAST: False}

    # Set randomization seed for deterministic training.
    random_seed = settings.get(SettingsLiterals.RANDOM_SEED, None)
    if distributed and random_seed is None:
        # Set by default for distributed training to ensure
        # all workers have same random parameters.
        random_seed = DistributedParameters.DEFAULT_RANDOM_SEED
    utils._set_random_seed(random_seed)
    utils._set_deterministic(settings.get(SettingsLiterals.DETERMINISTIC, False))

    # Extract Automl Settings
    dataset_id = settings.get(SettingsLiterals.DATASET_ID, None)
    validation_dataset_id = settings.get(SettingsLiterals.VALIDATION_DATASET_ID, None)

    split_ratio = settings[CommonTrainingLiterals.SPLIT_RATIO]
    ignore_data_errors = settings.get(SettingsLiterals.IGNORE_DATA_ERRORS, True)
    output_directory = settings[SettingsLiterals.OUTPUT_DIR]
    run_scoring = settings.get(SettingsLiterals.OUTPUT_SCORING, False)

    task_type = settings.get(SettingsLiterals.TASK_TYPE, None)
    masks_required = task_type == Tasks.IMAGE_INSTANCE_SEGMENTATION

    tile_grid_size = settings.get(TilingLiterals.TILE_GRID_SIZE, None)
    tile_overlap_ratio = settings.get(TilingLiterals.TILE_OVERLAP_RATIO, None)

    # Setup Dataset
    use_bg_label = detection.use_bg_label(model_name)
    if utils.is_aml_dataset_input(settings):
        training_dataset, validation_dataset = read_aml_dataset(dataset_id=dataset_id,
                                                                validation_dataset_id=validation_dataset_id,
                                                                split_ratio=split_ratio,
                                                                ignore_data_errors=ignore_data_errors,
                                                                output_dir=output_directory,
                                                                master_process=master_process,
                                                                use_bg_label=use_bg_label,
                                                                masks_required=masks_required,
                                                                tile_grid_size=tile_grid_size,
                                                                tile_overlap_ratio=tile_overlap_ratio)
        logger.info("[train dataset_id: {}, validation dataset_id: {}]".format(dataset_id, validation_dataset_id))
    else:
        image_folder = settings.get(SettingsLiterals.IMAGE_FOLDER, None)

        if image_folder is None:
            raise AutoMLVisionValidationException("Either images_folder or dataset_id needs to be specified",
                                                  has_pii=False)
        else:
            image_folder = os.path.join(settings[SettingsLiterals.DATA_FOLDER], image_folder)

        annotations_file, annotations_test_file = get_labels_files_paths_from_settings(settings)

        training_dataset, validation_dataset = read_file_dataset(image_folder=image_folder,
                                                                 annotations_file=annotations_file,
                                                                 annotations_test_file=annotations_test_file,
                                                                 split_ratio=split_ratio,
                                                                 ignore_data_errors=ignore_data_errors,
                                                                 output_dir=output_directory,
                                                                 master_process=master_process,
                                                                 use_bg_label=use_bg_label,
                                                                 masks_required=masks_required,
                                                                 tile_grid_size=tile_grid_size,
                                                                 tile_overlap_ratio=tile_overlap_ratio)
        logger.info("[train file: {}, validation file: {}]".format(annotations_file, annotations_test_file))

    if training_dataset.classes != validation_dataset.classes:
        all_classes = list(set(training_dataset.classes + validation_dataset.classes))
        training_dataset.reset_classes(all_classes)
        validation_dataset.reset_classes(all_classes)

    logger.info("# train images: {}, # validation images: {}, # labels: {}".format(
        len(training_dataset), len(validation_dataset), training_dataset.num_classes - 1))  # excluding "--bg--" class

    # TODO: Remove this padding logic when we upgrade pytorch with the fix below
    # https://github.com/pytorch/pytorch/commit/a69910868a5962e2d699c6069154836e262a29e2
    if distributed:
        world_size = distributed_utils.get_world_size()
        if len(training_dataset) < world_size:
            training_dataset.pad(world_size)
        if len(validation_dataset) < world_size:
            validation_dataset.pad(world_size)
        logger.info("After padding with world_size = {}, # train images: {}, # validation images: {}".format(
            world_size, len(training_dataset), len(validation_dataset)))

    training_dataset_wrapper, validation_dataset_wrapper = setup_dataset_wrappers(
        training_dataset, validation_dataset, tile_grid_size)

    # Setup Model
    model_wrapper = detection.setup_model(model_name=model_name,
                                          number_of_classes=training_dataset_wrapper.dataset.num_classes,
                                          classes=training_dataset_wrapper.dataset.classes,
                                          device=device,
                                          distributed=distributed,
                                          rank=rank,
                                          settings=settings)

    # if the model exposes some transformations
    # enable those in the datasets.
    training_dataset_wrapper.dataset.transform = model_wrapper.get_train_validation_transform()
    validation_dataset_wrapper.dataset.transform = model_wrapper.get_train_validation_transform()
    # Replace model.transform resize and normalize with identity methods
    # so that we avoid re-doing the transform in the model
    if training_dataset_wrapper.dataset.transform is not None and \
            validation_dataset_wrapper.dataset.transform is not None:
        logger.info("Found transform not None in both training and validation dataset - disabling in model.")
        model_wrapper.disable_model_transform()
    else:
        logger.info("Transform is None for datasets. Keep it in the model - this will increase GPU mem usage.")

    # Load model weight from previously saved checkpoint for incremental training
    load_from_pretrained_checkpoint(settings, model_wrapper, distributed)

    num_params = sum([p.data.nelement() for p in model_wrapper.parameters()])
    logger.info("[model: {}, #param: {}]".format(model_name, num_params))

    # Setup Dataloaders

    train_loader = loaders.setup_dataloader(training_dataset_wrapper, **train_data_loader_settings)
    validation_loader = loaders.setup_dataloader(validation_dataset_wrapper, **validation_data_loader_settings)

    # setup optimizer
    optimizer = setup_optimizer(model_wrapper.model, settings=settings)
    # setup lr_scheduler
    lr_scheduler = setup_lr_scheduler(optimizer, batches_per_epoch=len(train_loader), settings=settings)
    loss_function = criterion.setup_criterion(CriterionNames.LOSS_FROM_MODEL)

    # Train Model

    logger.info("[start training: train batch_size: {}, val batch_size: {}]".format(
        train_data_loader_settings[DataLoaderParameterLiterals.BATCH_SIZE],
        validation_data_loader_settings[DataLoaderParameterLiterals.BATCH_SIZE]))

    system_meter.log_system_stats()

    train.train(model=model_wrapper,
                optimizer=optimizer,
                scheduler=lr_scheduler,
                train_data_loader=train_loader,
                val_data_loader=validation_loader,
                criterion=loss_function,
                device=device,
                settings=settings,
                output_dir=output_directory,
                azureml_run=azureml_run)

    if master_process and run_scoring:
        model_settings = {} if model_wrapper.model_settings is None else \
            model_wrapper.model_settings.get_settings_dict()
        score_validation_data(run=azureml_run, model_settings=model_settings,
                              settings=settings, device=device,
                              score_with_model=_score_with_model)


def _parse_argument_settings(automl_settings: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Parse all arguments and merge settings

    :param automl_settings: Dictionary with all training and model settings
    :type automl_settings: Dict[str, Any]
    :return: tuple of the automl settings dictionary with all settings filled in and a list of any unknown args
    :rtype: Tuple[Dict[str, Any], List[str]]
    """

    parser = argparse.ArgumentParser(description="Object detection", allow_abbrev=False)
    add_task_agnostic_train_parameters(parser, training_settings_defaults)

    # Metric
    parser.add_argument(utils._make_arg(TrainingLiterals.VALIDATION_METRIC_TYPE),
                        choices=ValidationMetricType.ALL_TYPES,
                        help="Metric computation method to use for validation metrics",
                        default=training_settings_defaults[TrainingLiterals.VALIDATION_METRIC_TYPE])

    # Tiling settings
    # Note that we use ast.literal_eval here as HyperDrive doesn't support search space with choice of tuples/lists.
    # Hence, we accept a string and parse it here.
    parser.add_argument(utils._make_arg(TilingLiterals.TILE_GRID_SIZE), type=ast.literal_eval,
                        help="The tile grid size to use for tiling the image during training/validation. \
                        Should be a tuple of two integers passed as a string. Example: --tile_grid_size \"(3, 2)\"")

    parser.add_argument(utils._make_arg(TilingLiterals.TILE_OVERLAP_RATIO), type=float,
                        help="Overlap ratio between adjacent tiles in each dimension",
                        default=training_settings_defaults[TilingLiterals.TILE_OVERLAP_RATIO])

    parser.add_argument(utils._make_arg(TilingLiterals.TILE_PREDICTIONS_NMS_THRESH), type=float,
                        help="The iou threshold to use to perform nms while merging predictions from tiles and \
                        image. Used in validation",
                        default=training_settings_defaults[TilingLiterals.TILE_PREDICTIONS_NMS_THRESH])

    # Model Settings
    parser.add_argument(utils._make_arg(ModelLiterals.MIN_SIZE), type=int,
                        help="Minimum size of the image to be rescaled before feeding it to the backbone",
                        default=ModelParameters.DEFAULT_MIN_SIZE)

    parser.add_argument(utils._make_arg(ModelLiterals.MAX_SIZE), type=int,
                        help="Maximum size of the image to be rescaled before feeding it to the backbone",
                        default=ModelParameters.DEFAULT_MAX_SIZE)

    parser.add_argument(utils._make_arg(ModelLiterals.BOX_SCORE_THRESH), type=float,
                        help="During inference, only return proposals with a classification score \
                        greater than box_score_thresh",
                        default=ModelParameters.DEFAULT_BOX_SCORE_THRESH)

    parser.add_argument(utils._make_arg(ModelLiterals.BOX_NMS_THRESH), type=float,
                        help="NMS threshold for the prediction head. Used during inference",
                        default=ModelParameters.DEFAULT_BOX_NMS_THRESH)

    parser.add_argument(utils._make_arg(ModelLiterals.BOX_DETECTIONS_PER_IMG), type=int,
                        help="Maximum number of detections per image, for all classes.",
                        default=ModelParameters.DEFAULT_BOX_DETECTIONS_PER_IMG)

    args, unknown = parser.parse_known_args()
    args_dict = vars(args)
    args_dict = utils.parse_model_conditional_space(args_dict)

    # When tile_grid_size is passed as part of conditional HP space, it would be a string. This functions parses
    # the string and converts it to a tuple.
    utils.fix_tiling_settings_in_args_dict(args_dict)

    return utils._merge_settings_args_defaults(automl_settings, args_dict, training_settings_defaults), unknown
