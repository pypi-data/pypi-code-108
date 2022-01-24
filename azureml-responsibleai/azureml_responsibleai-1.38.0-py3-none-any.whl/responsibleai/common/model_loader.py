# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model loader used to load AzureML models into memory."""
from abc import ABC, abstractmethod
import tempfile
from typing import Any, Union

from azureml._base_sdk_common._docstring_wrapper import experimental
from azureml.core import Model, Workspace
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track, trace
from azureml.responsibleai.common._constants import LoggingConstants as LogCons

try:
    import mlflow
    mlflow_import_error = False
except ImportError:
    mlflow_import_error = True

_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


@experimental
class ModelLoader(ABC):
    """Model loader used to load AzureML models into memory."""

    @abstractmethod
    def load(self, dirpath):
        """
        Load the model from the specified directory.

        :param dirpath: Directory into which the AzureML model has been downloaded.
        :return: Python model with fit and predict methods.
        """
        raise NotImplementedError

    @track(_get_logger, custom_dimensions={'app_name': 'ModelLoader'}, activity_type=LogCons.PUBLIC_API)
    def load_by_model_id(self,
                         workspace: Workspace,
                         model_id: str) -> object:
        """
        Load the specified model.

        :param workspace: Workspace containing the model
        :param model_id: Identifies the model to load
        """
        model = Model(workspace=workspace, id=model_id)

        download_dir = tempfile.mkdtemp()
        model.download(target_dir=download_dir)
        return self.load(download_dir)

    @staticmethod
    def _load_mlflow_model(workspace: Workspace, model_id: str) -> Any:
        mlflow.set_tracking_uri(workspace.get_mlflow_tracking_uri())

        model = Model._get(workspace, id=model_id)
        model_uri = "models:/{}/{}".format(model.name, model.version)
        return mlflow.pyfunc.load_model(model_uri)._model_impl

    @staticmethod
    @track(_get_logger, custom_dimensions={'app_name': 'ModelLoader'}, activity_type=LogCons.PUBLIC_API)
    def load_model_from_workspace(workspace: Workspace,
                                  model_loader: Union[str, 'ModelLoader'],
                                  model_id: str) -> Any:
        """Load a model via MLFlow or using the ModelLoader.

        :param workspace: The workspace containing the Model
        :param model_loader: Either the string 'mflow' or a ModelLoader object
        :param model_id: The id of the target model '<name>:<version>'
        """
        _logger = _get_logger()
        model_estimator = None
        if isinstance(model_loader, str) and model_loader == "mlflow":
            if mlflow_import_error:
                raise ImportError("mlflow not installed, cannot load mlflow model")
            _logger.info("mlflow model detected")
            model_estimator = ModelLoader._load_mlflow_model(
                workspace=workspace,
                model_id=model_id)
        elif isinstance(model_loader, ModelLoader):
            _logger.info("Loading model using supplied ModelLoader")
            model_estimator = model_loader.load_by_model_id(workspace=workspace,
                                                            model_id=model_id)
        return model_estimator
