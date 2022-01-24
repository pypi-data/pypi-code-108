# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Entry script that is invoked by the driver script from automl."""

import argparse
import time

from distutils.util import strtobool
from typing import Any, Dict, List, Tuple, cast

from azureml.automl.core.shared.constants import Tasks

from azureml.automl.dnn.vision.common import artifacts_utils, utils
from azureml.automl.dnn.vision.common.constants import (
    ArtifactLiterals, SettingsLiterals, DistributedLiterals, TrainingLiterals as CommonTrainingLiterals
)
from azureml.automl.dnn.vision.common.trainer.lrschedule import setup_lr_scheduler
from azureml.automl.dnn.vision.common.trainer.optimize import setup_optimizer
from azureml.automl.dnn.vision.object_detection.common.constants import (
    ModelNames, TrainingLiterals as ODTrainingLiterals, ValidationMetricType, TilingLiterals
)
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import (
    ModelSize, YoloLiterals, YoloParameters, training_settings_defaults, yolo_hyp_defaults, safe_to_log_settings
)
from azureml.automl.dnn.vision.object_detection_yolo.data.utils import setup_dataloaders
from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper
from azureml.automl.dnn.vision.object_detection_yolo.writers.score import _score_with_model
from azureml.core.run import Run

from .trainer.train import train
from .utils.utils import init_seeds
from ..common.data_utils import validate_labels_files_paths
from ..common.exceptions import AutoMLVisionValidationException
from ..common.logging_utils import get_logger, clean_settings_for_logging
from ..common.parameters import add_task_agnostic_train_parameters
from ..common.system_meter import SystemMeter
from ..common.sku_validation import validate_gpu_sku
from ..object_detection.common.object_detection_utils import score_validation_data
from ..object_detection.models import detection

azureml_run = Run.get_context()

logger = get_logger(__name__)


@utils._exception_handler
def run(automl_settings: Dict[str, Any]) -> None:
    """Invoke training by passing settings and write the resulting model.

    :param automl_settings: Dictionary with all training and model settings
    :type automl_settings: Dict[str, Any]
    """
    script_start_time = time.time()

    settings, unknown = _parse_argument_settings(automl_settings)

    utils._top_initialization(settings)

    task_type = settings.get(SettingsLiterals.TASK_TYPE, None)

    if not task_type:
        raise AutoMLVisionValidationException("Task type was not found in automl settings.",
                                              has_pii=False)
    utils._set_logging_parameters(task_type, settings)

    # TODO: support multi-gpu
    if DistributedLiterals.DISTRIBUTED in settings:
        if settings[DistributedLiterals.DISTRIBUTED]:
            logger.warning("Distributed is not supported for yolo. Continuing with a single gpu.")
            settings[DistributedLiterals.DISTRIBUTED] = False
    else:
        settings[DistributedLiterals.DISTRIBUTED] = False

    if unknown:
        logger.info("Got unknown args, will ignore them.")

    logger.info("Final settings (pii free): \n {}".format(clean_settings_for_logging(settings, safe_to_log_settings)))
    logger.info("Settings not logged (might contain pii): \n {}".format(settings.keys() - safe_to_log_settings))

    validate_labels_files_paths(settings)

    system_meter = SystemMeter(log_static_sys_info=True)
    system_meter.log_system_stats()

    tb_writer = utils.init_tensorboard()

    # Set random seed
    init_seeds(1)

    device = settings[SettingsLiterals.DEVICE]
    validate_gpu_sku(device=device)
    output_directory = ArtifactLiterals.OUTPUT_DIR

    utils.warn_for_cpu_devices(device, azureml_run)

    masks_required = task_type == Tasks.IMAGE_INSTANCE_SEGMENTATION

    tile_grid_size = settings.get(TilingLiterals.TILE_GRID_SIZE, None)
    if tile_grid_size is not None:
        logger.info("Tiling is not supported for yolo models. Ignoring tile_grid_size parameter.")

    # Set data loaders
    train_loader, validation_loader = setup_dataloaders(settings, output_directory, masks_required)

    # Update # of class
    nc = train_loader.dataset.dataset.num_classes

    # Create model
    settings['cls'] *= nc / 80.  # scale coco-tuned settings['cls'] to current dataset
    settings['gr'] = 1.0  # giou loss ratio (obj_loss = 1.0 or giou)

    model_wrapper = cast(YoloV5Wrapper,
                         detection.setup_model(model_name=ModelNames.YOLO_V5,
                                               number_of_classes=nc,
                                               classes=train_loader.dataset.dataset.classes,
                                               device=device,
                                               distributed=False,
                                               # TODO only add the relevant fields in the settings
                                               specs=settings))

    # TODO: when large or xlarge is chosen, reduce batch_size to avoid CUDA out of memory
    # TODO: make sure model_size exists in all types accepted by model_wrapper
    if device != 'cpu' and model_wrapper.model_size in ['large', 'xlarge']:
        logger.warning("[model_size (medium) is supported on 12GiB GPU memory with a batch_size of 16. "
                       "Your choice of model_size ({}) and a batch_size of {} might lead to CUDA OOM]"
                       .format(model_wrapper.model_size, settings[CommonTrainingLiterals.TRAINING_BATCH_SIZE]))

    # TODO: remove this when supporting ddp for yolo
    # Download a pretrained checkpoint to local disk for incremental training
    utils.download_checkpoint_for_incremental_training(settings)

    # Load model weight from previously saved checkpoint for incremental training
    artifacts_utils.load_from_pretrained_checkpoint(settings, model_wrapper, distributed=False)

    num_params = sum(x.numel() for x in model_wrapper.parameters())  # number parameters
    logger.info("[model: {} ({}), # layers: {}, # param: {}]".format(
        settings[SettingsLiterals.MODEL_NAME],
        model_wrapper.model_size,
        len(list(model_wrapper.parameters())),
        num_params))

    # setup optimizer
    optimizer = setup_optimizer(model_wrapper.model, settings=settings)
    # setup lr_scheduler
    lr_scheduler = setup_lr_scheduler(optimizer, batches_per_epoch=len(train_loader), settings=settings)

    # Train
    train(model_wrapper=model_wrapper, optimizer=optimizer, scheduler=lr_scheduler,
          train_loader=train_loader, validation_loader=validation_loader,
          output_dir=output_directory, azureml_run=azureml_run, tb_writer=tb_writer)

    # Run scoring
    run_scoring = settings.get(SettingsLiterals.OUTPUT_SCORING, False)
    if run_scoring:
        score_validation_data(run=azureml_run, model_settings=model_wrapper.model_settings.get_settings_dict(),
                              settings=settings, device=device,
                              score_with_model=_score_with_model)

    utils.log_script_duration(script_start_time, settings, azureml_run)


