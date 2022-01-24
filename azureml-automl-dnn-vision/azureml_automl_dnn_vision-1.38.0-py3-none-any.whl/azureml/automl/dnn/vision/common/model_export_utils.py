# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper Utils for model deployment."""
import json
import os
import tempfile
from typing import Any, Callable, Dict, List, Optional, Union

import pkg_resources
import torch

import azureml.automl.core.shared.constants as shared_constants
from azureml.automl.core.inference import inference
from azureml.automl.core.shared import logging_utilities
from azureml.automl.dnn.vision.classification.models.base_model_wrapper import BaseModelWrapper
from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.object_detection.models.base_model_wrapper import \
    BaseObjectDetectionModelWrapper
from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper
from azureml.core.run import Run, _OfflineRun
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext

logger = get_logger(__name__)


def prepare_model_export(run: Run, output_dir: str, task_type: str,
                         model_settings: Optional[Dict[str, Any]] = {},
                         save_as_mlflow: bool = False, is_yolo: bool = False) -> None:
    """Save model and weights to artifacts, generate score script and
        conda environment yml, and save run properties needed for model export

    :param run: The current azureml run object
    :type run: azureml.core.Run
    :param output_dir: Name of dir to save model files.
    :type output_dir: str
    :param task_type: Task type used in training.
    :type task_type: str
    :param model_settings: Settings for the model
    :type model_settings: dict
    :param save_as_mlflow: Flag to save as mlflow model
    :type save_as_mlflow: bool
    :param is_yolo: True if experiment is object detection yolo
    :type is_yolo: bool
    """
    automl_run_context = AzureAutoMLRunContext(run)

    strs_to_save = {}

    torch_model = torch.load(os.path.join(output_dir, shared_constants.PT_MODEL_FILENAME),
                             map_location='cpu')

    models_to_upload = {
        # load the checkpoint of the best model to be saved in outputs
        shared_constants.PT_MODEL_PATH: torch_model
    }

    # Save conda environment file into artifacts
    try:
        strs_to_save[shared_constants.CONDA_ENV_FILE_PATH] = _create_conda_env_file_content(run)
    except Exception as e:
        logger.warning("Failed to create conda environment file.")
        logging_utilities.log_traceback(e, logger)

    # Save scoring file into artifacts
    try:
        scoring_file_str = _get_scoring_file(run=run,
                                             task_type=task_type,
                                             model_settings=model_settings,
                                             is_yolo=is_yolo)
        strs_to_save[shared_constants.SCORING_FILE_PATH] = scoring_file_str
    except Exception as e:
        logger.warning("Failed to create score inference file.")
        logging_utilities.log_traceback(e, logger)

    # TODO: Remove once mlflow support is implemented
    if save_as_mlflow:
        logger.warning("save_as_mlflow is True but isn't supported yet. Defaulting to save_as_mlflow=False")
        save_as_mlflow = False

    # Upload files to artifact store
    automl_run_context.batch_save_artifacts(working_directory=os.getcwd(),
                                            input_strs=strs_to_save,
                                            model_outputs=models_to_upload,
                                            save_as_mlflow=save_as_mlflow
                                            )

    # Get model artifacts file paths
    scoring_data_loc = automl_run_context._get_artifact_id(shared_constants.SCORING_FILE_PATH)
    conda_env_data_loc = automl_run_context._get_artifact_id(shared_constants.CONDA_ENV_FILE_PATH)
    model_artifacts_file = automl_run_context._get_artifact_id(shared_constants.PT_MODEL_PATH)

    # Add paths to run properties for model deployment
    properties_to_add = {
        inference.AutoMLInferenceArtifactIDs.ScoringDataLocation: scoring_data_loc,
        inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation: conda_env_data_loc,
        inference.AutoMLInferenceArtifactIDs.ModelDataLocation: model_artifacts_file
    }
    run.add_properties(properties_to_add)


def _create_conda_env_file_content(run: Run) -> Any:
    """
    Return conda/pip dependencies for the current run.

    If there are any changes to the conda environment file, the version of the conda environment
    file should be updated in the vendor.

    :param run: The current azureml run object
    :type run: azureml.core.run
    :return: Conda dependencies as string
    :rtype: str
    """
    env = run.get_environment()
    conda_deps = env.python.conda_dependencies

    # Add necessary extra package dependencies
    for conda_package in inference.get_local_conda_versions(inference.AutoMLVisionCondaPackagesList):
        conda_deps.add_conda_package(conda_package)

    # Add pytorch channel to download pytorch and torchvision
    conda_deps.add_channel('pytorch')

    # Renames environment to 'project environment' instead
    # using the default generated name
    conda_deps._conda_dependencies['name'] = 'project_environment'
    return conda_deps.serialize_to_string()


