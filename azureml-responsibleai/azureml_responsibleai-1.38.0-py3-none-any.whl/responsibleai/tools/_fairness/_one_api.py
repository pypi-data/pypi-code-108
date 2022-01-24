# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import joblib
import json
import os
import pathlib
import shutil
import tempfile
import uuid

from typing import Any, List, Union

from azureml.core import Workspace, Experiment, Run
from azureml.core import Dataset, Model
from azureml.core import RunConfiguration, ScriptRunConfig
from azureml.core.conda_dependencies import CondaDependencies
from azureml.data.tabular_dataset import TabularDataset
from azureml.exceptions import UserErrorException
from azureml._base_sdk_common._docstring_wrapper import experimental

from azureml._common._error_definition import AzureMLError

from azureml.responsibleai.common.model_loader import ModelLoader

from fairlearn.metrics._group_metric_set import _create_group_metric_set
from . import upload_dashboard_dictionary
from azureml.responsibleai.common._errors.error_definitions import (
    DuplicateTargetNameError, InvalidDatasetTypeError, InvalidModelTypeError)
from azureml.responsibleai.common._constants import LoggingConstants as LogCons
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


def _check_dataset(dataset: Union[TabularDataset, str]):
    if not isinstance(dataset, (TabularDataset, str)):
        raise UserErrorException._with_error(
            AzureMLError.create(
                InvalidDatasetTypeError,
                actual_type=type(dataset),
                target='dataset'
            )
        )


def _check_model(model: Union[Model, str]):
    if not isinstance(model, (Model, str)):
        raise UserErrorException._with_error(
            AzureMLError.create(
                InvalidModelTypeError,
                actual_type=type(model),
                target='model'
            )
        )


def _get_model(workspace: Workspace,
               model: Union[str, Model],
               model_loader: ModelLoader):
    """Turn the model_ref into a callable model."""
    _check_model(model)
    if isinstance(model, str):
        m = Model(workspace, id=model)
    else:
        m = model
    # Check model has eliminated alternatives

    download_dir = tempfile.mkdtemp()
    m.download(target_dir=download_dir)
    return m.id, model_loader.load(download_dir)


def _check_col_names(X_col_names: List[str],
                     y_col_name: str,
                     A_col_names: List[str]):
    """Check that y_col_name doesn't appear in X or A."""
    if y_col_name in X_col_names:
        raise UserErrorException._with_error(
            AzureMLError.create(
                DuplicateTargetNameError,
                arg_name='X_column_names',
                target='y_column_name'
            )
        )

    if y_col_name in A_col_names:
        raise UserErrorException._with_error(
            AzureMLError.create(
                DuplicateTargetNameError,
                arg_name='sensitive_feature_column_names',
                target='y_column_name'
            )
        )


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Fairness'}, activity_type=LogCons.PUBLIC_API)
def upload_fairness_local(run: Run,
                          widget_title: str,
                          datastore_name: str,
                          model: Union[str, Model],
                          model_loader: ModelLoader,
                          dataset: Union[str, TabularDataset],
                          X_column_names: List[str],
                          y_column_name: str,
                          sensitive_feature_column_names: List[str],
                          model_type: str) -> str:
    """Create and upload a Fairness widget on the current compute.

    This function takes in a Model and Dataset, and uses them to compute
    and upload fairness data to the given Run.

    The model must be registered in AzureML (and supplied either as
    the Model object itself, or the id), and a model_loader supplied
    as well.
    The model_loader is an object with a `load(model_directory)` method
    which can use the specified directory to provide an object with a
    `predict()` method.

    The dataset must be a TabularDataset, with the X_column_names,
    y_column_name and sensitive_feature_column_names listed out
    (note that y_column_name cannot appear in the other two lists).

    The model_type specifies the kind of model we have,
    binary_classification, regression or prediction. This determines
    the set of metrics calculated.

    Since the uploaded dashboard includes some of the input data (specifically
    the sensitive features specified, along with the true and predicted values),
    there is a mandatory `datastore_name` argument to specify the destination
    for the upload. Controls on this datastore may prevent the dashboard from
    rendering in Azure Machine Learning Studio. If there are no confidentiality
    concerns, then `run.experiment.workspace.get_default_datastore().name` may
    be supplied.

    :param run: The run to use for the upload
    :param widget_title: The title for the widget in the portal
    :param datastore_name: The datastore to use for the upload
    :param model: The AzureML model to be used
    :param model_loader: Object to turn downloaded Model files into an object
    :param dataset: The AzureML Dataset to be used
    :param X_column_names: The names of the columns from the dataset
                           to use for X
    :param y_column_name: The name of the column to use for y
    :param sensitive_feature_column_names: The names of the columns
                                           to use as sensitive features
    :param model_type: The kind of model supplied
    """
    _check_col_names(X_column_names, y_column_name,
                     sensitive_feature_column_names)

    # Grab the data
    _check_dataset(dataset)
    if isinstance(dataset, TabularDataset):
        data_df = dataset.to_pandas_dataframe()
        ds_id = dataset.id
        ds_name = dataset.name
    elif isinstance(dataset, str):
        ds = Dataset.get_by_id(
            workspace=run.experiment.workspace,
            id=dataset)
        data_df = ds.to_pandas_dataframe()
        ds_id = dataset
        ds_name = None
    # No else due to _check_dataset
    X = data_df[X_column_names]
    y_true = data_df[y_column_name]
    A = data_df[sensitive_feature_column_names]

    # Get the model
    model_id, loaded_model = _get_model(
        run.experiment.workspace,
        model,
        model_loader)

    # Generate y_pred
    y_pred = loaded_model.predict(X)

    # Generate the dashboard_dict
    A_dict = A.to_dict(orient='list')
    dash_dict = _create_group_metric_set(y_true=y_true,
                                         predictions={model_id: y_pred},
                                         sensitive_features=A_dict,
                                         prediction_type=model_type)
    # Upload it
    widget_id = upload_dashboard_dictionary(run,
                                            datastore_name,
                                            dash_dict,
                                            dashboard_name=widget_title,
                                            dataset_id=ds_id,
                                            dataset_name=ds_name)

    return widget_id

