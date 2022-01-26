from functools import reduce
from typing import List, Union, Optional, Dict, Any
from dataclasses import asdict
import logging
from pathlib import Path
from uuid import uuid4

from clients_core.api_match_client import MatchSpec
from adt_clients import AnalyticDatasetClient, AnalyticDatasetDefinitionClient
from adt_clients.models import AnalyticDatasetModel, Granularity, AnalyticDatasetFormat
from workspace_clients import WorkspaceServiceAssetsClient, WorkspaceServiceContainersClient
from workspace_clients.models import AssetType, ContainerModel, AssetModel, AssetEmbed
from sd_clients import ClientStore
from file_service_client import FileServiceClient, FileStoreServiceClient
from vrs_clients import PlotlyVisualizationResourceClient, VisualizationResourceClient
from e360_charting.builders import BaseVisualisation

from iqvia_e360.exceptions import ClientWrapperError
from iqvia_e360.models import AdtReportAssetModel, ContainerAssetModel, ClientStoreAssetModel


logger = logging.getLogger(__name__)
ADT_OUTPUT_TYPE = "AnalyticDataset/OutputType"
ADT_TYPES = {
    "CSV": ("csv", "text/csv"),
    "PARQUET": ("parquet", "application/vnd.apache.parquet"),
    "ZIP": ("zip", "application/zip"),
    "MULTIPARTPARQUETZIP ": ("zip", "application/zip")
}


