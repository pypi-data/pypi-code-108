from typing import List
from typing import Optional

from tecton import conf
from tecton._internals import metadata_service
from tecton._internals.sdk_decorators import sdk_public_method
from tecton_proto.metadataservice.metadata_service_pb2 import GetAllEntitiesRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetAllFeatureServicesRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetAllSavedFeatureDataFramesRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetAllTransformationsRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetAllVirtualDataSourcesRequest
from tecton_proto.metadataservice.metadata_service_pb2 import ListWorkspacesRequest
from tecton_proto.metadataservice.metadata_service_pb2 import QueryFeatureViewsRequest


@sdk_public_method
def list_feature_views(workspace_name: Optional[str] = None) -> List[str]:
    """
    Returns a list of all registered FeatureViews.

    :return: A list of strings.
    """
    request = QueryFeatureViewsRequest()
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().QueryFeatureViews(request)
    return [proto.fco_metadata.name for proto in response.feature_views if not proto.HasField("feature_table")]


@sdk_public_method
def list_feature_tables(workspace_name: Optional[str] = None) -> List[str]:
    """
    Returns a list of all registered FeatureTables.

    :return: A list of strings.
    """
    request = QueryFeatureViewsRequest()
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().QueryFeatureViews(request)
    return [proto.fco_metadata.name for proto in response.feature_views if proto.HasField("feature_table")]


@sdk_public_method
def list_feature_services(workspace_name: Optional[str] = None) -> List[str]:
    """
    Returns a list of all registered FeatureServices.

    :return: A list of strings.
    """
    request = GetAllFeatureServicesRequest()
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetAllFeatureServices(request)
    return [proto.fco_metadata.name for proto in response.feature_services]


@sdk_public_method
def list_transformations(workspace_name: Optional[str] = None) -> List[str]:
    """
    Returns a list of all registered Transformations.

    :return: A list of strings.
    """
    request = GetAllTransformationsRequest()
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetAllTransformations(request)
    return [proto.fco_metadata.name for proto in response.new_transformations]


@sdk_public_method
def list_entities(workspace_name: Optional[str] = None) -> List[str]:
    """
    Returns a list of all registered Entities.

    :returns: A list of strings.
    """
    request = GetAllEntitiesRequest()
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetAllEntities(request)
    return [proto.fco_metadata.name for proto in response.entities]


@sdk_public_method
def list_data_sources(workspace_name: Optional[str] = None) -> List[str]:
    """
    Returns a list of the names of all registered Data Sources.

    :return: A list of strings.
    """
    request = GetAllVirtualDataSourcesRequest()
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetAllVirtualDataSources(request)
    return [proto.fco_metadata.name for proto in response.virtual_data_sources]


@sdk_public_method
def list_workspaces() -> List[str]:
    """
    Returns a list of the names of all registered Workspaces.

    :return: A list of strings.
    """
    request = ListWorkspacesRequest()
    response = metadata_service.instance().ListWorkspaces(request)
    return [workspace.name for workspace in response.workspaces]


@sdk_public_method
def list_datasets(workspace_name: Optional[str] = None) -> List[str]:
    """
    Returns a list of all registered Datasets.

    :return: A list of strings.
    """
    request = GetAllSavedFeatureDataFramesRequest()
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetAllSavedFeatureDataFrames(request)
    return [sfdf.info.name for sfdf in response.saved_feature_dataframes]