# ===================================================================


script_name = '_fairness_script.py'

pip_packages = [
    'azureml-dataset-runtime',
    'azureml-responsibleai'
]


def _make_dir_and_copy_files():
    script_temp_dir = pathlib.Path(tempfile.mkdtemp())

    current_dir = pathlib.Path(os.path.dirname(__file__))

    target_files = [
        script_name
    ]

    for target in target_files:
        src_path = current_dir / target
        shutil.copy(str(src_path), str(script_temp_dir))

    return script_temp_dir.resolve()


@experimental
@track(_get_logger, custom_dimensions={'app_name': 'Fairness'}, activity_type=LogCons.PUBLIC_API)
def upload_fairness_remote(workspace: Workspace,
                           run_config: RunConfiguration,
                           experiment_name: str,
                           widget_title: str,
                           datastore_name: str,
                           model: Union[str, Model],
                           model_loader: Any,
                           dataset: Union[str, TabularDataset],
                           X_column_names: List[str],
                           y_column_name: str,
                           sensitive_feature_column_names: List[str],
                           model_type: str) -> Run:
    """Create and upload fairness widget using a remote run.

    This function runs the `upload_fairness_local` function in
    a remote AzureML run. As such, rather than a Run object,
    this accepts a Workspace, RunConfiguration and experiment name.

    Since the uploaded dashboard includes some of the input data (specifically
    the sensitive features specified, along with the true and predicted values),
    there is a mandatory `datastore_name` argument to specify the destination
    for the upload. Controls on this datastore may prevent the dashboard from
    rendering in Azure Machine Learning Studio. If there are no confidentiality
    concerns, then `run.experiment.workspace.get_default_datastore().name` may
    be supplied.

    :param workspace: The AzureML workspace to use
    :param run_config: A `RunConfiguration` object specifying the required dependencies
                       and compute target
    :param experiment_name: The name of the experiment in which to create the run
    :param widget_title: The title for the widget in the portal
    :param datastore_name: The datastore in which to store the upload
    :param model: The AzureML model to be used
    :param model_loader: Object to turn downloaded Model files into an object
    :param dataset: The AzureML Dataset to be used
    :param X_column_names: The names of the columns from the dataset
                           to use for X
    :param y_column_name: The name of the column to use for y
    :param sensitive_feature_column_names: The names of the columns
                                           to use as sensitive features
    :param model_type: The kind of model supplied
    """
    # Sanity checks
    _check_col_names(X_column_names,
                     y_column_name,
                     sensitive_feature_column_names)

    # Extract the Model id
    m_id, _ = _get_model(workspace, model, model_loader)

    # Run upload_fairness_local() in a
    # remote run
    script_temp_dir = _make_dir_and_copy_files()

    # Pickle the loader
    loader_filename = "loader-{0}.pkl".format(uuid.uuid4())

    joblib.dump(value=model_loader,
                filename=str(script_temp_dir / loader_filename))

    # Add the dependencies we need
    passed_in_packages = [
        CondaDependencies._get_package_name_with_extras(x)
        for x in
        run_config.environment.python.conda_dependencies.pip_packages
    ]
    for p in pip_packages:
        # Don't override a package that a user passed in
        p_with_extras = CondaDependencies._get_package_name_with_extras(p)
        if p_with_extras not in passed_in_packages:
            run_config.environment.python.conda_dependencies.add_pip_package(p)

    # Grab the model

    # Find the dataset id
    _check_dataset(dataset)
    if isinstance(dataset, TabularDataset):
        dataset_id = dataset.id
    elif isinstance(dataset, str):
        dataset_id = dataset
    # No else due to _check_dataset call

    # Generate the arguments for the script
    script_arguments = [
        '--title', widget_title,
        '--datastore', datastore_name,
        '--model_id', m_id,
        '--model_loader_file', loader_filename,
        '--dataset_id', dataset_id,
        '--X_column_names', json.dumps(list(X_column_names)),
        '--y_column_name', y_column_name,
        '--A_column_names', json.dumps(list(sensitive_feature_column_names)),
        '--prediction_type', model_type
    ]

    script_run_config = ScriptRunConfig(source_directory=str(script_temp_dir),
                                        script=script_name,
                                        run_config=run_config,
                                        arguments=script_arguments)

    experiment = Experiment(workspace, experiment_name)
    run = experiment.submit(script_run_config)

    return run
