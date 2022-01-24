# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the client that uploads and downloads explanations."""

import json
import numpy as np
import os
import pandas as pd
import pickle
import scipy as sp

from operator import itemgetter

from typing import Dict, List

from interpret_community.common.explanation_utils import (
    _sort_values, _sort_feature_list_multiclass, _unsort_1d, module_logger)
from interpret_community.dataset.dataset_wrapper import DatasetWrapper
from interpret_community.explanation.explanation import (
    _create_local_explanation, _create_global_explanation, BaseExplanation)
from interpret_community.explanation.explanation import (
    FeatureImportanceExplanation, GlobalExplanation,
    ExpectedValuesMixin, ClassesMixin, PerClassMixin)

from azureml._common._error_definition import AzureMLError
from azureml._restclient.assets_client import AssetsClient
from azureml._restclient.constants import RUN_ORIGIN
from azureml.core import Experiment, Run, Workspace, Dataset
from azureml.exceptions import UserErrorException
from azureml.interpret.common._errors.error_definitions import (
    ClassNumberMismatch,
    EvalDataMismatch, ExperimentMissingIdAndName,
    ExplanationFilterNotFound, ExplanationFiltersNotFound, ExplanationNotFound,
    InvalidYTrueDimension, SampleLimitExceeded, InvalidExplanationDataType)
from azureml.interpret.common.constants import (
    ExplainParams, ExplainType, History, BackCompat, IO,
    RunPropertiesAndTags, VizData)
from azureml.interpret.common.explanation_utils import ArtifactUploader
from azureml.interpret.common.model_summary import ModelSummary

from azureml.interpret.common.exceptions import (
    SamplesExceededException, ExplanationNotFoundException,
    NoExperimentNameOrIdException, DimensionMismatchException,
    InvalidExplanationException)

from azureml.interpret._internal.constants import (FALSE, TRUE, LOCAL_IMP_SIZE_LIMIT,
                                                   U_LOCAL_IMPORTANCE_VALUES,
                                                   U_EVAL_DATA, U_EVAL,
                                                   U_YS_PRED,
                                                   U_YS_PRED_PROBA)


def _unsort_2d(values, order):
    """Unsort a sorted 2d array based on the order that was used to sort it.

    :param values: The array that has been sorted.
    :type values: numpy.array
    :param order: The order list that was originally used to sort values.
    :type order: numpy.ndarray
    :return: The unsorted array.
    :rtype: numpy.array
    """
    return np.array([_unsort_1d(values[i], order[i]).tolist() for i in range(len(order))])


def _translate_y_to_indices(y, classes):
    """Convert actual values to class indices.

    :param y: List of values in target.
    :type y: list
    :param classes: List of values in classes.
    :type classes: list
    :return: Translated indexed based values of y.
    :rtype: list
    """
    if y is not None and classes is not None:
        if all(isinstance(some_class, str) for some_class in y):
            try:
                y_int = []
                for val in y:
                    y_int.append(classes.index(val))
                return y_int
            except ValueError:
                module_logger.error('Unable to map some class to index')
    return y


def _create_download_dir():
    """Create a consistently named and placed directory for explanation downloads.

    :return: The download path relative to the current directory.
    :rtype: str
    """
    # create the downloads folder
    download_dir = './download_explanation/'
    os.makedirs(download_dir, exist_ok=True)
    return download_dir


def _create_artifact_path(explanation_id=None):
    """Return the artifact path from the explanation id.

    :param explanation_id: The explanation ID the file is stored under.
        If None, it is assumed that the run is using an old storage format.
    :type explanation_id: str
    :return: artifact path.
    :rtype: str
    """
    if explanation_id is not None:
        return 'explanation/{}/'.format(explanation_id[:History.ID_PATH_2004])
    else:
        # backwards compatibility February 2019
        return 'explanation/'


def _download_artifact(run, download_dir, artifact_name, extension, explanation_id=None, file_type=IO.JSON):
    """Download an artifact file from a run and load the contents.

    :param run: The run artifacts are stored under.
    :type run: azureml.core.run.Run
    :param download_dir: The directory to which the file should be downloaded.
    :type download_dir: str
    :param artifact_name: The path of the artifact in the cloud.
    :type artifact_name: str
    :param extension: '.interpret.json' for v5, '.json' for earlier versions.
    :type extension: str
    :param explanation_id: The explanation ID the file is stored under.
        If None, it is assumed that the run is using an old storage format.
    :type explanation_id: str
    :param file_type: A switch for pickle or JSON storage.
    :type file_type: str
    :return: The loaded values from the artifact that has been downloaded.
    :rtype: object
    """
    if artifact_name.startswith(RUN_ORIGIN):
        _, artifact_name = os.path.split(artifact_name)
    artifact_path = _create_artifact_path(explanation_id)
    interpret_string = '.interpret' if 'interpret' in extension else ''
    file_name = '{}{}{}.{}'.format(artifact_path, artifact_name, interpret_string, file_type)
    path = os.path.join(download_dir, file_name)
    try:
        run.download_file(file_name, path)
    except UserErrorException:
        # back compat April 2020
        artifact_path = 'explanation/{}/'.format(explanation_id) if explanation_id is not None else 'explanation/'
        file_name = '{}{}{}.{}'.format(artifact_path, artifact_name, interpret_string, file_type)
        path = os.path.join(download_dir, file_name)
        run.download_file(file_name, path)
    with open(path, 'rb') as f:
        file_string = f.read()
        if file_type == IO.JSON:
            values = json.loads(file_string.decode(IO.UTF8))
        else:
            values = pickle.loads(file_string)
    return values


def _load_artifact(path):
    """Load a downloaded artifact file directly into memory.

    :param path: The path to the JSON encoded file on disk.
    :type path: str
    :return: The loaded values from the file.
    :rtype: object
    """
    with open(path, 'rb') as f:
        file_string = f.read()
        return json.loads(file_string.decode(IO.UTF8))


def _load_sharded_data(name, file_dict, storage_metadata, download_dir, extension, explanation_id=None):
    """Download and aggregate a chunk of data from its sharded storage format.

    :param name: The name/data type of the chunk to download_dir
    :type name: str
    :param file_dict: Dictionary which here holds the name of the file to load data from.
    :type file_dict: dict
    :param storage_metadata: The metadata dictionary for the asset's stored data
    :type storage_metadata: dict[str: dict[str: Union(str, int)]]
    :param download_dir: The directory to which the asset's files should be downloaded
    :type download_dir: str
    :param extension: '.interpret.json' for v5, '.json' for earlier versions.
    :type extension: str
    :param explanation_id: The explanation ID the data is stored under.
        If None, it is assumed that the asset is using an old storage format.
    :type explanation_id: str
    :param top_k: If specified, limit the ordered data returned to the most important features and values
    :type top_k: int
    :return: The data chunk, anything from 1D to 3D, int or str
    """
    num_columns_to_return = int(storage_metadata[name][History.NUM_FEATURES])
    num_blocks = int(storage_metadata[name][History.NUM_BLOCKS])
    file_name = file_dict[name]
    if BackCompat.OLD_NAME in storage_metadata[name]:
        module_logger.debug('Working with constructed metadata from a v1 asset')
        # Backwards compatibility as of January 2019
        name = storage_metadata[name][BackCompat.OLD_NAME]
    # Backwards compatibility as of February 2019
    connector = '/' if explanation_id is not None else '_'
    artifact = _load_artifact('{}{}0'.format(file_name, connector) + extension)
    full_data = np.array(artifact)
    concat_dim = full_data.ndim - 1
    # Get the blocks
    for idx in range(1, num_blocks):
        block_name = '{}{}{}'.format(file_name, connector, idx)
        block = np.array(_load_artifact(block_name + extension))
        full_data = np.concatenate([full_data, block], axis=concat_dim)
        num_columns_read = full_data.shape[-1]
        if num_columns_read >= num_columns_to_return:
            break
    full_data_list = full_data[..., :num_columns_to_return]
    return full_data_list


def _load_sharded_data_from_list(data_list, storage_metadata, download_dir, file_dict, extension,
                                 explanation_id=None):
    """Check each data name in the list.

    If available on the stored explanation, download the sharded chunks and reconstruct the explanation.

    :param data_list: A list of data names for each kind of data to download.
    :type data_tuples: list[str]
    :param storage_metadata: The metadata dictionary for the asset's stored data.
    :type storage_metadata: dict[str: dict[str: Union(str, int)]]
    :param download_dir: The directory to which the asset's files should be downloaded.
    :type download_dir: str
    :param file_dict: Dictionary which here holds the name of the file to load data from.
    :type file_dict: dict
    :param extension: '.interpret.json' for v5, '.json' for earlier versions.
    :type extension: str
    :param explanation_id: The explanation ID the data is stored under.
        If None, it is assumed that the asset is using an old storage format.
    :type explanation_id: str
    :param top_k: If specified, limit the ordered data returned to the most important features and values.
    :type top_k: int
    :return: A dictionary of the data that was able to be downloaded from run history.
    :rtype: dict
    """
    output_kwargs = {}
    for history_name in data_list:
        if history_name in file_dict:
            module_logger.debug('Downloading ' + history_name)
            values = _load_sharded_data(history_name, file_dict, storage_metadata, download_dir, extension,
                                        explanation_id=explanation_id)
            output_kwargs[history_name] = np.array(values)
    return output_kwargs


def _download_artifacts(run, download_dir, extension, explanation_id=None):
    """Download all artifacts from a given explanation.

    :param run: The run artifacts are stored on.
    :type run: azureml.core.run.Run
    :param download_dir: The directory to which the asset's files should be downloaded
    :type download_dir: str
    :param extension: '.interpret.json' for v5, '.json' for earlier versions.
    :type extension: str
    :param explanation_id: The explanation ID the data is stored under.
        If None, it is assumed that the asset is using an old storage format.
    :type explanation_id: str
    :return: A dictionary mapping short names of data to full file paths.
    :rtype: dict
    """

    if explanation_id is not None:
        artifact_path = os.path.join('explanation', explanation_id[:History.ID_PATH_2004])
    else:
        # backwards compatibility February 2019
        artifact_path = 'explanation'
    run.download_files(prefix=artifact_path, output_directory=download_dir)
    try:
        files = os.listdir(os.path.join(download_dir, artifact_path))
    except FileNotFoundError:
        # back compat April 2020
        artifact_path = os.path.join('explanation', explanation_id) if explanation_id is not None else 'explanation'
        run.download_files(prefix=artifact_path, output_directory=download_dir)
        files = os.listdir(os.path.join(download_dir, artifact_path))
    file_dict = {}
    for f in files:
        if extension in f:
            json_len = len(extension)
            short_name = f if f[-json_len:] != extension else f[:-json_len]
        else:
            json_len = len('.json')
            short_name = f if f[-json_len:] != '.json' else f[:-json_len]
        # TODO extend in case someone has more than 10 shards
        short_name = short_name if short_name[-2] != '_' else short_name[:-2]
        file_dict[short_name] = os.path.join(download_dir, artifact_path, short_name)

    return file_dict