def _get_scoring_file(run: Run, task_type: str, model_settings: Optional[Dict[str, Any]] = {},
                      is_yolo: Optional[bool] = False) -> str:
    """
    Return scoring file to be used at the inference time.

    If there are any changes to the scoring file, the version of the scoring file should
    be updated in the vendor.

    :param run: The current azureml run object
    :type run: azureml.core.Run
    :param task_type: Task type used in training
    :type task_type: str
    :param model_settings: Settings for the model
    :type model_settings: dict
    :param is_yolo: True if experiment is object detection yolo
    :type is_yolo: bool
    :return: Scoring python file as a string
    :rtype: str
    """
    scoring_file_path = pkg_resources.resource_filename(
        inference.PACKAGE_NAME, os.path.join('inference', 'score_images.txt'))

    # Ensure correct path is used to import _score_with_model in the script
    score_path = 'object_detection_yolo.writers' if is_yolo else 'object_detection.writers'
    if task_type in shared_constants.Tasks.ALL_IMAGE_CLASSIFICATION:
        score_path = 'classification.inference'

    model_name = inference._get_model_name(run.id)

    if model_settings is None:
        model_settings = {}

    with open(scoring_file_path, 'r') as scoring_file_ptr:
        content = scoring_file_ptr.read()
        content = content.replace('<<task_type>>', task_type)
        content = content.replace('<<score_path>>', score_path)
        content = content.replace('<<model_name>>', model_name)
        content = content.replace('<<model_settings>>', json.dumps(model_settings))

    return content


def load_model(task_type: str,
               model_path: str,
               **model_settings: Dict[str, Any]) -> Union[BaseObjectDetectionModelWrapper,
                                                          YoloV5Wrapper,
                                                          BaseModelWrapper]:
    """Load model for model deployment

    :param task_type: Task type used in training.
    :type task_type: str
    :param model_path: Path to the model file
    :type model_path: str
    :param model_settings: Settings for the model
    :type model_settings: dict
    :return: Loaded model wrapper
    :rtype: typing.Union[object_detection.models.CommonObjectDetectionModelWrapper,
                         object_detection_yolo.models.Model,
                         classification.models.BaseModelWrapper]
    """
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    if task_type in shared_constants.Tasks.ALL_IMAGE_CLASSIFICATION:
        from azureml.automl.dnn.vision.classification.common.classification_utils import \
            _load_model_wrapper as classification_load_model_wrapper
        return classification_load_model_wrapper(torch_model_file=model_path, distributed=False, rank=0,
                                                 device=device, model_settings=model_settings)
    else:
        from azureml.automl.dnn.vision.object_detection.common.object_detection_utils import \
            _load_model_wrapper as od_load_model_wrapper
        return od_load_model_wrapper(torch_model_file=model_path, device=device, model_settings=model_settings)


def run_inference(model: Union[BaseObjectDetectionModelWrapper, YoloV5Wrapper, BaseModelWrapper],
                  request_body: bytes, score_with_model: Callable[..., None]) -> bytes:
    """ Run inferencing for deployed models

    :param model: Model to use for inferencing
    :type model: typing.Union[object_detection.models.CommonObjectDetectionModelWrapper,
                              object_detection_yolo.models.Model,
                              classification.models.BaseModelWrapper]
    :param request_body: Data of image to score
    :type request_body: str
    :param score_with_model: method to be called for scoring
    :type score_with_model: Callable
    :return: Output of inferencing
    :rtype: bytes
    """
    with tempfile.NamedTemporaryFile() as output_filename_fp, \
        tempfile.NamedTemporaryFile(mode="w") as image_list_file_fp, \
            tempfile.NamedTemporaryFile() as image_file_fp:

        image_file_fp.write(request_body)
        image_file_fp.flush()

        image_list_file_fp.write(image_file_fp.name)
        image_list_file_fp.flush()

        root_dir = ""
        device = utils._get_default_device()
        score_with_model(model,
                         run=_OfflineRun(),
                         target_path=None,
                         output_file=output_filename_fp.name,
                         root_dir=root_dir,
                         image_list_file=image_list_file_fp.name,
                         device=device,
                         num_workers=0)
        output_filename_fp.flush()
        return output_filename_fp.read()


def run_inference_batch(model: Union[BaseObjectDetectionModelWrapper, YoloV5Wrapper, BaseModelWrapper],
                        mini_batch: List[str], score_with_model: Callable[..., None],
                        batch_size: Optional[int] = None) -> List[str]:
    """ Run inferencing for deployed models

    :param model: Model to use for inferencing
    :type model: typing.Union[object_detection.models.CommonObjectDetectionModelWrapper,
                              object_detection_yolo.models.Model,
                              classification.models.BaseModelWrapper]
    :param mini_batch: list of filepaths to images to score
    :type mini_batch: list[str]
    :param score_with_model: method to be called for scoring
    :type score_with_model: Callable
    :param batch_size: batch size for inferencing
    :type batch_size: int
    :return: Output of inferencing
    :rtype: list[str]
    """
    with tempfile.TemporaryDirectory() as tmp_output_dir:
        with tempfile.NamedTemporaryFile(mode="w") as image_list_file_fp:

            image_list_file_fp.write('\n'.join(mini_batch))
            image_list_file_fp.flush()

            device = utils._get_default_device()
            output_file_path = os.path.join(tmp_output_dir,
                                            "predictions.txt")

            if batch_size:
                logger.info("Scoring with batch size: {}.".format(batch_size))
                score_with_model(model,
                                 run=_OfflineRun(),
                                 target_path=None,
                                 output_file=output_file_path,
                                 root_dir="",
                                 image_list_file=image_list_file_fp.name,
                                 device=device,
                                 batch_size=batch_size,
                                 num_workers=0)
            else:
                logger.info("Scoring with default value for batch size.")
                score_with_model(model,
                                 run=_OfflineRun(),
                                 target_path=None,
                                 output_file=output_file_path,
                                 root_dir="",
                                 image_list_file=image_list_file_fp.name,
                                 device=device,
                                 num_workers=0)

            logger.info("Finished batch inferencing")

            results = []
            with open(output_file_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip('\n')
                    results.append(line)

            return results
