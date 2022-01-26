from typing import TYPE_CHECKING, Optional, Union
from dataclasses import asdict
from pathlib import Path

from marshmallow_dataclass import dataclass as ma_dataclass

from workspace_clients import AssetModel, ContainerModel, WorkspaceServiceAssetsClient, WorkspaceServiceContainersClient
from adt_clients import Granularity, AnalyticDatasetFormat, AnalyticDatasetModel
from dataclasses import InitVar
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from iqvia_e360 import E360Context


@ma_dataclass
class ClientStoreAssetModel(AssetModel):
    e360_context: InitVar['E360Context'] = None
    delete_method: Optional[str] = None
    service_client: Optional[str] = None

    def __post_init__(self, assets_client: 'WorkspaceServiceAssetsClient', e360_context: 'E360Context') -> None:
        self.e360_context = e360_context
        self.assets_client = assets_client

    @property
    def can_purge(self) -> bool:
        return self.e360_context and self.delete_method and self.service_client

    @classmethod
    def type_matches(cls, model: AssetModel):
        return cls.type == model.type and cls.subtype == model.subtype

    @classmethod
    def create(cls, model: AssetModel, store: 'E360Context') -> 'ClientStoreAssetModel':
        for klass in ClientStoreAssetModel.__subclasses__():
            if klass.type_matches(model):
                return klass(e360_context=store, assets_client=model.assets_client, **asdict(model))
        return ClientStoreAssetModel(e360_context=store, assets_client=model.assets_client, **asdict(model))

    def delete(self, purge: bool = False) -> bool:
        """
        Delete service resources first, as some rely on WS assets to test access rights
        """
        cont = True
        if self.can_purge and purge and self.metadata.get("LocalAssetId"):
            client = getattr(self.e360_context, self.service_client)()
            cont = getattr(client, self.delete_method)(self.metadata["LocalAssetId"])
        return cont and super().delete()


@ma_dataclass
class AdtReportAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete"
    service_client: str = "get_adt_client"
    type: str = "Analytic Dataset"
    subtype: str = "Report"

    def download(self, location: Union[Path, str] = None) -> Path:
        return self.e360_context.download_adt_report(self, location)

    def delete(self, purge: bool = False) -> bool:
        """
        ADT will delete workspace assets when the report is deleted
        """
        if self.metadata.get("LocalAssetId"):
            client = getattr(self.e360_context, self.service_client)()
            return getattr(client, self.delete_method)(self.metadata["LocalAssetId"])
        return True


@ma_dataclass
class AdtDefinitionAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete"
    service_client: str = "get_adt_definition_client"
    type: str = "Analytic Dataset"
    subtype: str = "Definition"

    def delete(self, purge: bool = False) -> bool:
        """
        ADT will delete workspace assets when the definition is deleted
        """
        if self.metadata.get("LocalAssetId"):
            client = getattr(self.e360_context, self.service_client)()
            return getattr(client, self.delete_method)(self.metadata["LocalAssetId"])
        return True


@ma_dataclass
class FileAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete_by_id"
    service_client: str = "get_fs_client"
    type: str = "Document"
    subtype: Optional[str] = None

    def delete(self, purge: bool = False) -> bool:
        cont = True
        if purge and self.metadata.get("Document/FileId"):
            client = getattr(self.e360_context, self.service_client)()
            cont = getattr(client, self.delete_method)(self.metadata["Document/FileId"])
        return cont and super().delete()


@ma_dataclass
class PlotlyVisualizationAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete_by_id"
    service_client: str = "get_vrs_plotly_client"
    type: str = "Visualisation"

    @classmethod
    def type_matches(cls, model: AssetModel) -> bool:
        return cls.type == model.type and model.metadata and model.metadata.get("VisType") == "Plotly"


@ma_dataclass
class VisualizationAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete_by_id"
    service_client: str = "get_vrs_client"
    type: str = "Visualisation"

    @classmethod
    def type_matches(cls, model: AssetModel) -> bool:
        return cls.type == model.type and model.metadata and model.metadata.get("VisType") == "GWAS"


@ma_dataclass
class ContainerAssetModel(ContainerModel):
    e360_context: InitVar['E360Context'] = None  # type: ignore

    def __post_init__(self, containers_client: 'WorkspaceServiceContainersClient', e360_context: 'E360Context') -> None:
        self.e360_context = e360_context
        self.containers_client = containers_client

    def upload_adt_file(self, file_path: Union[Path, str], name: str,
                        granularity: Granularity,
                        format_: AnalyticDatasetFormat, dataset_release_id: str = None) -> AnalyticDatasetModel:
        return self.e360_context.upload_adt_file(self, file_path, name, granularity, format_, dataset_release_id)

    def create_child_container(self, name: str, description: str = "") -> 'ContainerAssetModel':
        return self.e360_context.create_workspace_container(self.id, name, description)

    def upload_document(self, file_path: Union[Path, str], name: str, description: str = "") -> AssetModel:
        return self.e360_context.upload_document_file(self, file_path, name, description)