class ExplanationClient(object):
    """Defines the client that uploads and downloads explanations.

    :param service_context: Holder for service information.
    :type service_context: ServiceContext
    :param run_id: A GUID that represents a run.
    :type run_id: str
    :param _run: A run. If passed in, other args will be ignored.
    :type _run: azureml.core.run.Run
    """

    def __init__(self, service_context, experiment_name, run_id, _run=None, datastore_name=None):
        """Create the client used to interact with explanations and run history.

        :param service_context: Holder for service information.
        :type service_context: ServiceContext
        :param run_id: A GUID that represents a run.
        :type run_id: str
        :param _run: A run. If passed in, `run_id` will be ignored.
        :type _run: azureml.core.run.Run
        :param datastore_name: Name of the datastore to use for uploads (defaults to workspace store)
        :type datastore_name: str
        """
        if _run is not None:
            module_logger.debug('Using run to initialize explanation client with service_context = {},'
                                'experiment_name = {}, run_id = {}'.format(service_context, experiment_name, run_id))
            self._run = _run
        else:
            module_logger.debug('Constructing run from workspace, experiment, and run ID')
            sc = service_context
            workspace = Workspace(sc.subscription_id, sc.resource_group_name, sc.workspace_name,
                                  auth=sc.get_auth(), _disable_service_check=True)
            experiment = Experiment(workspace, experiment_name)
            self._run = Run(experiment, run_id=run_id)

        self._datastore_name = datastore_name
        if self._datastore_name is not None:
            module_logger.info("Using datastore {0} for uploads".format(self._datastore_name))
        else:
            module_logger.info("Using default datastore for uploads")

        service_context._add_user_agent(service_context._get_assets_restclient(), 'mli_user_agent')

    @classmethod
    def from_run(cls, run, datastore_name=None):
        """Create the client with factory method given a run.

        :param cls: The ExplanationClient class.
        :type cls: ExplanationClient
        :param run: The run explanations will be attached to.
        :type run: azureml.core.run.Run
        :param datastore_name: Name of the datastore to use for uploads (defaults to workspace store)
        :type datastore_name: str
        :return: An instance of the ExplanationClient.
        :rtype: ExplanationClient
        """
        return cls(run.experiment.workspace.service_context,
                   run.experiment,
                   run.id,
                   _run=run,
                   datastore_name=datastore_name)

    @classmethod
    def from_run_id(cls, workspace, experiment_name, run_id, datastore_name=None):
        """Create the client with factory method given a run ID.

        :param cls: The ExplanationClient class.
        :type cls: ExplanationClient
        :param workspace: An object that represents a workspace.
        :type workspace: azureml.core.workspace.Workspace
        :param experiment_name: The name of an experiment.
        :type experiment_name: str
        :param run_id: A GUID that represents a run.
        :type run_id: str
        :param datastore_name: Name of the datastore to use for uploads (defaults to workspace store)
        :type datastore_name: str
        :return: An instance of the ExplanationClient.
        :rtype: ExplanationClient
        """
        return cls(workspace.service_context, experiment_name, run_id, datastore_name=datastore_name)

    @property
    def run(self):
        """Get the run from the explanation client.

        :return: The run object.
        :rtype: azureml.core.run.Run
        """
        return self._run

    def _validate_explanation_object(self, explanation):
        """Validate the model explanation object before saving to run history.

        :param explanation: The explanation object.
        :type explanation: interpret_community.explanation.explanation.BaseExplanation
        """
        if not BaseExplanation._does_quack(explanation):
            raise InvalidExplanationException._with_error(
                AzureMLError.create(
                    InvalidExplanationDataType, actual=type(explanation), expected='BaseExplanation',
                    target="explanation_client_validation"
                )
            )

    def upload_model_explanation(self,
                                 explanation,
                                 max_num_blocks=None,
                                 block_size=None,
                                 top_k=None,
                                 comment=None,
                                 init_dataset_id=None,
                                 eval_dataset_id=None,
                                 ys_pred_dataset_id=None,
                                 ys_pred_proba_dataset_id=None,
                                 upload_datasets=False,
                                 model_id=None,
                                 true_ys=None,
                                 visualization_points=5000) -> None:
        """Upload the model explanation information to run history.

        :param explanation: The explanation information to save.
        :type explanation: interpret_community.explanation.explanation.BaseExplanation
        :param max_num_blocks: The maximum number of blocks to store.
        :type max_num_blocks: int
        :param block_size: The size of each block for the summary stored in artifacts storage.
        :type block_size: int
        :param top_k: Number of important features stored in the explanation. If specified, only the
            names and values corresponding to the top K most important features will be returned/stored.
            If this is the case, global_importance_values and per_class_values will contain the top k sorted values
            instead of the usual full list of unsorted values.
        :type top_k: int
        :param comment: An optional string to identify the explanation. The string is displayed when listing
            explanations, which allows identification of uploaded explanations.
        :type comment: str
        :param init_dataset_id: The ID of the initialization (background) dataset in the Dataset service, if
            available. Used to link the explanation to the Dataset.
        :type init_dataset_id: str
        :param eval_dataset_id: The ID of the evaluation dataset in the Dataset service, if available. Used to link
            the explanation to the Dataset.
        :type eval_dataset_id: str
        :param ys_pred_dataset_id: The ID of the predicted values dataset in the Dataset service, if available.
        :type ys_pred_dataset_id: str
        :param ys_pred_proba_dataset_id: The ID of the predicted probability values dataset in the Dataset service,
            if available.
        :type ys_pred_proba_dataset_id: str
        :param upload_datasets: If set to True and no dataset IDs are passed in, the evaluation dataset will be
            uploaded to Azure storage as a Dataset object. This will allow the explanation to be linked to the Dataset
            in the web view.
        :type upload_datasets: bool
        :param model_id: The MMS model ID.
        :type model_id: str
        :param true_ys: The true labels for the evaluation examples.
        :type true_ys: list | pandas.Dataframe | numpy.ndarray
        :param visualization_points: If set to an integer, this is the upper bound on the number of points that will
            be available for visualization in the web UI. If set to a list of integers, these integers will be used as
            indices for selecting a sample of points (original data and explanations) to be visualized in the web UI.
            If not planning to view the explanation in the web UI, this parameter can be set to 0 and no extra
            computation or storage will take place.

            The upper limit for either the integer or the length of the list is currently 20000 (twenty thousand). In
            the case that a larger integer or longer list is passed in, the function will fail. The intention is to
            limit the amount of data entering the web UI for performance reasons. With more evaluation, this limit may
            be raised.
        :type visualization_points: int or list[int]
        """
        self._upload_model_explanation_internal(explanation,
                                                max_num_blocks,
                                                block_size,
                                                top_k,
                                                comment,
                                                init_dataset_id,
                                                eval_dataset_id,
                                                ys_pred_dataset_id,
                                                ys_pred_proba_dataset_id,
                                                upload_datasets,
                                                model_id,
                                                true_ys,
                                                visualization_points)
        # Nothing else to do

    def _upload_model_explanation_internal(self,
                                           explanation,
                                           max_num_blocks=None,
                                           block_size=None,
                                           top_k=None,
                                           comment=None,
                                           init_dataset_id=None,
                                           eval_dataset_id=None,
                                           ys_pred_dataset_id=None,
                                           ys_pred_proba_dataset_id=None,
                                           upload_datasets=False,
                                           model_id=None,
                                           true_ys=None,
                                           visualization_points=5000) -> str:
        """Uploads the explanation.

        See upload_model_explanation() for the arguments. This returns the
        id of the uploaded Asset.
        """
        self._validate_explanation_object(explanation)
        VISUALIZATION_MAXIMUM = 20000
        is_viz_turned_on = True
        index_getter = None
        has_local_explanation = hasattr(explanation, U_LOCAL_IMPORTANCE_VALUES)
        sparse_eval_data = False
        if isinstance(visualization_points, int):
            if visualization_points > VISUALIZATION_MAXIMUM:
                raise SamplesExceededException._with_error(
                    AzureMLError.create(
                        SampleLimitExceeded, actual=visualization_points, limit=VISUALIZATION_MAXIMUM,
                        target="visualization_points"
                    )
                )
            elif visualization_points == 0:
                is_viz_turned_on = False
            else:
                if has_local_explanation and not explanation.is_local_sparse:
                    num_viz_points = self._get_num_viz_points(visualization_points, explanation)
                else:
                    num_viz_points = visualization_points
        elif isinstance(visualization_points, list):
            viz_points_size = len(visualization_points)
            if viz_points_size > VISUALIZATION_MAXIMUM:
                raise SamplesExceededException._with_error(
                    AzureMLError.create(
                        SampleLimitExceeded, actual=viz_points_size, limit=VISUALIZATION_MAXIMUM,
                        target="visualization_points"
                    )
                )
            elif viz_points_size == 0:
                is_viz_turned_on = False
            else:
                if has_local_explanation and not explanation.is_local_sparse:
                    num_viz_points = self._get_num_viz_points(viz_points_size, explanation)
                    index_getter = itemgetter(*visualization_points[0:num_viz_points])
                else:
                    index_getter = itemgetter(*visualization_points)

        uploader = ArtifactUploader(self._run, max_num_blocks=max_num_blocks, block_size=block_size)
        module_logger.debug('Initializing AssetsClient')
        assets_client = AssetsClient(self._run.experiment.workspace.service_context)
        classification = ClassesMixin._does_quack(explanation)
        explainer_type = ExplainType.TABULAR
        module_logger.debug('Initializing ModelSummary')
        summary_object = ModelSummary()
        single_artifact_list = []
        sharded_artifact_list = []

        is_raw = False
        is_engineered = False
        num_features = 0
        if FeatureImportanceExplanation._does_quack(explanation):
            if explanation.features is not None:
                features = explanation.features if isinstance(explanation.features, list) else \
                    explanation.features.tolist()
                module_logger.debug('Adding features to artifacts list')
                single_artifact_list.append((History.FEATURES, features, None, IO.JSON))
                num_features = explanation.num_features
            is_raw = explanation.is_raw
            is_engineered = explanation.is_engineered

        num_examples = 0
        if has_local_explanation:
            local_importance_values = explanation._local_importance_values
            if explanation.is_local_sparse:
                if sp.sparse.issparse(local_importance_values):
                    module_logger.debug('Adding sparse local importance values to artifacts list')
                    sparse_data = self._convert_sparse_to_list(local_importance_values)
                else:
                    module_logger.debug('Adding sparse multiclass local importance values to artifacts list')
                    sparse_data = []
                    for sparse_local_values in local_importance_values:
                        sparse_data.append(self._convert_sparse_to_list(sparse_local_values))
                single_artifact_list.append((History.LOCAL_IMPORTANCE_VALUES_SPARSE,
                                            sparse_data,
                                            None, IO.JSON))
            else:
                module_logger.debug('Adding dense local importance values to artifacts list')
                single_artifact_list.append((History.LOCAL_IMPORTANCE_VALUES,
                                             local_importance_values,
                                             None, IO.JSON))
            del local_importance_values
            num_examples = explanation.num_examples

        num_classes = 1
        if ClassesMixin._does_quack(explanation):
            num_classes = explanation.num_classes

        if ExpectedValuesMixin._does_quack(explanation):
            module_logger.debug('Adding expected values to artifacts list')
            single_artifact_list.append((History.EXPECTED_VALUES, explanation.expected_values,
                                         None, IO.JSON))

        if GlobalExplanation._does_quack(explanation):
            global_importance_rank = explanation.global_importance_rank
            ranked_global_values = explanation.get_ranked_global_values()
            global_length = top_k if top_k is not None else len(global_importance_rank)
            global_importance_rank = global_importance_rank[:global_length]
            ranked_global_values = ranked_global_values[:global_length]

            if classification and PerClassMixin._does_quack(explanation):
                per_class_rank = np.array(explanation.per_class_rank)
                ranked_per_class_values = np.array(explanation.get_ranked_per_class_values())
                per_class_length = top_k if top_k is not None else per_class_rank.shape[1]
                per_class_rank = per_class_rank[:, :per_class_length]
                ranked_per_class_values = ranked_per_class_values[:, :per_class_length]
            if explanation.features is not None:
                ranked_global_names = explanation.get_ranked_global_names()
                if isinstance(ranked_global_names[0], str):
                    global_ordered_features = ranked_global_names
                else:
                    global_ordered_features = _sort_values(explanation.features,
                                                           global_importance_rank).tolist()
                global_ordered_features = global_ordered_features[:global_length]
                module_logger.debug('Adding global importance names to sharded artifacts list')
                sharded_artifact_list.append((History.GLOBAL_NAMES, np.array(global_ordered_features)))

                if classification and PerClassMixin._does_quack(explanation):
                    ranked_per_class_names = explanation.get_ranked_per_class_names()
                    if isinstance(ranked_per_class_names[0][0], str):
                        per_class_ordered_features = ranked_per_class_names
                    else:
                        per_class_ordered_features = _sort_feature_list_multiclass(explanation.features,
                                                                                   per_class_rank)
                    # Pick the top-k features for per class. This saves memory as the user specified
                    # top_k parameter may be lower than the size of individual per class feature importance
                    # lists.
                    pruned_class_ordered_features = []
                    for single_class_ordered_features in per_class_ordered_features:
                        pruned_class_ordered_features.append(single_class_ordered_features[:per_class_length])
                    # Convert to np array
                    per_class_ordered_features = np.array(pruned_class_ordered_features)
                    module_logger.debug('Adding per class names to sharded artifacts list')
                    sharded_artifact_list.append((History.PER_CLASS_NAMES, per_class_ordered_features))
            module_logger.debug('Adding global importance rank to sharded artifacts list')
            sharded_artifact_list.append((History.GLOBAL_RANK, np.array(global_importance_rank)))
            module_logger.debug('Adding global importance values to sharded artifacts list')
            sharded_artifact_list.append((History.GLOBAL_VALUES, np.array(ranked_global_values)))

            if classification and PerClassMixin._does_quack(explanation):
                sharded_artifact_list.append((History.PER_CLASS_RANK, np.array(per_class_rank)))
                sharded_artifact_list.append((History.PER_CLASS_VALUES, np.array(ranked_per_class_values)))

        if classification and explanation.classes is not None:
            classes = explanation.classes
            if isinstance(classes, np.ndarray):
                classes = classes.tolist()
            explanation_n_classes = len(classes)
            if classes is not None and num_classes is not None and explanation_n_classes != num_classes:
                raise DimensionMismatchException._with_error(
                    AzureMLError.create(
                        ClassNumberMismatch, actual=explanation_n_classes, expected=num_classes,
                    )
                )

            if has_local_explanation:
                local_importances_size = len(explanation._local_importance_values)
                if num_classes != local_importances_size:
                    raise DimensionMismatchException._with_error(
                        AzureMLError.create(
                            ClassNumberMismatch, actual=local_importances_size, expected=num_classes,
                        )
                    )
            module_logger.debug('Adding classes to artifacts list')
            classes_dict = {History.NUM_CLASSES: explanation_n_classes}
            single_artifact_list.append((History.CLASSES, classes, classes_dict, IO.JSON))

        module_logger.debug('Uploading artifacts to storage')
        uploader.upload_single_artifact_list(summary_object, single_artifact_list, explanation.id)
        del single_artifact_list
        module_logger.debug('Uploading sharded artifacts to storage')
        uploader.upload_sharded_artifact_list(summary_object, sharded_artifact_list, explanation.id)
        del sharded_artifact_list

        meta_dict = summary_object.get_metadata_dictionary()
        artifact_list = summary_object.get_artifacts()

        if init_dataset_id is not None:
            meta_dict[History.INIT_DATASET_ID] = init_dataset_id

        if eval_dataset_id is None and hasattr(explanation, U_EVAL_DATA) and upload_datasets:
            module_logger.debug('Uploading evaluation dataset')
            eval_dataset_id = self._upload_dataset_to_service(explanation.eval_data,
                                                              explanation,
                                                              'eval_dataset.json',
                                                              U_EVAL)

        # Note: only upload ys_pred and ys_pred_proba if eval dataset was uploaded
        if eval_dataset_id is not None and upload_datasets:
            if ys_pred_dataset_id is None and hasattr(explanation, History.EVAL_Y_PRED):
                module_logger.debug('Uploading predicted labels')
                ys_pred_dataset_id = self._upload_dataset_to_service(explanation.eval_y_predicted,
                                                                     explanation,
                                                                     'ys_pred.json',
                                                                     U_YS_PRED)

            if ys_pred_proba_dataset_id is None and hasattr(explanation, History.EVAL_Y_PRED_PROBA):
                module_logger.debug('Uploading predicted probabilities')
                ys_pred_proba_dataset_id = self._upload_dataset_to_service(explanation.eval_y_predicted_proba,
                                                                           explanation,
                                                                           'ys_pred_proba.json',
                                                                           U_YS_PRED_PROBA)

        if eval_dataset_id is not None:
            meta_dict[History.EVAL_DATASET_ID] = eval_dataset_id
        if ys_pred_dataset_id is not None:
            meta_dict[History.EVAL_Y_PRED] = ys_pred_dataset_id
        if ys_pred_proba_dataset_id is not None:
            meta_dict[History.EVAL_Y_PRED_PROBA] = ys_pred_proba_dataset_id

        if model_id is None and hasattr(explanation, History.MODEL_ID):
            model_id = explanation.model_id

        upload_dir = uploader._create_upload_dir(explanation.id)

        # add eval_data_viz to the upload
        # this is a subset of original eval_data to be stored as an artifact for viz in UI
        viz_dict = {}
        eval_data_for_viz = None
        if index_getter is not None:
            viz_dict[History.INDICES] = num_viz_points
        if is_viz_turned_on and hasattr(explanation, U_EVAL_DATA):
            eval_data_original = explanation._eval_data
            eval_data = None
            # Try to keep numpy type if possible to reduce memory usage
            if isinstance(eval_data_original, pd.DataFrame):
                eval_data = eval_data_original.values
            elif isinstance(eval_data_original, np.ndarray):
                eval_data = eval_data_original
            elif isinstance(eval_data_original, list):
                eval_data = eval_data_original
            elif sp.sparse.issparse(eval_data_original):
                sparse_eval_data = True
                module_logger.debug('Sparse evaluation data cannot be uploaded. Studio view will be reduced.')
            else:
                module_logger.debug('Data type of eval_data not recognized. Skipping viz data upload.')
            if eval_data is not None:
                if len(eval_data) > num_viz_points:
                    random_indices = None
                    if index_getter is None:
                        random_indices = sorted(np.random.choice(len(eval_data),
                                                num_viz_points, replace=False).tolist())
                        viz_dict[History.INDICES] = random_indices
                        index_getter = itemgetter(*random_indices)
                    eval_data_for_viz = list(index_getter(eval_data))
                else:
                    eval_data_for_viz = eval_data
                assert isinstance(eval_data_for_viz, list) or isinstance(eval_data_for_viz, np.ndarray)
                uploader._upload_artifact(upload_dir, History.EVAL_DATA_VIZ, eval_data_for_viz)
                temp_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, self._run.id, upload_dir,
                                                                  History.EVAL_DATA_VIZ))
                artifact_list.append({History.PREFIX: temp_path})
                viz_dict[VizData.TEST_DATA] = temp_path

        if true_ys is not None and is_viz_turned_on:
            ys_data = None
            if isinstance(true_ys, pd.DataFrame):
                ys_data = true_ys.values.tolist()
            elif isinstance(true_ys, np.ndarray):
                ys_data = true_ys.tolist()
            elif isinstance(true_ys, list):
                ys_data = true_ys
            else:
                module_logger.debug('Data type of true_ys not recognized and cannot be uploaded.')
            if isinstance(true_ys[0], list):
                raise DimensionMismatchException._with_error(
                    AzureMLError.create(
                        InvalidYTrueDimension, target="true_ys"
                    )
                )
            if ys_data is not None:
                if classification and explanation.classes is not None:
                    ys_data = _translate_y_to_indices(ys_data, classes)

                if index_getter is None:
                    if len(ys_data) > num_viz_points:
                        random_indices = sorted(np.random.choice(len(ys_data),
                                                num_viz_points, replace=False).tolist())
                        viz_dict[VizData.INDICES] = random_indices
                        index_getter = itemgetter(*random_indices)
                        true_ys_for_viz = list(index_getter(ys_data))
                    else:
                        true_ys_for_viz = ys_data
                else:
                    true_ys_for_viz = list(index_getter(ys_data))

                if eval_data_for_viz is not None and len(true_ys_for_viz) != len(eval_data_for_viz):
                    raise DimensionMismatchException._with_error(
                        AzureMLError.create(
                            EvalDataMismatch, X_length=len(eval_data_for_viz), y_length=len(true_ys_for_viz),
                        )
                    )

                uploader._upload_artifact(upload_dir, History.TRUE_YS_VIZ, true_ys_for_viz)
                temp_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, self._run.id, upload_dir,
                                                                  History.TRUE_YS_VIZ))
                artifact_list.append({History.PREFIX: temp_path})
                viz_dict[VizData.TRUE_Y] = temp_path

        y_pred_attr = hasattr(explanation, History.EVAL_Y_PRED)
        has_eval_y_predicted = y_pred_attr and explanation.eval_y_predicted is not None
        if is_viz_turned_on and has_eval_y_predicted:
            y_pred = explanation.eval_y_predicted
            if isinstance(y_pred, np.ndarray):
                y_pred = y_pred.tolist()
            if classification and explanation.classes is not None:
                y_pred = _translate_y_to_indices(y_pred, classes)
            if index_getter is None:
                if len(y_pred) > num_viz_points:
                    random_indices = sorted(np.random.choice(len(y_pred),
                                            num_viz_points, replace=False).tolist())
                    viz_dict[History.INDICES] = random_indices
                    index_getter = itemgetter(*random_indices)
                    ys_pred_for_viz = list(index_getter(y_pred))
                else:
                    ys_pred_for_viz = y_pred
            else:
                ys_pred_for_viz = list(index_getter(y_pred))
            uploader._upload_artifact(upload_dir, History.YS_PRED_VIZ, ys_pred_for_viz)
            temp_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, self._run.id, upload_dir,
                                                              History.YS_PRED_VIZ))
            artifact_list.append({History.PREFIX: temp_path})
            viz_dict[VizData.PREDICTED_Y] = temp_path

        y_pred_proba_attr = hasattr(explanation, History.EVAL_Y_PRED_PROBA)
        has_eval_y_predicted_proba = y_pred_proba_attr and explanation.eval_y_predicted_proba is not None
        if is_viz_turned_on and has_eval_y_predicted_proba:
            y_pred_proba = explanation.eval_y_predicted_proba
            y_pred_proba_size = len(y_pred_proba[0])
            if y_pred_proba_size != explanation.num_classes:
                raise DimensionMismatchException._with_error(
                    AzureMLError.create(
                        ClassNumberMismatch, actual=y_pred_proba_size, expected=explanation.num_classes,
                    )
                )
            if isinstance(y_pred_proba, np.ndarray):
                y_pred_proba = y_pred_proba.tolist()
            if index_getter is None:
                if len(y_pred_proba) > num_viz_points:
                    random_indices = sorted(np.random.choice(len(y_pred_proba),
                                            num_viz_points, replace=False).tolist())
                    viz_dict[History.INDICES] = random_indices
                    index_getter = itemgetter(*random_indices)
                    ys_pred_proba_for_viz = list(index_getter(y_pred_proba))
                else:
                    ys_pred_proba_for_viz = y_pred_proba
            else:
                ys_pred_proba_for_viz = list(index_getter(y_pred_proba))
            uploader._upload_artifact(upload_dir, History.YS_PRED_PROBA_VIZ, ys_pred_proba_for_viz)
            temp_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, self._run.id, upload_dir,
                                                              History.YS_PRED_PROBA_VIZ))
            artifact_list.append({History.PREFIX: temp_path})
            viz_dict[VizData.PROBABILITY_Y] = temp_path

        is_local_attr = hasattr(explanation, U_LOCAL_IMPORTANCE_VALUES)
        enable_local_viz = False
        # Note: we shouldn't be uploading sparse local importance values currently because viz can't handle it
        if is_local_attr:
            enable_local_viz = explanation._local_importance_values is not None and not explanation.is_local_sparse
        if is_viz_turned_on:
            if enable_local_viz:
                if index_getter is None:
                    temp_path = None
                    for prefix_dict in artifact_list:
                        if History.LOCAL_IMPORTANCE_VALUES in prefix_dict[History.PREFIX]:
                            temp_path = prefix_dict[History.PREFIX]
                            break
                else:
                    local_vals_for_viz = self._get_local_importance_vals_for_viz(index_getter, explanation)
                    uploader._upload_artifact(upload_dir, History.LOCAL_IMPORTANCE_VIZ, local_vals_for_viz)
                    temp_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, self._run.id, upload_dir,
                                                                      History.LOCAL_IMPORTANCE_VIZ))
                    artifact_list.append({History.PREFIX: temp_path})
                viz_dict[VizData.PRECOMPUTED_LOCAL_FEATURE_IMPORTANCE_SCORES] = temp_path
            else:
                temp_path = None
                temp_path_names = None
                for prefix_dict in artifact_list:
                    # Note: we only want the first one of each, corresponding to sharded artifact 0
                    # we can break loop once we've caught both of them
                    if History.GLOBAL_VALUES in prefix_dict[History.PREFIX] and temp_path is None:
                        temp_path = prefix_dict[History.PREFIX]
                        if temp_path_names is not None:
                            break
                    if History.GLOBAL_NAMES in prefix_dict[History.PREFIX] and temp_path_names is None:
                        temp_path_names = prefix_dict[History.PREFIX]
                        if temp_path is not None:
                            break
                if temp_path is not None and temp_path_names is not None:
                    viz_dict[VizData.PRECOMPUTED_GLOBAL_FEATURE_IMPORTANCE_SCORES] = temp_path
                    viz_dict[VizData.PRECOMPUTED_GLOBAL_FEATURE_IMPORTANCE_NAMES] = temp_path_names

        if is_viz_turned_on:
            if History.FEATURES in meta_dict:
                features_path = None
                for prefix_dict in artifact_list:
                    if History.FEATURES in prefix_dict[History.PREFIX]:
                        features_path = prefix_dict[History.PREFIX]
                viz_dict[VizData.DATA_SUMMARY_FEATURE_NAMES] = features_path
            if History.CLASSES in meta_dict:
                classes_path = None
                for prefix_dict in artifact_list:
                    if History.CLASSES in prefix_dict[History.PREFIX]:
                        classes_path = prefix_dict[History.PREFIX]
                viz_dict[VizData.DATA_SUMMARY_CLASS_NAMES] = classes_path
            if History.EXPECTED_VALUES in meta_dict:
                expected_path = None
                for prefix_dict in artifact_list:
                    if History.EXPECTED_VALUES in prefix_dict[History.PREFIX]:
                        expected_path = prefix_dict[History.PREFIX]
                if not enable_local_viz:
                    viz_dict[VizData.PRECOMPUTED_GLOBAL_FEATURE_IMPORTANCE_INTERCEPT] = expected_path
                else:
                    viz_dict[VizData.PRECOMPUTED_LOCAL_FEATURE_IMPORTANCE_INTERCEPT] = expected_path

        # upload viz artifact
        if is_viz_turned_on:
            module_logger.debug('Uploading visualization data')
            uploader._upload_artifact(upload_dir, History.VISUALIZATION_DICT, viz_dict)
            viz_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, self._run.id, upload_dir,
                                                             History.VISUALIZATION_DICT))
            artifact_list.append({History.PREFIX: viz_path})
            meta_dict[History.VISUALIZATION_DICT] = viz_path

        # upload rich metadata information
        module_logger.debug('Uploading explanation metadata')
        uploader._upload_artifact(upload_dir, History.RICH_METADATA, meta_dict)
        metadata_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, self._run.id, upload_dir,
                                                              History.RICH_METADATA))
        artifact_list.append({History.PREFIX: metadata_path})

        # Allow derived classes to upload anything they need
        module_logger.debug("Uploading any extra data")
        extra_artifacts = self._extra_artifact_uploads(
            explanation,
            max_num_blocks,
            block_size,
            top_k,
            comment,
            init_dataset_id,
            eval_dataset_id,
            ys_pred_dataset_id,
            ys_pred_proba_dataset_id,
            upload_datasets,
            model_id,
            true_ys,
            visualization_points
        )
        artifact_list = artifact_list + extra_artifacts

        # set env variable to increase flush task queue, to prevent error:
        # "Failed to flush task queue within 300 seconds"
        os.environ['AZUREML_RUN_KILL_SIGNAL_TIMEOUT_SEC'] = '3600'
        self._run.upload_folder(upload_dir, upload_dir, datastore_name=self._datastore_name)

        experiment_name = None
        experiment_id = None
        try:
            experiment_id = self._run.experiment.id
        except AttributeError:
            try:
                experiment_name = self._run.experiment.name
            except AttributeError:
                raise NoExperimentNameOrIdException._with_error(AzureMLError.create(ExperimentMissingIdAndName))

        prop_dict = {
            History.TYPE: History.EXPLANATION,
            ExplainType.MODEL: ExplainType.CLASSIFICATION if classification else ExplainType.REGRESSION,
            ExplainType.DATA: explainer_type,
            ExplainType.EXPLAIN: explanation.method,
            ExplainType.MODEL_TASK: explanation.model_task,
            ExplainType.METHOD: explanation.method,
            ExplainType.MODEL_CLASS: explanation.model_type,
            ExplainType.IS_RAW: is_raw,
            ExplainType.IS_ENG: is_engineered,
            History.METADATA_ARTIFACT: metadata_path,
            History.VERSION: History.EXPLANATION_ASSET_TYPE_V8,
            History.EXPLANATION_ID: explanation.id,
            History.COMMENT: comment,
            History.GLOBAL: GlobalExplanation._does_quack(explanation),
            History.LOCAL: has_local_explanation,
            History.INIT_DATASET_ID: init_dataset_id,
            History.EVAL_DATASET_ID: eval_dataset_id,
            History.EVAL_Y_PRED: ys_pred_dataset_id,
            History.EVAL_Y_PRED_PROBA: ys_pred_proba_dataset_id,
            History.NUM_CLASSES: num_classes,
            History.NUM_EXAMPLES: num_examples,
            History.NUM_FEATURES: num_features
        }

        if experiment_name is not None:
            prop_dict[History.EXPERIMENT_NAME] = experiment_name
        if experiment_id is not None:
            prop_dict[History.EXPERIMENT_ID] = experiment_id
        if model_id is not None:
            prop_dict[History.MODEL_ID] = model_id
        if sparse_eval_data:
            prop_dict[History.SPARSE_DATA] = True

        # Hook to modify the properties if needed
        self._update_asset_properties(prop_dict)

        module_logger.debug('Creating explanation asset')
        asset = assets_client.create_asset(
            History.EXPLANATION_ASSET,
            artifact_list,
            run_id=self._run.id,
            metadata_dict={},
            properties=prop_dict,
            asset_type=self._get_asset_type()
        )
        self._run.tag(RunPropertiesAndTags.MODEL_EXPLANATION_TAG, 'True')
        return asset.id

    def _update_asset_properties(self, prop_dict: Dict):
        """Modify the properties of the about-to-be-created Asset.

        This can be overridden in derived classes if needed.
        """
        pass

    def _get_asset_type(self) -> str:
        """Return the type of Asset to be created.

        This can be overridden in derived classes if needed.
        """
        return History.ASSET_TYPE

    def _extra_artifact_uploads(
            self,
            explanation,
            max_num_blocks,
            block_size,
            top_k,
            comment,
            init_dataset_id,
            eval_dataset_id,
            ys_pred_dataset_id,
            ys_pred_proba_dataset_id,
            upload_datasets,
            model_id,
            true_ys,
            visualization_points) -> List[Dict[str, str]]:
        """Upload extra artifacts

        Derived classes can override this if they want to add to the uploads
        """
        return []

    def _get_local_importance_vals_for_viz(self, index_getter, explanation):
        """Gets the samples local importance values used for visualization.

        :param index_getter: The sampling function used to reduce the local importance values for visualization.
        :type index_getter: itemgetter
        :param explanation: The explanation to get the local importance values from for getting the json file size.
        :type explanation: interpret_community.explanation.explanation.BaseExplanation
        :return: The local importance values used for visualization.
        :rtype: list[list[float]] or list[float]
        """
        if ClassesMixin._does_quack(explanation):
            local_vals = explanation._local_importance_values
            local_vals_for_viz = [list(index_getter(class_vals)) for class_vals in local_vals]
        else:
            local_vals_for_viz = list(index_getter(explanation._local_importance_values))
        return local_vals_for_viz

    def _get_num_viz_points(self, visualization_points, explanation):
        """Cuts the number of local importance points such that the memory is less than the LOCAL_IMP_SIZE_LIMIT.

        :param visualization_points: The upper bound on the number of points that will be available for
            visualization in the web UI
        :type visualization_points: int
        :param explanation: The explanation to get the local importance values from for estimating the size.
        :type explanation: interpret_community.explanation.explanation.BaseExplanation
        :return: The number of points to sample down to.
        :rtype: int
        """
        sampled_viz_points = min(visualization_points, explanation.num_examples)
        ordered_indexes = list(range(sampled_viz_points))
        index_getter = itemgetter(*ordered_indexes)
        local_vals_for_viz = self._get_local_importance_vals_for_viz(index_getter, explanation)
        local_importance_size = np.array(local_vals_for_viz).nbytes
        if local_importance_size > LOCAL_IMP_SIZE_LIMIT:
            sampled_viz_points = int(sampled_viz_points / (local_importance_size / LOCAL_IMP_SIZE_LIMIT))
        return sampled_viz_points

    def download_model_explanation(self, explanation_id=None, top_k=None, comment=None, raw=None, engineered=None):
        """Download a model explanation that has been stored in run history.

        :param explanation_id: If specified, tries to download the asset from the run with the given explanation ID.
            If unspecified, returns the most recently uploaded explanation.
        :type explanation_id: str
        :param top_k: If specified, limit the ordered data returned to the most important features and values.
            If this is the case, global_importance_values and per_class_values will contain the top k sorted values
            instead of the usual full list of unsorted values.
        :type top_k: int
        :param comment: A string used to filter explanations based on the strings they were uploaded with. Requires an
            exact match. If multiple explanations share this string, the most recent will be returned.
        :type comment: str
        :param raw: If True or False, explanations will be filtered based on whether they are raw or not. If nothing
            is specified, this filter will not be applied.
        :type raw: bool or None
        :param engineered: If True or False, explanations will be filtered based on whether they are engineered or
            not. If nothing is specified, this filter will not be applied.
        :type engineered: bool or None
        :return: The explanation as it was uploaded to run history
        :rtype: interpret_community.explanation.explanation.BaseExplanation
        """
        if top_k is None:
            module_logger.debug('Downloading model explanation as batch')
            return self._download_explanation_as_batch(explanation_id=explanation_id, comment=comment, raw=raw,
                                                       engineered=engineered)
        else:
            module_logger.debug('Downloading explanations with top k features')
            return self._download_explanation_top_k(explanation_id=explanation_id, top_k=top_k, comment=comment,
                                                    raw=raw, engineered=engineered)

    def _download_explanation_as_batch(self, explanation_id=None, comment=None, raw=None, engineered=None):
        """Get an explanation from run history.

        :param explanation_id: If specified, tries to download the asset from the run with the given explanation ID.
            If unspecified, returns the most recently uploaded explanation.
        :type explanation_id: str
        :param comment: A string used to filter explanations based on the strings they were uploaded with. Requires an
            exact match. If multiple explanations share this string, the most recent will be returned.
        :type comment: str
        :param raw: If True or False, explanations will be filtered based on whether they are raw or not. If nothing
            is specified, this filter will not be applied.
        :type raw: bool or None
        :param engineered: If True or False, explanations will be filtered based on whether they are engineered or
            not. If nothing is specified, this filter will not be applied.
        :type engineered: bool or None
        :return: The explanation as it was uploaded to run history
        :rtype: interpret_community.explanation.explanation.BaseExplanation
        """
        kwargs = {}
        module_logger.debug('Creating download directory')
        download_dir = _create_download_dir()
        module_logger.debug('Creating assets client')
        assets_client = AssetsClient(self._run.experiment.workspace.service_context)
        module_logger.debug('Retrieving explanation assets')

        mli_extension = '.interpret.json'

        if explanation_id is not None:
            properties = {History.EXPLANATION_ID: explanation_id}
            explanation_list = list(assets_client.list_assets_with_query(run_id=self._run.id,
                                                                         properties=properties,
                                                                         asset_type=self._get_asset_type()))
            if len(explanation_list) == 0:
                # June 2020
                explanation_list = assets_client.list_assets_by_properties_run_id_name(self._run.id,
                                                                                       History.EXPLANATION_ASSET,
                                                                                       properties)
            if len(explanation_list) > 0:
                explanation_asset = explanation_list[0]
            else:
                error_string = "Could not find an explanation asset with id {}".format(explanation_id)
                module_logger.debug(error_string)
                raise ExplanationNotFoundException._with_error(
                    AzureMLError.create(
                        ExplanationNotFound, explanation_id=explanation_id,
                    )
                )

            error_string = 'Explanation asset with id {} does not have {}={}'
            if comment is not None:
                error_string = error_string.format(explanation_id, 'comment', comment)
                if History.COMMENT in explanation_asset.properties:
                    if explanation_asset.properties.get(History.COMMENT, None) != comment:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='comment', filter_value=comment,
                            )
                        )
                else:
                    if explanation_asset.meta.get(History.COMMENT, None) != comment:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='comment', filter_value=comment,
                            )
                        )
            if raw is not None:
                error_string = error_string.format(explanation_id, 'raw', raw)
                if ExplainType.IS_RAW in explanation_asset.properties:
                    if (explanation_asset.properties.get(ExplainType.IS_RAW, '').lower() == TRUE.lower()) != raw:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='raw', filter_value=raw,
                            )
                        )
                else:
                    if (explanation_asset.meta[ExplainType.IS_RAW].lower() == TRUE.lower()) != raw:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='raw', filter_value=raw,
                            )
                        )
            elif engineered is not None:
                error_string = error_string.format(explanation_id, 'engineered', engineered)
                if ExplainType.IS_ENG in explanation_asset.properties:
                    is_eng_asset = explanation_asset.properties.get(ExplainType.IS_ENG, '').lower() == TRUE.lower()
                    if is_eng_asset != engineered:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='engineered', filter_value=engineered,
                            )
                        )
                else:
                    if (explanation_asset.meta[ExplainType.IS_ENG].lower() == TRUE.lower()) != engineered:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='engineered', filter_value=engineered,
                            )
                        )
        else:
            # first try property filtering
            properties = {}
            if comment is not None:
                properties[History.COMMENT] = comment
            if raw is not None:
                properties[ExplainType.IS_RAW] = str(raw)
            if engineered is not None:
                properties[ExplainType.IS_ENG] = str(engineered)
            explanation_list = list(assets_client.list_assets_with_query(run_id=self._run.id,
                                                                         properties=properties,
                                                                         asset_type=self._get_asset_type()))
            if len(explanation_list) == 0:
                # June 2020
                explanation_list = assets_client.list_assets_by_properties_run_id_name(self._run.id,
                                                                                       History.EXPLANATION_ASSET,
                                                                                       properties)
            if len(explanation_list) == 0:
                # May 2020
                explanation_assets = assets_client.list_assets_with_query(run_id=self._run.id,
                                                                          name=History.EXPLANATION_ASSET)
                explanation_assets = list(filter(lambda x: len(x.meta.keys()) > 0, explanation_assets))
                if comment is not None:
                    explanation_assets = list(filter(lambda x: x.meta[History.COMMENT] == comment,
                                                     explanation_assets))
                if raw is not None:
                    def exp_filter(asset):
                        result = (asset.meta[ExplainType.IS_RAW].lower() == TRUE.lower()) == raw
                        return result
                    explanation_assets = list(filter(exp_filter, explanation_assets))
                elif engineered is not None:
                    filtered = filter(lambda x: (x.meta[ExplainType.IS_ENG].lower() == TRUE.lower()) == engineered,
                                      explanation_assets)
                    explanation_assets = list(filtered)
                if len(explanation_assets) == 0:
                    raise ExplanationNotFoundException._with_error(
                        AzureMLError.create(
                            ExplanationFiltersNotFound, explanation_id=explanation_id,
                            filter_names=['comment', 'raw'],
                        )
                    )
            else:
                explanation_assets = explanation_list
            # sort assets by upload time and return latest
            explanation_assets = sorted(explanation_assets, key=lambda asset: asset.created_time)
            explanation_asset = explanation_assets[-1]
            properties = explanation_asset.properties
            if History.EXPLANATION_ID in properties:
                explanation_id = properties[History.EXPLANATION_ID]
            elif History.EXPLANATION_ID in explanation_asset.meta:
                explanation_id = explanation_asset.meta[History.EXPLANATION_ID]

        # everything that might be available from the asset for construction an explanation
        local_importance_vals = None

        # back compat as of March 2019
        is_v2_release_asset = History.VERSION_TYPE in explanation_asset.properties

        if is_v2_release_asset:
            version = explanation_asset.properties[History.VERSION_TYPE]
            is_under_v3_asset = True
        elif History.VERSION in explanation_asset.properties:
            version = explanation_asset.properties[History.VERSION]
            is_under_v3_asset = False
        else:
            version = explanation_asset.meta[History.VERSION]
            # because it can't be v2 release here
            is_under_v3_asset = version == History.EXPLANATION_ASSET_TYPE_V2
        is_under_v4_asset = is_under_v3_asset or version == History.EXPLANATION_ASSET_TYPE_V3
        is_under_v5_asset = is_under_v4_asset or version == History.EXPLANATION_ASSET_TYPE_V4
        is_under_v7_asset = (is_under_v5_asset or version == History.EXPLANATION_ASSET_TYPE_V5
                             or version == History.EXPLANATION_ASSET_TYPE_V6)
        is_under_v8_asset = is_under_v7_asset or version == History.EXPLANATION_ASSET_TYPE_V7
        if is_under_v5_asset:
            mli_extension = '.json'
        file_dict = _download_artifacts(self._run, download_dir, mli_extension, explanation_id=explanation_id)

        module_logger.debug('Explanation asset is version {}'.format(version))
        if ExplainType.EXPLAIN in explanation_asset.properties:
            explanation_method = explanation_asset.properties[ExplainType.EXPLAIN]
        elif ExplainType.EXPLAIN in explanation_asset.meta:
            # backcompat May 2020
            explanation_method = explanation_asset.meta[ExplainType.EXPLAIN]
        else:
            # backwards compatibilty as of February 2019
            explanation_method = ExplainType.SHAP
        storage_metadata = _load_artifact(file_dict[History.RICH_METADATA] + mli_extension)
        # classification and local importances are stored differently in non v1 assets
        if ExplainType.MODEL in explanation_asset.properties:
            classification = explanation_asset.properties[ExplainType.MODEL] == ExplainType.CLASSIFICATION
        elif ExplainType.MODEL in explanation_asset.meta:
            # May 2020
            classification = explanation_asset.meta[ExplainType.MODEL] == ExplainType.CLASSIFICATION
        elif is_v2_release_asset:
            classification = History.PER_CLASS_VALUES in storage_metadata
        if History.LOCAL_IMPORTANCE_VALUES in file_dict:
            module_logger.debug('Downloading local importance values from >v2')
            local_importance_filename = file_dict[History.LOCAL_IMPORTANCE_VALUES] + mli_extension
            local_importance_vals = np.array(_load_artifact(local_importance_filename))
        elif History.LOCAL_IMPORTANCE_VALUES_SPARSE in file_dict:
            module_logger.debug('Downloading sparse local importance values')
            local_importance_filename = file_dict[History.LOCAL_IMPORTANCE_VALUES_SPARSE] + mli_extension
            local_vals_sparse = _load_artifact(local_importance_filename)
            local_importance_vals = self._convert_artifact_to_sparse_local(local_vals_sparse)
        elif is_v2_release_asset:
            module_logger.debug('Downloading local importance values from release v2')
            local_importance_vals = np.array(_load_artifact(file_dict[BackCompat.SHAP_VALUES] + mli_extension))
        if History.FEATURES in file_dict:
            kwargs[ExplainParams.FEATURES] = np.array(_load_artifact(file_dict[History.FEATURES] + mli_extension))
        else:
            try:
                # v2 release asset back compat as of March 2019
                kwargs[ExplainParams.FEATURES] = _download_artifact(self._run, download_dir, History.FEATURES,
                                                                    mli_extension, explanation_id=explanation_id)
            except UserErrorException:
                kwargs[ExplainParams.FEATURES] = None

        if not is_under_v8_asset:
            kwargs[ExplainParams.MODEL_TYPE] = explanation_asset.properties[ExplainType.MODEL_CLASS]
            explanation_method = explanation_asset.properties[ExplainType.METHOD]
            is_raw = explanation_asset.properties.get(ExplainType.IS_RAW, FALSE).lower() == TRUE.lower()
            kwargs[ExplainParams.IS_RAW] = is_raw
            is_eng = explanation_asset.properties.get(ExplainType.IS_ENG, FALSE).lower() == TRUE.lower()
            kwargs[ExplainParams.IS_ENG] = is_eng
            if History.INIT_DATASET_ID in storage_metadata:
                kwargs[History.INIT_DATA] = storage_metadata[History.INIT_DATASET_ID]
            if History.EVAL_DATASET_ID in storage_metadata:
                kwargs[History.EVAL_DATA] = storage_metadata[History.EVAL_DATASET_ID]
            if History.EVAL_Y_PRED in storage_metadata:
                kwargs[History.EVAL_Y_PRED] = storage_metadata[History.EVAL_Y_PRED]
            if History.EVAL_Y_PRED_PROBA in storage_metadata:
                kwargs[History.EVAL_Y_PRED_PROBA] = storage_metadata[History.EVAL_Y_PRED_PROBA]
            if History.MODEL_ID in explanation_asset.properties:
                kwargs[History.MODEL_ID] = explanation_asset.properties[History.MODEL_ID]
            if History.NUM_FEATURES in explanation_asset.properties:
                num_features = explanation_asset.properties[History.NUM_FEATURES]
                kwargs[History.NUM_FEATURES] = int(num_features) if isinstance(num_features, str) else num_features
        elif not is_under_v4_asset:
            # May 2020
            kwargs[ExplainParams.MODEL_TYPE] = explanation_asset.meta[ExplainType.MODEL_CLASS]
            explanation_method = explanation_asset.meta[ExplainType.METHOD]
            is_raw = explanation_asset.meta.get(ExplainType.IS_RAW, FALSE).lower() == TRUE.lower()
            kwargs[ExplainParams.IS_RAW] = is_raw
            is_eng = explanation_asset.meta.get(ExplainType.IS_ENG, FALSE).lower() == TRUE.lower()
            kwargs[ExplainParams.IS_ENG] = is_eng
            if History.INIT_DATASET_ID in storage_metadata:
                kwargs[History.INIT_DATA] = storage_metadata[History.INIT_DATASET_ID]
            if History.EVAL_DATASET_ID in storage_metadata:
                kwargs[History.EVAL_DATA] = storage_metadata[History.EVAL_DATASET_ID]
            if History.EVAL_Y_PRED in storage_metadata:
                kwargs[History.EVAL_Y_PRED] = storage_metadata[History.EVAL_Y_PRED]
            if History.EVAL_Y_PRED_PROBA in storage_metadata:
                kwargs[History.EVAL_Y_PRED_PROBA] = storage_metadata[History.EVAL_Y_PRED_PROBA]
            if History.MODEL_ID in explanation_asset.meta:
                kwargs[History.MODEL_ID] = explanation_asset.meta[History.MODEL_ID]
            if History.NUM_FEATURES in explanation_asset.meta:
                num_features = explanation_asset.meta[History.NUM_FEATURES]
                kwargs[History.NUM_FEATURES] = int(num_features) if isinstance(num_features, str) else num_features

        kwargs[ExplainParams.METHOD] = explanation_method
        kwargs[ExplainParams.CLASSIFICATION] = classification
        if classification:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.CLASSIFICATION
        else:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.REGRESSION
        if History.EXPECTED_VALUES in file_dict or is_v2_release_asset:
            module_logger.debug('Downloading expected values')
            expected_values_artifact = _load_artifact(file_dict[History.EXPECTED_VALUES] + mli_extension)
            kwargs[ExplainParams.EXPECTED_VALUES] = np.array(expected_values_artifact)

        if local_importance_vals is not None:
            module_logger.debug('Creating local explanation')
            local_explanation = _create_local_explanation(local_importance_values=local_importance_vals,
                                                          explanation_id=explanation_id,
                                                          **kwargs)
            kwargs[ExplainParams.LOCAL_EXPLANATION] = local_explanation
            no_short_global_values = History.GLOBAL_VALUES not in storage_metadata
            # back compat April 2020
            if no_short_global_values and BackCompat.GLOBAL_IMPORTANCE_VALUES not in storage_metadata:
                module_logger.debug('Global importance values not found, returning local explanation')
                return local_explanation

        # Include everything available on storage metadata
        if History.CLASSES in storage_metadata:
            module_logger.debug('Downloading class names')
            if History.NUM_CLASSES in explanation_asset.properties:
                num_classes = explanation_asset.properties[History.NUM_CLASSES]
                kwargs[History.NUM_CLASSES] = int(num_classes) if isinstance(num_classes, str) else num_classes
            elif History.NUM_CLASSES in explanation_asset.meta:
                num_classes = explanation_asset.meta[History.NUM_CLASSES]
                kwargs[History.NUM_CLASSES] = int(num_classes) if isinstance(num_classes, str) else num_classes
            try:
                # v2 release asset back compat as of March 2019
                # TODO
                kwargs[ExplainParams.CLASSES] = _download_artifact(self._run, download_dir, History.CLASSES,
                                                                   mli_extension, explanation_id=explanation_id)
            except UserErrorException:
                kwargs[ExplainParams.CLASSES] = None

        download_list = [
            History.GLOBAL_NAMES,
            History.GLOBAL_RANK,
            History.GLOBAL_VALUES,
            History.PER_CLASS_NAMES,
            History.PER_CLASS_RANK,
            History.PER_CLASS_VALUES,
            # back compat April 2020
            BackCompat.GLOBAL_IMPORTANCE_NAMES,
            BackCompat.GLOBAL_IMPORTANCE_RANK,
            BackCompat.GLOBAL_IMPORTANCE_VALUES
        ]
        module_logger.debug('Downloading sharded data')
        downloads = _load_sharded_data_from_list(download_list, storage_metadata, download_dir, file_dict,
                                                 mli_extension, explanation_id=explanation_id)

        if History.GLOBAL_RANK in downloads:
            global_rank = downloads[History.GLOBAL_RANK]
            global_values = downloads[History.GLOBAL_VALUES]
        else:
            # back compat April 2020
            global_rank = downloads[BackCompat.GLOBAL_IMPORTANCE_RANK]
            global_values = downloads[BackCompat.GLOBAL_IMPORTANCE_VALUES]
        kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK] = global_rank

        if History.PER_CLASS_RANK in file_dict:
            kwargs[History.PER_CLASS_RANK] = downloads[History.PER_CLASS_RANK]

        global_rank_length = len(kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK])
        # check that the full explanation is available in run history so that it can be unsorted
        if kwargs[History.FEATURES] is not None:
            full_available = global_rank_length == len(kwargs[History.FEATURES])
        else:
            full_available = max(kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK]) == global_rank_length - 1

        if full_available:
            # if we retrieve the whole explanation, we can reconstruct unsorted value order
            global_importance_values_unsorted = _unsort_1d(global_values, global_rank)
            kwargs[ExplainParams.GLOBAL_IMPORTANCE_VALUES] = global_importance_values_unsorted

            if History.PER_CLASS_RANK in file_dict:
                per_class_importance_values_unsorted = _unsort_2d(downloads[History.PER_CLASS_VALUES],
                                                                  downloads[History.PER_CLASS_RANK])
                kwargs[History.PER_CLASS_VALUES] = per_class_importance_values_unsorted
        else:
            # if we only retrieve top k, unsorted values cannot be fully reconstructed
            if History.GLOBAL_NAMES in file_dict:
                kwargs[History.RANKED_GLOBAL_NAMES] = downloads[History.GLOBAL_NAMES]
            if BackCompat.GLOBAL_IMPORTANCE_NAMES in file_dict:
                kwargs[History.RANKED_GLOBAL_NAMES] = downloads[BackCompat.GLOBAL_IMPORTANCE_NAMES]
            kwargs[History.RANKED_GLOBAL_VALUES] = global_values

            if History.PER_CLASS_RANK in file_dict:
                if History.PER_CLASS_NAMES in file_dict:
                    kwargs[History.RANKED_PER_CLASS_NAMES] = downloads[History.PER_CLASS_NAMES]
                kwargs[History.RANKED_PER_CLASS_VALUES] = downloads[History.PER_CLASS_VALUES]
        module_logger.debug('Creating global explanation from downloaded explanation data')
        return _create_global_explanation(explanation_id=explanation_id, **kwargs)

    def _download_explanation_top_k(self, explanation_id=None, top_k=None, comment=None, raw=None, engineered=None):
        """Get an explanation from run history.

        :param explanation_id: If specified, tries to download the asset from the run with the given explanation ID.
            If unspecified, returns the most recently uploaded explanation.
        :type explanation_id: str
        :param top_k: If specified, limit the ordered data returned to the most important features and values.
            If this is the case, global_importance_values and per_class_values will contain the top k sorted values
            instead of the usual full list of unsorted values.
        :type top_k: int
        :param comment: A string used to filter explanations based on the strings they were uploaded with. Requires an
            exact match. If multiple explanations share this string, the most recent will be returned.
        :type comment: str
        :param raw: If True or False, explanations will be filtered based on whether they are raw or not. If nothing
            is specified, this filter will not be applied.
        :type raw: bool or None
        :param engineered: If True or False, explanations will be filtered based on whether they are engineered or
            not. If nothing is specified, this filter will not be applied.
        :type engineered: bool or None
        :return: The explanation as it was uploaded to run history
        :rtype: interpret_community.explanation.explanation.BaseExplanation
        """
        kwargs = {}
        module_logger.debug('Creating download directory')
        download_dir = _create_download_dir()
        module_logger.debug('Creating assets client')
        assets_client = AssetsClient(self._run.experiment.workspace.service_context)
        module_logger.debug('Retrieving explanation assets')

        mli_extension = '.interpret.json'

        if explanation_id is not None:
            properties = {History.EXPLANATION_ID: explanation_id}
            properties = {History.EXPLANATION_ID: explanation_id}
            explanation_list = list(assets_client.list_assets_with_query(run_id=self._run.id,
                                                                         properties=properties,
                                                                         asset_type=self._get_asset_type()))
            if len(explanation_list) == 0:
                # June 2020
                explanation_list = assets_client.list_assets_by_properties_run_id_name(self._run.id,
                                                                                       History.EXPLANATION_ASSET,
                                                                                       properties)
            if len(explanation_list) > 0:
                explanation_asset = explanation_list[0]
            else:
                error_string = 'Could not find an explanation asset with id ' + explanation_id
                module_logger.debug(error_string)
                raise ExplanationNotFoundException._with_error(
                    AzureMLError.create(
                        ExplanationNotFound, explanation_id=explanation_id,
                    )
                )

            error_string = 'Explanation asset with id {} does not have {}={}'
            if comment is not None:
                error_string = error_string.format(explanation_id, 'comment', comment)
                if History.COMMENT in explanation_asset.properties:
                    if explanation_asset.properties.get(History.COMMENT, None) != comment:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='comment', filter_value=comment,
                            )
                        )
                else:
                    if explanation_asset.meta.get(History.COMMENT, None) != comment:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='comment', filter_value=comment,
                            )
                        )
            if raw is not None:
                error_string = error_string.format(explanation_id, 'raw', raw)
                if ExplainType.IS_RAW in explanation_asset.properties:
                    if (explanation_asset.properties.get(ExplainType.IS_RAW, '').lower() == TRUE.lower()) != raw:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='raw', filter_value=raw,
                            )
                        )
                else:
                    if (explanation_asset.meta[ExplainType.IS_RAW].lower() == TRUE.lower()) != raw:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='raw', filter_value=raw,
                            )
                        )
            elif engineered is not None:
                error_string = error_string.format(explanation_id, 'engineered', engineered)
                if ExplainType.IS_ENG in explanation_asset.properties:
                    is_eng_asset = explanation_asset.properties.get(ExplainType.IS_ENG, '').lower() == TRUE.lower()
                    if is_eng_asset != engineered:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='engineered', filter_value=engineered,
                            )
                        )
                else:
                    if (explanation_asset.meta[ExplainType.IS_ENG].lower() == TRUE.lower()) != engineered:
                        module_logger.debug(error_string)
                        raise ExplanationNotFoundException._with_error(
                            AzureMLError.create(
                                ExplanationFilterNotFound, explanation_id=explanation_id,
                                filter_name='engineered', filter_value=engineered,
                            )
                        )
        else:
            # first try property filtering
            properties = {}
            if comment is not None:
                properties[History.COMMENT] = comment
            if raw is not None:
                properties[ExplainType.IS_RAW] = str(raw)
            if engineered is not None:
                properties[ExplainType.IS_ENG] = str(engineered)
            explanation_list = list(assets_client.list_assets_with_query(run_id=self._run.id,
                                                                         properties=properties,
                                                                         asset_type=self._get_asset_type()))
            if len(explanation_list) == 0:
                # June 2020
                explanation_list = assets_client.list_assets_by_properties_run_id_name(self._run.id,
                                                                                       History.EXPLANATION_ASSET,
                                                                                       properties)
            if len(explanation_list) == 0:
                # May 2020
                explanation_assets = assets_client.list_assets_with_query(run_id=self._run.id,
                                                                          name=History.EXPLANATION_ASSET)
                explanation_assets = list(filter(lambda x: len(x.meta.keys()) > 0, explanation_assets))
                if comment is not None:
                    explanation_assets = list(filter(lambda x: x.meta[History.COMMENT] == comment,
                                                     explanation_assets))
                if raw is not None:
                    def exp_filter(asset):
                        return (asset.meta[ExplainType.IS_RAW].lower() == TRUE.lower()) == raw
                    explanation_assets = list(filter(exp_filter, explanation_assets))
                elif engineered is not None:
                    filtered = filter(lambda x: (x.meta[ExplainType.IS_ENG].lower() == TRUE.lower()) == engineered,
                                      explanation_assets)
                    explanation_assets = list(filtered)
                if len(explanation_assets) == 0:
                    raise ExplanationNotFoundException._with_error(
                        AzureMLError.create(
                            ExplanationFiltersNotFound, explanation_id=explanation_id,
                            filter_names=['comment', 'raw'],
                        )
                    )
            else:
                explanation_assets = explanation_list
            # sort assets by upload time and return latest
            explanation_assets = sorted(explanation_assets, key=lambda asset: asset.created_time)
            explanation_asset = explanation_assets[-1]
            properties = explanation_asset.properties
            if History.EXPLANATION_ID in properties:
                explanation_id = properties[History.EXPLANATION_ID]
            elif History.EXPLANATION_ID in explanation_asset.meta:
                explanation_id = explanation_asset.meta[History.EXPLANATION_ID]

        # everything that might be available from the asset for construction an explanation
        local_importance_vals = None

        # back compat as of March 2019
        is_v2_release_asset = History.VERSION_TYPE in explanation_asset.properties

        if is_v2_release_asset:
            version = explanation_asset.properties[History.VERSION_TYPE]
            is_under_v3_asset = True
        elif History.VERSION in explanation_asset.properties:
            version = explanation_asset.properties[History.VERSION]
            is_under_v3_asset = False
        else:
            version = explanation_asset.meta[History.VERSION]
            # because it can't be v1 or v2 release here
            is_under_v3_asset = version == History.EXPLANATION_ASSET_TYPE_V2
        is_under_v4_asset = is_under_v3_asset or version == History.EXPLANATION_ASSET_TYPE_V3
        is_under_v5_asset = is_under_v4_asset or version == History.EXPLANATION_ASSET_TYPE_V4
        is_under_v7_asset = (is_under_v5_asset or version == History.EXPLANATION_ASSET_TYPE_V5
                             or version == History.EXPLANATION_ASSET_TYPE_V6)
        is_under_v8_asset = is_under_v7_asset or version == History.EXPLANATION_ASSET_TYPE_V7
        if is_under_v5_asset:
            mli_extension = '.json'
        file_dict = _download_artifacts(self._run, download_dir, mli_extension, explanation_id=explanation_id)

        module_logger.debug('Explanation asset is version {}'.format(version))
        if ExplainType.EXPLAIN in explanation_asset.properties:
            explanation_method = explanation_asset.properties[ExplainType.EXPLAIN]
        elif ExplainType.EXPLAIN in explanation_asset.meta:
            # backcompat May 2020
            explanation_method = explanation_asset.meta[ExplainType.EXPLAIN]
        else:
            # backwards compatibilty as of February 2019
            explanation_method = ExplainType.SHAP
        storage_metadata = _load_artifact(file_dict[History.RICH_METADATA] + mli_extension)
        # classification and local importances are stored differently in non v1 assets
        if ExplainType.MODEL in explanation_asset.properties:
            classification = explanation_asset.properties[ExplainType.MODEL] == ExplainType.CLASSIFICATION
        elif ExplainType.MODEL in explanation_asset.meta:
            # May 2020
            classification = explanation_asset.meta[ExplainType.MODEL] == ExplainType.CLASSIFICATION
        elif is_v2_release_asset:
            classification = History.PER_CLASS_VALUES in storage_metadata
        if History.LOCAL_IMPORTANCE_VALUES in storage_metadata:
            module_logger.debug('Downloading local importance values from >=v2')
            local_importance_vals = np.array(_download_artifact(self._run,
                                                                download_dir,
                                                                History.LOCAL_IMPORTANCE_VALUES,
                                                                mli_extension,
                                                                explanation_id=explanation_id))
        elif History.LOCAL_IMPORTANCE_VALUES_SPARSE in storage_metadata:
            module_logger.debug('Downloading sparse local importance values')
            local_vals_sparse = _download_artifact(self._run, download_dir,
                                                   History.LOCAL_IMPORTANCE_VALUES_SPARSE,
                                                   mli_extension, explanation_id=explanation_id)
            local_importance_vals = self._convert_artifact_to_sparse_local(local_vals_sparse)
        elif is_v2_release_asset:
            module_logger.debug('Downloading local importance values from release v2')
            local_importance_vals = np.array(_load_artifact(file_dict[BackCompat.SHAP_VALUES] + mli_extension))
        if History.FEATURES in file_dict:
            kwargs[ExplainParams.FEATURES] = np.array(_load_artifact(file_dict[History.FEATURES] + mli_extension))
        else:
            try:
                # v2 release asset back compat as of March 2019
                kwargs[ExplainParams.FEATURES] = _download_artifact(self._run, download_dir, History.FEATURES,
                                                                    mli_extension, explanation_id=explanation_id)
            except UserErrorException:
                kwargs[ExplainParams.FEATURES] = None

        if not is_under_v8_asset:
            kwargs[ExplainParams.MODEL_TYPE] = explanation_asset.properties[ExplainType.MODEL_CLASS]
            explanation_method = explanation_asset.properties[ExplainType.METHOD]
            is_raw = explanation_asset.properties.get(ExplainType.IS_RAW, FALSE).lower() == TRUE.lower()
            kwargs[ExplainParams.IS_RAW] = is_raw
            is_eng = explanation_asset.properties.get(ExplainType.IS_ENG, FALSE).lower() == TRUE.lower()
            kwargs[ExplainParams.IS_ENG] = is_eng
            if History.INIT_DATASET_ID in storage_metadata:
                kwargs[History.INIT_DATA] = storage_metadata[History.INIT_DATASET_ID]
            if History.EVAL_DATASET_ID in storage_metadata:
                kwargs[History.EVAL_DATA] = storage_metadata[History.EVAL_DATASET_ID]
            if History.EVAL_Y_PRED in storage_metadata:
                kwargs[History.EVAL_Y_PRED] = storage_metadata[History.EVAL_Y_PRED]
            if History.EVAL_Y_PRED_PROBA in storage_metadata:
                kwargs[History.EVAL_Y_PRED_PROBA] = storage_metadata[History.EVAL_Y_PRED_PROBA]
            if History.MODEL_ID in explanation_asset.properties:
                kwargs[History.MODEL_ID] = explanation_asset.properties[History.MODEL_ID]
            if History.NUM_FEATURES in explanation_asset.properties:
                num_features = explanation_asset.properties[History.NUM_FEATURES]
                kwargs[History.NUM_FEATURES] = int(num_features) if isinstance(num_features, str) else num_features
        elif not is_under_v4_asset:
            # May 2020
            kwargs[ExplainParams.MODEL_TYPE] = explanation_asset.meta[ExplainType.MODEL_CLASS]
            explanation_method = explanation_asset.meta[ExplainType.METHOD]
            is_raw = explanation_asset.meta.get(ExplainType.IS_RAW, FALSE).lower() == TRUE.lower()
            kwargs[ExplainParams.IS_RAW] = is_raw
            is_eng = explanation_asset.meta.get(ExplainType.IS_ENG, FALSE).lower() == TRUE.lower()
            kwargs[ExplainParams.IS_ENG] = is_eng
            if History.INIT_DATASET_ID in storage_metadata:
                kwargs[History.INIT_DATA] = storage_metadata[History.INIT_DATASET_ID]
            if History.EVAL_DATASET_ID in storage_metadata:
                kwargs[History.EVAL_DATA] = storage_metadata[History.EVAL_DATASET_ID]
            if History.EVAL_Y_PRED in storage_metadata:
                kwargs[History.EVAL_Y_PRED] = storage_metadata[History.EVAL_Y_PRED]
            if History.EVAL_Y_PRED_PROBA in storage_metadata:
                kwargs[History.EVAL_Y_PRED_PROBA] = storage_metadata[History.EVAL_Y_PRED_PROBA]
            if History.MODEL_ID in explanation_asset.meta:
                kwargs[History.MODEL_ID] = explanation_asset.meta[History.MODEL_ID]
            if History.NUM_FEATURES in explanation_asset.meta:
                num_features = explanation_asset.meta[History.NUM_FEATURES]
                kwargs[History.NUM_FEATURES] = int(num_features) if isinstance(num_features, str) else num_features

        kwargs[ExplainParams.METHOD] = explanation_method
        kwargs[ExplainParams.CLASSIFICATION] = classification
        if classification:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.CLASSIFICATION
        else:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.REGRESSION
        if History.EXPECTED_VALUES in storage_metadata or is_v2_release_asset:
            module_logger.debug('Downloading expected values')
            expected_values_artifact = _download_artifact(self._run,
                                                          download_dir,
                                                          History.EXPECTED_VALUES,
                                                          mli_extension,
                                                          explanation_id=explanation_id)
            kwargs[ExplainParams.EXPECTED_VALUES] = np.array(expected_values_artifact)

        if local_importance_vals is not None:
            module_logger.debug('Creating local explanation')
            local_explanation = _create_local_explanation(local_importance_values=local_importance_vals,
                                                          explanation_id=explanation_id,
                                                          **kwargs)
            kwargs[ExplainParams.LOCAL_EXPLANATION] = local_explanation
            no_short_global_values = History.GLOBAL_VALUES not in storage_metadata
            if no_short_global_values and BackCompat.GLOBAL_IMPORTANCE_VALUES not in storage_metadata:
                module_logger.debug('Global importance values not found, returning local explanation')
                return local_explanation

        # Include everything available on storage metadata
        if History.CLASSES in storage_metadata:
            module_logger.debug('Downloading class names')
            if History.NUM_CLASSES in explanation_asset.properties:
                num_classes = explanation_asset.properties[History.NUM_CLASSES]
                kwargs[History.NUM_CLASSES] = int(num_classes) if isinstance(num_classes, str) else num_classes
            elif History.NUM_CLASSES in explanation_asset.meta:
                num_classes = explanation_asset.meta[History.NUM_CLASSES]
                kwargs[History.NUM_CLASSES] = int(num_classes) if isinstance(num_classes, str) else num_classes
            try:
                # v2 release asset back compat as of March 2019
                kwargs[ExplainParams.CLASSES] = _download_artifact(self._run,
                                                                   download_dir,
                                                                   History.CLASSES,
                                                                   mli_extension,
                                                                   explanation_id=explanation_id)
            except UserErrorException:
                kwargs[ExplainParams.CLASSES] = None

        download_list = [
            History.GLOBAL_NAMES,
            History.GLOBAL_RANK,
            History.GLOBAL_VALUES,
            History.PER_CLASS_NAMES,
            History.PER_CLASS_RANK,
            History.PER_CLASS_VALUES,
            # back compat April 2020
            BackCompat.GLOBAL_IMPORTANCE_NAMES,
            BackCompat.GLOBAL_IMPORTANCE_RANK,
            BackCompat.GLOBAL_IMPORTANCE_VALUES
        ]

        downloads = self._download_sharded_data_from_list(download_list,
                                                          storage_metadata,
                                                          download_dir,
                                                          mli_extension,
                                                          explanation_id=explanation_id,
                                                          top_k=top_k)

        if History.GLOBAL_RANK in downloads:
            global_rank = downloads[History.GLOBAL_RANK]
            global_values = downloads[History.GLOBAL_VALUES]
        else:
            # back compat April 2020
            global_rank = downloads[BackCompat.GLOBAL_IMPORTANCE_RANK]
            global_values = downloads[BackCompat.GLOBAL_IMPORTANCE_VALUES]
        kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK] = global_rank

        if History.PER_CLASS_RANK in downloads:
            kwargs[History.PER_CLASS_RANK] = downloads[History.PER_CLASS_RANK]

        global_rank_length = len(kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK])
        # check that the full explanation is available in run history so that it can be unsorted
        if kwargs[History.FEATURES] is not None:
            full_available = global_rank_length == len(kwargs[History.FEATURES])
        else:
            full_available = max(kwargs[ExplainParams.GLOBAL_IMPORTANCE_RANK]) == global_rank_length - 1

        if top_k is None and full_available:
            # if we retrieve the whole explanation, we can reconstruct unsorted value order
            global_importance_values_unsorted = _unsort_1d(global_values, global_rank)
            kwargs[ExplainParams.GLOBAL_IMPORTANCE_VALUES] = global_importance_values_unsorted

            if History.PER_CLASS_RANK in downloads:
                per_class_importance_values_unsorted = _unsort_2d(downloads[History.PER_CLASS_VALUES],
                                                                  downloads[History.PER_CLASS_RANK])
                kwargs[History.PER_CLASS_VALUES] = per_class_importance_values_unsorted
        else:
            # if we only retrieve top k, unsorted values cannot be fully reconstructed
            if History.GLOBAL_NAMES in downloads:
                kwargs[History.RANKED_GLOBAL_NAMES] = downloads[History.GLOBAL_NAMES]
            if BackCompat.GLOBAL_IMPORTANCE_NAMES in downloads:
                kwargs[History.RANKED_GLOBAL_NAMES] = downloads[BackCompat.GLOBAL_IMPORTANCE_NAMES]
            kwargs[History.RANKED_GLOBAL_VALUES] = global_values

            if History.PER_CLASS_RANK in downloads:
                if History.PER_CLASS_NAMES in downloads:
                    kwargs[History.RANKED_PER_CLASS_NAMES] = downloads[History.PER_CLASS_NAMES]
                kwargs[History.RANKED_PER_CLASS_VALUES] = downloads[History.PER_CLASS_VALUES]
        return _create_global_explanation(explanation_id=explanation_id, **kwargs)

    def list_model_explanations(self, comment=None, raw=None, engineered=None):
        """Return a dictionary of metadata for all model explanations available.

        :param comment: A string used to filter explanations based on the strings they were uploaded with. Requires an
            exact match.
        :type comment: str
        :param raw: If True or False, explanations will be filtered based on whether they are raw or not. If nothing
            is specified, this filter will not be applied.
        :type raw: bool or None
        :param engineered: If True or False, explanations will be filtered based on whether they are engineered or
            not. If nothing is specified, this filter will not be applied.
        :type engineered: bool or None
        :return: A dictionary of explanation metadata such as id, data type, explanation method, model type,
            and upload time, sorted by upload time
        :rtype: dict
        """
        module_logger.debug('Listing model explanations')
        assets_client = AssetsClient(self._run.experiment.workspace.service_context)
        properties = {}
        if comment is not None:
            properties[History.COMMENT] = comment
        if raw is not None:
            properties[ExplainType.IS_RAW] = str(raw)
        if engineered is not None:
            properties[ExplainType.IS_ENG] = str(engineered)
        explanation_assets = list(assets_client.list_assets_with_query(run_id=self._run.id,
                                                                       properties=properties,
                                                                       asset_type=self._get_asset_type()))
        if len(explanation_assets) == 0:
            # June 2020
            explanation_assets = assets_client.list_assets_by_properties_run_id_name(self._run.id,
                                                                                     History.EXPLANATION_ASSET,
                                                                                     properties)
        output_summary = []
        if len(explanation_assets) > 0:
            for asset in explanation_assets:
                props = asset.properties
                if History.COMMENT in props:
                    meta_dict = {
                        History.ID: props[History.EXPLANATION_ID] if History.EXPLANATION_ID in props else None,
                        History.COMMENT: props[History.COMMENT] if History.COMMENT in props else None,
                        ExplainType.DATA: props[ExplainType.DATA] if ExplainType.DATA in props else None,
                        ExplainType.EXPLAIN: props[ExplainType.EXPLAIN] if ExplainType.EXPLAIN in props else None,
                        ExplainType.MODEL: props[ExplainType.MODEL] if ExplainType.MODEL in props else None,
                        ExplainType.IS_RAW: props[ExplainType.IS_RAW] if ExplainType.IS_RAW in props else None,
                        ExplainType.IS_ENG: props[ExplainType.IS_ENG] if ExplainType.IS_ENG in props else None,
                        History.UPLOAD_TIME: asset.created_time
                    }
                    output_summary.append(meta_dict)
                else:
                    asset_meta_dict = self._v6_output_summary(asset, comment, raw, engineered)
                    if asset_meta_dict is not None:
                        output_summary.append(asset_meta_dict)
        else:
            explanation_assets = list(assets_client.list_assets_with_query(run_id=self._run.id,
                                                                           name=History.EXPLANATION_ASSET))
            for asset in explanation_assets:
                asset_meta_dict = self._v6_output_summary(asset, comment, raw, engineered)
                if asset_meta_dict is not None:
                    output_summary.append(asset_meta_dict)
        return sorted(output_summary, key=lambda meta: meta[History.UPLOAD_TIME])

    def _v6_output_summary(self, asset, comment, raw, engineered):
        """Backwards compatibility as of May 2020."""

        if comment is not None:
            if History.COMMENT not in asset.meta or asset.meta[History.COMMENT] != comment:
                return None
        if raw is not None:
            if ExplainType.IS_RAW not in asset.meta or (asset.meta[ExplainType.IS_RAW].lower() == TRUE.lower()) != raw:
                return None
        if engineered is not None:
            no_eng = ExplainType.IS_ENG not in asset.meta
            if no_eng or (asset.meta[ExplainType.IS_ENG].lower() == TRUE.lower()) != engineered:
                return None
        meta_dict = {
            History.ID: asset.meta[History.EXPLANATION_ID] if History.EXPLANATION_ID in asset.meta else None,
            History.COMMENT: asset.meta[History.COMMENT] if History.COMMENT in asset.meta else None,
            ExplainType.DATA: asset.meta[ExplainType.DATA] if ExplainType.DATA in asset.meta else None,
            ExplainType.EXPLAIN: asset.meta[ExplainType.EXPLAIN] if ExplainType.EXPLAIN in asset.meta else None,
            ExplainType.MODEL: asset.meta[ExplainType.MODEL] if ExplainType.MODEL in asset.meta else None,
            ExplainType.IS_RAW: asset.meta[ExplainType.IS_RAW] if ExplainType.IS_RAW in asset.meta else None,
            ExplainType.IS_ENG: asset.meta[ExplainType.IS_ENG] if ExplainType.IS_ENG in asset.meta else None,
            History.UPLOAD_TIME: asset.created_time
        }
        return meta_dict

    def _download_sharded_data(self, download_dir, storage_metadata, name, extension, explanation_id=None,
                               top_k=None):
        """Download and aggregate a chunk of data from its sharded storage format.

        :param download_dir: The directory to which the asset's files should be downloaded.
        :type download_dir: str
        :param storage_metadata: The metadata dictionary for the asset's stored data.
        :type storage_metadata: dict[str: dict[str: Union(str, int)]]
        :param name: The name/data type of the chunk to save to download_dir.
        :type name: str
        :param extension: '.interpret.json' for v5, '.json' for earlier versions.
        :type extension: str
        :param explanation_id: The explanation ID the data is stored under.
            If None, it is assumed that the asset is using an old storage format.
        :type explanation_id: str
        :param top_k: If specified, limit the ordered data returned to the most important features and values
        :type top_k: int
        :return: The data chunk, anything from 1D to 3D.
        :rtype: int or str
        """
        num_columns_to_return = int(storage_metadata[name][History.NUM_FEATURES])
        if top_k is not None:
            module_logger.debug('Top k is set, potentially reducing number of columns returned')
            num_columns_to_return = min(top_k, num_columns_to_return)
        num_blocks = int(storage_metadata[name][History.NUM_BLOCKS])
        if BackCompat.OLD_NAME in storage_metadata[name]:
            module_logger.debug('Working with constructed metadata from a v1 asset')
            # Backwards compatibility as of January 2019
            name = storage_metadata[name][BackCompat.OLD_NAME]
        # Backwards compatibility as of February 2019
        connector = '/' if explanation_id is not None else '_'
        artifact = _download_artifact(self._run, download_dir, '{}{}0'.format(name, connector), extension,
                                      explanation_id=explanation_id)
        full_data = np.array(artifact)
        concat_dim = full_data.ndim - 1
        # Get the blocks
        for idx in range(1, num_blocks):
            block_name = '{}{}{}'.format(name, connector, idx)
            block = np.array(_download_artifact(self._run, download_dir, block_name, extension))
            full_data = np.concatenate([full_data, block], axis=concat_dim)
            num_columns_read = full_data.shape[concat_dim]
            if num_columns_read >= num_columns_to_return:
                break
        full_data_list = full_data[..., :num_columns_to_return]
        return full_data_list

    def _download_sharded_data_from_list(self,
                                         data_list,
                                         storage_metadata,
                                         download_dir,
                                         extension,
                                         explanation_id=None,
                                         top_k=None):
        """Check each data name in the list.

        If available on the stored explanation, download the sharded chunks and reconstruct the explanation.

        :param list: A list of data names for each kind of data to download.
        :type list: list[str]
        :param storage_metadata: The metadata dictionary for the asset's stored data.
        :type storage_metadata: dict[str: dict[str: Union(str, int)]]
        :param download_dir: The directory to which the asset's files should be downloaded.
        :type download_dir: str
        :param extension: '.interpret.json' for v5, '.json' for earlier versions.
        :type extension: str
        :param explanation_id: The explanation ID the data is stored under.
            If None, it is assumed that the asset is using an old storage format.
        :type explanation_id: str
        :param top_k: If specified, limit the ordered data returned to the most important features and values
        :type top_k: int
        :return: A dictionary of the data that was able to be downloaded from run history.
        :rtype: dict
        """
        output_kwargs = {}
        for history_name in data_list:
            if history_name in storage_metadata:
                module_logger.debug('Downloading ' + history_name)
                values = self._download_sharded_data(download_dir,
                                                     storage_metadata,
                                                     history_name,
                                                     extension,
                                                     explanation_id=explanation_id,
                                                     top_k=top_k)
                output_kwargs[history_name] = np.array(values)
        return output_kwargs

    def _get_v2_file_dict_from_v1(self, v1_file_dict):
        v1_dict_copy = v1_file_dict.copy()
        names_dict = {
            BackCompat.FEATURE_NAMES: History.FEATURES,
            BackCompat.OVERALL_FEATURE_ORDER: BackCompat.GLOBAL_IMPORTANCE_NAMES,
            BackCompat.OVERALL_IMPORTANCE_ORDER: BackCompat.GLOBAL_IMPORTANCE_RANK,
            BackCompat.OVERALL_SUMMARY: BackCompat.GLOBAL_IMPORTANCE_VALUES,
            BackCompat.PER_CLASS_FEATURE_ORDER: History.PER_CLASS_NAMES,
            BackCompat.PER_CLASS_IMPORTANCE_ORDER: History.PER_CLASS_RANK,
            BackCompat.PER_CLASS_SUMMARY: History.PER_CLASS_VALUES
        }

        for key in v1_dict_copy.keys():
            if key in names_dict:
                v1_file_dict[names_dict[key]] = v1_file_dict[key]

        return v1_file_dict

    def _get_v2_metadata_from_v1(self, v1_metadata):
        """Convert the v1 asset metadata dict to a v2 asset metadata dict.

        :param v1_metadata: A flat dict of v1 metadata.
        :type v1_metadata: dict[str: int]
        :return: A rich dict of v2 metadata.
        :rtype: dict[str: dict[str: Union(str, int)]]
        """
        storage_metadata = {
            BackCompat.GLOBAL_IMPORTANCE_NAMES: self._get_v2_shard_from_v1(v1_metadata,
                                                                           BackCompat.OVERALL_FEATURE_ORDER,
                                                                           BackCompat.GLOBAL_IMPORTANCE_NAMES),
            BackCompat.GLOBAL_IMPORTANCE_RANK: self._get_v2_shard_from_v1(v1_metadata,
                                                                          BackCompat.OVERALL_IMPORTANCE_ORDER,
                                                                          BackCompat.GLOBAL_IMPORTANCE_RANK),
            BackCompat.GLOBAL_IMPORTANCE_VALUES: self._get_v2_shard_from_v1(v1_metadata,
                                                                            BackCompat.OVERALL_SUMMARY,
                                                                            BackCompat.GLOBAL_IMPORTANCE_VALUES)
        }

        # these fields may or may not exist on v1 assets
        if History.BLOCK_SIZE + '_' + BackCompat.PER_CLASS_FEATURE_ORDER in v1_metadata:
            storage_metadata[History.PER_CLASS_NAMES] = \
                self._get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_FEATURE_ORDER, History.PER_CLASS_NAMES)
            storage_metadata[History.PER_CLASS_RANK] = \
                self._get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_IMPORTANCE_ORDER, History.PER_CLASS_RANK)
            storage_metadata[History.PER_CLASS_VALUES] = \
                self._get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_SUMMARY, History.PER_CLASS_VALUES)
        if History.NUM_CLASSES in v1_metadata:
            class_dict = {
                BackCompat.NAME: History.CLASSES,
                History.NUM_CLASSES: v1_metadata[History.NUM_CLASSES]
            }
            storage_metadata[History.CLASSES] = class_dict
        return storage_metadata

    @staticmethod
    def _get_v2_shard_from_v1(v1_metadata, v1_name, v2_name):
        """Get specific metadata for v2 shards from v1 metadata.

        :param v1_metadata: A flat dict of v1 metadata.
        :type v1_metadata: dict[str: int]
        :param v1_name: The v1 name for the chunked data.
        :type v1_name: str
        :param v2_name: The v2 name for the chunked data.
        :type v2_name: str
        :return: The dict of shard metadata.
        :rtype: dict[str: str | int]
        """
        return {
            History.NAME: v2_name,
            BackCompat.OLD_NAME: v1_name,
            History.BLOCK_SIZE: v1_metadata[History.BLOCK_SIZE + '_' + v1_name],
            History.MAX_NUM_BLOCKS: v1_metadata[History.MAX_NUM_BLOCKS + '_' + v1_name],
            History.NUM_BLOCKS: v1_metadata[History.NUM_BLOCKS + '_' + v1_name],
            History.NUM_FEATURES: v1_metadata[History.NUM_FEATURES + '_' + v1_name]
        }

    def _upload_dataset_to_service(self, data, explanation, filename, dataset_suffix):
        """Upload data to the Dataset service.

        :param data: One of the data collections passed into an explainer.
        :type data: All the data collection types supported by an explainer plus DatsetWrapper.
        :param explanation: An Explanation object.
        :type explanation: Explanation
        :param filename: The name the file should have on disk and in the Datastore.
        :type file: str
        :param dataset_suffix: The end of the dataset name.
        :type dataset_suffix: str
        :return: The ID of the Dataset if it could be uploaded, else None.
        :rtype: str or None
        """
        EXPLAIN_DATASETS_DIR = './explain_model_datasets/'
        DATASTORE_DIR = '{}{}/'.format(EXPLAIN_DATASETS_DIR, explanation.id)

        FILENAME = filename
        FILEPATH = EXPLAIN_DATASETS_DIR + FILENAME
        if data is not None:
            os.makedirs(EXPLAIN_DATASETS_DIR, exist_ok=True)
            with open(FILEPATH, 'w') as f:
                to_dump = data
                if isinstance(to_dump, DatasetWrapper):
                    to_dump = to_dump.original_dataset
                if isinstance(to_dump, pd.DataFrame):
                    to_dump = to_dump.values.tolist()
                if isinstance(to_dump, np.ndarray):
                    to_dump = to_dump.tolist()
                if sp.sparse.issparse(to_dump):
                    module_logger.warn('Cannot upload a sparse dataset to the Dataset service.')
                    return None
                json.dump(to_dump, f)
            if self._datastore_name is None:
                ds = self._run.experiment.workspace.get_default_datastore()
            else:
                ds = self._run.experiment.workspace.datastores[self._datastore_name]
            module_logger.debug("ds name: {0}".format(ds.name))
            # local and datastore directories don't have to be the same
            # only the filename is kept from local - if you want directories, must go in target_path
            ds.upload_files([FILEPATH], target_path=DATASTORE_DIR, show_progress=False)
            json_path = ds.path('{}{}'.format(DATASTORE_DIR, FILENAME))
            module_logger.debug("json_path: {0}".format(json_path))
            dataset = Dataset.from_json_files(json_path)
            dataset_obj = dataset.register(self._run.experiment.workspace, explanation.id[:12] + dataset_suffix,
                                           exist_ok=True, update_if_exist=True)
            return dataset_obj.id
        return None

    def _download_viz_data(self, raw=False):
        explanation = self.list_model_explanations(raw=raw)[0]
        download_dir = os.path.join('download_viz_data', explanation['id'][:History.ID_PATH_2004])
        os.makedirs(download_dir, exist_ok=True)
        artifact_path = _create_artifact_path(explanation.get('id'))
        self.run.download_files(prefix=artifact_path, output_directory=download_dir, append_prefix=False)

        viz_data_dict = {}
        viz_data = {}
        mli_extension = '.interpret.json'

        # Load the viz data dict
        with open(os.path.join(download_dir, History.VISUALIZATION_DICT + mli_extension), 'rb') as f:
            file_string = f.read()
            viz_data_dict = json.loads(file_string.decode(IO.UTF8))

        # Load the individual data in viz
        eval_data_viz = None
        if VizData.TEST_DATA in viz_data_dict:
            with open(os.path.join(download_dir, History.EVAL_DATA_VIZ + mli_extension), 'rb') as f:
                file_string = f.read()
                eval_data_viz = json.loads(file_string.decode(IO.UTF8))

        true_y_viz = None
        if VizData.TRUE_Y in viz_data_dict:
            with open(os.path.join(download_dir, History.TRUE_YS_VIZ + mli_extension), 'rb') as f:
                file_string = f.read()
                true_y_viz = json.loads(file_string.decode(IO.UTF8))

        viz_data[VizData.TEST_DATA] = eval_data_viz
        viz_data[VizData.TRUE_Y] = true_y_viz
        return viz_data_dict, viz_data

    def _convert_sparse_to_list(self, sparse_local_values):
        """Converts a sparse explanation to a list.

        :param sparse_local_values: The sparse matrix to be converted to a list representation that includes
            the data, indices, indptr and shape.
        :type sparse_local_values: scipy.sparse.csr_matrix
        :return: The local importance values as a list representation.
        :rtype: list[list[int | float]]
        """
        sparse_data = []
        sparse_data.append(sparse_local_values.data.tolist())
        sparse_data.append(sparse_local_values.indices.tolist())
        sparse_data.append(sparse_local_values.indptr.tolist())
        sparse_data.append(list(sparse_local_values.shape))
        return sparse_data

    def _convert_list_to_sparse(self, sparse_local_values_list):
        """Converts a list representation of an explanation to a sparse matrix.

        :param sparse_local_values_list: The list representation that includes
            the data, indices, indptr and shape to be converted to a sparse matrix.
        :type sparse_local_values_list: list[list[int | float]]
        :return: The local importance values as a sparse matrix.
        :rtype: scipy.sparse.csr_matrix
        """
        data = sparse_local_values_list[0]
        indices = sparse_local_values_list[1]
        indptr = sparse_local_values_list[2]
        shape = tuple(sparse_local_values_list[3])
        return sp.sparse.csr_matrix((data, indices, indptr), shape)

    def _convert_artifact_to_sparse_local(self, local_vals_sparse):
        """Converts an artifact to sparse local importance values.

        :param local_vals_sparse: The list representation that includes
            the data, indices, indptr and shape to be converted to a sparse matrix.
            In multiclass case this includes the per class local importance values
            as well, so it will be a 3 dimensional list of values.
        :type local_vals_sparse: list[list[int | float]] or list[list[list[int | float]]]
        :return: The local importance values as a sparse matrix.
        :rtype: list[scipy.sparse.csr_matrix] or scipy.sparse.csr_matrix
        """
        if isinstance(local_vals_sparse[0][0], list):
            local_importance_vals = []
            for class_importance_values in local_vals_sparse:
                local_importance_vals.append(self._convert_list_to_sparse(class_importance_values))
        else:
            local_importance_vals = self._convert_list_to_sparse(local_vals_sparse)
        return local_importance_vals
