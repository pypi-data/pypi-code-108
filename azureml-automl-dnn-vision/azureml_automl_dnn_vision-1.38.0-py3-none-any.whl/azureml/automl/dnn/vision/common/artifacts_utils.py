# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Functions to help save the artifacts at the end of the training."""

import os
import json
import time

import torch
from torch.nn.modules import Module

import azureml.automl.core.shared.constants as shared_constants
from azureml.automl.dnn.vision.common.constants import ArtifactLiterals, SettingsLiterals, CommonSettings
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException, \
    AutoMLVisionRuntimeUserException
from azureml.automl.dnn.vision.common.model_export_utils import prepare_model_export
from azureml.automl.dnn.vision.common.torch_utils import intersect_dicts
from azureml.automl.dnn.vision.common.utils import logger, \
    _set_train_run_properties, _distill_run_from_experiment
from azureml.automl.dnn.vision.object_detection.common.constants import ModelNames
from azureml.automl.dnn.vision.object_detection.models.object_detection_model_wrappers \
    import BaseObjectDetectionModelWrapper
from azureml.core.run import Run
from typing import Union, Any, Dict, Optional, List


def write_artifacts(model_wrapper: Union[BaseObjectDetectionModelWrapper, Module],
                    best_model_weights: Dict[str, Any], labels: List[str],
                    output_dir: str, run: Run, best_metric: float,
                    task_type: str, device: Optional[str] = None,
                    enable_onnx_norm: Optional[bool] = False,
                    model_settings: Optional[Dict[str, Any]] = None,
                    save_as_mlflow: bool = False, is_yolo: bool = False) -> None:
    """Export onnx model and write artifacts at the end of training.

    :param model_wrapper: Model wrapper or model
    :type model_wrapper: Union[CommonObjectDetectionModelWrapper, Model]
    :param best_model_weights: weights of the best model
    :type best_model_weights: dict
    :param labels: list of classes
    :type labels: List[str]
    :param output_dir: Name of dir to save model files. If it does not exist, it will be created.
    :type output_dir: String
    :param run: azureml run object
    :type run: azureml.core.run.Run
    :param best_metric: best metric value to store in properties
    :type best_metric: float
    :param task_type: task type
    :type task_type: str
    :param device: device where model should be run (usually 'cpu' or 'cuda:0' if it is the first gpu)
    :type device: str
    :param enable_onnx_norm: enable normalization when exporting onnx
    :type enable_onnx_norm: bool
    :param model_settings: Settings for the model
    :type model_settings: dict
    :param save_as_mlflow: Flag that indicates whether to save in mlflow format
    :type save_as_mlflow: bool
    :param is_yolo: Flag that indicates if the model is a yolo model
    :type is_yolo: bool
    """
    os.makedirs(output_dir, exist_ok=True)

    model_wrapper.load_state_dict(best_model_weights)

    # Export and save the torch onnx model.
    onnx_file_path = os.path.join(output_dir, ArtifactLiterals.ONNX_MODEL_FILE_NAME)
    model_wrapper.export_onnx_model(file_path=onnx_file_path, device=device, enable_norm=enable_onnx_norm)

    # Explicitly Save the labels to a json file.
    if labels is None:
        raise AutoMLVisionValidationException('No labels were found in the dataset wrapper', has_pii=False)
    label_file_path = os.path.join(output_dir, ArtifactLiterals.LABEL_FILE_NAME)
    with open(label_file_path, 'w') as f:
        json.dump(labels, f)

    _set_train_run_properties(run, model_wrapper.model_name, best_metric)

    folder_name = os.path.basename(output_dir)
    run.upload_folder(name=folder_name, path=output_dir)

    prepare_model_export(run=run,
                         output_dir=output_dir,
                         task_type=task_type,
                         model_settings=model_settings,
                         save_as_mlflow=save_as_mlflow,
                         is_yolo=is_yolo)