def _parse_argument_settings(automl_settings: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Parse all arguments and merge settings

    :param automl_settings: Dictionary with all training and model settings
    :type automl_settings: Dict[str, Any]
    :return: tuple of the automl settings dictionary with all settings filled in and a list of any unknown args
    :rtype: Tuple[Dict[str, Any], List[str]]
    """

    parser = argparse.ArgumentParser(description="Object detection (using yolov5)", allow_abbrev=False)
    add_task_agnostic_train_parameters(parser, training_settings_defaults)

    # Metric
    parser.add_argument(utils._make_arg(ODTrainingLiterals.VALIDATION_METRIC_TYPE),
                        choices=ValidationMetricType.ALL_TYPES,
                        help="Metric computation method to use for validation metrics",
                        default=training_settings_defaults[ODTrainingLiterals.VALIDATION_METRIC_TYPE])

    # Model (yolov5) Settings
    parser.add_argument(utils._make_arg(YoloLiterals.IMG_SIZE), type=int,
                        help='Image size for train and validation',
                        default=YoloParameters.DEFAULT_IMG_SIZE)

    parser.add_argument(utils._make_arg(YoloLiterals.MODEL_SIZE), type=str,
                        choices=ModelSize.ALL_TYPES,
                        help='Model size in {small, medium, large, xlarge}',
                        default=YoloParameters.DEFAULT_MODEL_SIZE)

    parser.add_argument(utils._make_arg(YoloLiterals.MULTI_SCALE),
                        type=lambda x: bool(strtobool(str(x))),
                        help='Enable multi-scale image by varying image size by +/- 50%%',
                        default=YoloParameters.DEFAULT_MULTI_SCALE)

    parser.add_argument(utils._make_arg(YoloLiterals.BOX_SCORE_THRESH), type=float,
                        help="During inference, only return proposals with a score \
                              greater than box_score_thresh. The score is the multiplication of \
                              the objectness score and classification probability",
                        default=YoloParameters.DEFAULT_BOX_SCORE_THRESH)

    parser.add_argument(utils._make_arg(YoloLiterals.BOX_IOU_THRESH), type=float,
                        help="IOU threshold used during inference in nms post processing",
                        default=YoloParameters.DEFAULT_BOX_IOU_THRESH)

    args, unknown = parser.parse_known_args()
    args_dict = vars(args)
    args_dict = utils.parse_model_conditional_space(args_dict)

    # Update training default settings with yolo specific hyper-parameters
    training_settings_defaults.update(yolo_hyp_defaults)

    # Training settings
    return utils._merge_settings_args_defaults(automl_settings, args_dict, training_settings_defaults), unknown
