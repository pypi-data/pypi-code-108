# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains utility classes and functions for classification."""
import os
from itertools import chain
from typing import Any, Dict, Tuple

import numpy as np
import pkg_resources
import torch
from sklearn.model_selection import train_test_split

import azureml.automl.core.shared.constants as shared_constants
from azureml.automl.runtime.shared.score._metric_base import NonScalarMetric
from azureml.automl.runtime.shared.score.scoring import constants as scoring_constants
from azureml.automl.dnn.vision.classification.common.constants import PackageInfo, ModelLiterals, \
    vit_batch_size_defaults, vit_mc_lrs, vit_ml_lrs
from azureml.automl.dnn.vision.classification.models import ModelFactory
from azureml.automl.dnn.vision.classification.models.base_model_wrapper import BaseModelWrapper
from azureml.automl.dnn.vision.common.artifacts_utils import _download_model_from_artifacts
from azureml.automl.dnn.vision.common.constants import ArtifactLiterals, MetricsLiterals, SettingsLiterals, \
    TrainingCommonSettings, TrainingLiterals as CommonTrainingLiterals
from azureml.automl.dnn.vision.common.data_utils import get_labels_files_paths_from_settings
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException, AutoMLVisionTrainingException
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.run import Run, _OfflineRun

logger = get_logger(__name__)


class _CondaUtils:

    @staticmethod
    def _all_dependencies():
        """Retrieve the packages from the site-packages folder by using pkg_resources.

        :return: A dict contains packages and their corresponding versions.
        """
        dependencies_versions = dict()
        for d in pkg_resources.working_set:
            dependencies_versions[d.key] = d.version
        return dependencies_versions

    @staticmethod
    def get_conda_dependencies():
        dependencies = _CondaUtils._all_dependencies()
        conda_packages = []
        pip_packages = []
        for package_name in PackageInfo.PIP_PACKAGE_NAMES:
            pip_packages.append('{}=={}'.format(package_name, dependencies[package_name]))

        for package_name in PackageInfo.CONDA_PACKAGE_NAMES:
            conda_packages.append('{}=={}'.format(package_name, dependencies[package_name]))

        cd = CondaDependencies.create(pip_packages=pip_packages, conda_packages=conda_packages,
                                      python_version=PackageInfo.PYTHON_VERSION)

        return cd


def _get_train_valid_sub_file_paths(output_dir):
    """Get the file paths (for training and validation) when input dataset
    is split into training and validation and used.

    :param output_dir: where the train and val files are saved.
    :type output_dir: str
    :return: full path for train and validation
    :rtype: Tuple[str, str]
    """
    new_train_file = os.path.join(output_dir, ArtifactLiterals.TRAIN_SUB_FILE_NAME)
    new_valid_file = os.path.join(output_dir, ArtifactLiterals.VAL_SUB_FILE_NAME)
    return new_train_file, new_valid_file


def _gen_validfile_from_trainfile(train_file, val_size=0.2, output_dir=None):
    """Split dataset into training and validation.

    :param train_file: full path for train file
    :type train_file: str
    :param val_size: ratio of input data to be put in validation
    :type val_size: float
    :param output_dir: where to save train and val files
    :type output_dir: str
    :return: full path for train and validation
    :rtype: str
    """
    new_train_file, new_valid_file = _get_train_valid_sub_file_paths(output_dir)

    if os.path.exists(new_train_file) and os.path.exists(new_valid_file):
        # If validation file is already generated from train file, return it.
        return new_train_file, new_valid_file

    os.makedirs(output_dir, exist_ok=True)

    lines = []
    num_lines = 0
    with open(train_file, "r") as f:
        for line in f:
            lines.append(line.strip())
            num_lines += 1

    indices = np.arange(num_lines)
    x_train, x_test, _, _ = train_test_split(indices, lines, test_size=val_size)

    newline = '\n'
    with open(new_train_file, "w") as f1:
        for idx in x_train:
            f1.write(lines[idx] + newline)

    with open(new_valid_file, "w") as f2:
        for idx in x_test:
            f2.write(lines[idx] + newline)

    return new_train_file, new_valid_file


