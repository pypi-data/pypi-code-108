# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""

import argparse
import os
import time
import torch

from azureml.automl.dnn.vision.classification.inference.score import _score_with_model
from azureml.automl.dnn.vision.classification.io.read.utils import read_aml_dataset, \
    _get_train_valid_dataset_wrappers
from azureml.automl.dnn.vision.classification.common.constants import (
    TrainingLiterals, ModelLiterals, ModelParameters, base_training_settings_defaults,
    multiclass_training_settings_defaults, multilabel_training_settings_defaults, safe_to_log_settings, vit_model_names
)
from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.constants import (
    SettingsLiterals, DistributedLiterals, DistributedParameters, TrainingLiterals as CommonTrainingLiterals
)
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException
from azureml.core.run import Run
from azureml.automl.dnn.vision.classification.common.classification_utils import get_vit_default_setting, \
    split_train_file_if_needed, score_validation_data

from .io.read.dataset_wrappers import AmlDatasetWrapper
from .models import ModelFactory
from .trainer.train import train
from ..common import distributed_utils
from ..common.data_utils import get_labels_files_paths_from_settings, validate_labels_files_paths
from ..common.logging_utils import get_logger, clean_settings_for_logging
from ..common.parameters import add_task_agnostic_train_parameters
from ..common.system_meter import SystemMeter
from ..common.sku_validation import validate_gpu_sku
from azureml.automl.dnn.vision.common.aml_dataset_base_wrapper import AmlDatasetBaseWrapper

from typing import cast

azureml_run = Run.get_context()

logger = get_logger(__name__)


@utils._exception_handler
def run(automl_settings, multilabel=False):
    """Invoke training by passing settings and write the output model.

    :param automl_settings: dictionary with automl settings
    :type automl_settings: dict
    :param multilabel: boolean flag for multilabel
    :type multilabel: bool
    """
    script_start_time = time.time()

    settings, unknown = _parse_argument_settings(automl_settings, multilabel)

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

    dataset_wrapper: AmlDatasetBaseWrapper = cast(AmlDatasetBaseWrapper, AmlDatasetWrapper)

    # Download required files before launching train_worker to avoid concurrency issues in distributed mode
    utils.download_required_files(settings, dataset_wrapper, ModelFactory())

    if not utils.is_aml_dataset_input(settings):
        split_train_file_if_needed(settings)

    # Decide to train in distributed mode or not based on gpu device count and distributed flag
    distributed = settings[DistributedLiterals.DISTRIBUTED]
    device_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
    if distributed and device_count > 1:
        logger.info("Starting distributed training with world_size: {}.".format(device_count))
        distributed_utils.update_settings_for_distributed_training(settings, device_count)
        # Launch multiple processes
        torch.multiprocessing.spawn(train_worker, args=(settings, multilabel), nprocs=device_count, join=True)
    else:
        if distributed:
            logger.warning("Distributed flag is {}, but is not supported as the device_count is {}. "
                           "Training using a single process and setting the flag to False."
                           .format(distributed, device_count))
            settings[DistributedLiterals.DISTRIBUTED] = False
        train_worker(0, settings, multilabel)

    utils.log_script_duration(script_start_time, settings, azureml_run)


# Adding handler to log exceptions directly in the child process if using multigpu
@utils._exception_logger
def train_worker(rank, settings, multilabel):
    """Invoke training on a single device and write the output model.

    :param rank: Rank of the process if invoked in distributed mode. 0 otherwise.
    :type rank: int
    :param settings: Dictionary with all training and model settings
    :type settings: dict
    :param multilabel: boolean flag for multilabel
    :type multilabel: bool
    """
    distributed_utils.enable_distributed_logging(settings, rank)

    distributed = settings[DistributedLiterals.DISTRIBUTED]
    if distributed:
        distributed_utils.setup_distributed_training(rank, settings, logger)

    sys_meter = SystemMeter(log_static_sys_info=True)
    sys_meter.log_system_stats()

    # set multilabel flag in settings
    settings[SettingsLiterals.MULTILABEL] = multilabel
    image_folder = settings.get(SettingsLiterals.IMAGE_FOLDER, None)
    dataset_id = settings.get(SettingsLiterals.DATASET_ID, None)
    validation_dataset_id = settings.get(SettingsLiterals.VALIDATION_DATASET_ID, None)
    split_ratio = settings[CommonTrainingLiterals.SPLIT_RATIO]
    output_dir = settings[SettingsLiterals.OUTPUT_DIR]
    device = torch.device("cuda:" + str(rank)) if distributed else settings[SettingsLiterals.DEVICE]
    master_process = distributed_utils.master_process()
    validate_gpu_sku(device=device)
    ignore_data_errors = settings[SettingsLiterals.IGNORE_DATA_ERRORS]
    run_scoring = settings.get(SettingsLiterals.OUTPUT_SCORING, False)

    utils.warn_for_cpu_devices(device, azureml_run)

    # set randomization seed for deterministic training
    random_seed = settings.get(SettingsLiterals.RANDOM_SEED, None)
    if distributed and random_seed is None:
        # Set by default for distributed training to ensure all workers have same random parameters.
        random_seed = DistributedParameters.DEFAULT_RANDOM_SEED
    utils._set_random_seed(random_seed)
    utils._set_deterministic(settings.get(SettingsLiterals.DETERMINISTIC, False))

    if utils.is_aml_dataset_input(settings):
        train_dataset_wrapper, valid_dataset_wrapper = read_aml_dataset(
            dataset_id=dataset_id, validation_dataset_id=validation_dataset_id, split_ratio=split_ratio,
            multilabel=multilabel, output_dir=output_dir, master_process=master_process,
            ignore_data_errors=ignore_data_errors)

        logger.info("[train dataset_id: {}, validation dataset_id: {}]".format(dataset_id, validation_dataset_id))
    else:
        labels_path, validation_labels_path = get_labels_files_paths_from_settings(settings)
        if labels_path is None and image_folder is None:
            raise AutoMLVisionValidationException("Neither images_folder nor labels_file were found "
                                                  "in automl settings", has_pii=False)

        image_folder_path = os.path.join(settings[SettingsLiterals.DATA_FOLDER], image_folder)

        train_dataset_wrapper, valid_dataset_wrapper = _get_train_valid_dataset_wrappers(
            root_dir=image_folder_path, train_file=labels_path, valid_file=validation_labels_path,
            multilabel=multilabel, ignore_data_errors=ignore_data_errors, settings=settings,
            master_process=master_process)

    if valid_dataset_wrapper.labels != train_dataset_wrapper.labels:
        all_labels = list(set(valid_dataset_wrapper.labels + train_dataset_wrapper.labels))
        train_dataset_wrapper.reset_labels(all_labels)
        valid_dataset_wrapper.reset_labels(all_labels)

    logger.info("# train images: {}, # validation images: {}, # labels: {}".format(
        len(train_dataset_wrapper), len(valid_dataset_wrapper), train_dataset_wrapper.num_classes))

    # TODO: Remove this padding logic when we upgrade pytorch with the fix below
    # https://github.com/pytorch/pytorch/commit/a69910868a5962e2d699c6069154836e262a29e2
    if distributed:
        world_size = distributed_utils.get_world_size()
        if len(train_dataset_wrapper) < world_size:
            train_dataset_wrapper.pad(world_size)
        if len(valid_dataset_wrapper) < world_size:
            valid_dataset_wrapper.pad(world_size)
        logger.info("After padding with world_size = {}, # train images: {}, # validation images: {}".format(
            world_size, len(train_dataset_wrapper), len(valid_dataset_wrapper)))

    # Train
    model_settings = train(dataset_wrapper=train_dataset_wrapper, valid_dataset=valid_dataset_wrapper,
                           settings=settings, device=device, output_dir=output_dir, azureml_run=azureml_run)

    if master_process and run_scoring:
        score_validation_data(azureml_run=azureml_run,
                              model_settings=model_settings,
                              ignore_data_errors=ignore_data_errors,
                              val_dataset_id=validation_dataset_id,
                              image_folder=image_folder,
                              device=device,
                              settings=settings,
                              score_with_model=_score_with_model)