class E360Context(ClientStore):
    """
    This class contains helper functions for getting hold for REST clients for various E360 services,
    as well as provides a set of convinience functions that will perform actions against E360 services using those clients
    """
    _adt_rest_client: AnalyticDatasetClient
    _adt_definition_rest_client: AnalyticDatasetDefinitionClient
    _ws_asset_rest_client: WorkspaceServiceAssetsClient
    _ws_container_rest_client: WorkspaceServiceContainersClient
    _fs_rest_client: FileServiceClient
    _fss_rest_client: FileStoreServiceClient
    _vrs_plotly_rest_client: PlotlyVisualizationResourceClient
    _vrs_rest_client: VisualizationResourceClient

    def get_vrs_plotly_client(self, user_id: str = None, **kwargs: Any) -> PlotlyVisualizationResourceClient:
        match_spec = MatchSpec(
            "visualization-resource-service",
            "Plotly", 1, 0, 0,
            ["visualizations-service"])
        return self._get_service_client(match_spec, PlotlyVisualizationResourceClient, "_vrs_plotly_rest_client", user_id, **kwargs)

    def get_vrs_client(self, user_id: str = None, **kwargs: Any) -> VisualizationResourceClient:
        match_spec = MatchSpec(
            "visualization-resource-service",
            "Visualizations", 1, 0, 0,
            ["visualizations-service"])
        return self._get_service_client(match_spec, VisualizationResourceClient, "_vrs_rest_client", user_id, **kwargs)

    def get_workspace_asset_client(self, user_id: str = None, **kwargs: Any) -> WorkspaceServiceAssetsClient:
        match_spec = MatchSpec(
            "E360-Workspace-Service",
            "AssetService", 3, 0, 0,
            ["e360_workspace_service"])
        return self._get_service_client(match_spec, WorkspaceServiceAssetsClient, "_ws_asset_rest_client", user_id, **kwargs)

    def get_workspace_container_client(self, user_id: str = None, **kwargs: Any) -> WorkspaceServiceContainersClient:
        match_spec = MatchSpec(
            "E360-Workspace-Service",
            "ContainerService", 2, 0, 0,
            ["e360_workspace_service"])

        return self._get_service_client(match_spec, WorkspaceServiceContainersClient, "_ws_container_rest_clien", user_id, **kwargs)

    def get_fs_client(self, user_id: str = None, **kwargs: Any) -> FileServiceClient:
        match_spec = MatchSpec(
            "E360-File-Service",
            "Files", 1, 0, 0,
            ["file-service"])

        return self._get_service_client(match_spec, FileServiceClient, "_fs_rest_client", user_id, **kwargs)

    def get_fss_client(self, user_id: str = None, **kwargs: Any) -> FileStoreServiceClient:
        match_spec = MatchSpec(
            "E360-Filestore-Service",
            "Files", 1, 0, 0,
            ["file-service"])

        return self._get_service_client(match_spec, FileStoreServiceClient, "_fss_rest_client", user_id, **kwargs)

    def get_adt_definition_client(self, user_id: str = None, **kwargs: Any) -> AnalyticDatasetDefinitionClient:
        match_spec = MatchSpec(
            "E360-AnalyticDatasetTools-Service",
            "AnalyticDatasetDefinition", 1, 0, 0,
            ["e360_analytic_dataset_tools_service"])

        return self._get_service_client(match_spec, AnalyticDatasetDefinitionClient, "_adt_definition_rest_client", user_id, **kwargs)

    def get_adt_client(self, user_id: str = None, **kwargs: Any) -> AnalyticDatasetClient:
        match_spec = MatchSpec(
            "E360-AnalyticDatasetTools-Service",
            "AnalyticDataset", 1, 0, 0,
            ["e360_analytic_dataset_tools_service"])

        return self._get_service_client(match_spec, AnalyticDatasetClient, "_adt_rest_client", user_id, **kwargs)

    def get_adt_reports(self, **filters: Any) -> List[AdtReportAssetModel]:
        """
        Get a list of ADT report assets, filtered by the provided attributes
        """
        ws_client = self.get_workspace_asset_client()
        params = {"subtype": "Report", "embed": "metadata", **filters}
        assets = ws_client.get_assets(type_=AssetType.ANALYTIC_DATASET, params=params)
        # Some corrupted assets are missing LocalAssetId and can't be used for downloads
        downloadable_assets = [asset for asset in assets if asset.metadata and "LocalAssetId" in asset.metadata]
        return [AdtReportAssetModel(e360_context=self, **asdict(i)) for i in downloadable_assets]

    def get_adt_report_by_id(self, id_: str) -> AdtReportAssetModel:
        reports = self.get_adt_reports(metadataKey="LocalAssetId", metadataValue=id_)
        if not reports:
            raise ClientWrapperError(f"No assets found for Analytic Dataset Report: {id_}")
        return reports[0]

    def get_adt_reports_by_name(self, name: str) -> List[AdtReportAssetModel]:
        return self.get_adt_reports(name=name)

    def get_workspace_containers(self, name: str = None) -> List[ContainerAssetModel]:
        ws_client = self.get_workspace_container_client()
        containers = ws_client.get(name=name)
        return [ContainerAssetModel(containers_client=ws_client, e360_context=self, **asdict(i)) for i in containers]

    def move_workspace_asset(self, asset: Union[str, AssetModel],
                             target_container: Union[ContainerModel, str],
                             new_name: str = None, hidden: bool = False) -> AssetModel:
        ws_client = self.get_workspace_asset_client()
        if isinstance(asset, AssetModel):
            asset = asset.id
        if isinstance(target_container, ContainerModel):
            target_container = target_container.id
        payload = [
            {"value": target_container, "path": "/parent/id", "op": "replace"},
            {"value": hidden, "path": "/isHidden", "op": "replace"},
        ]
        if new_name:
            payload.append({"value": new_name, "path": "/name", "op": "replace"})

        return ws_client.patch_asset(asset, payload)

    def create_workspace_container(self, target_container: Union[ContainerModel, str], name: str, description: str = "") -> ContainerAssetModel:
        if isinstance(target_container, ContainerModel):
            target_container = target_container.id
        ws_client = self.get_workspace_container_client()
        new_container = ws_client.post(ContainerModel(name=name, parent={"id": target_container}, description=description))
        return ContainerAssetModel(containers_client=ws_client, e360_context=self, **asdict(new_container))

    def download_adt_report(self, asset: Union[AdtReportAssetModel, str], location: Union[Path, str] = None) -> Optional[Path]:
        if isinstance(asset, str):
            ws_client = self.get_workspace_asset_client()
            asset_model = ws_client.get_by_id(asset)
        else:
            asset_model = asset
        report_id = asset_model.metadata["LocalAssetId"]
        adt_type = ADT_TYPES[asset_model.metadata[ADT_OUTPUT_TYPE]]
        if location is None:
            replace_pairs = [(" ", "_"), ("/", "_")]
            path = reduce(lambda acc, it: acc.replace(*it), replace_pairs, asset_model.name)
            location_path = Path(f"{path}.{adt_type[0]}")
        else:
            location_path = Path(location)
        return self.download_adt_report_by_id(report_id, location_path, adt_type[1])

    def download_adt_report_by_id(self, report_id: str, location: Union[Path, str], content_type: str) -> Optional[Path]:
        location = Path(location)
        adt_client = self.get_adt_client()
        ok = adt_client.download_report(report_id, location, content_type)
        return location if ok else None

    def create_workspace_asset(self, asset: AssetModel) -> AssetModel:
        ws_client = self.get_workspace_asset_client()
        return ws_client.post(asset)

    def upload_document_file(self, target_container: Union[ContainerModel, str], file_path: Union[Path, str], name: str, description: str = "") -> Optional[AssetModel]:
        file_path = Path(file_path)
        if isinstance(target_container, ContainerModel):
            target_container = target_container.id
        fs_client = self.get_fs_client()
        upload = fs_client.create(file_path)
        metadata = {
            "Document/FilePath": file_path.name,
            "Document/FileId": upload["id"]
        }
        asset = AssetModel(
            is_hidden=False,
            id=upload["id"],
            parent={"id": target_container},
            name=name,
            description=description,
            type=AssetType.DOCUMENT.value, metadata=metadata)
        try:
            return self.create_workspace_asset(asset)
        except Exception:
            fs_client.delete_by_id(upload["id"])
            return None

    def upload_adt_file(self, target_container: Union[ContainerModel, str], file_path: Union[Path, str], name: str, granularity: Granularity, format_: AnalyticDatasetFormat, dataset_release_id: str = None) -> AnalyticDatasetModel:
        file_path = Path(file_path)
        adt_client = self.get_adt_client()
        definition_client = self.get_adt_definition_client()
        upload = adt_client.upload_file(file_path, granularity, format_, dataset_release_id=dataset_release_id)
        definition = definition_client.get(upload.definition_id)
        self.move_workspace_asset(definition.asset_id, target_container, name)
        self.move_workspace_asset(upload.asset_id, target_container, name)
        return upload

    def create_plotly_visualization(self, vis_payload: Dict, target_container: Union[ContainerModel, str],
                                    name: str, description: str = "", from_plotly: bool = True) -> AssetModel:
        if isinstance(target_container, ContainerModel):
            target_container = target_container.id
        vrs_client = self.get_vrs_plotly_client()
        vrs_object = vrs_client.create(vis_payload, from_plotly=from_plotly)
        asset = AssetModel(
            id=str(uuid4()),
            parent={"id": target_container},
            name=name,
            description=description,
            type=AssetType.VISUALIZATION.value,
            metadata={
                "LocalAssetId": vrs_object.id,
                "VisType": "Plotly"
            })
        return self.create_workspace_asset(asset)

    def create_plotly_visualization_from_object(self, visualization_obj: BaseVisualisation, target_container: Union[ContainerModel, str],
                                                name: str, description: str = "") -> AssetModel:
        return self.create_plotly_visualization(visualization_obj.dump(), target_container, name, description, from_plotly=False)

    def get_assets(self, *args: Any, user_id: str = None, **kwargs: Any) -> List[AssetModel]:
        ws_client = self.get_workspace_asset_client(user_id)
        embed = kwargs.get("embed", [])
        embed.append(AssetEmbed.METADATA)
        kwargs["embed"] = embed
        assets = ws_client.get_assets(*args, **kwargs)
        return [ClientStoreAssetModel.create(asset, self) for asset in assets]