def split_train_file_if_needed(settings):
    """ Split the train file into train file and validation file if validation file is not provided.

    This step needs to be done before launching distributed training so that there are no concurrency issues
    where multiple processes are writing to the same output validation file.

    :param settings: Dictionary with all training and model settings
    :type settings: Dict
    """
    labels_path, validation_labels_path = get_labels_files_paths_from_settings(settings)
    if validation_labels_path is None:
        _gen_validfile_from_trainfile(train_file=labels_path,
                                      val_size=settings[CommonTrainingLiterals.SPLIT_RATIO],
                                      output_dir=settings[SettingsLiterals.OUTPUT_DIR])


def _get_model_params(model, model_name=None):
    """Separate learnable model params into three groups (the last, the rest (except batchnorm layers), and batchnorm)
    to apply different training configurations.

    :param model: model class
    :type model object
    :param model_name: current network name
    :type str
    :return: groups of model params
    :rtype: lists
    """
    if model_name is None:
        raise AutoMLVisionValidationException('model_name cannot be None', has_pii=False)

    inception_last_layers = ['AuxLogits.', 'fc.']
    seresnext_last_layers = ['last_linear']
    models_last_layers = ['fc.']

    model_to_layers = {'inception': inception_last_layers, 'seresnext': seresnext_last_layers}

    last_layer_names = model_to_layers.get(model_name, models_last_layers)

    rest_params = []
    last_layer_params = []
    batchnorm_params = []

    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if any(map(lambda x: name.startswith(x), last_layer_names)):
            last_layer_params.append(param)
        else:
            if 'bn' in name:
                batchnorm_params.append(param)
            else:
                rest_params.append(param)

    return last_layer_params, rest_params, batchnorm_params


def load_model_from_artifacts(run_id, device, experiment_name=None, distributed=False, rank=0,
                              model_settings={}):
    """
    :param run_id: run id of the run that produced the model
    :type run_id: str
    :param device: device to use
    :type device: torch.device
    :param experiment_name: name of experiment that contained the run id
    :type experiment_name: str
    :param distributed: flag that indicates if the model is going to be used in distributed mode
    :type distributed: bool
    :param rank: rank of the process in distributed mode
    :type rank: int
    :param model_settings: Optional argument to update model settings
    :type model_settings: Dictionary
    :return: Model Wrapper object
    :rtype: classification.models.base_model_wrapper.BaseModelWrapper
    """
    _download_model_from_artifacts(run_id=run_id, experiment_name=experiment_name)

    return _load_model_wrapper(shared_constants.PT_MODEL_FILENAME, distributed, rank, device, model_settings)


def _load_model_wrapper(torch_model_file, distributed, rank, device, model_settings={}) -> BaseModelWrapper:

    checkpoint = torch.load(torch_model_file, map_location=device)
    model_state = checkpoint['model_state']
    model_name = checkpoint['model_name']
    number_of_classes = checkpoint['number_of_classes']
    specs = checkpoint['specs']
    settings = specs['model_settings']
    # make sure we overwrite those matching model settings with the user provided ones (if any)
    image_size_key_mapping = {
        ModelLiterals.RESIZE_SIZE: ModelLiterals.VALID_RESIZE_SIZE,
        ModelLiterals.CROP_SIZE: ModelLiterals.VALID_CROP_SIZE,
    }
    for key in model_settings:
        if key in image_size_key_mapping and image_size_key_mapping[key] in settings:
            settings[image_size_key_mapping[key]] = model_settings[key]
        elif key in settings:
            settings[key] = model_settings[key]

    model_wrapper: BaseModelWrapper = ModelFactory().get_model_wrapper(model_name=model_name,
                                                                       num_classes=number_of_classes,
                                                                       multilabel=specs['multilabel'],
                                                                       distributed=distributed,
                                                                       rank=rank,
                                                                       device=device,
                                                                       model_state=model_state,
                                                                       settings=settings)

    model_wrapper.labels = specs['labels']

    return model_wrapper


