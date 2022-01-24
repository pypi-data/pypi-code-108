# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC, abstractmethod
from responsibleai import ModelAnalysis
from typing import Any, Generic, List, TypeVar

from azureml._common._error_definition import AzureMLError
from azureml._restclient.assets_client import AssetsClient
from azureml._restclient.models import Asset
from azureml.core import Experiment, Run, Workspace
from azureml.exceptions import AzureMLException, UserErrorException

from azureml.responsibleai.common._constants import AssetProperties
from azureml.responsibleai.common._errors.error_definitions import AssetNotFoundError
from azureml.responsibleai.tools._common.constants import AzureMLTypes, PropertyKeys


TRequest = TypeVar('TRequest')  # Type for subclasses of BaseRequest


class BaseManager(ABC, Generic[TRequest]):
    def __init__(self,
                 service_context,
                 experiment_name: str,
                 analysis_id: str,
                 model_analysis_run: Run):
        """Initialize the BaseManager."""
        super(BaseManager, self).__init__()
        self._experiment_name = experiment_name
        self._analysis_id = analysis_id
        self._service_context = service_context
        self._assets_client = AssetsClient(service_context)
        self._model_analysis_run = model_analysis_run

        self._assets: List[Asset] = []

    @property
    def experiment_name(self) -> str:
        return self._experiment_name

    @property
    def analysis_id(self) -> str:
        """Return the id of the parent ModelAnalysisRun"""
        return self._analysis_id

    @property
    def _experiment(self):
        workspace = Workspace(
            self._service_context.subscription_id,
            self._service_context.resource_group_name,
            self._service_context.workspace_name,
            auth=self._service_context.get_auth(),
            _disable_service_check=True)
        return Experiment(workspace, self._experiment_name)

    @abstractmethod
    def list(self) -> List:
        """List the objects which have been computed by this manager."""
        pass

    @abstractmethod
    def download_by_id(self, id: str):
        """Download a particular object."""
        pass

    @abstractmethod
    def _compute_and_upload(
        self,
        requests: List[TRequest],
        model_analysis: ModelAnalysis,
        run: Run,
    ):
        """Compute insights from a request and upload the result to a given run."""
        pass

    def _get_asset(
        self,
        id: str,
        asset_type: str,
        version: str,
        id_property: str = AssetProperties.UPLOAD_ID,
    ) -> Asset:
        """Get the asset with the given ID if it exists.
        :param id: ID of the asset.
        :param asset_type: Type of the asset to fetch.
        :param version: Version of asset to fetch.
        :param id_property: Name of the asset ID property.
        :return: Model analysis asset.
        """
        for asset in self._get_assets(asset_type, version):
            if asset.properties.get(id_property) == id:
                return asset

        raise AzureMLException._with_error(
            AzureMLError.create(
                AssetNotFoundError,
                asset_type=asset_type,
                attributes={id_property: id}
            )
        )

    def _get_assets(self, asset_type: str, version: str) -> List[Any]:
        query_props = {
            PropertyKeys.ANALYSIS_TYPE: asset_type,
            PropertyKeys.ANALYSIS_ID: self.analysis_id,
            PropertyKeys.VERSION: version
        }
        self._assets = list(
            self._assets_client.list_assets_with_query(
                properties=query_props,
                asset_type=AzureMLTypes.MODEL_ANALYSIS))

        if len(self._assets) == 0:
            raise UserErrorException._with_error(
                AzureMLError.create(
                    AssetNotFoundError,
                    asset_type=asset_type,
                    attributes=query_props,
                )
            )

        return self._assets