def _parse_argument_settings(automl_settings, multilabel):
    """Parse all arguments and merge settings

    :param automl_settings: dictionary with automl settings
    :type automl_settings: dict
    :param multilabel: boolean flag for multilabel
    :type multilabel: bool
    :return: tuple with automl settings dictionary with all settings filled in and unknown args
    :rtype: tuple
    """

    # get model_name
    if SettingsLiterals.MODEL_NAME in automl_settings:
        model_name = automl_settings[SettingsLiterals.MODEL_NAME]
    else:  # get model_name from inputs
        tmp_parser = argparse.ArgumentParser(description="tmp", allow_abbrev=False)
        utils.add_model_arguments(tmp_parser)
        tmp_args, _ = tmp_parser.parse_known_args()
        tmp_args_dict = utils.parse_model_conditional_space(vars(tmp_args))
        model_name = tmp_args_dict[SettingsLiterals.MODEL_NAME]

    # set default settings
    training_settings_defaults = base_training_settings_defaults
    multi_class_defaults = multiclass_training_settings_defaults
    multi_label_defaults = multilabel_training_settings_defaults

    # update default settings for vits
    if model_name and model_name in vit_model_names:
        vit_training_defaults, vit_multiclass_defaults, vit_multilabel_defaults = get_vit_default_setting(model_name)
        training_settings_defaults.update(vit_training_defaults)
        multi_class_defaults.update(vit_multiclass_defaults)
        multi_label_defaults.update(vit_multilabel_defaults)

    if multilabel:
        training_settings_defaults.update(multi_label_defaults)
        training_settings_defaults.update({SettingsLiterals.MULTILABEL: True})
    else:
        training_settings_defaults.update(multi_class_defaults)

    parser = argparse.ArgumentParser(description="Image classification", allow_abbrev=False)
    add_task_agnostic_train_parameters(parser, training_settings_defaults)

    # Weighted loss
    parser.add_argument(utils._make_arg(TrainingLiterals.WEIGHTED_LOSS), type=int,
                        help="0 for no weighted loss, "
                             "1 for weighted loss with sqrt(class_weights), "
                             "and 2 for weighted loss with class_weights",
                        default=training_settings_defaults[TrainingLiterals.WEIGHTED_LOSS])

    # Model Settings
    parser.add_argument(utils._make_arg(ModelLiterals.VALID_RESIZE_SIZE), type=int,
                        help="Image size to which to resize before cropping for validation dataset",
                        default=ModelParameters.DEFAULT_VALID_RESIZE_SIZE)

    parser.add_argument(utils._make_arg(ModelLiterals.VALID_CROP_SIZE), type=int,
                        help="Image crop size which is input to your neural network for validation dataset",
                        default=ModelParameters.DEFAULT_VALID_CROP_SIZE)

    parser.add_argument(utils._make_arg(ModelLiterals.TRAIN_CROP_SIZE), type=int,
                        help="Image crop size which is input to your neural network for train dataset",
                        default=ModelParameters.DEFAULT_TRAIN_CROP_SIZE)

    args, unknown = parser.parse_known_args()
    args_dict = vars(args)
    args_dict = utils.parse_model_conditional_space(args_dict)

    return utils._merge_settings_args_defaults(automl_settings, args_dict, training_settings_defaults), unknown