def score_validation_data(azureml_run, model_settings, ignore_data_errors,
                          val_dataset_id, image_folder, device, settings, score_with_model):
    """ Runs validations on the best model to give predictions output

    :param azureml_run: azureml run object
    :type azureml_run: azureml.Run
    :param model_settings: dictionary containing model settings
    :type model_settings: dict
    :param ignore_data_errors: boolean flag on whether to ignore input data errors
    :type ignore_data_errors: bool
    :param val_dataset_id: The validation dataset id
    :type val_dataset_id: str
    :param image_folder: default prefix to be added to the paths contained in image_list_file
    :type image_folder: str
    :param device: device to use for scoring
    :type device: str
    :param settings: dictionary containing settings
    :type settings: dict
    :param score_with_model: method to be called for scoring
    :type score_with_model: Callable
    """
    logger.info("Beginning validation for the best model")

    # Get image_list_file with path
    root_dir = image_folder
    val_labels_file = settings.get(SettingsLiterals.VALIDATION_LABELS_FILE, None)
    if val_labels_file is not None:
        val_labels_file = os.path.join(settings[SettingsLiterals.LABELS_FILE_ROOT], val_labels_file)
        root_dir = os.path.join(settings[SettingsLiterals.DATA_FOLDER], image_folder)

    if val_labels_file is None and val_dataset_id is None:
        logger.warning("No validation dataset or validation file was given, skipping scoring run.")
        return

    # Get target path
    target_path = settings.get(SettingsLiterals.OUTPUT_DATASET_TARGET_PATH, None)
    if target_path is None:
        target_path = AmlDatasetHelper.get_default_target_path()

    batch_size = settings.get(CommonTrainingLiterals.VALIDATION_BATCH_SIZE, None)
    if batch_size is None:
        batch_size = settings.get(CommonTrainingLiterals.TRAINING_BATCH_SIZE)

    output_file = settings.get(SettingsLiterals.VALIDATION_OUTPUT_FILE, None)
    num_workers = settings[SettingsLiterals.NUM_WORKERS]
    log_scoring_file_info = settings.get(SettingsLiterals.LOG_SCORING_FILE_INFO, False)

    model_wrapper = load_model_from_artifacts(azureml_run.id, device=device, model_settings=model_settings)

    logger.info("[start scoring for validation data: batch_size: {}]".format(batch_size))
    score_with_model(model_wrapper=model_wrapper,
                     run=azureml_run, target_path=target_path,
                     output_file=output_file, root_dir=root_dir,
                     image_list_file=val_labels_file, batch_size=batch_size,
                     ignore_data_errors=ignore_data_errors,
                     input_dataset_id=val_dataset_id,
                     device=device,
                     num_workers=num_workers,
                     log_output_file_info=log_scoring_file_info)