def save_model_checkpoint(epoch: int, model_name: str, number_of_classes: int, specs: Dict[str, Any],
                          model_state: Dict[str, Any], optimizer_state: Dict[str, Any],
                          lr_scheduler_state: Dict[str, Any],
                          output_dir: str, model_file_name_prefix: str = '',
                          model_file_name: str = shared_constants.PT_MODEL_FILENAME) -> None:
    """Saves a model checkpoint to a file.

    :param epoch: the training epoch
    :type epoch: int
    :param model_name: Model name
    :type model_name: str
    :param number_of_classes: number of classes for the model
    :type number_of_classes: int
    :param specs: model specifications
    :type specs: dict
    :param model_state: model state dict
    :type model_state: dict
    :param optimizer_state: optimizer state dict
    :type optimizer_state: dict
    :param lr_scheduler_state: lr scheduler state
    :type lr_scheduler_state: dict
    :param output_dir: output folder for the checkpoint file
    :type output_dir: str
    :param model_file_name_prefix: prefix to use for the output file
    :type model_file_name_prefix: str
    :param model_file_name: name of the output file that contains the checkpoint
    :type model_file_name: str
    """
    checkpoint_start = time.time()

    os.makedirs(output_dir, exist_ok=True)
    model_location = os.path.join(output_dir, model_file_name_prefix + model_file_name)

    torch.save({
        'epoch': epoch,
        'model_name': model_name,
        'number_of_classes': number_of_classes,
        'specs': specs,
        'model_state': model_state,
        'optimizer_state': optimizer_state,
        'lr_scheduler_state': lr_scheduler_state,
    }, model_location)

    checkpoint_creation_time = time.time() - checkpoint_start
    logger.info('Model checkpoint creation ({}) took {:.2f}s.'
                .format(model_location, checkpoint_creation_time))


def _download_model_from_artifacts(run_id: str, experiment_name: Optional[str] = None) -> None:
    logger.info("Start fetching model from artifacts")
    run = _distill_run_from_experiment(run_id, experiment_name)
    run.download_file(os.path.join(ArtifactLiterals.OUTPUT_DIR, shared_constants.PT_MODEL_FILENAME),
                      shared_constants.PT_MODEL_FILENAME)
    logger.info("Finished downloading files from artifacts")


def load_from_pretrained_checkpoint(settings: Dict[str, Any], model_wrapper: Any, distributed: bool) -> None:
    """Load model weights from pretrained checkpoint via run_id or FileDataset id

    :param settings: dictionary containing settings for training
    :type settings: dict
    :param model_wrapper: Model wrapper
    :type model_wrapper:
    :param distributed: Training in distributed mode or not
    :type distributed: bool
    """
    checkpoint_run_id = settings.get(SettingsLiterals.CHECKPOINT_RUN_ID, None)
    checkpoint_dataset_id = settings.get(SettingsLiterals.CHECKPOINT_DATASET_ID, None)
    checkpoint_filename = settings.get(SettingsLiterals.CHECKPOINT_FILENAME, None)
    ckpt_local_path = None
    if checkpoint_run_id:
        ckpt_local_path = shared_constants.PT_MODEL_FILENAME
    elif checkpoint_dataset_id and checkpoint_filename:
        ckpt_local_path = os.path.join(CommonSettings.TORCH_HUB_CHECKPOINT_DIR, checkpoint_filename)

    if ckpt_local_path:
        logger.info('Trying to load weights from a pretrained checkpoint')
        checkpoint = torch.load(ckpt_local_path, map_location='cpu')
        logger.info("[checkpoint model_name: {}, number_of_classes: {}, specs: {}]"
                    .format(checkpoint['model_name'], checkpoint['number_of_classes'], checkpoint['specs']))
        if checkpoint['model_name'] == model_wrapper.model_name:
            torch_model = model_wrapper.model.module if distributed else model_wrapper.model
            # Gracefully handle size mismatch, missing and unexpected keys errors
            state_dict = intersect_dicts(checkpoint['model_state'], torch_model.state_dict())
            if len(state_dict.keys()) == 0:
                raise AutoMLVisionValidationException("Could not load pretrained model weights. "
                                                      "State dict intersection is empty.", has_pii=False)
            if model_wrapper.model_name == ModelNames.YOLO_V5:
                state_dict = {'model.' + k: v for k, v in state_dict.items()}
            torch_model.load_state_dict(state_dict, strict=False)
            logger.info('checkpoint is successfully loaded')
        else:
            msg = ("checkpoint is NOT loaded since model_name is {} while checkpoint['model_name'] is {}"
                   .format(model_wrapper.model_name, checkpoint['model_name']))
            raise AutoMLVisionRuntimeUserException(msg)