def log_classification_metrics(classification_metrics: Any, computed_metrics: Any,
                               primary_metric: str, azureml_run: Run, final_epoch: bool = False,
                               best_model_metrics: Any = None) -> None:
    """Logs all metrics passed in the dictionary to the run history of the given run.

    :param classification_metrics: classification metrics object
        with the supported metrics for the run.
    :type classification_metrics:
        <class 'vision.metrics.classification_metrics.ClassificationMetrics'>
    :param computed_metrics: Dictionary with metrics and
        respective values to be logged to Run History.
    :type computed_metrics: dict
    :param primary_metric: primary metric for the task.For multilabel its iou, otherwise accuracy.
    :type primary_metric: str
    :param azureml_run: The run object.
    :type azureml_run: azureml.core.run
    :param final_epoch: Flag indicating the final epoch.
    :type final_epoch: bool
    :param best_model_metrics: Dictionary with metrics and respective values to be logged
        to Run History corresponding to the best model.
    :type best_model_metrics: dict

    """
    if azureml_run is None:
        raise AutoMLVisionTrainingException("Cannot log metrics to Run History \
            since azureml_run is None", has_pii=False)

    logger.info("Logging metrics in Run History.")

    if isinstance(azureml_run, _OfflineRun):
        logger.warn("Cannot log metrics to Run History since azureml_run is of type _OfflineRun")

    for metric_name, value in computed_metrics.items():

        # Log primary metric and loss for training data
        if metric_name == MetricsLiterals.AUTOML_CLASSIFICATION_TRAIN_METRICS:
            if value[primary_metric] is not np.nan:
                azureml_run.log(primary_metric + '_train',
                                round(value[primary_metric], 5))
            logger.info("{}: {}".format(primary_metric + '_train', round(value[primary_metric], 5)))
            if value[scoring_constants.LOG_LOSS] is not np.nan:
                azureml_run.log(scoring_constants.LOG_LOSS + '_train',
                                round(value[scoring_constants.LOG_LOSS], 5))
            logger.info("{}: {}".format(scoring_constants.LOG_LOSS + '_train',
                                        round(value[scoring_constants.LOG_LOSS], 5)))

        # Metrics for the last epoch - confusion matrix, classification report, accuracy table.
        # confusion matrix and accuracy table is only available for multiclass.
        if final_epoch and best_model_metrics is not None:
            classification_summary_dict = dict()
            log_header = None
            log_classification_report = True

            if metric_name == MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS:
                for nonscalar_metric in chain(scoring_constants.CLASSIFICATION_NONSCALAR_SET):
                    if nonscalar_metric not in classification_metrics._unsupported_metrics and \
                            nonscalar_metric in best_model_metrics[
                                MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS]:

                        # Log confusion matrix - multiclass
                        if nonscalar_metric == scoring_constants.CONFUSION_MATRIX:
                            confusion_matrix = best_model_metrics[
                                MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][nonscalar_metric]
                            if not NonScalarMetric.is_error_metric(confusion_matrix):
                                azureml_run.log_confusion_matrix(
                                    nonscalar_metric, confusion_matrix)
                                logger.info("{}: {}".format(scoring_constants.CONFUSION_MATRIX, confusion_matrix[
                                    MetricsLiterals.DATA][MetricsLiterals.MATRIX]))
                            else:
                                logger.error("Non scalar metric {} returned a error:{}".format(
                                    nonscalar_metric, confusion_matrix))

                        # Log accuracy table - multiclass
                        if nonscalar_metric == scoring_constants.ACCURACY_TABLE:
                            accuracy_table = best_model_metrics[
                                MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][nonscalar_metric]
                            if not NonScalarMetric.is_error_metric(accuracy_table):
                                azureml_run.log_accuracy_table(
                                    nonscalar_metric, accuracy_table)
                            else:
                                logger.error("Non scalar metric {} returned a error:{}".format(
                                    nonscalar_metric, accuracy_table))

                        # Log classification report - multiclass and multilabel
                        if nonscalar_metric == scoring_constants.CLASSIFICATION_REPORT:
                            classification_report_dict = best_model_metrics[
                                MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][
                                    nonscalar_metric]

                            if not NonScalarMetric.is_error_metric(classification_report_dict):
                                classification_report_metric = [
                                    MetricsLiterals.PRECISION, MetricsLiterals.RECALL,
                                    MetricsLiterals.F1_SCORE, MetricsLiterals.SUPPORT]
                                header = [item for item in chain(
                                    classification_report_dict[MetricsLiterals.DATA][MetricsLiterals.CLASS_LABELS],
                                    classification_report_dict[MetricsLiterals.DATA][MetricsLiterals.AVERAGE])]
                                log_header = [item for item in chain(
                                    range(len(classification_report_dict[MetricsLiterals.DATA][
                                        MetricsLiterals.CLASS_LABELS])),
                                    classification_report_dict[MetricsLiterals.DATA][MetricsLiterals.AVERAGE])]
                                classification_summary_dict[MetricsLiterals.CLASS_NAME] = header
                                for index, metric in enumerate(classification_report_metric):
                                    classification_summary_dict[metric] = np.around(np.array(
                                        classification_report_dict[MetricsLiterals.DATA][
                                            MetricsLiterals.MATRIX])[:, index], 5).tolist()
                            else:
                                log_classification_report = False
                                logger.error("Non scalar metric {} returned a error:{}".format(
                                    nonscalar_metric, classification_report_dict))

                if log_classification_report:
                    classification_report_metric = [
                        MetricsLiterals.IOU, MetricsLiterals.AUC, MetricsLiterals.AVERAGE_PRECISION]

                    average_metric = [MetricsLiterals.MICRO, MetricsLiterals.MACRO,
                                      MetricsLiterals.WEIGHTED]
                    classwise_scores_dict = dict()
                    average_scores_dict = dict()

                    #  Aggregate classwise metrics for the classification report
                    for classwise_metric in scoring_constants.CLASSIFICATION_CLASSWISE_SET:
                        if classwise_metric not in classification_metrics._unsupported_metrics and \
                            classwise_metric in best_model_metrics[
                                MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS]:
                            for metric in classification_report_metric:
                                if metric.lower() in classwise_metric.lower():
                                    classwise_scores_dict[classwise_metric] = best_model_metrics[
                                        MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][
                                            classwise_metric]

                    #  Aggregate scalar metrics for the classification report
                    for scalar_metric in chain(scoring_constants.CLASSIFICATION_SCALAR_SET,
                                               scoring_constants.CLASSIFICATION_MULTILABEL_SET):
                        if scalar_metric not in classification_metrics._unsupported_metrics and \
                            scalar_metric in best_model_metrics[
                                MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS]:
                            for metric in classification_report_metric:
                                if metric.lower() in scalar_metric.lower():
                                    average_scores_dict[scalar_metric] = round(best_model_metrics[
                                        MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS][
                                            scalar_metric], 5)

                    # Add the aggregated classwise and scalar metrics
                    # to the classification report.
                    for metric in classification_report_metric:
                        scores = []
                        for classwise_metric in classwise_scores_dict:
                            if metric.lower() in classwise_metric.lower():
                                if not NonScalarMetric.is_error_metric(
                                        classwise_scores_dict[classwise_metric]) or\
                                        np.isscalar(classwise_scores_dict[classwise_metric]):
                                    classwise_scores_list = list(classwise_scores_dict[classwise_metric].values())
                                    classwise_scores_list = [round(val, 5) for val in classwise_scores_list]
                                    scores.extend(classwise_scores_list)
                                else:
                                    logger.error("Unable to compute class metric {}.".format(classwise_metric))

                        # Add the average metrics to the classification report.
                        for avg_metric_name in average_metric:
                            for avg_metric in average_scores_dict:
                                if metric.lower() in avg_metric.lower() and \
                                        avg_metric_name.lower() in avg_metric.lower():
                                    scores.append(
                                        average_scores_dict[avg_metric])

                        if len(scores) == len(classification_metrics.labels) + len(average_metric):
                            classification_summary_dict[metric] = scores

                    # Log the classification report.
                    if len(classification_summary_dict) > 0:
                        for row in range(len(classification_metrics.labels) + len(average_metric)):
                            log_row_dict = {metric_col: metric_val[row] for metric_col, metric_val in
                                            classification_summary_dict.items()}
                            azureml_run.log_row(scoring_constants.CLASSIFICATION_REPORT, **log_row_dict)
                        if log_header is not None:
                            classification_summary_dict[MetricsLiterals.CLASS_NAME] = log_header
                            logger.info("{}: {}".format(scoring_constants.CLASSIFICATION_REPORT,
                                                        classification_summary_dict))

        if metric_name == MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS:
            azureml_run.log(scoring_constants.LOG_LOSS,
                            round(value[scoring_constants.LOG_LOSS], 5))
            logger.info("{}: {}".format(scoring_constants.LOG_LOSS,
                                        round(value[scoring_constants.LOG_LOSS], 5)))

            # Log scalar metrics for evaluation data
            for scalar_metric in chain(scoring_constants.CLASSIFICATION_SCALAR_SET,
                                       scoring_constants.CLASSIFICATION_MULTILABEL_SET):
                if scalar_metric not in classification_metrics._unsupported_metrics and \
                        scalar_metric in computed_metrics[MetricsLiterals.AUTOML_CLASSIFICATION_EVAL_METRICS]:
                    if value[scalar_metric] is not np.nan:
                        azureml_run.log(scalar_metric, round(value[scalar_metric], 5))
                    logger.info("{}: {}".format(scalar_metric, round(value[scalar_metric], 5)))


def get_vit_default_setting(model_name: str) -> Tuple[Dict, Dict, Dict]:
    """Get default setting for ViT models.

    :param model_name: model_name of the vit model: ModelNames.VITS16R224, ModelNames.VITB16R224, ModelNames.VITL16R224
    :type model_name: str
    :return: training_settings_defaults, multiclass_training_settings_defaults, multilabel_training_settings_defaults
    :rtype: Tuple[Dict, Dict, Dict]
    """

    training_settings_defaults = {
        CommonTrainingLiterals.TRAINING_BATCH_SIZE: vit_batch_size_defaults[model_name],
        CommonTrainingLiterals.VALIDATION_BATCH_SIZE: vit_batch_size_defaults[model_name],
        CommonTrainingLiterals.GRAD_CLIP_TYPE: TrainingCommonSettings.DEFAULT_VIT_GRAD_CLIP_TYPE}
    multiclass_training_settings_defaults = {CommonTrainingLiterals.LEARNING_RATE: vit_mc_lrs[model_name]}
    multilabel_training_settings_defaults = {CommonTrainingLiterals.LEARNING_RATE: vit_ml_lrs[model_name]}

    return training_settings_defaults, multiclass_training_settings_defaults, multilabel_training_settings_defaults
